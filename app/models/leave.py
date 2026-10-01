from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import String, Date, Numeric, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True,
                                     default=lambda: str(uuid4()))
    employee_id: Mapped[str] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE")
    )
    leave_type: Mapped[str] = mapped_column(String(30))
    start_date: Mapped[date]
    end_date: Mapped[date]
    duration_days: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    reason: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="en_attente")
    validator_id: Mapped[str | None] = mapped_column(ForeignKey("employees.id"))
    validated_at: Mapped[datetime | None]
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    employee = relationship(
        "Employee",
        back_populates="leave_requests",
        foreign_keys=[employee_id],
    )