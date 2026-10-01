"""Modele EmployeeRelation — Relations entre 2 employes.

Types de relations :
- ami
- couple
- famille
- ancien_collegue
- mentor
"""
from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base


class EmployeeRelation(Base):
    """Relation entre 2 employes (ex: ami, en couple, famille)."""
    __tablename__ = "employee_relations"

    __table_args__ = (
        # Empeche les doublons (A-B et B-A = meme relation)
        UniqueConstraint(
            "employee_a_id", "employee_b_id",
            name="uq_relation_pair"
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    # Ordre normalise : employee_a_id < employee_b_id (alphabetique)
    employee_a_id: Mapped[str] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE")
    )
    employee_b_id: Mapped[str] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE")
    )
    # Type de relation
    relation_type: Mapped[str] = mapped_column(String(30))
    # ami, couple, famille, ancien_collegue, mentor
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)