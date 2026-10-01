from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import String, Numeric, ForeignKey, Text, Date, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (
        # Empeche les doublons : 1 seul type d'alerte par employe et par mois
        UniqueConstraint(
            "employee_id", "type", "period_month",
            name="uq_alert_employee_type_month",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True,
                                     default=lambda: str(uuid4()))
    employee_id: Mapped[str | None] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE")
    )
    type: Mapped[str] = mapped_column(String(50))
    severity: Mapped[str] = mapped_column(String(20))
    title: Mapped[str | None] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    risk_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    status: Mapped[str] = mapped_column(String(20), default="active")
    resolved_by: Mapped[str | None]
    resolved_at: Mapped[datetime | None]
    detected_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    period_month: Mapped[date | None] = mapped_column(Date)