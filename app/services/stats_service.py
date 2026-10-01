from datetime import date
from sqlalchemy import func, select
from app.db.connection import get_session
from app.models.employee import Employee, Department
from app.models.leave import LeaveRequest
from app.models.recruitment import Interview, JobOffer, Application
from app.models.alert import Alert


class StatsService:
    """Service de calcul des KPIs (Modules 1 et 2 du CDC)."""

    # ========== MODULE 1 : ACCUEIL ==========
    def get_dashboard_kpis(self) -> dict:
        """KPIs principaux du tableau de bord (CDC §1)."""
        from app.models.recruitment import Candidate  # Import local
    
        with get_session() as db:
            # ========== 1. EMPLOYES ==========
            total_employees = db.scalar(
                select(func.count()).select_from(Employee)
            ) or 0

            active_employees = db.scalar(
                select(func.count()).select_from(Employee)
                .where(Employee.status == "actif")
            ) or 0

            # ========== 2. ABSENCES & CONGES ==========
            first = date.today().replace(day=1)
            absents = db.scalar(
                select(func.count(func.distinct(LeaveRequest.employee_id)))
                .where(
                    LeaveRequest.start_date >= first,
                    LeaveRequest.status == "valide",
                )
            ) or 0

            # ========== 3. TURNOVER ANNUEL ==========
            turnover_raw = db.scalar(
                select(func.count()).select_from(Employee)
                .where(Employee.departure_date >= date.today().replace(month=1, day=1))
            ) or 0
            turnover_rate = round(100 * turnover_raw / max(active_employees, 1), 2)

            if turnover_rate > 10:
                turnover_label = "Zone anormale"
                turnover_alert = True
            else:
                turnover_label = "Zone maitrisee"
                turnover_alert = False

            # ========== 4. RECRUTEMENT ==========
            open_positions = db.scalar(
                select(func.count()).select_from(JobOffer)
                .where(JobOffer.status == "active")
            ) or 0

            total_candidates = db.scalar(
                select(func.count()).select_from(Candidate)
            ) or 0

            selected_candidates = db.scalar(
                select(func.count()).select_from(Application)
                .where(Application.status.in_(["preselectionne", "entretien"]))
            ) or 0

            # ========== 5. MASSE SALARIALE ==========
            payroll = db.scalar(
                select(func.sum(Employee.salary_base + func.coalesce(Employee.salary_variable, 0)))
                .where(Employee.status == "actif")
            ) or 0

            # ========== 6. ANCIENNETE ==========
            emps = db.scalars(select(Employee).where(Employee.status == "actif")).all()
            avg_seniority = round(
                sum(e.seniority_years for e in emps) / max(len(emps), 1), 2
            )

            return {
                # --- Employes ---
                "total_employees": total_employees,
                "active_employees": active_employees,

                # --- Absences ---
                "absences_this_month": absents,

                # --- Turnover ---
                "annual_turnover_rate": turnover_rate,
                "turnover_label": turnover_label,
                "turnover_alert": turnover_alert,

                # --- Recrutement ---
                "open_positions": open_positions,
                "total_candidates": total_candidates,
                "selected_candidates": selected_candidates,

                # --- Masse salariale ---
                "annual_payroll": float(payroll),

                # --- Anciennete ---
                "average_seniority_years": avg_seniority,
            }
    
    def get_headcount_by_department(self) -> list[dict]:
        """Repartition des effectifs (CDC §1).

        Trie par nombre d'employes DECROISSANT (le plus grand en premier).
        """
        with get_session() as db:
            stmt = (
                select(Department.name, func.count(Employee.id).label("count"))
                .join(Employee, Employee.department_id == Department.id)
                .where(Employee.status == "actif")
                .group_by(Department.name)
                .order_by(func.count(Employee.id).desc()) 
            )
            return [{"name": r[0], "count": r[1]} for r in db.execute(stmt)]

    # ========== MODULE 2 : EMPLOYES ==========
    def get_employee_kpis(self) -> dict:
        """Effectif, taux presence / absence (CDC §2)."""
        with get_session() as db:
            total = db.scalar(
                select(func.count()).select_from(Employee)
                .where(Employee.status == "actif")
            ) or 0

            year_start = date.today().replace(month=1, day=1)
            total_absent = db.scalar(
                select(func.sum(LeaveRequest.duration_days))
                .where(
                    LeaveRequest.start_date >= year_start,
                    LeaveRequest.status == "valide",
                )
            ) or 0

            # Estimation : 220 jours ouvres x effectif
            work_days = 220 * total
            absence_rate = round(100 * float(total_absent) / work_days, 2) if work_days else 0
            presence_rate = round(100 - absence_rate, 2)

            return {
                "total_employees": total,
                "presence_rate": presence_rate,
                "absence_rate": absence_rate,
            }

    def get_all_employees(self) -> list[dict]:
        """Retourne la liste des employes en dict (sur pour l'UI)."""
        with get_session() as db:
            emps = db.scalars(
                select(Employee).order_by(Employee.last_name)
            ).all()
            return [
                {
                    "id": str(e.id),
                    "employee_code": e.employee_code,
                    "first_name": e.first_name,
                    "last_name": e.last_name,
                    "full_name": e.full_name,
                    "email": e.email,
                    "phone": e.phone,                        # ← NOUVEAU
                    "birth_date": e.birth_date,              # ← NOUVEAU
                    "age": e.age,                            # ← NOUVEAU (calculé)
                    "gender": e.gender,
                    "job_title": e.job_title,
                    "department": e.department.name if e.department else "—",
                    "department_id": str(e.department_id) if e.department_id else None,
                    "manager_id": str(e.manager_id) if e.manager_id else None,
                    "contract_type": e.contract_type or "—",
                    "status": e.status,
                    "hire_date": e.hire_date,
                    "seniority_years": e.seniority_years,
                    "salary_base": float(e.salary_base or 0),
                    "salary_variable": float(e.salary_variable or 0),
                    "disc_profile": e.disc_profile,
                    "city": e.city,
                    "work_mode": e.work_mode,
                    "remote_days_per_week": e.remote_days_per_week or 0,
                }
                for e in emps
            ]

    def get_all_departments(self) -> list[dict]:
        """Retourne la liste des departements en dict."""
        with get_session() as db:
            depts = db.scalars(
                select(Department).order_by(Department.name)
            ).all()
            return [
                {
                    "id": str(d.id),
                    "name": d.name,
                    "code": d.code,
                    "management_style": d.management_style,
                    "manager_id": str(d.manager_id) if d.manager_id else None,
                }
                for d in depts
            ]

    def get_employee_leave_history(self, employee_id: str) -> list[dict]:
        """Historique des conges (CDC §2)."""
        with get_session() as db:
            stmt = (
                select(LeaveRequest)
                .where(LeaveRequest.employee_id == employee_id)
                .order_by(LeaveRequest.start_date.desc())
            )
            return [
                {
                    "id": r.id,
                    "type": r.leave_type,
                    "start": r.start_date,
                    "end": r.end_date,
                    "duration": float(r.duration_days),
                    "status": r.status,
                }
                for r in db.scalars(stmt)
            ]

    # ========== GRAPHIQUES ==========
    def get_alerts_monthly(self) -> list[dict]:
        """Evolution des alertes par mois (CDC §3)."""
        with get_session() as db:
            stmt = (
                select(
                    func.to_char(Alert.detected_at, "YYYY-MM").label("month"),
                    func.count().filter(Alert.severity == "critique").label("critiques"),
                    func.count().filter(Alert.severity == "preventif").label("preventives"),
                )
                .group_by("month")
                .order_by("month")
            )
            return [
                {"month": r.month, "critiques": r.critiques, "preventives": r.preventives}
                for r in db.execute(stmt)
            ]
    
        # =====================================================
    # GESTION DES CONGES
    # =====================================================
    def validate_leave(self, leave_id: str) -> bool:
        """Passe une demande de conge au statut 'valide'.

        Retourne True si succes, False sinon.
        """
        from app.models.leave import LeaveRequest
        try:
            with get_session() as db:
                leave = db.get(LeaveRequest, leave_id)
                if not leave:
                    return False
                leave.status = "valide"
                # validate maintenant (pas besoin de validator_id pour l'instant)
                return True
        except Exception as e:
            print(f"[StatsService] Erreur validation conge: {e}")
            return False

    def create_leave_request(
        self,
        employee_id: str,
        leave_type: str,
        start_date,
        end_date,
        reason: str = "",
    ) -> bool:
        """Cree une nouvelle demande de conge.

        Retourne True si succes, False sinon.
        """
        from app.models.leave import LeaveRequest
        from decimal import Decimal

        try:
            with get_session() as db:
                # Calcul de la duree en jours
                duration = (end_date - start_date).days + 1

                new_leave = LeaveRequest(
                    employee_id=employee_id,
                    leave_type=leave_type,
                    start_date=start_date,
                    end_date=end_date,
                    duration_days=Decimal(str(duration)),
                    reason=reason or None,
                    status="en_attente",
                )
                db.add(new_leave)
                return True
        except Exception as e:
            print(f"[StatsService] Erreur creation conge: {e}")
            return False        

     # =====================================================
    # GESTION DES EMPLOYES
    # =====================================================
    def create_employee(
        self,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
        birth_date,
        job_title: str,
        department_id: str,
        contract_type: str,
        hire_date,
        city: str,
        salary_base: float,
        salary_variable: float = 0.0,
        work_mode: str = "présentiel",
    ) -> str:
        """Cree un nouvel employe en base.

        Genere automatiquement :
        - employee_code : EMP-XXXX (auto-incremente)
        - status : "actif"
        - remote_days_per_week : 0

        Returns:
            L'ID de l'employe cree
        """
        from uuid import uuid4
        from decimal import Decimal
        from app.models.employee import Employee

        with get_session() as db:
            # ========== 1. Generer un code employe unique ==========
            count = db.scalar(
                select(func.count()).select_from(Employee)
            ) or 0
            # Cherche le premier code libre
            code_seq = count + 1
            while True:
                candidate_code = f"EMP-{code_seq:04d}"
                exists = db.scalar(
                    select(Employee.id).where(Employee.employee_code == candidate_code)
                )
                if not exists:
                    break
                code_seq += 1

            # ========== 2. Creer l'employe ==========
            emp = Employee(
                id=str(uuid4()),
                employee_code=candidate_code,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone or None,
                birth_date=birth_date,
                job_title=job_title,
                department_id=department_id or None,
                manager_id=None,
                contract_type=contract_type,
                status="actif",
                hire_date=hire_date,
                city=city or None,
                work_mode=work_mode,
                remote_days_per_week=0,
                salary_base=Decimal(str(salary_base)),
                salary_variable=Decimal(str(salary_variable)) if salary_variable else None,
            )
            db.add(emp)
            db.flush()
            emp_id = str(emp.id)

        return emp_id

    def email_exists(self, email: str) -> bool:
        """Verifie si un email est deja utilise."""
        from app.models.employee import Employee
        with get_session() as db:
            result = db.scalar(
                select(Employee.id).where(Employee.email == email)
            )
            return result is not None
    
    def get_absence_repartition(self) -> list[dict]:
        """Repartition des absences par type (CDC §3)."""
        with get_session() as db:
            stmt = (
                select(LeaveRequest.leave_type, func.count())
                .group_by(LeaveRequest.leave_type)
            )
            return [{"type": r[0], "count": r[1]} for r in db.execute(stmt)]