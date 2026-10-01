from datetime import datetime
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import String, Numeric, ForeignKey, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class MatchSession(Base):
    __tablename__ = "match_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True,
                                     default=lambda: str(uuid4()))
    mode: Mapped[str] = mapped_column(String(20))
    pivot_person_id: Mapped[str]
    pivot_person_type: Mapped[str] = mapped_column(String(20), default="employee")
    department_id: Mapped[str | None] = mapped_column(ForeignKey("departments.id"))
    status: Mapped[str] = mapped_column(String(20), default="en_cours")
    total_targets: Mapped[int | None]
    completed: Mapped[int] = mapped_column(Integer, default=0)
    algorithm_version: Mapped[str | None] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    finished_at: Mapped[datetime | None]


class MatchResult(Base):
    __tablename__ = "match_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True,
                                     default=lambda: str(uuid4()))
    session_id: Mapped[str] = mapped_column(
        ForeignKey("match_sessions.id", ondelete="CASCADE")
    )
    target_person_id: Mapped[str]
    target_person_type: Mapped[str] = mapped_column(String(20), default="employee")
    global_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    skills_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    communication_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    friction_risk: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    hierarchy_risk: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    diagnosis: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)