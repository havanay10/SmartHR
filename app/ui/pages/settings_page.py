"""Page Parametres — Configuration de l'application.

Ameliorations :
- Header avec ligne gradient
- SettingsCard avec accent vertical
- Champs avec pillule de valeur
- Boutons sans emoji
- Section status avec pastilles colorees
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QScrollArea, QFrame, QLabel, QPushButton, QMessageBox,
    QSpinBox, QDoubleSpinBox, QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSignal

from app.services.settings_service import SettingsService
from app.services.audit_service import AuditService


# =====================================================
# HELPERS VISUELS
# =====================================================
class ColorDot(QFrame):
    def __init__(self, color: str, size: int = 8):
        super().__init__()
        self.setFixedSize(size, size)
        self.setStyleSheet(f"""
            background-color: {color};
            border-radius: {size // 2}px;
            border: none;
        """)


class IconSquare(QLabel):
    def __init__(self, letter: str, color: str, bg: str, size: int = 32):
        super().__init__()
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText(letter)
        self.setStyleSheet(f"""
            background-color: {bg};
            color: {color};
            border-radius: {size // 3}px;
            font-size: {size // 3}pt;
            font-weight: 800;
            border: none;
        """)


# =====================================================
# SECTION DE PARAMETRES
# =====================================================
class SettingsCard(QFrame):
    """Carte pour une section de parametres avec accent vertical."""

    def __init__(self, title: str, description: str = "",
                 accent: str = "#0D7A6A"):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
            }
        """)

        self.v = QVBoxLayout(self)
        self.v.setContentsMargins(24, 20, 24, 20)
        self.v.setSpacing(18)

        # Header avec trait vertical + titre
        head_row = QHBoxLayout()
        head_row.setSpacing(10)

        accent_bar = QFrame()
        accent_bar.setFixedSize(3, 20)
        accent_bar.setStyleSheet(f"""
            background-color: {accent};
            border-radius: 2px;
            border: none;
        """)
        head_row.addWidget(accent_bar)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("""
            font-size: 13pt; font-weight: 800; color: #0F1E2E;
            background: transparent; border: none;
        """)
        head_row.addWidget(title_lbl)
        head_row.addStretch()

        self.v.addLayout(head_row)

        if description:
            desc_lbl = QLabel(description)
            desc_lbl.setStyleSheet("""
                font-size: 9.5pt; color: #7A8B9C;
                background: transparent; border: none;
                padding-left: 13px;
            """)
            desc_lbl.setWordWrap(True)
            self.v.addWidget(desc_lbl)

        # Separateur fin
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #EEF2F6; border: none;")
        self.v.addWidget(sep)

    def add_field(self, label: str, widget, description: str = ""):
        """Ajoute un champ label + widget + description."""
        row = QHBoxLayout()
        row.setSpacing(20)

        left = QVBoxLayout()
        left.setSpacing(3)

        lbl = QLabel(label)
        lbl.setStyleSheet("""
            font-size: 10pt; color: #0F1E2E; font-weight: 700;
            background: transparent; border: none;
        """)
        left.addWidget(lbl)

        if description:
            d = QLabel(description)
            d.setStyleSheet("""
                font-size: 8.5pt; color: #7A8B9C;
                background: transparent; border: none;
            """)
            d.setWordWrap(True)
            left.addWidget(d)

        row.addLayout(left, 1)
        row.addWidget(widget, 0, Qt.AlignmentFlag.AlignRight)

        self.v.addLayout(row)


# =====================================================
# INFO ROW (pour infos systeme)
# =====================================================
class InfoRow(QFrame):
    """Ligne d'information lecture seule."""

    def __init__(self, label: str, value: str,
                 status: str = None,
                 status_color: str = "#0D7A6A"):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border-radius: 8px;
                border: 1px solid #EEF2F6;
            }
        """)
        h = QHBoxLayout(self)
        h.setContentsMargins(14, 10, 14, 10)
        h.setSpacing(12)

        # Label
        lbl = QLabel(label)
        lbl.setStyleSheet("""
            font-size: 9pt; color: #7A8B9C; font-weight: 700;
            letter-spacing: 0.5px;
            background: transparent; border: none;
        """)
        h.addWidget(lbl)

        # Valeur
        val = QLabel(str(value))
        val.setStyleSheet("""
            font-size: 10pt; color: #0F1E2E; font-weight: 700;
            background: transparent; border: none;
        """)
        val.setWordWrap(True)
        h.addWidget(val, 1)

        # Status badge (optionnel)
        if status:
            badge = QFrame()
            badge.setStyleSheet(f"""
                background-color: {status_color}18;
                border-radius: 10px;
                border: 1px solid {status_color}40;
            """)
            badge_h = QHBoxLayout(badge)
            badge_h.setContentsMargins(10, 4, 14, 4)
            badge_h.setSpacing(6)
            badge_h.addWidget(ColorDot(status_color, 6))

            btxt = QLabel(status.upper())
            btxt.setStyleSheet(f"""
                font-size: 8pt; font-weight: 800; color: {status_color};
                letter-spacing: 0.5px;
                background: transparent; border: none;
            """)
            badge_h.addWidget(btxt)
            h.addWidget(badge)


# =====================================================
# PAGE PRINCIPALE
# =====================================================
class SettingsPage(QWidget):
    """Page Parametres."""

    navigate_to = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.svc = SettingsService()
        self.current_settings = self.svc.get_all_settings()

        # Layout racine
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: #F4F6F9; border: none; }")

        inner = QWidget()
        inner.setStyleSheet("background-color: #F4F6F9;")
        scroll.setWidget(inner)
        outer.addWidget(scroll)

        layout = QVBoxLayout(inner)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(20)

        # ============================================
        # HEADER
        # ============================================
        header = QHBoxLayout()

        left = QVBoxLayout()
        left.setSpacing(6)

        bc = QLabel("SMARTRH  /  PARAMÈTRES")
        bc.setStyleSheet("""
            color: #7A8B9C; font-size: 9pt; font-weight: 800;
            letter-spacing: 1.2px;
            background: transparent; border: none;
        """)
        left.addWidget(bc)

        t = QLabel("Paramètres de l'application")
        t.setStyleSheet("""
            font-size: 20pt; font-weight: 800; color: #0F1E2E;
            background: transparent; border: none;
        """)
        left.addWidget(t)

        s = QLabel(
            "Configurez les règles métier et consultez les informations système. "
            "Les modifications nécessitent un redémarrage de l'application."
        )
        s.setStyleSheet("""
            font-size: 10pt; color: #7A8B9C;
            background: transparent; border: none;
        """)
        s.setWordWrap(True)
        left.addWidget(s)

        header.addLayout(left, 1)

        # Badge version
        version_badge = QFrame()
        version_badge.setStyleSheet("""
            background-color: #E8F5F1;
            border-radius: 12px;
            border: 1px solid #D1FAE5;
        """)
        vb_layout = QHBoxLayout(version_badge)
        vb_layout.setContentsMargins(12, 6, 16, 6)
        vb_layout.setSpacing(8)
        vb_layout.addWidget(ColorDot("#0D7A6A", 8))

        vb_txt = QLabel(f"VERSION {self.current_settings['app_version']}")
        vb_txt.setStyleSheet("""
            background: transparent;
            color: #0D7A6A;
            font-size: 8.5pt;
            font-weight: 800;
            letter-spacing: 0.6px;
            border: none;
        """)
        vb_layout.addWidget(vb_txt)

        header.addWidget(version_badge, 0, Qt.AlignmentFlag.AlignTop)

        layout.addLayout(header)

        # Ligne gradient
        gradient = QFrame()
        gradient.setFixedHeight(3)
        gradient.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2E86DE, stop:1 #0D7A6A
                );
                border: none;
                border-radius: 2px;
            }
        """)
        layout.addWidget(gradient)

        # ============================================
        # SECTION 1 : Informations application
        # ============================================
        info_card = SettingsCard(
            "Informations de l'application",
            "Données système en lecture seule",
            accent="#2E86DE"
        )

        # Grid 2 colonnes
        info_grid = QGridLayout()
        info_grid.setSpacing(10)

        # Row 1 : nom + version
        info_grid.addWidget(InfoRow(
            "Nom",
            self.current_settings["app_name"]
        ), 0, 0)

        info_grid.addWidget(InfoRow(
            "Version",
            self.current_settings["app_version"]
        ), 0, 1)

        # Row 2 : DB (full width)
        db_url = self.current_settings["database_url"]
        if "@" in db_url:
            db_display = "PostgreSQL 16  •  " + db_url.split("@")[-1]
        else:
            db_display = db_url

        info_grid.addWidget(InfoRow(
            "Base de données",
            db_display
        ), 1, 0, 1, 2)

        # Row 3 : export dir (full width)
        info_grid.addWidget(InfoRow(
            "Dossier exports",
            self.current_settings["export_dir"]
        ), 2, 0, 1, 2)

        info_card.v.addLayout(info_grid)
        layout.addWidget(info_card)

        # ============================================
        # SECTION 2 : Règles métier
        # ============================================
        rules_card = SettingsCard(
            "Règles métier (CDC)",
            "Ces seuils contrôlent le comportement des alertes et du scoring IA.",
            accent="#0D7A6A"
        )

        # Seuil absences
        self.spin_absence = QSpinBox()
        self.spin_absence.setRange(1, 30)
        self.spin_absence.setValue(self.current_settings["absence_alert_threshold"])
        self.spin_absence.setSuffix(" jours")
        self.spin_absence.setStyleSheet(self._spinbox_style())
        rules_card.add_field(
            "Seuil d'alerte absences",
            self.spin_absence,
            "Nombre de jours d'absence par mois avant déclenchement d'une alerte critique"
        )

        # Séparateur
        sep1 = QFrame()
        sep1.setFixedHeight(1)
        sep1.setStyleSheet("background-color: #EEF2F6; border: none;")
        rules_card.v.addWidget(sep1)

        # Multiplicateur congés
        self.spin_leave = QDoubleSpinBox()
        self.spin_leave.setRange(1.0, 5.0)
        self.spin_leave.setSingleStep(0.1)
        self.spin_leave.setValue(self.current_settings["leave_risk_multiplier"])
        self.spin_leave.setSuffix(" x moyenne")
        self.spin_leave.setStyleSheet(self._spinbox_style())
        rules_card.add_field(
            "Multiplicateur de risque congés",
            self.spin_leave,
            "Multiplicateur appliqué à la moyenne pour détecter les congés excessifs"
        )

        # Séparateur
        sep2 = QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet("background-color: #EEF2F6; border: none;")
        rules_card.v.addWidget(sep2)

        # Seuil match IA
        self.spin_match = QSpinBox()
        self.spin_match.setRange(0, 100)
        self.spin_match.setValue(self.current_settings["match_score_threshold"])
        self.spin_match.setSuffix(" %")
        self.spin_match.setStyleSheet(self._spinbox_style())
        rules_card.add_field(
            "Seuil de présélection IA",
            self.spin_match,
            "Score minimum pour qu'un candidat soit automatiquement présélectionné"
        )

        layout.addWidget(rules_card)

        # =====================================================
        # SECTION 3 : Informations système
        # =====================================================
        sys_card = SettingsCard(
            "Informations système",
            "État des fichiers et ressources nécessaires",
            accent="#7C3AED"
        )

        sys_grid = QGridLayout()
        sys_grid.setSpacing(10)

        env_exists = self.svc.ENV_FILE.exists()
        if env_exists:
            sys_grid.addWidget(InfoRow(
                "Fichier .env",
                str(self.svc.ENV_FILE),
                status="Présent",
                status_color="#0D7A6A"
            ), 0, 0, 1, 2)
        else:
            sys_grid.addWidget(InfoRow(
                "Fichier .env",
                str(self.svc.ENV_FILE),
                status="Manquant",
                status_color="#C0392B"
            ), 0, 0, 1, 2)

        sys_card.v.addLayout(sys_grid)
        layout.addWidget(sys_card)

        # =====================================================
        # SECTION 4 : Actions (footer bar)
        # =====================================================
        actions_card = QFrame()
        actions_card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
            }
        """)
        ac_layout = QHBoxLayout(actions_card)
        ac_layout.setContentsMargins(24, 16, 24, 16)
        ac_layout.setSpacing(14)

        # Message d'info avec pastille
        ac_layout.addWidget(ColorDot("#F39C12", 8))

        info_lbl = QLabel(
            "Les modifications seront appliquées au prochain démarrage de l'application."
        )
        info_lbl.setStyleSheet("""
            font-size: 9.5pt; color: #B9770E; font-weight: 600;
            background: transparent; border: none;
        """)
        ac_layout.addWidget(info_lbl)
        ac_layout.addStretch()

        # Bouton Reset
        btn_reset = QPushButton("Valeurs par défaut")
        btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_reset.setMinimumHeight(40)
        btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #5A6B7D;
                border: 1px solid #E4E9EF;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 9.5pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #F4F6F9;
                border-color: #94A3B8;
                color: #0F1E2E;
            }
        """)
        btn_reset.clicked.connect(self._reset_defaults)
        ac_layout.addWidget(btn_reset)

        # Bouton Enregistrer
        btn_save = QPushButton("Enregistrer les modifications")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setMinimumHeight(40)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #0D7A6A;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 9.5pt;
                font-weight: 700;
            }
            QPushButton:hover { background-color: #0A6456; }
            QPushButton:pressed { background-color: #084C41; }
        """)
        btn_save.clicked.connect(self._save_settings)
        ac_layout.addWidget(btn_save)

        layout.addWidget(actions_card)

        layout.addStretch()

    # =====================================================
    # HELPERS UI
    # =====================================================
    def _spinbox_style(self) -> str:
        return """
            QSpinBox, QDoubleSpinBox {
                border: 1px solid #E4E9EF;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 10pt;
                font-weight: 600;
                color: #0F1E2E;
                background-color: #F8FAFC;
                min-width: 170px;
            }
            QSpinBox:focus, QDoubleSpinBox:focus {
                border: 1px solid #0D7A6A;
                background-color: #FFFFFF;
            }
            QSpinBox::up-button, QDoubleSpinBox::up-button,
            QSpinBox::down-button, QDoubleSpinBox::down-button {
                width: 20px;
                border: none;
                background: transparent;
            }
            QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 5px solid #64748B;
                width: 0; height: 0;
            }
            QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #64748B;
                width: 0; height: 0;
            }
        """

    # =====================================================
    # ACTIONS
    # =====================================================
    def _save_settings(self):
        """Enregistre les parametres modifies dans .env."""
        updates = {
            "ABSENCE_ALERT_THRESHOLD": self.spin_absence.value(),
            "LEAVE_RISK_MULTIPLIER": round(self.spin_leave.value(), 2),
            "MATCH_SCORE_THRESHOLD": self.spin_match.value(),
        }

        errors = []
        for key, value in updates.items():
            ok, msg = self.svc.validate_value(key, value)
            if not ok:
                errors.append(f"{key} : {msg}")

        if errors:
            QMessageBox.warning(
                self, "Validation",
                "Erreurs détectées :\n\n" + "\n".join(errors)
            )
            return

        count, errors = self.svc.update_multiple_settings(updates)

        if errors:
            QMessageBox.critical(
                self, "Erreur",
                "Certains paramètres n'ont pas pu être enregistrés :\n\n"
                + "\n".join(errors)
            )
        else:
            AuditService().log_action(
                action="update_setting",
                entity_type="setting",
                entity_id=",".join(updates.keys()),
                details=f"{count} paramètre(s) modifié(s)",
            )

            QMessageBox.information(
                self, "Succès",
                f"{count} paramètre(s) enregistré(s).\n\n"
                "Redémarrez l'application pour appliquer les modifications."
            )

    def _reset_defaults(self):
        """Reinitialise les seuils par defaut."""
        reply = QMessageBox.question(
            self, "Confirmation",
            "Voulez-vous réinitialiser tous les seuils aux valeurs par défaut ?\n\n"
            "• Seuil absences : 5 jours\n"
            "• Multiplicateur congés : 1.5\n"
            "• Seuil match IA : 80%",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        ok, msg = self.svc.reset_to_defaults()

        self.spin_absence.setValue(5)
        self.spin_leave.setValue(1.5)
        self.spin_match.setValue(80)

        if ok:
            QMessageBox.information(
                self, "Succès",
                "Paramètres réinitialisés.\n\n"
                "Redémarrez l'application pour appliquer."
            )
        else:
            QMessageBox.warning(self, "Attention", msg)