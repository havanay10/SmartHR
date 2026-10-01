"""Service de journal d'audit.

Trace toutes les actions utilisateurs dans la table audit_logs.
Conforme RGPD : qui a fait quoi, quand, sur quoi.
"""
from datetime import datetime, date, timedelta
from uuid import uuid4

from sqlalchemy import select, func, or_
from app.db.connection import get_session
from app.models.user import User, AuditLog


# Catalogue des actions avec leurs icones et libelles
ACTION_CATALOG = {
    "create_employee":  ("➕", "Création employé",   "#0D7A6A"),
    "validate_leave":   ("✅", "Validation congé",    "#0D7A6A"),
    "create_leave":     ("📅", "Création congé",     "#2E86DE"),
    "resolve_alert":    ("✓",  "Résolution alerte",  "#0D7A6A"),
    "create_job_offer": ("💼", "Création offre",     "#2E86DE"),
    "create_relation":  ("🔗", "Relation créée",     "#8E44AD"),
    "delete_relation":  ("🗑️", "Relation supprimée", "#C0392B"),
    "create_binome":    ("🤝", "Binôme créé",        "#0D7A6A"),
    "delete_binome":    ("🗑️", "Binôme archivé",    "#C0392B"),
    "generate_report":  ("📄", "Rapport généré",    "#B9770E"),
    "update_setting":   ("⚙️", "Paramètre modifié",  "#7A8B9C"),
    "login":            ("🔑", "Connexion",           "#0D7A6A"),
    "logout":           ("🚪", "Déconnexion",        "#7A8B9C"),
}


class AuditService:
    """Service du journal d'audit."""

    # Cache du user par defaut (DRH Rakoto)
    _default_user_id = None

    # =====================================================
    # ECRITURE
    # =====================================================
    def log_action(
        self,
        action: str,
        entity_type: str = None,
        entity_id: str = None,
        details: str = None,
        user_id: str = None,
    ) -> bool:
        """Enregistre une action dans le journal.

        Args:
            action: code de l'action (ex: 'create_employee')
            entity_type: type de l'entite (ex: 'employee', 'leave')
            entity_id: UUID de l'entite concernee
            details: texte descriptif
            user_id: ID utilisateur (si None, utilise l'utilisateur par defaut)

        Returns:
            True si succes, False sinon.
        """
        try:
            # Recupere le user par defaut si non fourni
            if user_id is None:
                user_id = self._get_default_user_id()

            with get_session() as db:
                log = AuditLog(
                    id=str(uuid4()),
                    user_id=user_id,
                    action=action,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    created_at=datetime.utcnow(),
                )
                db.add(log)
            return True
        except Exception as e:
            print(f"[AuditService] Erreur log: {e}")
            return False

    def _get_default_user_id(self) -> str | None:
        """Recupere l'ID du DRH par defaut (avec cache)."""
        if AuditService._default_user_id:
            return AuditService._default_user_id

        try:
            with get_session() as db:
                user = db.scalar(
                    select(User).where(User.email == "rakoto@smartrh.fr")
                )
                if user:
                    AuditService._default_user_id = str(user.id)
                    return AuditService._default_user_id

                # Sinon premier user actif
                user = db.scalar(
                    select(User).where(User.is_active == True).limit(1)
                )
                if user:
                    AuditService._default_user_id = str(user.id)
                    return AuditService._default_user_id
        except Exception as e:
            print(f"[AuditService] Erreur user par defaut: {e}")

        return None

    # =====================================================
    # LECTURE
    # =====================================================
    def get_logs(
        self,
        limit: int = 100,
        action_filter: str = None,
        days_back: int = None,
    ) -> list[dict]:
        """Retourne les derniers logs avec infos enrichies."""
        with get_session() as db:
            stmt = select(AuditLog).order_by(AuditLog.created_at.desc())

            # Filtre par action
            if action_filter and action_filter != "all":
                stmt = stmt.where(AuditLog.action == action_filter)

            # Filtre par date
            if days_back is not None:
                cutoff = datetime.utcnow() - timedelta(days=days_back)
                stmt = stmt.where(AuditLog.created_at >= cutoff)

            stmt = stmt.limit(limit)
            logs = db.scalars(stmt).all()

            result = []
            for log in logs:
                # Recupere l'utilisateur
                user = db.get(User, log.user_id) if log.user_id else None
                user_name = user.full_name if user and user.full_name else "Système"
                user_email = user.email if user else "—"

                # Recupere l'entite concernee (nom)
                entity_name = self._get_entity_name(db, log.entity_type, log.entity_id)

                # Icone + libelle
                action_code = log.action or "unknown"
                cat = ACTION_CATALOG.get(action_code, ("🔹", action_code, "#7A8B9C"))
                icon, label, color = cat

                result.append({
                    "id": str(log.id),
                    "action": action_code,
                    "action_label": label,
                    "action_icon": icon,
                    "action_color": color,
                    "entity_type": log.entity_type,
                    "entity_id": str(log.entity_id) if log.entity_id else None,
                    "entity_name": entity_name,
                    "user_name": user_name,
                    "user_email": user_email,
                    "created_at": log.created_at,
                })
            return result

    def _get_entity_name(self, db, entity_type: str, entity_id: str) -> str | None:
        """Retourne le nom de l'entite concernee (employee, etc.)."""
        if not entity_type or not entity_id:
            return None

        try:
            if entity_type == "employee":
                from app.models.employee import Employee
                emp = db.get(Employee, entity_id)
                return emp.full_name if emp else None

            elif entity_type == "leave":
                from app.models.leave import LeaveRequest
                leave = db.get(LeaveRequest, entity_id)
                if leave:
                    emp = db.get(__import__("app.models.employee",
                                            fromlist=["Employee"]).Employee,
                                 leave.employee_id)
                    return f"{emp.full_name} ({leave.leave_type})" if emp else None

            elif entity_type == "alert":
                from app.models.alert import Alert
                alert = db.get(Alert, entity_id)
                return alert.title if alert else None

            elif entity_type == "job_offer":
                from app.models.recruitment import JobOffer
                offer = db.get(JobOffer, entity_id)
                return offer.title if offer else None

            elif entity_type == "relation":
                # Retourne un libelle simple
                return "Relation entre 2 employés"

            elif entity_type == "binome":
                return "Binôme"

            elif entity_type == "report":
                from app.models.report import Report
                r = db.get(Report, entity_id)
                return r.title if r else None

            elif entity_type == "setting":
                return entity_id  # la cle est le nom
        except Exception:
            return None

        return None

    # =====================================================
    # KPIs
    # =====================================================
    def get_kpis(self) -> dict:
        """Retourne les KPIs du journal."""
        with get_session() as db:
            total = db.scalar(select(func.count()).select_from(AuditLog)) or 0

            # Aujourd'hui
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_count = db.scalar(
                select(func.count()).select_from(AuditLog)
                .where(AuditLog.created_at >= today_start)
            ) or 0

            # Cette semaine (7 jours)
            week_ago = datetime.utcnow() - timedelta(days=7)
            week_count = db.scalar(
                select(func.count()).select_from(AuditLog)
                .where(AuditLog.created_at >= week_ago)
            ) or 0

            # Repartition par type
            stmt = (
                select(AuditLog.action, func.count(AuditLog.id).label("n"))
                .group_by(AuditLog.action)
                .order_by(func.count(AuditLog.id).desc())
            )
            by_action = {}
            for row in db.execute(stmt):
                by_action[row.action] = row.n

            return {
                "total": total,
                "today": today_count,
                "week": week_count,
                "by_action": by_action,
            }

    def get_available_actions(self) -> list[tuple]:
        """Retourne la liste des actions pour les filtres."""
        with get_session() as db:
            stmt = (
                select(AuditLog.action, func.count(AuditLog.id))
                .group_by(AuditLog.action)
                .order_by(AuditLog.action)
            )
            result = []
            for action, count in db.execute(stmt):
                if action in ACTION_CATALOG:
                    icon, label, color = ACTION_CATALOG[action]
                else:
                    icon, label, color = "🔹", action, "#7A8B9C"
                result.append({
                    "code": action,
                    "label": label,
                    "icon": icon,
                    "color": color,
                    "count": count,
                })
            return result