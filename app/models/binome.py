"""Modele Binome — Association de 2 employes en equipe.

Cree depuis la page SmartMatch quand on clique "Assigner en Binôme".
"""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class Binome(Base):
    """Un binome = 2 employes associes en equipe de travail."""
    __tablename__ = "binomes"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    # Pivot et Cible (on garde les 2 dans un ordre consistant)
    employee_a_id: Mapped[str] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE")
    )
    employee_b_id: Mapped[str] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE")
    )
    # Score au moment de la creation
    score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    # Diagnostic au moment de la creation
    diagnosis: Mapped[str | None] = mapped_column(String(200))
    # Statut
    status: Mapped[str] = mapped_column(String(20), default="active")
    # "active" ou "archive"

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)