"""Page Journal d'audit — Traçabilité RGPD.

Ameliorations :
- KPI cards custom avec carres colores (remplace les emojis)
- Log rows avec indicator carre + hierarchies claires
- Section header avec pastille + ligne gradient
- Filtres ameliorees avec chips uniformes
- Time display sans emoji
- Typographie homogene
"""
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QScrollArea, QFrame, QLabel, QPushButton, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from app.services.audit_service import AuditService


# =====================================================
# HELPERS VISUELS
# =====================================================
class ColorDot(QFrame):
    """Pastille colorée."""

    def __init__(self, color: str, size: int = 8):
        super().__init__()
        self.setFixedSize(size, size)
        self.setStyleSheet(f"""
            background-color: {color};
            border-radius: {size // 2}px;
            border: none;
        """)


class IconSquare(QLabel):
    """Carré arrondi coloré avec lettre (remplace les emojis KPI)."""

    def __init__(self, letter: str, color: str, bg: str, size: int = 36):
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


class ActionIndicator(QLabel):
    """Carré coloré pour identifier le type d'action."""

    def __init__(self, letter: str, color: str, bg: str, size: int = 42):
        super().__init__()
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText(letter)
        self.setStyleSheet(f"""
            background-color: {bg};
            color: {color};
            border-radius: 10px;
            font-size: {size // 3}pt;
            font-weight: 800;
            border: none;
        """)


def action_letter(action_code: str) -> str:
    """Retourne une lettre pour identifier un type d'action."""
    if not action_code:
        return "•"

    code = action_code.lower().strip()

    mapping = {
        "validate_leave": "V",
        "create_leave": "C",
        "resolve_alert": "R",
        "create_job_offer": "O",
        "create_employee": "E",
        "delete_employee": "D",
        "update_employee": "U",
        "create_relation": "L",
        "delete_relation": "L",
        "create_binome": "B",
        "delete_binome": "B",
        "generate_report": "P",
        "export_candidates_csv": "X",
        "import_cv": "I",
    }

    return mapping.get(code, code[:1].upper())


# =====================================================
# LIGNE DE LOG
# =====================================================
class LogRow(QFrame):
    """Ligne d'un log dans le journal."""

    def __init__(self, log: dict):
        super().__init__()
        self.setMinimumHeight(80)

        color = log.get("action_color", "#7A8B9C")
        action_code = log.get("action_code", log.get("action", ""))
        action_label = log.get("action_label", "—")

        # Lettre de l'indicateur
        letter = action_letter(action_code)

        # Fond pastel à 20% d'opacité
        bg_pastel = f"{color}20"

        self.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border-radius: 10px;
                border: 1px solid #E4E9EF;
                border-left: 4px solid {color};
            }}
            QFrame:hover {{
                background-color: #FAFDFB;
            }}
        """)

        h = QHBoxLayout(self)
        h.setContentsMargins(18, 12, 18, 12)
        h.setSpacing(16)

        # Indicateur coloré avec lettre
        indicator = ActionIndicator(letter, color, bg_pastel, size=42)
        h.addWidget(indicator, 0, Qt.AlignmentFlag.AlignVCenter)

        # Contenu principal
        v = QVBoxLayout()
        v.setSpacing(4)

        # Ligne 1 : action label + user
        line1 = QHBoxLayout()
        line1.setSpacing(10)

        action_lbl = QLabel(action_label)
        action_lbl.setStyleSheet(f"""
            font-size: 11pt; color: {color}; font-weight: 800;
            background: transparent; border: none;
        """)
        line1.addWidget(action_lbl)

        line1.addStretch()

        # User avec pastille
        user_container = QFrame()
        user_container.setStyleSheet("""
            background-color: #F1F5F9;
            border-radius: 10px;
            border: none;
        """)
        user_layout = QHBoxLayout(user_container)
        user_layout.setContentsMargins(8, 3, 12, 3)
        user_layout.setSpacing(6)
        user_layout.addWidget(ColorDot("#64748B", 6))

        user_lbl = QLabel(log.get("user_name", "—"))
        user_lbl.setStyleSheet("""
            font-size: 8.5pt; color: #475569; font-weight: 700;
            background: transparent; border: none;
        """)
        user_layout.addWidget(user_lbl)

        line1.addWidget(user_container)

        v.addLayout(line1)

        # Ligne 2 : entité impactée
        entity = log.get("entity_name")
        if entity:
            entity_lbl = QLabel(entity)
            entity_lbl.setStyleSheet("""
                font-size: 9.5pt; color: #5A6B7D;
                background: transparent; border: none;
                padding-left: 2px;
            """)
            entity_lbl.setWordWrap(True)
            v.addWidget(entity_lbl)

        # Ligne 3 : temps
        created = log.get("created_at")
        if created and hasattr(created, "strftime"):
            delta = datetime.utcnow() - created
            seconds = int(delta.total_seconds())
            if seconds < 60:
                time_str = "à l'instant"
            elif seconds < 3600:
                time_str = f"il y a {seconds // 60} min"
            elif seconds < 86400:
                time_str = f"il y a {seconds // 3600} h"
            else:
                time_str = created.strftime("%d/%m/%Y à %H:%M")
        else:
            time_str = "—"

        time_lbl = QLabel(time_str)
        time_lbl.setStyleSheet("""
            font-size: 8.5pt; color: #94A3B8;
            background: transparent; border: none;
            padding-left: 2px;
        """)
        v.addWidget(time_lbl)

        h.addLayout(v, 1)

        # Badge "Système" à droite
        system_badge = QFrame()
        system_badge.setStyleSheet("""
            background-color: #F1F5F9;
            border-radius: 10px;
            border: 1px solid #E2E8F0;
        """)
        sb_layout = QHBoxLayout(system_badge)
        sb_layout.setContentsMargins(10, 5, 14, 5)
        sb_layout.setSpacing(6)
        sb_layout.addWidget(ColorDot("#64748B", 6))

        sys_txt = QLabel("SYSTÈME")
        sys_txt.setStyleSheet("""
            background: transparent;
            color: #475569;
            font-size: 8pt;
            font-weight: 800;
            letter-spacing: 0.6px;
            border: none;
        """)
        sb_layout.addWidget(sys_txt)

        h.addWidget(system_badge, 0, Qt.AlignmentFlag.AlignVCenter)


# =====================================================
# KPI CARD CUSTOM
# =====================================================
class KpiCardCustom(QFrame):
    """Carte KPI avec carré coloré au lieu d'un emoji."""

    def __init__(self, title: str, value: str, subtitle: str,
                 letter: str, accent: str):
        super().__init__()
        self.setMinimumHeight(130)

        accent_map = {
            "green": ("#E8F5F1", "#0D7A6A"),
            "blue": ("#E0F0FF", "#2E86DE"),
            "orange": ("#FEF3C7", "#F39C12"),
            "purple": ("#EDE9FE", "#7C3AED"),
            "red": ("#FEE2E2", "#C0392B"),
            "gray": ("#F1F5F9", "#64748B"),
        }
        bg, fg = accent_map.get(accent, ("#F1F5F9", "#475569"))

        self.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
                border-top: 3px solid {fg};
            }}
        """)

        v = QVBoxLayout(self)
        v.setContentsMargins(20, 16, 20, 18)
        v.setSpacing(10)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet("""
            font-size: 8.5pt; color: #5A6B7D; font-weight: 800;
            letter-spacing: 0.8px; background: transparent; border: none;
        """)
        top_row.addWidget(title_lbl)
        top_row.addStretch()

        top_row.addWidget(IconSquare(letter, fg, bg, size=34))
        v.addLayout(top_row)

        val_lbl = QLabel(value)
        val_lbl.setStyleSheet("""
            font-size: 26pt; font-weight: 800; color: #0F1E2E;
            background: transparent; border: none;
        """)
        v.addWidget(val_lbl)

        sub_lbl = QLabel(subtitle)
        sub_lbl.setStyleSheet("""
            font-size: 9pt; color: #7A8B9C;
            background: transparent; border: none;
        """)
        v.addWidget(sub_lbl)

        v.addStretch()


# =====================================================
# BOUTON FILTRE
# =====================================================
class FilterChip(QPushButton):
    """Chip de filtre par action."""

    def __init__(self, label: str, count: int, code: str, is_active: bool = False):
        super().__init__(f"{label} ({count})")
        self.code = code
        self.setCheckable(True)
        self.setChecked(is_active)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(36)
        self._apply_style(is_active)

    def _apply_style(self, is_active: bool):
        if is_active:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #0F1E2E;
                    color: #FFFFFF;
                    border: none;
                    padding: 8px 18px;
                    border-radius: 10px;
                    font-size: 9pt;
                    font-weight: 700;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    color: #5A6B7D;
                    border: 1px solid #E4E9EF;
                    padding: 8px 18px;
                    border-radius: 10px;
                    font-size: 9pt;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #F4F6F9;
                    color: #0D7A6A;
                    border-color: #0D7A6A;
                }
            """)

    def set_active(self, active: bool):
        self.setChecked(active)
        self._apply_style(active)


# =====================================================
# PAGE PRINCIPALE
# =====================================================
class AuditPage(QWidget):
    """Page Journal d'audit."""

    navigate_to = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.svc = AuditService()
        self.current_filter = "all"

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

        bc = QLabel("SMARTRH  /  GOUVERNANCE & LIENS  /  JOURNAL D'AUDIT")
        bc.setStyleSheet("""
            color: #7A8B9C; font-size: 9pt; font-weight: 800;
            letter-spacing: 1px;
            background: transparent; border: none;
        """)
        left.addWidget(bc)

        t = QLabel("Journal d'audit")
        t.setStyleSheet("""
            font-size: 20pt; font-weight: 800; color: #0F1E2E;
            background: transparent; border: none;
        """)
        left.addWidget(t)

        s = QLabel(
            "Traçabilité de toutes les actions : qui a fait quoi, quand et sur quoi. "
            "Conforme RGPD."
        )
        s.setStyleSheet("""
            font-size: 10pt; color: #7A8B9C;
            background: transparent; border: none;
        """)
        s.setWordWrap(True)
        left.addWidget(s)

        header.addLayout(left, 1)

        # Badge "Registre actif"
        badge_registre = QFrame()
        badge_registre.setStyleSheet("""
            background-color: #E8F5F1;
            border-radius: 12px;
            border: 1px solid #D1FAE5;
        """)
        br_layout = QHBoxLayout(badge_registre)
        br_layout.setContentsMargins(12, 6, 16, 6)
        br_layout.setSpacing(8)
        br_layout.addWidget(ColorDot("#0D7A6A", 8))

        br_txt = QLabel("REGISTRE ACTIF & IMMUABLE")
        br_txt.setStyleSheet("""
            background: transparent;
            color: #0D7A6A;
            font-size: 8.5pt;
            font-weight: 800;
            letter-spacing: 0.6px;
            border: none;
        """)
        br_layout.addWidget(br_txt)

        header.addWidget(badge_registre, 0, Qt.AlignmentFlag.AlignTop)

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
        # CHARGEMENT KPI
        # ============================================
        try:
            kpis = self.svc.get_kpis()
        except Exception:
            kpis = {"total": 0, "today": 0, "week": 0, "by_action": {}}

        # ============================================
        # 4 KPI CARDS
        # ============================================
        kpi_row = QGridLayout()
        kpi_row.setSpacing(16)

        kpi_row.addWidget(KpiCardCustom(
            title="Total actions",
            value=str(kpis["total"]),
            subtitle="Depuis le début",
            letter="T",
            accent="green",
        ), 0, 0)

        kpi_row.addWidget(KpiCardCustom(
            title="Aujourd'hui",
            value=str(kpis["today"]),
            subtitle="Actions du jour",
            letter="A",
            accent="blue",
        ), 0, 1)

        kpi_row.addWidget(KpiCardCustom(
            title="Cette semaine",
            value=str(kpis["week"]),
            subtitle="7 derniers jours",
            letter="S",
            accent="orange",
        ), 0, 2)

        kpi_row.addWidget(KpiCardCustom(
            title="Types d'action",
            value=str(len(kpis["by_action"])),
            subtitle="Actions distinctes",
            letter="Y",
            accent="purple",
        ), 0, 3)

        layout.addLayout(kpi_row)

        # ============================================
        # SECTION FILTRES (dans une carte)
        # ============================================
        filter_card = QFrame()
        filter_card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
            }
        """)
        filter_v = QVBoxLayout(filter_card)
        filter_v.setContentsMargins(16, 14, 16, 14)
        filter_v.setSpacing(12)

        # Ligne 1 : titre + rafraîchir
        title_row = QHBoxLayout()
        title_row.setSpacing(10)

        title_row.addWidget(ColorDot("#0D7A6A", 8))

        title_lbl = QLabel("FILTRER PAR ACTION")
        title_lbl.setStyleSheet("""
            font-size: 10.5pt; font-weight: 800; color: #5A6B7D;
            letter-spacing: 1.2px;
            background: transparent; border: none;
        """)
        title_row.addWidget(title_lbl)

        title_row.addStretch()

        btn_refresh = QPushButton("Rafraîchir")
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setMinimumHeight(34)
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #5A6B7D;
                border: 1px solid #E4E9EF;
                border-radius: 8px;
                padding: 6px 16px;
                font-size: 9pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #F4F6F9;
                color: #0D7A6A;
                border-color: #0D7A6A;
            }
        """)
        btn_refresh.clicked.connect(self._reload)
        title_row.addWidget(btn_refresh)

        filter_v.addLayout(title_row)

        # Ligne 2 : chips
        self.filters_container = QHBoxLayout()
        self.filters_container.setSpacing(8)
        filter_v.addLayout(self.filters_container)

        layout.addWidget(filter_card)

        # ============================================
        # LISTE DES LOGS
        # ============================================
        self.logs_card = QFrame()
        self.logs_card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
            }
        """)
        self.logs_v = QVBoxLayout(self.logs_card)
        self.logs_v.setContentsMargins(16, 16, 16, 16)
        self.logs_v.setSpacing(10)

        layout.addWidget(self.logs_card)
        layout.addStretch()

        # Rendu initial
        self._render_filters()
        self._render_logs()

    # =====================================================
    # RENDU
    # =====================================================
    def _render_filters(self):
        """Affiche les chips de filtre."""
        while self.filters_container.count():
            item = self.filters_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Bouton "Toutes"
        try:
            total = self.svc.get_kpis().get("total", 0)
        except Exception:
            total = 0

        chip_all = FilterChip(
            "Toutes", total, "all",
            is_active=(self.current_filter == "all")
        )
        chip_all.clicked.connect(lambda: self._on_filter_change("all"))
        self.filters_container.addWidget(chip_all)

        # Boutons par action
        try:
            actions = self.svc.get_available_actions()
        except Exception:
            actions = []

        for a in actions[:8]:
            chip = FilterChip(
                a["label"], a["count"], a["code"],
                is_active=(self.current_filter == a["code"])
            )
            chip.clicked.connect(lambda _, c=a["code"]: self._on_filter_change(c))
            self.filters_container.addWidget(chip)

        self.filters_container.addStretch()

    def _render_logs(self):
        """Affiche les logs selon le filtre actif."""
        while self.logs_v.count():
            item = self.logs_v.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

        try:
            logs = self.svc.get_logs(limit=50, action_filter=self.current_filter)
        except Exception as e:
            print(f"[AuditPage] Erreur logs: {e}")
            logs = []

        if not logs:
            empty = QFrame()
            empty.setStyleSheet("""
                QFrame {
                    background-color: #F8FAFC;
                    border-radius: 10px;
                    border: 1px dashed #E4E9EF;
                }
            """)
            ev = QVBoxLayout(empty)
            ev.setContentsMargins(40, 60, 40, 60)
            ev.setSpacing(10)

            dot_row = QHBoxLayout()
            dot_row.addStretch()
            dot_row.addWidget(ColorDot("#B8C4D0", 10))
            dot_row.addStretch()
            ev.addLayout(dot_row)

            msg = QLabel("Aucune action enregistrée pour ce filtre")
            msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            msg.setStyleSheet("""
                font-size: 11pt; color: #7A8B9C; font-weight: 700;
                background: transparent; border: none;
            """)
            ev.addWidget(msg)

            sub = QLabel("Les actions apparaîtront ici dès qu'elles seront effectuées")
            sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sub.setStyleSheet("""
                font-size: 9.5pt; color: #B8C4D0;
                background: transparent; border: none;
            """)
            ev.addWidget(sub)

            self.logs_v.addWidget(empty)
            return

        for log in logs:
            row = LogRow(log)
            self.logs_v.addWidget(row)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    # =====================================================
    # ACTIONS
    # =====================================================
    def _on_filter_change(self, code: str):
        """Change le filtre actif."""
        self.current_filter = code
        self._render_filters()
        self._render_logs()

    def _reload(self):
        """Recharge tout."""
        self._render_filters()
        self._render_logs()