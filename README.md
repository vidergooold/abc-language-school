# ABC Language School

Инфраструктура развёртывания:

- Frontend: **Vercel**
- Backend: **Railway**
- Database: **Railway PostgreSQL plugin**

Основные команды запуска из корня проекта:

```bash
npm run dev:frontend
```

Запуск frontend на Vite.

```bash
npm run dev:backend
```

Запуск backend на `8000` через `backend/venv`.

```bash
npm run dev:backend:clean
```

Сначала освобождает порт `8000`, затем запускает backend. Это основной вариант, если раньше `uvicorn` был остановлен некорректно и оставил занятый порт.

```bash
npm run free:backend-port
```

Только освобождает порт `8000` без запуска сервера.

## Seed scripts

Скрипты для заполнения базы данных тестовыми данными. Запускаются из папки `backend/`:

```bash
cd backend
python seeds/seed_all.py
```

Canonical seed — заполняет все базовые справочники, демо-расписание и student_groups.

```bash
cd backend
python seed_student_groups.py
```

`seed_student_groups.py` — запустить после основного seed для заполнения таблицы `student_groups` по всем группам. Исправляет пустую матрицу посещаемости («В выбранной группе пока нет активных студентов»). Скрипт идемпотентен — безопасно запускать повторно.
