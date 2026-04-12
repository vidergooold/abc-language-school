from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from app.core.database import Base


class ReportCache(Base):
    """
    Кэш сформированных отчётов.
    Тяжёлые агрегаты (посещаемость, загрузка преподавателей)
    вычисляются по расписанию и сохраняются здесь.
    Фронт читает из кэша — без нагрузки на БД при каждом запросе.
    """
    __tablename__ = "report_cache"

    id          = Column(Integer, primary_key=True, index=True)
    report_type = Column(String(100), nullable=False, index=True)  # attendance / teacher_load / finance
    period      = Column(String(20),  nullable=True,  index=True)  # напр. "2026-04"
    params_hash = Column(String(64),  nullable=True)               # MD5 параметров
    data        = Column(JSON,        nullable=False)               # результат отчёта
    generated_at = Column(DateTime,   default=datetime.utcnow)
    expires_at   = Column(DateTime,   nullable=True)               # когда устаревает
