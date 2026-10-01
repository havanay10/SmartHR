from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True,
                                     default=lambda: str(uuid4()))
    report_type: Mapped[str] = mapped_column(String(50))
    title: Mapped[str | None] = mapped_column(String(200))
    file_url: Mapped[str | None]
    file_format: Mapped[str | None] = mapped_column(String(10))
    file_size_kb: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="en_generation")
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)