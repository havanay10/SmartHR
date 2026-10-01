"""Service d'analyse predictive ML pour le turnover.

Utilise scikit-learn (RandomForestClassifier) pour predire
le risque de depart d'un employe.

Features extraites :
- Anciennete
- Salaire
- Nombre d'alertes actives
- Jours d'absence dans l'annee
- Mode de travail
- CDI ou non

Note : les labels d'entrainement sont derives de regles metier
car on n'a pas encore d'historique reel de departs. Dans un vrai
systeme, les labels viendraient des departs observes.
"""
from datetime import date, timedelta

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

from sqlalchemy import select, func
from app.db.connection import get_session
from app.models.employee import Employee
from app.models.leave import LeaveRequest
from app.models.alert import Alert


class PredictionService:
    """Prediction du risque de turnover via Machine Learning."""

    # Cache du modele (evite de re-entrainer a chaque appel)
    _model = None
    _scaler = None
    _feature_names = None
    _last_train_size = 0

    # - alert_count : signal le plus fort (burnout)
    # - leave_days_year : signal moyen (désengagement)
    # - seniority_years : anciennete au depart (depart "naturel" ou non)
    FEATURE_NAMES = [
        "alert_count",
        "leave_days_year",
        "seniority_years",
    ]

    # Seuils metier (utilises pour calculer les labels d'entrainement)
    RISK_ALERT_COUNT = 2       # >= 2 alertes => signal fort
    RISK_LEAVE_DAYS = 10       # >= 10 jours d'absence => signal fort
    RISK_SENIORITY_LOW = 1     # < 1 an => nouvel arrivant
    RISK_SALARY_LOW = 50000    # < 50k => sous la mediane

    # Raisons de départ considérées comme "risque" (à éviter)
    RISKY_DEPARTURE_REASONS = [
            "démission",
            "demission",
            "rupture",
            "licenciement",
            "abandon",
        ]
    # =====================================================
    # EXTRACTION DES FEATURES
    # =====================================================
    def extract_features(self, include_departed: bool = False) -> pd.DataFrame:
        """Extrait les features pour tous les employes.

        Args:
            include_departed: si True, inclut aussi les anciens employes
                              (utile pour l'entrainement du modele)
        """
        with get_session() as db:
            if include_departed:
                employees = db.scalars(
                    select(Employee).where(Employee.status.in_(["actif", "sorti"]))
                ).all()
            else:
                employees = db.scalars(
                    select(Employee).where(Employee.status == "actif")
                ).all()

            today = date.today()
            year_start = date(today.year, 1, 1)

            rows = []
            for emp in employees:
                # Nombre d'alertes (toutes, pas juste actives)
                # Important : pour les anciens, leurs alertes ont pu etre resolues apres leur depart
                alerts = db.scalar(
                    select(func.count()).select_from(Alert)
                    .where(
                        Alert.employee_id == emp.id,
                    )
                ) or 0

                # Jours de conges valides cette annee
                # Pour les sortis : on prend TOUTES leurs absences (pas juste cette annee)
                # Pour les actifs : cette annee seulement
                if emp.status == "sorti":
                    leave_days = db.scalar(
                        select(func.sum(LeaveRequest.duration_days))
                        .where(
                            LeaveRequest.employee_id == emp.id,
                            LeaveRequest.status == "valide",
                        )
                    ) or 0
                else:
                    leave_days = db.scalar(
                        select(func.sum(LeaveRequest.duration_days))
                        .where(
                            LeaveRequest.employee_id == emp.id,
                            LeaveRequest.start_date >= year_start,
                            LeaveRequest.status == "valide",
                        )
                    ) or 0

                work_mode = (emp.work_mode or "").lower()

                # Ancienneté au moment du DÉPART pour les anciens
                # Sinon ancienneté actuelle pour les actifs
                if emp.status == "sorti" and emp.departure_date and emp.hire_date:
                    delta = emp.departure_date - emp.hire_date
                    seniority = round(delta.days / 365.25, 2)
                else:
                    seniority = float(emp.seniority_years)

                rows.append({
                    "employee_id": str(emp.id),
                    "employee_name": emp.full_name,
                    "job_title": emp.job_title,
                    "status": emp.status,
                    "departure_date": emp.departure_date,
                    "departure_reason": emp.departure_reason,
                    "seniority_years": seniority,       # ← nouvelle valeur
                    "salary_base": float(emp.salary_base or 0),
                    "alert_count": int(alerts),
                    "leave_days_year": float(leave_days),
                    "is_hybrid": 1 if "hybride" in work_mode else 0,
                    "is_remote": 1 if ("télétravail" in work_mode
                                        or "teletravail" in work_mode
                                        or "remote" in work_mode) else 0,
                    "has_manager": 1 if emp.manager_id else 0,
                    "is_cdi": 1 if (emp.contract_type or "").upper() == "CDI" else 0,
                })

            return pd.DataFrame(rows)

    # =====================================================
    # LABELS D'ENTRAINEMENT (synthetiques)
    # =====================================================
    

    def _compute_target(self, df: pd.DataFrame) -> np.ndarray:
        """Calcule un label binaire.

        Label = 1 si : départ à risque (démission, rupture, licenciement)
        Label = 0 si : actif OU départ normal (retraite, fin CDD)
        """
        labels = []

        for _, row in df.iterrows():
            status = (row.get("status") or "").lower()
            reason = (row.get("departure_reason") or "").lower()

            if status == "sorti":
                # Ancien : label = 1 SEULEMENT si départ à risque
                is_risky = any(r in reason for r in self.RISKY_DEPARTURE_REASONS)
                labels.append(1 if is_risky else 0)
            else:
                # Actif : label = 0 (n'est pas encore parti)
                labels.append(0)

        labels = np.array(labels)

        # Securite : 2 classes nécessaires
        if len(np.unique(labels)) < 2:
            labels[0] = 1 - labels[0]

        return labels
    # =====================================================
    # ENTRAINEMENT
    # =====================================================
    def train(self, force: bool = False) -> dict:
        """Entraine le modele sur les donnees actuelles (avec vrais labels)."""
        # Inclut les anciens employes pour l'entrainement
        df = self.extract_features(include_departed=True)

        if len(df) < 4:
            return {"trained": False, "error": "Pas assez de donnees (< 4 employes)"}

        # Evite de re-entrainer si les donnees n'ont pas change
        if not force and self._model is not None and self._last_train_size == len(df):
            return self._get_model_info()

        X = df[self.FEATURE_NAMES].values
        y = self._compute_target(df)

        # Securite : besoin de 2 classes
        if len(np.unique(y)) < 2:
            y[0] = 1 - y[0]   # Force au moins 2 classes

        # Normalisation
        self._scaler = StandardScaler()
        X_scaled = self._scaler.fit_transform(X)

        # Modele RandomForest
        self._model = RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            random_state=42,
        )
        self._model.fit(X_scaled, y)
        self._feature_names = self.FEATURE_NAMES
        self._last_train_size = len(df)

        return self._get_model_info()

    def _get_model_info(self) -> dict:
        """Retourne les infos du modele entraine."""
        if self._model is None:
            return {"trained": False}

        importances = self._model.feature_importances_
        importance_dict = dict(zip(self._feature_names, importances))
        sorted_imp = sorted(importance_dict.items(), key=lambda x: -x[1])

        return {
            "trained": True,
            "n_samples": self._last_train_size,
            "n_features": len(self._feature_names),
            "feature_importances": sorted_imp,
        }

    # =====================================================
    # PREDICTIONS
    # =====================================================
    def predict_all(self) -> list[dict]:
        """Predit le risque pour tous les employes (mode hybride).

        Score = 70% regles metier + 30% correction ML
        """
        # Entraine si necessaire
        if self._model is None:
            self.train()

        df = self.extract_features(include_departed=False)
        if df.empty:
            return []

        # ============================================
        # 1. Score par REGLES (transparent et explicable)
        # ============================================
        rule_scores = self._compute_rule_score(df)

        # ============================================
        # 2. Score ML (si modele disponible)
        # ============================================
        ml_scores = np.zeros(len(df))
        if self._model is not None and self._scaler is not None:
            try:
                X = df[self.FEATURE_NAMES].values
                X_scaled = self._scaler.transform(X)
                ml_scores = self._model.predict_proba(X_scaled)[:, 1] * 100
            except Exception as e:
                print(f"[PredictionService] Erreur ML: {e}")

        # ============================================
        # 3. Score hybride : 70% regles + 30% ML
        # ============================================
        final_scores = 0.7 * rule_scores + 0.3 * ml_scores

        results = []
        for i, row in df.iterrows():
            score = round(float(final_scores[i]), 1)

            # Niveau
                        # Seuils ajustes pour mieux distinguer
            if score >= 55:
                level, color = "Élevé", "#C0392B"
            elif score >= 25:
                level, color = "Modéré", "#F39C12"
            else:
                level, color = "Faible", "#0D7A6A"

            # Raisons (explicables)
            reasons = []
            if row["alert_count"] >= 2:
                reasons.append(f"{int(row['alert_count'])} alertes actives")
            elif row["alert_count"] == 1:
                reasons.append("1 alerte active")
            if row["leave_days_year"] >= 10:
                reasons.append(f"{row['leave_days_year']:.0f}j d'absence")
            elif row["leave_days_year"] >= 5:
                reasons.append(f"{row['leave_days_year']:.0f}j d'absence")
            if row["seniority_years"] < 1:
                reasons.append("Nouvel arrivant")
            if row["salary_base"] < self.RISK_SALARY_LOW:
                reasons.append("Salaire sous la médiane")

            results.append({
                "employee_id": row["employee_id"],
                "employee_name": row["employee_name"],
                "job_title": row["job_title"],
                "risk_score": score,
                "risk_level": level,
                "risk_color": color,
                "reasons": reasons,
                "alert_count": int(row["alert_count"]),
                "leave_days_year": float(row["leave_days_year"]),
                "seniority_years": float(row["seniority_years"]),
                "rule_score": round(float(rule_scores[i]), 1),
                "ml_score": round(float(ml_scores[i]), 1),
            })

        # Tri par risque decroissant
        results.sort(key=lambda x: -x["risk_score"])
        return results

    def _compute_rule_score(self, df: pd.DataFrame) -> np.ndarray:
        """Calcule un score de risque base sur des REGLES metier.

        Score = 0 a 100.
        """
        scores = []

        for _, row in df.iterrows():
            score = 0

            # ============ Alertes ============
            # Alertes (signal fort)
            n = row["alert_count"]
            if n >= 3:
                score += 50      # Augmente de 40 a 50
            elif n == 2:
                score += 35
            elif n == 1:
                score += 15

            # ============ Absences ============
            days = row["leave_days_year"]
            if days >= 20:
                score += 40       # 20+ jours = burnout
            elif days >= 15:
                score += 32
            elif days >= 10:
                score += 24
            elif days >= 5:
                score += 12

            # ============ Anciennete ============
            sen = row["seniority_years"]
            if sen < 1:
                score += 15       # Nouvel arrivant = risque
            elif sen < 2:
                score += 8

            # ============ Salaire ============
            if row["salary_base"] < self.RISK_SALARY_LOW:
                score += 8

            scores.append(min(100, score))

        return np.array(scores)

    def get_summary(self) -> dict:
        """Retourne un resume des predictions."""
        predictions = self.predict_all()
        if not predictions:
            return {"total": 0, "high": 0, "medium": 0, "low": 0}

        return {
            "total": len(predictions),
            "high": sum(1 for p in predictions if p["risk_level"] == "Élevé"),
            "medium": sum(1 for p in predictions if p["risk_level"] == "Modéré"),
            "low": sum(1 for p in predictions if p["risk_level"] == "Faible"),
        }