"""AuditLog — журнал всех CREATE / UPDATE / DELETE / LOGIN операций.

Новые поля по сравнению с предыдущей версией:
  + user_role        — роль пользователя на момент действия
  + http_method      — GET / POST / PUT / PATCH / DELETE
  + endpoint         — /api/v1/groups/5
  + status_code      — 200, 201, 422, 500 …
  + request_body     — тело запроса (JSON, тред пассворды/токена)
  + old_value        — состояние до изменения (JSON)
  + new_value        — состояние после изменения (JSON)
  + duration_ms      — время выполнения запроса в миллисекундах
  + user_agent       — строка User-Agent браузера/клиента
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Index
from app.core.database import Base


class AuditLog(Base):
    """Журнал действий. Заполняется:
      - автоматически через AuditMiddleware (все POST/PUT/PATCH/DELETE);
      - вручную через write_audit_log() в роутерах (напр. LOGIN, спец. действия).
    """
    __tablename__ = "audit_log"

    id           = Column(Integer, primary_key=True, index=True)

    # Кто
    user_id      = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    user_email   = Column(String(255), nullable=True)   # дублируем для истории
    user_role    = Column(String(50),  nullable=True)   # admin / teacher / student

    # Что
    action       = Column(String(100), nullable=False, index=True)  # CREATE/UPDATE/DELETE/LOGIN…
    entity_type  = Column(String(100), nullable=False, index=True)  # news / lesson / payment…
    entity_id    = Column(Integer,     nullable=True)

    # HTTP-контекст (заполняет Middleware)
    http_method  = Column(String(10),  nullable=True)   # POST, PATCH, DELETE…
    endpoint     = Column(String(500), nullable=True)   # /api/v1/groups/5
    status_code  = Column(Integer,     nullable=True)   # 200 / 201 / 422 / 500
    duration_ms  = Column(Integer,     nullable=True)   # время ответа в мс
    user_agent   = Column(String(500), nullable=True)
    ip_address   = Column(String(50),  nullable=True)

    # Что изменилось
    request_body = Column(Text, nullable=True)          # JSON запроса (без паролей)
    old_value    = Column(Text, nullable=True)          # JSON до
    new_value    = Column(Text, nullable=True)          # JSON после
    details      = Column(Text, nullable=True)          # доп. комментарий

    created_at   = Column(DateTime, default=datetime.utcnow, index=True)

    # Составной индекс для быстрых выборок в админке
    __table_args__ = (
        Index("ix_audit_entity", "entity_type", "entity_id"),
        Index("ix_audit_user_time", "user_id", "created_at"),
    )
