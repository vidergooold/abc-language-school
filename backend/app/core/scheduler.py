"""APScheduler для автоматической публикации запланированных новостей."""
import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = AsyncIOScheduler()

async def publish_scheduled_news():
    """Вызывает эндпоинт публикации каждые 5 минут."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://127.0.0.1:8000/api/v1/admin/news/publish-scheduled",
                timeout=30.0
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("published", 0) > 0:
                    print(f"[Scheduler] Опубликовано {data['published']} новостей: {data['titles']}")
            else:
                print(f"[Scheduler] Ошибка публикации: {response.status_code}")
        except Exception as e:
            print(f"[Scheduler] Исключение: {e}")

def start_scheduler():
    """Запускает планировщик с задачей каждые 5 минут."""
    scheduler.add_job(
        publish_scheduled_news,
        trigger=IntervalTrigger(minutes=5),
        id="publish_scheduled_news",
        name="Автопубликация запланированных новостей",
        replace_existing=True,
    )
    scheduler.start()
    print("[Scheduler] APScheduler запущен — проверка каждые 5 минут")

def shutdown_scheduler():
    """Останавливает планировщик при завершении приложения."""
    if scheduler.running:
        scheduler.shutdown()
        print("[Scheduler] APScheduler остановлен")
