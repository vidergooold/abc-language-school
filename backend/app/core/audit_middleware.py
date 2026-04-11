"""Автоматическое логирование всех изменяющих HTTP-запросов.

Принцип работы:
  1. Перехватывает каждый POST / PUT / PATCH / DELETE запрос.
  2. До передачи запроса дальше читает тело и декодирует JWT-токен.
  3. Запускает обработчик, замеряет время.
  4. После ответа записывает запись в audit_log в отдельной асинх сессии.

Правила фильтрации:
  - GET-запросы не логируются (чтение не является изменением).
  - /api/v1/auth/login логируется с action=LOGIN отдельно через write_audit_log().
  - /api/v1/audit/* не логируется (избегаем рекурсию).
  - Тело запроса очищается от полей password / token / secret перед сохранением.
  - Тело > 8 KB не сохраняется (upload endpointы).
  - Ошибка записи в audit не должна убивать основной запрос.
"""
import json
import logging
import time
from typing import Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from jose import jwt, JWTError

logger = logging.getLogger(__name__)

# Методы, которые изменяют данные
_MUTATION_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

# Префиксы, которые не логируем
_SKIP_PREFIXES = (
    "/api/v1/audit",   # избегаем рекурсию
    "/docs",
    "/openapi",
    "/redoc",
)

# Поля, которые нельзя сохранять в лог
_SENSITIVE_FIELDS = {"password", "token", "secret", "access_token", "refresh_token", "hashed_password"}

# Максимальный размер тела запроса для хранения
_MAX_BODY_BYTES = 8192  # 8 KB


def _sanitize(data: dict) -> dict:
    """Замаскирует чувствительные поля в словаре."""
    return {
        k: "***" if k.lower() in _SENSITIVE_FIELDS else v
        for k, v in data.items()
    }


def _action_from_method(method: str, path: str) -> str:
    """Определяет логическое название действия."""
    if method == "POST":
        # Специфичные workflow-эндпоинты
        if "/confirm" in path:   return "CONFIRM"
        if "/reject" in path:    return "REJECT"
        if "/cancel" in path:    return "CANCEL"
        if "/activate" in path:  return "ACTIVATE"
        if "/withdraw" in path:  return "WITHDRAW"
        if "/assign" in path:    return "ASSIGN"
        if "/publish" in path:   return "PUBLISH"
        if "/archive" in path:   return "ARCHIVE"
        if "/pin" in path:       return "PIN"
        if "/like" in path:      return "LIKE"
        if "/login" in path:     return "LOGIN"
        return "CREATE"
    if method == "PUT":    return "UPDATE"
    if method == "PATCH":  return "UPDATE"
    if method == "DELETE": return "DELETE"
    return method


def _entity_from_path(path: str) -> tuple[str, Optional[int]]:
    """Извлекает тип сущности и entity_id из URL.

    Пример: /api/v1/groups/5/lessons → ('groups', 5)
    """
    parts = [p for p in path.split("/") if p and p not in ("api", "v1", "admin")]
    entity_type = parts[0] if parts else "unknown"
    entity_id: Optional[int] = None
    for part in parts[1:]:
        if part.isdigit():
            entity_id = int(part)
            break
    return entity_type, entity_id


def _decode_user_from_request(request: Request) -> tuple[Optional[int], Optional[str], Optional[str]]:
    """Декодирует JWT-токен из заголовка без DB-запроса.

    Returns (user_id, user_email, user_role) or (None, None, None).
    """
    from app.core.security import SECRET_KEY, ALGORITHM

    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None, None, None
    token = auth[7:]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return (
            int(payload.get("sub", 0)) or None,
            payload.get("email"),
            payload.get("role"),
        )
    except (JWTError, Exception):
        return None, None, None


class AuditMiddleware(BaseHTTPMiddleware):
    """Перехватывает все мутирующие запросы и пишет в audit_log."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        # ─ Фильтр 1: только мутирующие методы
        if request.method not in _MUTATION_METHODS:
            return await call_next(request)

        path = request.url.path

        # ─ Фильтр 2: исключения
        if any(path.startswith(p) for p in _SKIP_PREFIXES):
            return await call_next(request)

        # ─ Читаем тело запроса (передаём body дальше через receive)
        body_bytes = await request.body()
        body_str: Optional[str] = None
        if body_bytes and len(body_bytes) <= _MAX_BODY_BYTES:
            try:
                parsed = json.loads(body_bytes.decode("utf-8", errors="replace"))
                if isinstance(parsed, dict):
                    parsed = _sanitize(parsed)
                body_str = json.dumps(parsed, ensure_ascii=False)
            except (json.JSONDecodeError, Exception):
                body_str = body_bytes.decode("utf-8", errors="replace")[:500]

        # ─ Распознаём пользователя из токена (без DB)
        user_id, user_email, user_role = _decode_user_from_request(request)

        # ─ Выполняем запрос
        t_start = time.monotonic()
        # Восстанавливаем receive, чтобы FastAPI мог прочитать body
        async def receive_override():
            return {"type": "http.request", "body": body_bytes, "more_body": False}

        request._receive = receive_override  # type: ignore[attr-defined]
        response = await call_next(request)
        duration_ms = int((time.monotonic() - t_start) * 1000)

        # ─ Определяем сущность и действие
        entity_type, entity_id = _entity_from_path(path)
        action = _action_from_method(request.method, path)

        # ─ Пишем в audit_log в отдельной сессии DB
        try:
            from app.core.database import AsyncSessionLocal
            from app.models.audit import AuditLog

            async with AsyncSessionLocal() as db:
                db.add(AuditLog(
                    user_id=user_id,
                    user_email=user_email,
                    user_role=user_role,
                    action=action,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    http_method=request.method,
                    endpoint=path[:500],
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                    user_agent=request.headers.get("user-agent", "")[:500],
                    ip_address=_get_client_ip(request),
                    request_body=body_str,
                ))
                await db.commit()
        except Exception as exc:
            # Ошибка audit не должна ломать основной запрос
            logger.error(f"[AUDIT] Ошибка записи: {exc}")

        return response


def _get_client_ip(request: Request) -> str:
    """Возвращает реальный IP клиента (X-Forwarded-For > X-Real-IP > client)."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip
    return request.client.host if request.client else "unknown"
