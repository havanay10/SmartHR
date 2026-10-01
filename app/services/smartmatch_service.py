from datetime import datetime
from uuid import uuid4
from sqlalchemy import func, select
from app.db.connection import get_session
from app.services.embedding_service import EmbeddingService
from app.models.employee import Employee, Department
from app.models.smartmatch import MatchSession, MatchResult


class SmartMatchService:
    """Service SmartMatch IA (CDC §5).

    Mode A : 1 vs 1 (duo)
    Mode B : 1 vs Tous (multi-scan departement)
    """

    def get_departments(self) -> list[dict]:
        with get_session() as db:
            depts = db.scalars(select(Department)).all()
            return [{"id": str(d.id), "name": d.name} for d in depts]

    def get_employees_by_department(self, dept_id: str) -> list[dict]:
        """Retourne les employes d'un departement avec TOUTES les infos utiles."""
        with get_session() as db:
            emps = db.scalars(
                select(Employee).where(
                    Employee.department_id == dept_id,
                    Employee.status == "actif",
                )
            ).all()

            dept = db.get(Department, dept_id)

            return [
                {
                    "id": str(e.id),
                    "first_name": e.first_name,
                    "last_name": e.last_name,
                    "name": e.full_name,
                    "job_title": e.job_title,
                    "disc": e.disc_profile,
                    "work_mode": e.work_mode or "—",
                    "remote_days_per_week": e.remote_days_per_week or 0,
                    "department": dept.name if dept else "—",
                }
                for e in emps
            ]

    # ========== MODE A : 1 vs 1 ==========
    def run_duo(self, pivot_id: str, target_id: str) -> dict:
        with get_session() as db:
            pivot = db.get(Employee, pivot_id)
            target = db.get(Employee, target_id)
            if not pivot or not target:
                raise ValueError("Employe introuvable")

            session = MatchSession(
                id=str(uuid4()),
                mode="duo",
                pivot_person_id=pivot_id,
                pivot_person_type="employee",
                status="termine",
                total_targets=1,
                completed=1,
                algorithm_version="v2.8-DeepTalent",
                finished_at=datetime.utcnow(),
            )
            db.add(session)
            db.flush()

            r = self._compute(pivot, target)

            # On ne passe QUE les colonnes de la table MatchResult
            db.add(MatchResult(
                id=str(uuid4()),
                session_id=session.id,
                target_person_id=target_id,
                target_person_type="employee",
                global_score=r["global_score"],
                skills_score=r["skills_score"],
                communication_score=r["communication_score"],
                friction_risk=r["friction_risk"],
                hierarchy_risk=r["hierarchy_risk"],
                diagnosis=r["diagnosis"],
            ))

            return {
                "session_id": session.id,
                "results": [{
                    "target_name": target.full_name,
                    "global_score": r["global_score"],
                    "skills_score": r["skills_score"],
                    "communication_score": r["communication_score"],
                    "diagnosis": r["diagnosis"],
                }],
            }

    # ========== MODE B : 1 vs Tous ==========
    def run_multi_scan(self, pivot_id: str) -> dict:
        with get_session() as db:
            pivot = db.get(Employee, pivot_id)
            if not pivot or not pivot.department_id:
                raise ValueError("Employe sans departement")

            targets = db.scalars(
                select(Employee).where(
                    Employee.department_id == pivot.department_id,
                    Employee.id != pivot_id,
                    Employee.status == "actif",
                )
            ).all()

            session = MatchSession(
                id=str(uuid4()),
                mode="multi_scan",
                pivot_person_id=pivot_id,
                pivot_person_type="employee",
                department_id=pivot.department_id,
                status="termine",
                total_targets=len(targets),
                completed=len(targets),
                algorithm_version="v2.8-DeepTalent",
                finished_at=datetime.utcnow(),
            )
            db.add(session)
            db.flush()

            results = []
            for t in targets:
                r = self._compute(pivot, t)

                # On ne passe QUE les colonnes de la table MatchResult
                db.add(MatchResult(
                    id=str(uuid4()),
                    session_id=session.id,
                    target_person_id=str(t.id),
                    target_person_type="employee",
                    global_score=r["global_score"],
                    skills_score=r["skills_score"],
                    communication_score=r["communication_score"],
                    friction_risk=r["friction_risk"],
                    hierarchy_risk=r["hierarchy_risk"],
                    diagnosis=r["diagnosis"],
                ))
                results.append({
                    "target_name": t.full_name,
                    "global_score": r["global_score"],
                    "skills_score": r["skills_score"],
                    "communication_score": r["communication_score"],
                    "diagnosis": r["diagnosis"],
                })

            results.sort(key=lambda x: x["global_score"], reverse=True)
            return {"session_id": session.id, "results": results}

    def count_past_matches(self, emp_a_id: str, emp_b_id: str) -> int:
        """Compte le nombre de comparaisons SmartMatch entre 2 employes.

        Different de la collaboration reelle (voir get_collaboration_stats).
        """
        from app.models.smartmatch import MatchSession, MatchResult
        with get_session() as db:
            # Cas 1 : A pivot, B cible
            count_1 = db.scalar(
                select(func.count()).select_from(MatchResult)
                .join(MatchSession, MatchSession.id == MatchResult.session_id)
                .where(
                    MatchSession.pivot_person_id == emp_a_id,
                    MatchResult.target_person_id == emp_b_id,
                )
            ) or 0

            # Cas 2 : B pivot, A cible
            count_2 = db.scalar(
                select(func.count()).select_from(MatchResult)
                .join(MatchSession, MatchSession.id == MatchResult.session_id)
                .where(
                    MatchSession.pivot_person_id == emp_b_id,
                    MatchResult.target_person_id == emp_a_id,
                )
            ) or 0

            return count_1 + count_2

    def get_collaboration_stats(self, emp_a_id: str, emp_b_id: str) -> dict:
        """Retourne les stats de collaboration REELLE entre 2 employes.

        Base sur la table projects + project_members.

        Retourne :
        {
            "n_projects": int,          # Nombre de projets en commun
            "n_months": int,             # Mois cumules de collaboration
            "projects": list[str],       # Noms des projets communs
        }
        """
        from app.models.project import Project, ProjectMember
        from datetime import date

        with get_session() as db:
            # Trouve les projets où A et B sont tous les deux membres
            stmt = (
                select(Project)
                .join(ProjectMember, ProjectMember.project_id == Project.id)
                .where(ProjectMember.employee_id.in_([emp_a_id, emp_b_id]))
                .group_by(Project.id)
                .having(func.count(ProjectMember.employee_id) == 2)
            )

            projects = db.scalars(stmt).all()

            # Calcule les mois cumules
            today = date.today()
            total_months = 0
            project_names = []

            for p in projects:
                start = p.start_date
                end = p.end_date or today

                # Calcul du nombre de mois
                months = (end.year - start.year) * 12 + (end.month - start.month)
                if months < 1:
                    months = 1  # Au moins 1 mois si le projet existe

                total_months += months
                project_names.append(p.name)

            return {
                "n_projects": len(projects),
                "n_months": total_months,
                "projects": project_names,
            }

        # =====================================================
    # GESTION DES BINOMES
    # =====================================================
    def create_binome(
        self,
        employee_a_id: str,
        employee_b_id: str,
        score: float = None,
        diagnosis: str = None,
    ) -> tuple[bool, str]:
        """Cree un binome entre 2 employes.

        Verifie qu'il n'existe pas deja.

        Returns:
            (success, message)
        """
        from app.models.binome import Binome

        # Securite : empecher de creer un binome avec soi-meme
        if employee_a_id == employee_b_id:
            return False, "Impossible de creer un binome avec le meme employe."

        # Ordre normalise (a < b) pour eviter les doublons inverses
        a, b = sorted([employee_a_id, employee_b_id])

        with get_session() as db:
            # Verifie si le binome existe deja
            existing = db.scalar(
                select(Binome).where(
                    Binome.employee_a_id == a,
                    Binome.employee_b_id == b,
                    Binome.status == "active",
                )
            )
            if existing:
                return False, "Ce binome existe deja dans le systeme."

            # Cree le binome
            binome = Binome(
                id=str(uuid4()),
                employee_a_id=a,
                employee_b_id=b,
                score=score,
                diagnosis=diagnosis,
                status="active",
            )
            db.add(binome)
            db.flush()

            return True, "Binome cree avec succes."

    def binome_exists(self, employee_a_id: str, employee_b_id: str) -> bool:
        """Verifie si un binome existe deja entre 2 employes."""
        from app.models.binome import Binome

        a, b = sorted([employee_a_id, employee_b_id])

        with get_session() as db:
            existing = db.scalar(
                select(Binome.id).where(
                    Binome.employee_a_id == a,
                    Binome.employee_b_id == b,
                    Binome.status == "active",
                )
            )
            return existing is not None
    
        # =====================================================
    # LECTURE DES BINOMES
    # =====================================================
    def get_all_binomes(self, limit: int = 20) -> list[dict]:
        """Retourne tous les binomes avec les infos des employes.

        Trie par date de creation decroissante (le plus recent en premier).
        """
        from app.models.binome import Binome
        from app.models.employee import Employee as EmpModel

        with get_session() as db:
            binomes = db.scalars(
                select(Binome)
                .where(Binome.status == "active")
                .order_by(Binome.created_at.desc())
                .limit(limit)
            ).all()

            result = []
            for b in binomes:
                emp_a = db.get(EmpModel, b.employee_a_id)
                emp_b = db.get(EmpModel, b.employee_b_id)

                result.append({
                    "id": str(b.id),
                    "employee_a_id": str(b.employee_a_id),
                    "employee_b_id": str(b.employee_b_id),
                    "employee_a_name": emp_a.full_name if emp_a else "—",
                    "employee_b_name": emp_b.full_name if emp_b else "—",
                    "employee_a_title": emp_a.job_title if emp_a else "—",
                    "employee_b_title": emp_b.job_title if emp_b else "—",
                    "employee_a_disc": emp_a.disc_profile if emp_a else "",
                    "employee_b_disc": emp_b.disc_profile if emp_b else "",
                    "score": float(b.score) if b.score else 0.0,
                    "diagnosis": b.diagnosis or "—",
                    "status": b.status,
                    "created_at": b.created_at,
                })
            return result

    def delete_binome(self, binome_id: str) -> bool:
        """Archive un binome (passe le status a 'archive')."""
        from app.models.binome import Binome

        with get_session() as db:
            b = db.get(Binome, binome_id)
            if not b:
                return False
            b.status = "archive"
            return True
            
    # ========== Moteur de calcul (heuristique) ==========
    def _compute(self, a: Employee, b: Employee) -> dict:
        """Calcul du score SmartMatch avec IA semantique.

        Score = 40% skills + 30% DISC + 30% semantique IA

        (Avant : 40% skills + 40% DISC + 20% friction)
        """
        # ==========================================
        # 1. Skills (meme departement)
        # ==========================================
        skills = 80.0 if a.department_id == b.department_id else 65.0

        # ==========================================
        # 2. Communication (DISC)
        # ==========================================
        compat_pairs = {("D", "I"), ("S", "C"), ("I", "S"), ("D", "C")}

        disc_a = a.disc_profile or "?"
        disc_b = b.disc_profile or "?"

        pair1 = (disc_a, disc_b)
        pair2 = (disc_b, disc_a)

        if pair1 in compat_pairs or pair2 in compat_pairs:
            comm = 90.0
        elif disc_a == disc_b:
            comm = 60.0
        else:
            comm = 70.0

        # ==========================================
        # 3. Similarite SEMANTIQUE (IA)
        # ==========================================
        semantic = 70.0  # valeur par defaut
        try:
            emb_svc = EmbeddingService()
            if emb_svc.is_available():
                profile_a = {
                    "job_title": a.job_title or "",
                    "department": a.department.name if a.department else "",
                    "disc": disc_a,
                }
                profile_b = {
                    "job_title": b.job_title or "",
                    "department": b.department.name if b.department else "",
                    "disc": disc_b,
                }
                semantic = emb_svc.profile_similarity(profile_a, profile_b)
        except Exception as e:
            print(f"[SmartMatchService] Erreur semantique: {e}")

        # ==========================================
        # 4. Friction et hierarchie
        # ==========================================
        if disc_a == disc_b:
            friction = 25.0
        elif pair1 in compat_pairs or pair2 in compat_pairs:
            friction = 15.0
        else:
            friction = 20.0

        hierarchy = 65.0 if (a.manager_id == b.id or b.manager_id == a.id) else 5.0

        # ==========================================
        # 5. Score final : 40% skills + 30% DISC + 30% IA
        # ==========================================
        base_score = 0.4 * skills + 0.3 * comm + 0.3 * semantic

        # ==========================================
        # 6. Ajustement relation (comme avant)
        # ==========================================
        relation = None
        relation_adj = 0
        relation_note = None

        try:
            from app.services.relationship_service import RelationshipService
            relation = RelationshipService().get_relation_between(str(a.id), str(b.id))
            if relation:
                relation_adj = relation.get("impact", 0)
                if relation_adj > 0:
                    relation_note = (
                        f"Relation '{relation['relation_label']}' détectée : "
                        f"bonus +{relation_adj} (affinité)"
                    )
                elif relation_adj < 0:
                    relation_note = (
                        f"Relation '{relation['relation_label']}' détectée : "
                        f"malus {relation_adj} (conflit d'intérêts)"
                    )
        except Exception as e:
            print(f"[SmartMatchService] Erreur relation: {e}")

        global_score = base_score + relation_adj
        global_score = max(0.0, min(100.0, global_score))
        global_score = round(global_score, 2)

        # ==========================================
        # 7. Diagnostic
        # ==========================================
        if global_score >= 80:
            diag = "Binome hautement complementaire"
        elif global_score >= 70:
            diag = "Binome complementaire"
        elif global_score >= 60:
            diag = "Binome a equilibrer"
        else:
            diag = "Binome a risque"

        if relation_adj <= -20:
            diag += " (conflit d'interets)"
        elif relation_adj >= 10:
            diag += " (affinite forte)"

        return {
            "global_score": global_score,
            "skills_score": skills,
            "communication_score": comm,
            "semantic_score": semantic,           # ⭐ NOUVEAU
            "friction_risk": friction,
            "hierarchy_risk": hierarchy,
            "diagnosis": diag,
            "relation": relation,
            "relation_adjustment": relation_adj,
            "relation_note": relation_note,
            "base_score": round(base_score, 2),
        }