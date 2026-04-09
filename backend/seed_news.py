import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from app.models.news import News

NEWS_DATA = [
    {"title": "График работы офиса в Новогодние праздники", "tag": "Объявление", "date": "25.12.2023", "body": "Уважаемые родители и обучающиеся! Поздравляем Вас С Наступающим Новым 2024 годом! Желаем Вам успехов и всего самого наилучшего!"},
    {"title": "График работы Лингвоцентра в праздничные дни", "date": "30.12.2023", "tag": "Объявление", "body": "30.12.2023 – 07.01.2024 — занятия проводиться не будут, офис закрыт. Занятия продолжатся с 08.01.2024 (понедельник) по расписанию."},
    {"title": "Приятных летних каникул!!!", "tag": "Каникулы", "date": "01.06.2022", "body": "Дорогие наши учащиеся! Уважаемые родители! Мы с радостью поздравляем Вас всех с долгожданными летними каникулами!"},
    {"title": "До встречи в Новом 2022-2023 учебном году!", "date": "15.08.2022", "tag": "Объявление", "body": "Напоминаем Вам, что в период с 01.06.22 по 15.08.2022 года Лингвоцентр не работает."},
    {"title": "График работы офиса", "tag": "Объявление", "date": "03.11.2021", "body": "Уважаемые родители и обучающиеся! 04.11.2021 офис Лингвоцентра не работает."},
    {"title": "Поздравляем с Днем народного единства!", "date": "04.11.2021", "tag": "Праздник", "body": "Желаем крепкого здоровья, счастья, благополучия, мира и процветания!"}
]

async def seed_news():
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://abc_user:yourpassword123@localhost:5432/abc_school")
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(select(News))
        existing_news = result.scalars().all()
        
        if len(existing_news) > 0:
            print(f"В базе уже есть {len(existing_news)} новостей. Пропускаем заполнение.")
            return
        
        for news_data in NEWS_DATA:
            date_parts = news_data["date"].split(".")
            news_date = datetime(int(date_parts[2]), int(date_parts[1]), int(date_parts[0]))
            news = News(title=news_data["title"], body=news_data["body"], tag=news_data["tag"], date=news_date)
            session.add(news)
        
        await session.commit()
        print(f"Успешно добавлено {len(NEWS_DATA)} новостей!")

if __name__ == "__main__":
    asyncio.run(seed_news())
