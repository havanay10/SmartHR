"""Service de gestion des relations entre employes."""
from datetime import datetime
from uuid import uuid4

from sqlalchemy import select, func, or_, and_
from app.db.connection import get_session
from app.models.employee import Employee
from app.models.relation import EmployeeRelation


# Types de relations disponibles (avec labels et emojis)
RELATION_TYPES = {
    "ami":             ("Ami(e)",               "🤝", "#2E86DE"),
    "couple":          ("En couple",            "💑", "#C0392B"),
    "famille":         ("Famille",              "👨‍👩‍👧", "#8E44AD"),
    "ancien_collegue": ("Ancien collègue",      "🏢", "#7A8B9C"),
    "mentor":          ("Mentor / Mentoré",     "🎓", "#0D7A6A"),
}
# Impact de chaque type de relation sur le score SmartMatch
# Positif = bonus, Négatif = malus (conflit d'interets)
RELATION_IMPACT = {
    "ami":             +10,   # Amis => bonne synergie
    "ancien_collegue": +5,    # Legere affinite
    "mentor":          -15,   # Risque hierarchique
    "couple":          -30,   # Conflit d'interets (sécurité)
    "famille":         -30,   # Conflit d'interets
}

class RelationshipService:
    """Service de gestion des relations entre employes."""

    # =====================================================
    # KPIs
    # =====================================================
    def get_kpis(self) -> dict:
        """Retourne les KPIs du module Liens."""
        with get_session() as db:
            total = db.scalar(
                select(func.count()).select_from(EmployeeRelation)
            ) or 0

            # Repartition par type
            stmt = (
                select(
                    EmployeeRelation.relation_type,
                    func.count(EmployeeRelation.id).label("count"),
                )
                .group_by(EmployeeRelation.relation_type)
            )
            by_type = {r.relation_type: r.count for r in db.execute(stmt)}

            # Nombre d'employes ayant au moins 1 relation
            employees_with_rel = db.scalar(
                select(func.count(func.distinct(EmployeeRelation.employee_a_id)))
            ) or 0

            return {
                "total_relations": total,
                "by_type": by_type,
                "employees_with_rel": employees_with_rel,
            }

    # =====================================================
    # LECTURE
    # =====================================================
    def get_all_relations(self) -> list[dict]:
        """Retourne toutes les relations avec les noms des employes."""
        with get_session() as db:
            relations = db.scalars(
                select(EmployeeRelation).order_by(EmployeeRelation.created_at.desc())
            ).all()

            result = []
            for r in relations:
                emp_a = db.get(Employee, r.employee_a_id)
                emp_b = db.get(Employee, r.employee_b_id)

                if not emp_a or not emp_b:
                    continue

                # Label du type
                type_info = RELATION_TYPES.get(r.relation_type, ("Autre", "🔗", "#7A8B9C"))

                result.append({
                    "id": str(r.id),
                    "employee_a_id": str(emp_a.id),
                    "employee_b_id": str(emp_b.id),
                    "employee_a_name": emp_a.full_name,
                    "employee_b_name": emp_b.full_name,
                    "employee_a_title": emp_a.job_title,
                    "employee_b_title": emp_b.job_title,
                    "employee_a_dept": emp_a.department.name if emp_a.department else "—",
                    "employee_b_dept": emp_b.department.name if emp_b.department else "—",
                    "relation_type": r.relation_type,
                    "relation_label": type_info[0],
                    "relation_icon": type_info[1],
                    "relation_color": type_info[2],
                    "notes": r.notes,
                    "created_at": r.created_at,
                })
            return result

    def get_relations_of_employee(self, employee_id: str) -> list[dict]:
        """Retourne toutes les relations d'un employe."""
        with get_session() as db:
            relations = db.scalars(
                select(EmployeeRelation)
                .where(
                    or_(
                        EmployeeRelation.employee_a_id == employee_id,
                        EmployeeRelation.employee_b_id == employee_id,
                    )
                )
            ).all()

            result = []
            for r in relations:
                other_id = r.employee_b_id if r.employee_a_id == employee_id else r.employee_a_id
                other = db.get(Employee, other_id)
                if not other:
                    continue

                type_info = RELATION_TYPES.get(r.relation_type, ("Autre", "🔗", "#7A8B9C"))
                result.append({
                    "relation_id": str(r.id),
                    "other_id": str(other.id),
                    "other_name": other.full_name,
                    "other_title": other.job_title,
                    "relation_type": r.relation_type,
                    "relation_label": type_info[0],
                    "relation_icon": type_info[1],
                })
            return result

    def get_all_employees(self) -> list[dict]:
        """Retourne tous les employes actifs."""
        with get_session() as db:
            emps = db.scalars(
                select(Employee)
                .where(Employee.status == "actif")
                .order_by(Employee.last_name)
            ).all()

            return [
                {
                    "id": str(e.id),
                    "name": e.full_name,
                    "job_title": e.job_title,
                    "department": e.department.name if e.department else "—",
                }
                for e in emps
            ]

    # =====================================================
    # ECRITURE
    # =====================================================
    def create_relation(
        self,
        employee_a_id: str,
        employee_b_id: str,
        relation_type: str,
        notes: str = None,
    ) -> tuple[bool, str]:
        """Cree une relation entre 2 employes.

        Regles metier :
        - Pas de relation avec soi-meme
        - Pas de doublon A-B / B-A
        - ⭐ Si type = "couple" : les 2 personnes doivent etre libres
        """
        if employee_a_id == employee_b_id:
            return False, "Impossible de créer une relation avec soi-même."

        if relation_type not in RELATION_TYPES:
            return False, f"Type de relation invalide : {relation_type}"

        # Ordre normalise
        a, b = sorted([employee_a_id, employee_b_id])

        with get_session() as db:
            # ========== 1. Verifier doublon ==========
            existing = db.scalar(
                select(EmployeeRelation).where(
                    EmployeeRelation.employee_a_id == a,
                    EmployeeRelation.employee_b_id == b,
                )
            )
            if existing:
                return False, "Cette relation existe déjà dans le système."

            # ========== 2. ⭐ Validation speciale COUPLE ==========
            if relation_type == "couple":
                conflict_a = self._has_existing_couple(db, a)
                conflict_b = self._has_existing_couple(db, b)

                if conflict_a or conflict_b:
                    # Recupere les noms des employes concernes
                    from app.models.employee import Employee

                    messages = []
                    if conflict_a:
                        emp_a = db.get(Employee, a)
                        if emp_a:
                            messages.append(f"{emp_a.full_name} est déjà en couple")
                    if conflict_b:
                        emp_b = db.get(Employee, b)
                        if emp_b:
                            messages.append(f"{emp_b.full_name} est déjà en couple")

                    return False, (
                        "Impossible de créer cette relation :\n"
                        + " ; ".join(messages)
                        + "\n\nUn employé ne peut être en couple qu'avec une seule personne."
                    )

            # ========== 3. Creation ==========
            relation = EmployeeRelation(
                id=str(uuid4()),
                employee_a_id=a,
                employee_b_id=b,
                relation_type=relation_type,
                notes=notes,
            )
            db.add(relation)
            return True, "Relation créée avec succès."

    def _has_existing_couple(self, db, employee_id: str) -> bool:
        """Verifie si un employe est deja en couple.

        Cherche dans les 2 sens (employee_a ou employee_b).
        """
        result = db.scalar(
            select(EmployeeRelation.id).where(
                EmployeeRelation.relation_type == "couple",
                or_(
                    EmployeeRelation.employee_a_id == employee_id,
                    EmployeeRelation.employee_b_id == employee_id,
                ),
            )
        )
        return result is not None

    def delete_relation(self, relation_id: str) -> bool:
        """Supprime une relation."""
        with get_session() as db:
            rel = db.get(EmployeeRelation, relation_id)
            if not rel:
                return False
            db.delete(rel)
            return True
        
    def get_relation_between(self, emp_a_id: str, emp_b_id: str) -> dict | None:
        """Retourne la relation entre 2 employes, ou None si aucune.

        Normalise l'ordre pour trouver la relation peu importe l'ordre
        de passage des IDs.
        """
        if emp_a_id == emp_b_id:
            return None

        # Ordre normalise (comme dans la creation)
        a, b = sorted([emp_a_id, emp_b_id])

        with get_session() as db:
            rel = db.scalar(
                select(EmployeeRelation).where(
                    EmployeeRelation.employee_a_id == a,
                    EmployeeRelation.employee_b_id == b,
                )
            )
            if not rel:
                return None

            type_info = RELATION_TYPES.get(
                rel.relation_type,
                ("Autre", "🔗", "#7A8B9C")
            )

            return {
                "id": str(rel.id),
                "relation_type": rel.relation_type,
                "relation_label": type_info[0],
                "relation_icon": type_info[1],
                "relation_color": type_info[2],
                "notes": rel.notes,
                "impact": RELATION_IMPACT.get(rel.relation_type, 0),
            }    