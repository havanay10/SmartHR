"""Service de gestion des parametres de l'application.

Lit et modifie le fichier .env sans casser les commentaires existants.
"""
from pathlib import Path
from typing import Any

from config import settings, BASE_DIR


class SettingsService:
    """Service de lecture/ecriture des parametres."""

    ENV_FILE = BASE_DIR / ".env"

    # Parametres modifiables avec leur type et description
    EDITABLE_SETTINGS = {
        "ABSENCE_ALERT_THRESHOLD": {
            "type": "int",
            "label": "Seuil d'alerte absences (jours)",
            "description": "Nombre de jours d'absence dans le mois avant alerte critique",
            "min": 1,
            "max": 30,
            "unit": "jours",
            "category": "regles_metier",
        },
        "LEAVE_RISK_MULTIPLIER": {
            "type": "float",
            "label": "Multiplicateur de risque conges",
            "description": "Multiplicateur applique a la moyenne pour detecter les conges excessifs",
            "min": 1.0,
            "max": 5.0,
            "step": 0.1,
            "unit": "x moyenne",
            "category": "regles_metier",
        },
        "MATCH_SCORE_THRESHOLD": {
            "type": "int",
            "label": "Seuil de preselection IA",
            "description": "Score minimum (%) pour qu'un candidat soit preselectionne",
            "min": 0,
            "max": 100,
            "unit": "%",
            "category": "regles_metier",
        },
    }

    # =====================================================
    # LECTURE
    # =====================================================
    def get_all_settings(self) -> dict:
        """Retourne tous les parametres actuels."""
        return {
            "absence_alert_threshold": settings.ABSENCE_ALERT_THRESHOLD,
            "leave_risk_multiplier": settings.LEAVE_RISK_MULTIPLIER,
            "match_score_threshold": settings.MATCH_SCORE_THRESHOLD,
            # Infos app
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "database_url": settings.DATABASE_URL,
            "export_dir": str(settings.EXPORT_DIR),
            "debug": settings.DB_ECHO,
        }

    def get_env_file_content(self) -> str:
        """Retourne le contenu brut du .env."""
        if not self.ENV_FILE.exists():
            return ""
        return self.ENV_FILE.read_text(encoding="utf-8")

    # =====================================================
    # ECRITURE
    # =====================================================
    def update_setting(self, key: str, value: Any) -> tuple[bool, str]:
        """Met a jour une cle dans le fichier .env.

        Preserve les commentaires et les autres lignes.

        Args:
            key: Nom de la variable (ex: ABSENCE_ALERT_THRESHOLD)
            value: Nouvelle valeur (convertie en string)

        Returns:
            (success, message)
        """
        if key not in self.EDITABLE_SETTINGS:
            return False, f"Paramètre non modifiable : {key}"

        if not self.ENV_FILE.exists():
            return False, f"Fichier .env introuvable : {self.ENV_FILE}"

        try:
            lines = self.ENV_FILE.read_text(encoding="utf-8").splitlines()
        except Exception as e:
            return False, f"Erreur lecture .env : {e}"

        # Nouvelle ligne
        new_line = f"{key}={value}"
        found = False
        new_lines = []

        for line in lines:
            stripped = line.strip()
            # Detecte la ligne correspondante (en ignorant les commentaires)
            if stripped and not stripped.startswith("#"):
                if "=" in stripped:
                    existing_key = stripped.split("=", 1)[0].strip()
                    if existing_key == key:
                        new_lines.append(new_line)
                        found = True
                        continue
            new_lines.append(line)

        # Si la cle n'existe pas, on l'ajoute
        if not found:
            if new_lines and new_lines[-1].strip():
                new_lines.append("")
            new_lines.append(new_line)

        # Ecriture
        try:
            self.ENV_FILE.write_text(
                "\n".join(new_lines) + "\n",
                encoding="utf-8"
            )
            return True, f"Paramètre '{key}' mis à jour (redémarrage requis)."
        except Exception as e:
            return False, f"Erreur écriture .env : {e}"

    def update_multiple_settings(self, updates: dict) -> tuple[int, list[str]]:
        """Met a jour plusieurs parametres d'un coup.

        Returns:
            (nombre_succes, liste_erreurs)
        """
        success_count = 0
        errors = []

        for key, value in updates.items():
            ok, msg = self.update_setting(key, value)
            if ok:
                success_count += 1
            else:
                errors.append(msg)

        return success_count, errors

    # =====================================================
    # REINITIALISATION
    # =====================================================
    def reset_to_defaults(self) -> tuple[bool, str]:
        """Reinitialise les seuils aux valeurs par defaut."""
        defaults = {
            "ABSENCE_ALERT_THRESHOLD": 5,
            "LEAVE_RISK_MULTIPLIER": 1.5,
            "MATCH_SCORE_THRESHOLD": 80,
        }
        count, errors = self.update_multiple_settings(defaults)
        if errors:
            return False, " ; ".join(errors)
        return True, f"{count} paramètres réinitialisés."

    # =====================================================
    # VALIDATION
    # =====================================================
    def validate_value(self, key: str, value: Any) -> tuple[bool, str]:
        """Valide une valeur selon sa definition."""
        if key not in self.EDITABLE_SETTINGS:
            return False, f"Paramètre inconnu : {key}"

        meta = self.EDITABLE_SETTINGS[key]
        type_name = meta["type"]

        try:
            if type_name == "int":
                v = int(value)
            elif type_name == "float":
                v = float(value)
            else:
                v = value

            if "min" in meta and v < meta["min"]:
                return False, f"Valeur minimale : {meta['min']}"
            if "max" in meta and v > meta["max"]:
                return False, f"Valeur maximale : {meta['max']}"

            return True, "OK"
        except (ValueError, TypeError):
            return False, f"Valeur invalide (attendu : {type_name})"