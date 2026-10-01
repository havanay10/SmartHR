from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4
from sqlalchemy import String, Numeric, ForeignKey, Text, Date, Integer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class JobOffer(Base):
    __tablename__ = "job_offers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    reference: Mapped[str | None] = mapped_column(String(50), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    department_id: Mapped[str | None] = mapped_column(ForeignKey("departments.id"))
    contract_type: Mapped[str | None] = mapped_column(String(20))
    location: Mapped[str | None] = mapped_column(String(150))
    salary_min: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    salary_max: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    experience_level: Mapped[str | None] = mapped_column(String(30))
    hard_skills: Mapped[list | None] = mapped_column(ARRAY(String))
    soft_skills: Mapped[list | None] = mapped_column(ARRAY(String))
    description: Mapped[str | None] = mapped_column(Text)         
    status: Mapped[str] = mapped_column(String(20), default="active")
    priority: Mapped[str | None] = mapped_column(String(20))
    published_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True,
                                     default=lambda: str(uuid4()))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    phone: Mapped[str | None] = mapped_column(String(20))
    city: Mapped[str | None] = mapped_column(String(100))
    cv_file_url: Mapped[str | None]
    cv_text: Mapped[str | None] = mapped_column(Text)
    years_experience: Mapped[int | None] = mapped_column(Integer)
    current_title: Mapped[str | None] = mapped_column(String(150))
    skills: Mapped[list | None] = mapped_column(ARRAY(String))
    disc_profile: Mapped[str | None] = mapped_column(String(5))
    match_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    ai_summary: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True,
                                     default=lambda: str(uuid4()))
    candidate_id: Mapped[str] = mapped_column(
        ForeignKey("candidates.id", ondelete="CASCADE")
    )
    job_offer_id: Mapped[str] = mapped_column(
        ForeignKey("job_offers.id", ondelete="CASCADE")
    )
    status: Mapped[str] = mapped_column(String(30), default="reçu")
    match_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    applied_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True,
                                     default=lambda: str(uuid4()))
    application_id: Mapped[str] = mapped_column(
        ForeignKey("applications.id", ondelete="CASCADE")
    )
    type: Mapped[str | None] = mapped_column(String(30))
    scheduled_at: Mapped[datetime | None]
    status: Mapped[str] = mapped_column(String(20), default="planifié")