from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey, Enum as SAEnum, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class DiscountType(str, enum.Enum):
    percentage = "percentage"   # процент от суммы
    fixed = "fixed"             # фиксированная сумма


class DiscountReason(str, enum.Enum):
    sibling = "sibling"         # скидка за второго ребёнка в семье
    loyalty = "loyalty"         # скидка постоянного ученика
    referral = "referral"       # скидка за приведённого друга
    promo = "promo"             # промокод
    social = "social"           # социальная скидка (многодетные, льготники)
    corporate = "corporate"     # корпоративный договор
    early_payment = "early_payment"  # скидка за раннюю оплату
    other = "other"


class Discount(Base):
    """
    Скидка, привязанная к конкретному студенту или группе.
    Применяется при генерации счетов (Invoice).

    Бизнес-правила:
    - is_active=True  — скидка действует
    - valid_until     — если дата истекла, скидка не применяется
    - max_uses        — если задан, скидка прекращается после N применений
    - used_count      — счётчик применений
    """
    __tablename__ = "discounts"

    id = Column(Integer, primary_key=True, index=True)

    # Кому применяется скидка
    student_group_id = Column(Integer, ForeignKey("student_groups.id"), nullable=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)  # на всю группу

    reason = Column(SAEnum(DiscountReason), nullable=False, default=DiscountReason.other)
    discount_type = Column(SAEnum(DiscountType), nullable=False, default=DiscountType.percentage)

    value = Column(Numeric(10, 2), nullable=False)  # % или рублей
    description = Column(Text, nullable=True)
    promo_code = Column(String(50), nullable=True, index=True)

    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True)
    max_uses = Column(Integer, nullable=True)   # None = без ограничений
    used_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def is_valid(self) -> bool:
        """Проверяет, действует ли скидка прямо сейчас."""
        now = datetime.utcnow()
        if not self.is_active:
            return False
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        if self.max_uses is not None and self.used_count >= self.max_uses:
            return False
        return True

    def apply(self, amount: float) -> float:
        """Возвращает сумму после применения скидки."""
        if not self.is_valid():
            return amount
        if self.discount_type == DiscountType.percentage:
            return round(amount * (1 - float(self.value) / 100), 2)
        else:
            return max(0.0, round(amount - float(self.value), 2))
