"""Modeles Project et ProjectMember.

Un projet a plusieurs membres (relation many-to-many).
Permet de calculer la collaboration reelle entre 2 employes.
"""
from datetime import date, datetime
from uuid import uuid4
from sqlalchemy import String, ForeignKey, Date, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    start_date: Mapped[date]
    end_date: Mapped[date | None]
    status: Mapped[str] = mapped_column(String(20), default="en_cours")
    # "en_cours" ou "termine"

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relation
    members: Mapped[list["ProjectMember"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )


class ProjectMember(Base):
    """Association : un employe participe a un projet."""
    __tablename__ = "project_members"

    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        primary_key=True,
    )
    employee_id: Mapped[str] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role: Mapped[str | None] = mapped_column(String(50))  # "lead", "membre"

    # Relation
    project: Mapped["Project"] = relationship(back_populates="members")