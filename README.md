# ABC Language School

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
