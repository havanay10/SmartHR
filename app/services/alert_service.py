from datetime import date, datetime, timedelta
from sqlalchemy import extract, select, func
from app.db.connection import get_session
from app.models.alert import Alert
from app.models.employee import Employee
from app.models.leave import LeaveRequest
from config import settings


class AlertService:
    """Service des alertes turnover (CDC §3).

    Regle 1 : > 5 jours d'absence dans le mois => alerte CRITIQUE
    Regle 2 : conges > moyenne * 1.5 => alerte PREVENTIVE
    Regle 3 : clic sur "Traiter l'anomalie" => statut "resolue"
    """

    # ---------- REGLE 1 : absences > seuil ----------
    def rule_absence_threshold(self, month: date | None = None):
        m = month or date.today().replace(day=1)
        start = m.replace(day=1)
        end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        with get_session() as db:
            stmt = (
                select(
                    LeaveRequest.employee_id,
                    func.sum(LeaveRequest.duration_days).label("total"),
                )
                .where(
                    LeaveRequest.start_date >= start,
                    LeaveRequest.end_date <= end,
                    LeaveRequest.status == "valide",
                )
                .group_by(LeaveRequest.employee_id)
                .having(func.sum(LeaveRequest.duration_days) > settings.ABSENCE_ALERT_THRESHOLD)
            )
            for row in db.execute(stmt):
                if self._exists(db, row.employee_id, "absences_repetees", start):
                    continue
                emp = db.get(Employee, row.employee_id)
                try:
                    db.add(Alert(
                        employee_id=row.employee_id,
                        type="absences_repetees",
                        severity="critique",
                        title=f"Absences repetees - {emp.full_name if emp else 'N/A'}",
                        description=(
                            f"{row.total} jours d'absence ce mois "
                            f"(seuil : {settings.ABSENCE_ALERT_THRESHOLD} jours)"
                        ),
                        risk_score=min(100, float(row.total) * 10),
                        status="active",
                        period_month=start,
                    ))
                    db.flush()
                except Exception:
                    db.rollback()
                    continue
                
    # ---------- REGLE 2 : conges excessifs ----------
    def rule_leave_excess(self, month: date | None = None):
        """Regle 2 : Total annuel de conges par employe > moyenne * 1.5.

        CORRECTION : on compte le TOTAL ANNUEL par employe (pas chaque conge).
        Exemple : 3 conges de 3j = 9j au total => peut declencher l'alerte.
        """
        today = date.today()
        year = today.year

        start_year = date(year, 1, 1)
        end_year = date(year, 12, 31)
        period_month = today.replace(day=1)   # pour la cle unique

        with get_session() as db:
            # ========== 1. Total annuel de conges par employe ==========
            stmt = (
                select(
                    LeaveRequest.employee_id,
                    func.sum(LeaveRequest.duration_days).label("total"),
                )
                .where(
                    LeaveRequest.start_date >= start_year,
                    LeaveRequest.end_date <= end_year,
                    LeaveRequest.status == "valide",
                )
                .group_by(LeaveRequest.employee_id)
            )
            rows = db.execute(stmt).all()

            if not rows:
                return  # Aucun conge cette annee

            # ========== 2. Moyenne des totaux par employe ==========
            # Recupere TOUS les employes actifs (meme ceux avec 0 conge)
            all_emps = db.scalars(
                select(Employee).where(Employee.status == "actif")
            ).all()
            nb_emps = len(all_emps) or 1

            # Somme totale des conges + nombre d'employes = moyenne
            total_all = sum(float(r.total) for r in rows)
            average = total_all / nb_emps
            threshold = average * settings.LEAVE_RISK_MULTIPLIER

            # ========== 3. Detection des employes au-dessus du seuil ==========
            for r in rows:
                total_emp = float(r.total)
                if total_emp <= threshold:
                    continue  # Sous le seuil

                if self._exists(db, r.employee_id, "conges_excessifs", period_month):
                    continue  # Alerte deja existante

                emp = db.get(Employee, r.employee_id)
                db.add(Alert(
                    employee_id=r.employee_id,
                    type="conges_excessifs",
                    severity="preventif",
                    title=f"Conges excessifs - {emp.full_name if emp else 'N/A'}",
                    description=(
                        f"{total_emp:.1f} jours de conges sur l'annee "
                        f"(moyenne : {average:.1f} j, seuil : {threshold:.1f} j)"
                    ),
                    risk_score=min(100, total_emp * 5),
                    status="active",
                    period_month=period_month,
                ))

    def rule_long_leave(self, month: date | None = None):
        """Regle 3 : Un conge unique > 10 jours dans l'annee => alerte preventive.

        Detecte les conges longue duree qui peuvent signaler :
        - Une fatigue importante
        - Un projet personnel lourd
        - Un risque de desengagement
        """
        today = date.today()
        year = today.year
        period_month = today.replace(day=1)

        with get_session() as db:
            # Cherche les conges individuels > 10 jours cette annee
            stmt = (
                select(LeaveRequest)
                .where(
                    extract("year", LeaveRequest.start_date) == year,
                    LeaveRequest.duration_days > 10,
                    LeaveRequest.status == "valide",
                )
            )
            leaves = db.scalars(stmt).all()

            for leave in leaves:
                if self._exists(db, leave.employee_id, "conge_longue_duree", period_month):
                    continue

                emp = db.get(Employee, leave.employee_id)
                db.add(Alert(
                    employee_id=leave.employee_id,
                    type="conge_longue_duree",
                    severity="preventif",
                    title=f"Conge longue duree - {emp.full_name if emp else 'N/A'}",
                    description=(
                        f"{float(leave.duration_days):.0f} jours de conge continu "
                        f"({leave.leave_type}) - verifier l'etat de fatigue"
                    ),
                    risk_score=min(100, float(leave.duration_days) * 4),
                    status="active",
                    period_month=period_month,
                ))
    
    # ---------- REGLE 3 : resolution ----------
    def resolve_alert(self, alert_id: str, user_id: str | None = None):
        with get_session() as db:
            alert = db.get(Alert, alert_id)
            if alert:
                alert.status = "resolue"
                alert.resolved_at = datetime.utcnow()
                alert.resolved_by = user_id

    # ---------- Public ----------
    def run_all_rules(self, month: date | None = None):
        """Declenche les 3 regles du CDC."""
        self.rule_absence_threshold(month)
        self.rule_leave_excess(month)
        self.rule_long_leave(month)        # ⭐ AJOUT

    def get_kpis(self) -> dict:
        with get_session() as db:
            active = db.scalar(
                select(func.count()).select_from(Alert).where(Alert.status == "active")
            ) or 0
            risks = db.scalar(
                select(func.count()).select_from(Alert)
                .where(Alert.status == "active", Alert.type == "conges_excessifs")
            ) or 0
            resolved = db.scalar(
                select(func.count()).select_from(Alert).where(Alert.status == "resolue")
            ) or 0
            return {
                "active_alerts": active,
                "detected_risks": risks,
                "resolved_alerts": resolved,
            }

    # =====================================================
    # STATISTIQUES POUR L'ANALYSE PREDICTIVE
    # =====================================================
    def get_top_employees_with_alerts(self, limit: int = 3) -> list[dict]:
        """Retourne les employes avec le plus d'alertes actives.

        Utile pour identifier les cas critiques a suivre en priorite.
        """
        from sqlalchemy import desc

        with get_session() as db:
            stmt = (
                select(
                    Alert.employee_id,
                    func.count(Alert.id).label("n_alerts"),
                    func.sum(Alert.risk_score).label("total_risk"),
                )
                .where(
                    Alert.status == "active",
                    Alert.employee_id.isnot(None),
                )
                .group_by(Alert.employee_id)
                .order_by(desc("n_alerts"))
                .limit(limit)
            )

            result = []
            for row in db.execute(stmt):
                emp = db.get(Employee, row.employee_id)
                if not emp:
                    continue
                result.append({
                    "employee_id": str(row.employee_id),
                    "employee_name": emp.full_name,
                    "job_title": emp.job_title,
                    "n_alerts": row.n_alerts,
                    "total_risk": float(row.total_risk or 0),
                    "avg_risk": round(float(row.total_risk or 0) / row.n_alerts, 1),
                })
            return result

    def get_absence_days_this_month(self) -> float:
        """Retourne le nombre TOTAL de jours d'absence valides ce mois."""
        from datetime import date
        from app.models.leave import LeaveRequest

        first = date.today().replace(day=1)
        with get_session() as db:
            total = db.scalar(
                select(func.sum(LeaveRequest.duration_days))
                .where(
                    LeaveRequest.start_date >= first,
                    LeaveRequest.status == "valide",
                )
            )
            return float(total or 0)

    def count_employees_with_many_alerts(self, threshold: int = 3) -> int:
        """Compte les employes avec AU MOINS X alertes actives."""
        from sqlalchemy import desc

        with get_session() as db:
            stmt = (
                select(
                    Alert.employee_id,
                    func.count(Alert.id).label("n"),
                )
                .where(
                    Alert.status == "active",
                    Alert.employee_id.isnot(None),
                )
                .group_by(Alert.employee_id)
                .having(func.count(Alert.id) >= threshold)
            )
            rows = list(db.execute(stmt))
            return len(rows)

    def get_critical_alerts_count(self) -> int:
        """Retourne le nombre d'alertes critiques actives."""
        with get_session() as db:
            count = db.scalar(
                select(func.count()).select_from(Alert)
                .where(
                    Alert.status == "active",
                    Alert.severity == "critique",
                )
            )
            return count or 0
    
    def get_alerts_evolution(self, months: int = 6) -> list[dict]:
        """Retourne le nombre d'alertes par mois sur les X derniers mois.

        Retourne : [{"month": "2025-04", "label": "Avr", "count": 5}, ...]
        """
        from datetime import date
        from sqlalchemy import func, extract

        MOIS_FR = ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin",
                   "Juil", "Août", "Sep", "Oct", "Nov", "Déc"]

        with get_session() as db:
            # Recupere les alertes des N derniers mois
            stmt = (
                select(
                    extract("year", Alert.detected_at).label("year"),
                    extract("month", Alert.detected_at).label("month"),
                    func.count(Alert.id).label("count"),
                )
                .group_by("year", "month")
                .order_by("year", "month")
            )
            rows = db.execute(stmt).all()

            # Dictionnaire pour lookup rapide
            data_by_month = {}
            for r in rows:
                key = f"{int(r.year)}-{int(r.month):02d}"
                data_by_month[key] = r.count

            # Genere les N derniers mois
            today = date.today()
            result = []
            for i in range(months - 1, -1, -1):
                # Recule de i mois
                m = today.month - i
                y = today.year
                while m <= 0:
                    m += 12
                    y -= 1
                key = f"{y}-{m:02d}"
                result.append({
                    "month": key,
                    "label": MOIS_FR[m - 1],
                    "count": data_by_month.get(key, 0),
                })
            return result

    def get_alert_types_distribution(self) -> list[dict]:
        """Retourne la repartition des alertes par type."""
        with get_session() as db:
            stmt = (
                select(Alert.type, func.count(Alert.id).label("count"))
                .group_by(Alert.type)
            )
            rows = db.execute(stmt).all()

            # Labels lisibles
            LABELS = {
                "absences_repetees": "Absences répétées",
                "conges_excessifs": "Congés excessifs",
                "surcharge": "Surcharge",
                "retards": "Retards",
            }

            result = []
            for r in rows:
                result.append({
                    "type": r.type,
                    "label": LABELS.get(r.type, r.type),
                    "count": r.count,
                })
            return result

    def get_historical_alerts(self, limit: int = 20) -> list[dict]:
        """Retourne les alertes resolues (historique)."""
        with get_session() as db:
            alerts = db.scalars(
                select(Alert)
                .where(Alert.status == "resolue")
                .order_by(Alert.resolved_at.desc())
                .limit(limit)
            ).all()

            out = []
            for a in alerts:
                emp = db.get(Employee, a.employee_id) if a.employee_id else None
                out.append({
                    "id": str(a.id),
                    "title": a.title or "",
                    "description": a.description or "",
                    "severity": a.severity,
                    "employee_name": emp.full_name if emp else "—",
                    "risk_score": float(a.risk_score or 0),
                    "resolved_at": a.resolved_at,
                    "detected_at": a.detected_at,
                })
            return out
    
    def get_active_alerts(self) -> list[dict]:
        """Retourne les alertes actives avec timestamp."""
        with get_session() as db:
            alerts = db.scalars(
                select(Alert).where(Alert.status == "active")
                .order_by(Alert.detected_at.desc())
            ).all()
            out = []
            for a in alerts:
                emp = db.get(Employee, a.employee_id) if a.employee_id else None
                out.append({
                    "id": str(a.id),
                    "title": a.title or "",
                    "description": a.description or "",
                    "severity": a.severity,
                    "employee_name": emp.full_name if emp else "-",
                    "risk_score": float(a.risk_score or 0),
                    "detected_at": a.detected_at,     # ← AJOUT : timestamp réel
                })
            return out

    # ---------- Helper ----------
    def _exists(self, db, emp_id, alert_type, month) -> bool:
        """Verifie si une alerte identique existe deja.

        IMPORTANT : on ignore le status pour empecher la recreation
        d'une alerte apres resolution.
        """
        month_normalized = month.replace(day=1)
        return db.scalar(
            select(Alert.id).where(
                Alert.employee_id == emp_id,
                Alert.type == alert_type,
                Alert.period_month == month_normalized,
                # PAS de filtre sur Alert.status !
            )
        ) is not None