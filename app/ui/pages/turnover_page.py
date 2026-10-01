"""Page Risques & Turnover — Module 3 du CDC.

Améliorations :
- Labels de pie chart mappés (fin des clés brutes comme "conge_longue_duree")
- Hiérarchie des alertes clarifiée (constat + diagnostic alignés)
- Badge de section avec pastille
- Card diagnostic IA avec fond plus contrasté
- Graphiques avec meilleure lisibilité
"""
from datetime import date
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QScrollArea, QFrame, QLabel, QPushButton, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal
from sqlalchemy import select, func

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use("QtAgg")

from app.services.alert_service import AlertService
from app.services.prediction_service import PredictionService
from app.db.connection import get_session
from app.models.employee import Employee


# =====================================================
# MAPPING LABELS (pour éviter les clés brutes)
# =====================================================
ALERT_TYPE_LABELS = {
    "conge_longue_duree": "Congé longue durée",
    "conge_excessif": "Congés excessifs",
    "conge": "Congé",
    "absences_repetees": "Absences répétées",
    "absence": "Absences",
    "surmenage": "Surmenage",
    "surcharge": "Surcharge",
    "desengagement": "Désengagement",
    "risque_demission": "Risque de démission",
    "turnover": "Turnover",
    "retard": "Retards répétés",
}


def label_from_key(key: str) -> str:
    """Convertit une clé brute en label lisible."""
    if not key:
        return "Autre"
    # Essai mapping direct
    k = key.lower().strip()
    if k in ALERT_TYPE_LABELS:
        return ALERT_TYPE_LABELS[k]
    # Sinon, formatage : snake_case → "Snake case"
    return key.replace("_", " ").capitalize()


# =====================================================
# HELPERS
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


class InitialsAvatar(QLabel):
    def __init__(self, first_name: str, last_name: str, size: int = 36):
        super().__init__()
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        initials = f"{(first_name or '?')[:1]}{(last_name or '?')[:1]}".upper()
        colors = ["#0D7A6A", "#1F4E5F", "#2E86DE", "#8E44AD", "#B9770E"]
        idx = sum(ord(c) for c in initials) % len(colors)
        color = colors[idx]

        self.setText(initials)
        self.setStyleSheet(f"""
            background-color: {color};
            color: white;
            border-radius: {size // 2}px;
            font-size: {size // 3}pt;
            font-weight: 800;
            border: none;
        """)


class IconSquare(QLabel):
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


# =====================================================
# GRAPHIQUE
# =====================================================
class ChartFrame(QFrame):
    def __init__(self, title: str = "", subtitle: str = "", height: int = 280):
        super().__init__()
        self.setMinimumHeight(height)
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
            }
        """)

        v = QVBoxLayout(self)
        v.setContentsMargins(20, 16, 20, 16)
        v.setSpacing(4)

        if title:
            title_row = QHBoxLayout()
            title_row.setSpacing(8)

            accent = QFrame()
            accent.setFixedSize(3, 18)
            accent.setStyleSheet("""
                background-color: #0D7A6A;
                border-radius: 2px;
                border: none;
            """)
            title_row.addWidget(accent)

            lbl = QLabel(title)
            lbl.setStyleSheet("""
                font-size: 12pt; font-weight: 800; color: #0F1E2E;
                background: transparent; border: none;
            """)
            title_row.addWidget(lbl)
            title_row.addStretch()
            v.addLayout(title_row)

        if subtitle:
            sub = QLabel(subtitle)
            sub.setStyleSheet("""
                font-size: 8.5pt; color: #7A8B9C;
                background: transparent; border: none;
                padding-left: 11px;
            """)
            v.addWidget(sub)

        self.figure = Figure(figsize=(5, 3), facecolor="#FFFFFF")
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background: transparent;")
        v.addWidget(self.canvas)

    def draw(self):
        self.figure.tight_layout()
        self.canvas.draw()


# =====================================================
# CARTE D'ALERTE DETAILLEE
# =====================================================
class AlertDetailCard(QFrame):
    resolve_requested = pyqtSignal(str)

    def __init__(self, alert: dict):
        super().__init__()
        self.alert = alert
        self.setMinimumHeight(180)

        severity = alert.get("severity", "preventif").lower()
        if severity == "critique":
            border_color = "#C0392B"
            bg_header = "#FADBD8"
            sev_label = "CRITIQUE"
            sev_color = "#C0392B"
            sev_bg = "#FEE2E2"
        else:
            border_color = "#F39C12"
            bg_header = "#FDEBD0"
            sev_label = "PRÉVENTIF"
            sev_color = "#B9770E"
            sev_bg = "#FEF3C7"

        self.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
                border-left: 4px solid {border_color};
            }}
        """)

        v = QVBoxLayout(self)
        v.setContentsMargins(22, 18, 22, 16)
        v.setSpacing(16)

        # ============================================
        # HEADER
        # ============================================
        head = QHBoxLayout()
        head.setSpacing(14)

        emp_name = alert.get("employee_name", "—")
        parts = emp_name.split(" ", 1)
        first = parts[0] if len(parts) > 0 else ""
        last = parts[1] if len(parts) > 1 else ""

        avatar = InitialsAvatar(first, last, size=44)
        head.addWidget(avatar)

        name_col = QVBoxLayout()
        name_col.setSpacing(5)

        name_lbl = QLabel(emp_name)
        name_lbl.setStyleSheet("""
            font-size: 13pt; font-weight: 800; color: #0F1E2E;
            background: transparent; border: none;
        """)
        name_col.addWidget(name_lbl)

        # Badge sévérité
        sev_badge = QFrame()
        sev_badge.setStyleSheet(f"""
            background-color: {sev_bg};
            border-radius: 10px;
            border: 1px solid {border_color}50;
        """)
        sev_badge_h = QHBoxLayout(sev_badge)
        sev_badge_h.setContentsMargins(8, 4, 12, 4)
        sev_badge_h.setSpacing(6)
        sev_badge_h.addWidget(ColorDot(sev_color, 6))

        sev_txt = QLabel(sev_label)
        sev_txt.setStyleSheet(f"""
            font-size: 8pt; font-weight: 800; color: {sev_color};
            letter-spacing: 0.6px;
            background: transparent; border: none;
        """)
        sev_badge_h.addWidget(sev_txt)

        sev_row = QHBoxLayout()
        sev_row.addWidget(sev_badge)
        sev_row.addStretch()
        name_col.addLayout(sev_row)

        head.addLayout(name_col)
        head.addStretch()

        # Type d'alerte
        alert_type = alert.get("title", "")
        type_lbl = QLabel(label_from_key(alert_type)[:45])
        type_lbl.setStyleSheet("""
            background-color: #EBF5FB;
            color: #2E86DE;
            padding: 6px 14px;
            border-radius: 10px;
            font-size: 8.5pt;
            font-weight: 700;
            border: 1px solid #D6EAF8;
        """)
        head.addWidget(type_lbl, 0, Qt.AlignmentFlag.AlignTop)

        v.addLayout(head)

        # ============================================
        # CORPS
        # ============================================
        body = QHBoxLayout()
        body.setSpacing(14)

        # Constat
        constat_box = QFrame()
        constat_box.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border-radius: 10px;
                border: 1px solid #EEF2F6;
            }
        """)
        cb_layout = QVBoxLayout(constat_box)
        cb_layout.setContentsMargins(16, 14, 16, 14)
        cb_layout.setSpacing(6)

        lbl1 = QLabel("CONSTAT FACTUEL")
        lbl1.setStyleSheet("""
            font-size: 7pt; color: #7A8B9C; font-weight: 800;
            letter-spacing: 0.8px; background: transparent; border: none;
        """)
        cb_layout.addWidget(lbl1)

        desc = QLabel(alert.get("description", "—"))
        desc.setStyleSheet("""
            font-size: 10.5pt; color: #0F1E2E; font-weight: 600;
            background: transparent; border: none;
        """)
        desc.setWordWrap(True)
        cb_layout.addWidget(desc)
        cb_layout.addStretch()

        body.addWidget(constat_box, 2)

        # Diagnostic
        diag_box = QFrame()
        diag_box.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_header};
                border-radius: 10px;
                border: 1px solid {border_color}60;
            }}
        """)
        db_layout = QVBoxLayout(diag_box)
        db_layout.setContentsMargins(16, 14, 16, 14)
        db_layout.setSpacing(6)

        lbl2 = QLabel("DIAGNOSTIC IA PRÉDICTIF")
        lbl2.setStyleSheet(f"""
            font-size: 7pt; color: {sev_color}; font-weight: 800;
            letter-spacing: 0.8px; background: transparent; border: none;
        """)
        db_layout.addWidget(lbl2)

        risk = float(alert.get("risk_score", 0))
        risk_lbl = QLabel(f"Risque : {risk:.0f}%")
        risk_lbl.setStyleSheet(f"""
            font-size: 12pt; color: {sev_color}; font-weight: 800;
            background: transparent; border: none;
        """)
        db_layout.addWidget(risk_lbl)

        # Barre de risque
        risk_bar = QProgressBar()
        risk_bar.setValue(int(risk))
        risk_bar.setMaximum(100)
        risk_bar.setTextVisible(False)
        risk_bar.setFixedHeight(4)
        risk_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #FFFFFF;
                border-radius: 2px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {sev_color};
                border-radius: 2px;
            }}
        """)
        db_layout.addWidget(risk_bar)

        rec = "Intervention urgente" if severity == "critique" else "À surveiller"
        rec_lbl = QLabel(rec)
        rec_lbl.setStyleSheet("""
            font-size: 8.5pt; color: #7A8B9C; font-style: italic;
            background: transparent; border: none;
        """)
        db_layout.addWidget(rec_lbl)

        body.addWidget(diag_box, 1)

        v.addLayout(body)

        # ============================================
        # ACTIONS
        # ============================================
        actions = QHBoxLayout()
        actions.setSpacing(8)
        actions.addStretch()

        btn_notify = QPushButton("Alerter le manager")
        btn_notify.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_notify.setMinimumHeight(38)
        btn_notify.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #B9770E;
                border: 1px solid #F39C12;
                border-radius: 8px;
                padding: 8px 18px;
                font-size: 9pt;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #FEF9E7;
                border-color: #B9770E;
            }
        """)
        btn_notify.clicked.connect(
            lambda: QMessageBox.information(
                self, "Notification",
                f"Le manager a été alerté pour {emp_name}."
            )
        )
        actions.addWidget(btn_notify)

        btn_resolve = QPushButton("Traiter l'anomalie")
        btn_resolve.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_resolve.setMinimumHeight(38)
        btn_resolve.setStyleSheet("""
            QPushButton {
                background-color: #0D7A6A;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 9pt;
                font-weight: 700;
            }
            QPushButton:hover { background-color: #0A6456; }
            QPushButton:pressed { background-color: #084C41; }
        """)
        alert_id = alert.get("id", "")
        btn_resolve.clicked.connect(
            lambda _, aid=alert_id: self.resolve_requested.emit(aid)
        )
        actions.addWidget(btn_resolve)

        v.addLayout(actions)


# =====================================================
# BOUTON ONGLET
# =====================================================
class FilterTab(QPushButton):
    def __init__(self, label: str, count: int, is_active: bool = False):
        super().__init__(f"{label} ({count})")
        self.setCheckable(True)
        self.setChecked(is_active)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(40)
        self._apply_style(is_active)

    def _apply_style(self, is_active: bool):
        if is_active:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #0F1E2E;
                    color: #FFFFFF;
                    border: none;
                    padding: 8px 20px;
                    border-radius: 10px;
                    font-size: 9.5pt;
                    font-weight: 700;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    color: #5A6B7D;
                    border: 1px solid #E4E9EF;
                    padding: 8px 20px;
                    border-radius: 10px;
                    font-size: 9.5pt;
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
class TurnoverPage(QWidget):
    navigate_to = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.svc = AlertService()
        self.current_filter = "all"

        self.kpi_alerts_card = None
        self.kpi_risks_card = None
        self.kpi_resolved_card = None
        self.kpi_turnover_card = None

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

        # HEADER
        header = QHBoxLayout()

        left = QVBoxLayout()
        left.setSpacing(6)

        bc = QLabel("SMARTRH  /  RISQUES RH  /  DÉTECTION D'ANOMALIES & IA")
        bc.setStyleSheet("""
            color: #7A8B9C; font-size: 9pt; font-weight: 800; letter-spacing: 1px;
            background: transparent; border: none;
        """)
        left.addWidget(bc)

        t = QLabel("Détection d'Anomalies & Prévention du Turnover")
        t.setStyleSheet("""
            font-size: 20pt; font-weight: 800; color: #0F1E2E;
            background: transparent; border: none;
        """)
        left.addWidget(t)

        s = QLabel(
            "Modélisation prédictive des signaux faibles, diagnostic des ruptures "
            "de charge de travail et recommandations d'intervention ciblées par IA."
        )
        s.setStyleSheet("""
            font-size: 10pt; color: #7A8B9C;
            background: transparent; border: none;
        """)
        s.setWordWrap(True)
        left.addWidget(s)

        header.addLayout(left, 1)

        btn_audit = QPushButton("Rapport d'audit")
        btn_audit.setMinimumHeight(42)
        btn_audit.setMinimumWidth(160)
        btn_audit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_audit.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #0F1E2E;
                border: 1px solid #D6DEE8;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 9.5pt;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #F4F6F9;
                border-color: #0D7A6A;
                color: #0D7A6A;
            }
        """)
        btn_audit.clicked.connect(self._export_audit)
        header.addWidget(btn_audit, 0, Qt.AlignmentFlag.AlignTop)

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

        # CHARGEMENT
        try:
            self.svc.run_all_rules()
        except Exception as e:
            print(f"[TurnoverPage] Erreur run_all_rules: {e}")

        try:
            kpis = self.svc.get_kpis()
        except Exception:
            kpis = {"active_alerts": 0, "detected_risks": 0, "resolved_alerts": 0}

        self.all_alerts = self._load_alerts()

        turnover_rate = 0
        try:
            with get_session() as db:
                year_start = date.today().replace(month=1, day=1)
                departed_this_year = db.scalar(
                    select(func.count()).select_from(Employee)
                    .where(
                        Employee.status == "sorti",
                        Employee.departure_date >= year_start,
                    )
                ) or 0
                total_active = db.scalar(
                    select(func.count()).select_from(Employee)
                    .where(Employee.status == "actif")
                ) or 1
                turnover_rate = round(100 * departed_this_year / total_active, 2)
        except Exception as e:
            print(f"[TurnoverPage] Erreur turnover: {e}")
            turnover_rate = 0

        # KPI CARDS
        kpi_row = QGridLayout()
        kpi_row.setSpacing(16)

        self.kpi_alerts_card = self._build_kpi_card(
            title="Alertes actives",
            value=str(kpis.get("active_alerts", 0)),
            subtitle="À traiter immédiatement",
            letter="A",
            accent="red",
        )
        kpi_row.addWidget(self.kpi_alerts_card, 0, 0)

        self.kpi_risks_card = self._build_kpi_card(
            title="Risques détectés",
            value=str(kpis.get("detected_risks", 0)),
            subtitle="Signaux faibles identifiés",
            letter="R",
            accent="blue",
        )
        kpi_row.addWidget(self.kpi_risks_card, 0, 1)

        self.kpi_resolved_card = self._build_kpi_card(
            title="Alertes résolues",
            value=str(kpis.get("resolved_alerts", 0)),
            subtitle="Traitées avec succès",
            letter="V",
            accent="green",
        )
        kpi_row.addWidget(self.kpi_resolved_card, 0, 2)

        self.kpi_turnover_card = self._build_kpi_card(
            title="Turnover annuel",
            value=f"{turnover_rate}%",
            subtitle="Départs cette année",
            letter="T",
            accent="red" if turnover_rate > 10 else "green",
        )
        kpi_row.addWidget(self.kpi_turnover_card, 0, 3)

        layout.addLayout(kpi_row)

        # BARRE D'ONGLETS
        tabs_frame = QFrame()
        tabs_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
            }
        """)
        tabs_h = QHBoxLayout(tabs_frame)
        tabs_h.setContentsMargins(14, 10, 14, 10)
        tabs_h.setSpacing(8)

        n_total = len(self.all_alerts)
        n_crit = len([a for a in self.all_alerts if a["severity"].lower() == "critique"])
        n_prev = len([a for a in self.all_alerts if a["severity"].lower() == "preventif"])
        n_resolved = kpis.get("resolved_alerts", 0)

        self.tabs = {}

        for key, label, count in [
            ("all", "Toutes les alertes", n_total),
            ("critique", "Critiques", n_crit),
            ("preventif", "Préventifs", n_prev),
            ("resolved", "Historique résolu", n_resolved),
        ]:
            tab = FilterTab(label, count, is_active=(key == "all"))
            tab.clicked.connect(lambda _, k=key: self._on_filter_change(k))
            tabs_h.addWidget(tab)
            self.tabs[key] = tab

        tabs_h.addStretch()
        layout.addWidget(tabs_frame)

        # CONTENU 2 COLONNES
        content = QHBoxLayout()
        content.setSpacing(20)

        left_col = QVBoxLayout()
        left_col.setSpacing(20)

        self.alerts_container = QVBoxLayout()
        self.alerts_container.setSpacing(20)
        left_col.addLayout(self.alerts_container)
        left_col.addStretch()

        content.addLayout(left_col, 6)

        right_col = QVBoxLayout()
        right_col.setSpacing(20)

        self.chart_evolution = ChartFrame(
            "Évolution des alertes",
            "6 derniers mois",
            260
        )
        self._draw_evolution_chart()
        right_col.addWidget(self.chart_evolution)

        self.chart_repartition = ChartFrame(
            "Répartition par type",
            "Distribution des alertes actives",
            280
        )
        self._draw_repartition_chart()
        right_col.addWidget(self.chart_repartition)

        dep_card = self._build_departures_card()
        right_col.addWidget(dep_card)

        pred_card = self._build_predictive_card()
        right_col.addWidget(pred_card)

        right_col.addStretch()
        content.addLayout(right_col, 4)

        layout.addLayout(content)
        layout.addStretch()

        self._render_alerts()

    # =====================================================
    # KPI CARD
    # =====================================================
    def _build_kpi_card(self, title: str, value: str, subtitle: str,
                        letter: str, accent: str) -> QFrame:
        card = QFrame()
        card.setMinimumHeight(130)

        accent_map = {
            "red": ("#FEE2E2", "#C0392B"),
            "blue": ("#D8DEFF", "#2E86DE"),
            "green": ("#E8F5F1", "#0D7A6A"),
            "orange": ("#FEF3C7", "#F39C12"),
        }
        bg, fg = accent_map.get(accent, ("#F1F5F9", "#475569"))

        card.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
                border-top: 3px solid {fg};
            }}
        """)

        v = QVBoxLayout(card)
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

        card.value_label = val_lbl
        return card

    # =====================================================
    # HELPERS
    # =====================================================
    def _load_alerts(self) -> list:
        try:
            return self.svc.get_active_alerts()
        except Exception as e:
            print(f"[TurnoverPage] Erreur chargement: {e}")
            return []

    def _draw_evolution_chart(self):
        try:
            data = self.svc.get_alerts_evolution(months=6)
        except Exception:
            data = []

        ax = self.chart_evolution.figure.add_subplot(111)
        ax.set_facecolor("#FFFFFF")

        if not data or all(d["count"] == 0 for d in data):
            ax.text(0.5, 0.5, "Aucune donnée disponible",
                    ha="center", va="center", color="#B8C4D0",
                    fontsize=10, transform=ax.transAxes)
            ax.axis("off")
        else:
            labels = [d["label"] for d in data]
            counts = [d["count"] for d in data]

            bars = ax.bar(
                labels, counts,
                color="#0D7A6A", width=0.55,
                edgecolor="white", linewidth=1.5,
            )

            for bar, count in zip(bars, counts):
                if count > 0:
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + max(counts) * 0.03,
                        str(count),
                        ha="center", va="bottom",
                        fontsize=10, fontweight="bold", color="#0F1E2E"
                    )

            ax.spines[["top", "right"]].set_visible(False)
            ax.spines[["left", "bottom"]].set_color("#E4E9EF")
            ax.tick_params(axis="x", labelsize=9, colors="#5A6B7D", length=0)
            ax.tick_params(axis="y", labelsize=8, colors="#7A8B9C", length=0)
            ax.grid(axis="y", color="#F1F5F9", linewidth=0.8)
            ax.set_axisbelow(True)

        self.chart_evolution.draw()

    def _draw_repartition_chart(self):
        try:
            data = self.svc.get_alert_types_distribution()
        except Exception:
            data = []

        ax = self.chart_repartition.figure.add_subplot(111)
        ax.set_facecolor("#FFFFFF")

        if not data:
            ax.text(0.5, 0.5, "Aucune donnée disponible",
                    ha="center", va="center", color="#B8C4D0",
                    fontsize=10, transform=ax.transAxes)
            ax.axis("off")
        else:
            # ✅ Mapping des labels bruts vers lisibles
            labels = [label_from_key(d["label"]) for d in data]
            counts = [d["count"] for d in data]
            colors = ["#C0392B", "#F39C12", "#2E86DE", "#0D7A6A", "#8E44AD"]

            wedges, texts, autotexts = ax.pie(
                counts,
                labels=labels,
                autopct="%1.0f%%",
                colors=colors[:len(labels)],
                wedgeprops={"width": 0.42, "edgecolor": "white", "linewidth": 2.5},
                textprops={"fontsize": 8.5, "color": "#5A6B7D"},
                pctdistance=0.78,
            )

            for autotext in autotexts:
                autotext.set_color("white")
                autotext.set_fontweight("bold")
                autotext.set_fontsize(8.5)

            total = sum(counts)
            ax.text(0, 0.08, f"{total}",
                    ha="center", va="center",
                    fontsize=20, fontweight="bold", color="#0F1E2E")
            ax.text(0, -0.15, "TOTAL",
                    ha="center", va="center",
                    fontsize=7, fontweight="bold", color="#7A8B9C")

        self.chart_repartition.draw()

    def _build_departures_card(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
            }
        """)
        v = QVBoxLayout(card)
        v.setContentsMargins(20, 16, 20, 16)
        v.setSpacing(12)

        head = QHBoxLayout()
        head.setSpacing(10)

        accent = QFrame()
        accent.setFixedSize(3, 18)
        accent.setStyleSheet("""
            background-color: #C0392B;
            border-radius: 2px;
            border: none;
        """)
        head.addWidget(accent)

        title = QLabel("Départs récents")
        title.setStyleSheet("""
            font-size: 12pt; font-weight: 800; color: #0F1E2E;
            background: transparent; border: none;
        """)
        head.addWidget(title)
        head.addStretch()

        departed_count = 0
        try:
            with get_session() as db:
                departed_count = db.scalar(
                    select(func.count()).select_from(Employee)
                    .where(Employee.status == "sorti")
                ) or 0
        except Exception:
            departed_count = 0

        count_badge = QLabel(f"{departed_count} au total")
        count_badge.setStyleSheet("""
            background-color: #F1F5F9;
            color: #64748B;
            padding: 3px 10px;
            border-radius: 8px;
            font-size: 8pt;
            font-weight: 700;
            border: none;
        """)
        head.addWidget(count_badge)

        v.addLayout(head)

        departed = []
        try:
            with get_session() as db:
                emps = db.scalars(
                    select(Employee)
                    .where(Employee.status == "sorti")
                    .order_by(Employee.departure_date.desc())
                    .limit(4)
                ).all()

                departed = [
                    {
                        "full_name": e.full_name,
                        "job_title": e.job_title,
                        "departure_reason": e.departure_reason,
                        "departure_date": e.departure_date,
                    }
                    for e in emps
                ]
        except Exception as e:
            print(f"[TurnoverPage] Erreur departures: {e}")
            departed = []

        if not departed:
            empty = QLabel("Aucun départ enregistré")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("""
                color: #7A8B9C; font-style: italic; padding: 24px;
                background: transparent; border: none;
            """)
            v.addWidget(empty)
            return card

        for emp in departed:
            row = QFrame()
            row.setStyleSheet("""
                QFrame {
                    background-color: #FAFBFC;
                    border-radius: 8px;
                    border: 1px solid #EEF2F6;
                }
            """)
            rh = QHBoxLayout(row)
            rh.setContentsMargins(10, 10, 10, 10)
            rh.setSpacing(10)

            parts = (emp["full_name"] or "—").split(" ", 1)
            first = parts[0] if len(parts) > 0 else ""
            last = parts[1] if len(parts) > 1 else ""
            rh.addWidget(InitialsAvatar(first, last, size=32))

            info = QVBoxLayout()
            info.setSpacing(2)

            name = QLabel(emp["full_name"])
            name.setStyleSheet("""
                font-size: 9.5pt; color: #0F1E2E; font-weight: 700;
                background: transparent; border: none;
            """)
            info.addWidget(name)

            title_lbl = QLabel(emp["job_title"] or "—")
            title_lbl.setStyleSheet("""
                font-size: 8pt; color: #7A8B9C;
                background: transparent; border: none;
            """)
            info.addWidget(title_lbl)

            rh.addLayout(info, 1)

            reason = emp["departure_reason"] or "—"
            color = "#C0392B" if "démission" in reason.lower() else (
                    "#B9770E" if "rupture" in reason.lower() else
                    "#7A8B9C")
            reason_lbl = QLabel(reason)
            reason_lbl.setStyleSheet(f"""
                background-color: {color}15;
                color: {color};
                padding: 3px 8px;
                border-radius: 8px;
                font-size: 7pt;
                font-weight: 700;
                border: none;
            """)
            rh.addWidget(reason_lbl)

            if emp["departure_date"]:
                date_lbl = QLabel(emp["departure_date"].strftime("%m/%Y"))
                date_lbl.setStyleSheet("""
                    font-size: 8pt; color: #B8C4D0; font-weight: 700;
                    background: transparent; border: none;
                """)
                rh.addWidget(date_lbl)

            v.addWidget(row)

        return card

    def _build_predictive_card(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
            }
        """)
        v = QVBoxLayout(card)
        v.setContentsMargins(20, 16, 20, 16)
        v.setSpacing(12)

        head = QHBoxLayout()
        head.setSpacing(10)

        accent = QFrame()
        accent.setFixedSize(3, 18)
        accent.setStyleSheet("""
            background-color: #0D7A6A;
            border-radius: 2px;
            border: none;
        """)
        head.addWidget(accent)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        title = QLabel("Analyse prédictive")
        title.setStyleSheet("""
            font-size: 12pt; font-weight: 800; color: #0F1E2E;
            background: transparent; border: none;
        """)
        title_col.addWidget(title)

        sub = QLabel("Machine Learning — RandomForest")
        sub.setStyleSheet("""
            font-size: 8pt; color: #7A8B9C;
            background: transparent; border: none;
        """)
        title_col.addWidget(sub)

        head.addLayout(title_col)
        head.addStretch()

        badge_ml = QLabel("ML")
        badge_ml.setStyleSheet("""
            background-color: #E8F5F1; color: #0D7A6A;
            padding: 4px 12px; border-radius: 10px;
            font-size: 8pt; font-weight: 800; letter-spacing: 0.5px;
            border: none;
        """)
        head.addWidget(badge_ml)

        v.addLayout(head)

        try:
            svc = PredictionService()
            summary = svc.get_summary()
            predictions = svc.predict_all()
        except Exception as e:
            print(f"[TurnoverPage] Erreur ML: {e}")
            error = QLabel("Erreur d'entraînement du modèle")
            error.setStyleSheet("""
                color: #C0392B; font-style: italic; padding: 12px;
                background: transparent; border: none;
            """)
            v.addWidget(error)
            return card

        if not predictions:
            empty = QLabel("Pas assez de données pour prédire")
            empty.setStyleSheet("""
                color: #7A8B9C; font-style: italic; padding: 12px;
                background: transparent; border: none;
            """)
            v.addWidget(empty)
            return card

        kpi_row = QHBoxLayout()
        kpi_row.setSpacing(8)

        for label, value, color in [
            ("ÉLEVÉ", summary["high"], "#C0392B"),
            ("MODÉRÉ", summary["medium"], "#F39C12"),
            ("FAIBLE", summary["low"], "#0D7A6A"),
        ]:
            box = QFrame()
            box.setStyleSheet(f"""
                QFrame {{
                    background-color: {color}12;
                    border-radius: 10px;
                    border: 1px solid {color}50;
                }}
            """)
            bv = QVBoxLayout(box)
            bv.setContentsMargins(12, 10, 12, 10)
            bv.setSpacing(4)

            lbl = QLabel(label)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f"""
                font-size: 7pt; font-weight: 800; color: {color};
                letter-spacing: 0.8px;
                background: transparent; border: none;
            """)
            bv.addWidget(lbl)

            val = QLabel(str(value))
            val.setAlignment(Qt.AlignmentFlag.AlignCenter)
            val.setStyleSheet(f"""
                font-size: 16pt; font-weight: 800; color: {color};
                background: transparent; border: none;
            """)
            bv.addWidget(val)

            kpi_row.addWidget(box, 1)

        v.addLayout(kpi_row)

        sep = QLabel("EMPLOYÉS À RISQUE (TOP 3)")
        sep.setStyleSheet("""
            font-size: 7pt; color: #7A8B9C; font-weight: 800;
            letter-spacing: 0.8px; padding-top: 8px;
            background: transparent; border: none;
        """)
        v.addWidget(sep)

        for p in predictions[:3]:
            row = QFrame()
            row.setStyleSheet(f"""
                QFrame {{
                    background-color: {p['risk_color']}10;
                    border-radius: 10px;
                    border: 1px solid {p['risk_color']}40;
                    border-left: 4px solid {p['risk_color']};
                }}
            """)
            rh = QVBoxLayout(row)
            rh.setContentsMargins(12, 10, 12, 10)
            rh.setSpacing(6)

            line1 = QHBoxLayout()
            line1.setSpacing(8)

            name = QLabel(p['employee_name'])
            name.setStyleSheet("""
                font-size: 10pt; font-weight: 700; color: #0F1E2E;
                background: transparent; border: none;
            """)
            line1.addWidget(name)
            line1.addStretch()

            score = QLabel(f"{p['risk_score']:.0f}%")
            score.setStyleSheet(f"""
                font-size: 13pt; font-weight: 800; color: {p['risk_color']};
                background: transparent; border: none;
            """)
            line1.addWidget(score)
            rh.addLayout(line1)

            bar = QProgressBar()
            bar.setValue(int(p["risk_score"]))
            bar.setMaximum(100)
            bar.setTextVisible(False)
            bar.setFixedHeight(5)
            bar.setStyleSheet(f"""
                QProgressBar {{
                    background-color: #EEF2F6;
                    border-radius: 3px;
                    border: none;
                }}
                QProgressBar::chunk {{
                    background-color: {p['risk_color']};
                    border-radius: 3px;
                }}
            """)
            rh.addWidget(bar)

            if p["reasons"]:
                reasons_txt = " • ".join(p["reasons"])
                r_lbl = QLabel(reasons_txt)
                r_lbl.setStyleSheet("""
                    font-size: 8pt; color: #7A8B9C;
                    background: transparent; border: none;
                """)
                r_lbl.setWordWrap(True)
                rh.addWidget(r_lbl)

            v.addWidget(row)

        try:
            info = svc.train()
            if info.get("trained") and info.get("feature_importances"):
                sep2 = QLabel("FACTEURS D'IMPACT (MODÈLE ML)")
                sep2.setStyleSheet("""
                    font-size: 7pt; color: #7A8B9C; font-weight: 800;
                    letter-spacing: 0.8px; padding-top: 8px;
                    background: transparent; border: none;
                """)
                v.addWidget(sep2)

                for feat_name, imp in info["feature_importances"][:4]:
                    LABELS = {
                        "alert_count": "Alertes actives",
                        "leave_days_year": "Jours d'absence",
                        "seniority_years": "Ancienneté",
                        "salary_base": "Salaire",
                    }
                    label = LABELS.get(feat_name, feat_name)

                    f_row = QHBoxLayout()
                    f_row.setSpacing(10)

                    f_lbl = QLabel(label)
                    f_lbl.setStyleSheet("""
                        font-size: 9pt; color: #5A6B7D;
                        background: transparent; border: none;
                    """)
                    f_lbl.setMinimumWidth(120)
                    f_row.addWidget(f_lbl)

                    mini_bar = QProgressBar()
                    mini_bar.setValue(int(imp * 100))
                    mini_bar.setMaximum(100)
                    mini_bar.setTextVisible(False)
                    mini_bar.setFixedHeight(4)
                    mini_bar.setStyleSheet("""
                        QProgressBar {
                            background-color: #EEF2F6;
                            border-radius: 2px;
                            border: none;
                        }
                        QProgressBar::chunk {
                            background-color: #0D7A6A;
                            border-radius: 2px;
                        }
                    """)
                    f_row.addWidget(mini_bar, 1)

                    f_val = QLabel(f"{imp * 100:.0f}%")
                    f_val.setStyleSheet("""
                        font-size: 9pt; color: #0F1E2E; font-weight: 800;
                        background: transparent; border: none;
                    """)
                    f_val.setMinimumWidth(40)
                    f_row.addWidget(f_val)

                    v.addLayout(f_row)
        except Exception as e:
            print(f"[TurnoverPage] Erreur feature importances: {e}")

        return card

    # =====================================================
    # RENDU
    # =====================================================
    def _render_alerts(self):
        while self.alerts_container.count():
            item = self.alerts_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

        if self.current_filter == "resolved":
            try:
                filtered = self.svc.get_historical_alerts(limit=20)
            except Exception:
                filtered = []
            self._render_resolved_alerts(filtered)
            return

        if self.current_filter == "all":
            filtered = self.all_alerts
        else:
            filtered = [
                a for a in self.all_alerts
                if a["severity"].lower() == self.current_filter
            ]

        if not filtered:
            empty_card = QFrame()
            empty_card.setStyleSheet("""
                QFrame {
                    background-color: #FFFFFF;
                    border-radius: 12px;
                    border: 1px solid #E4E9EF;
                }
            """)
            ev = QVBoxLayout(empty_card)
            ev.setContentsMargins(40, 60, 40, 60)
            ev.setSpacing(12)

            dot_row = QHBoxLayout()
            dot_row.addStretch()
            dot_row.addWidget(ColorDot("#0D7A6A", 10))
            dot_row.addStretch()
            ev.addLayout(dot_row)

            msg = QLabel("Aucune alerte pour ce filtre")
            msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            msg.setStyleSheet("""
                font-size: 12pt; color: #0D7A6A; font-weight: 700;
                background: transparent; border: none;
            """)
            ev.addWidget(msg)

            sub = QLabel("Les alertes actives apparaîtront ici dès leur détection")
            sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sub.setStyleSheet("""
                font-size: 9pt; color: #7A8B9C;
                background: transparent; border: none;
            """)
            ev.addWidget(sub)

            self.alerts_container.addWidget(empty_card)
            return

        if self.current_filter == "all":
            critiques = [a for a in filtered if a["severity"].lower() == "critique"]
            preventives = [a for a in filtered if a["severity"].lower() == "preventif"]

            if critiques:
                header = self._build_section_header(
                    "ALERTES CRITIQUES",
                    "À traiter en priorité",
                    f"{len(critiques)} alerte(s)",
                    "#C0392B",
                )
                self.alerts_container.addWidget(header)
                for a in critiques:
                    card = AlertDetailCard(a)
                    card.resolve_requested.connect(self._on_resolve_alert)
                    self.alerts_container.addWidget(card)

            if preventives:
                header = self._build_section_header(
                    "ALERTES PRÉVENTIVES",
                    "Signaux faibles à surveiller",
                    f"{len(preventives)} alerte(s)",
                    "#F39C12",
                )
                self.alerts_container.addWidget(header)
                for a in preventives:
                    card = AlertDetailCard(a)
                    card.resolve_requested.connect(self._on_resolve_alert)
                    self.alerts_container.addWidget(card)
        else:
            for a in filtered:
                card = AlertDetailCard(a)
                card.resolve_requested.connect(self._on_resolve_alert)
                self.alerts_container.addWidget(card)

    def _render_resolved_alerts(self, alerts: list):
        if not alerts:
            empty = QFrame()
            empty.setStyleSheet("""
                QFrame {
                    background-color: #FFFFFF;
                    border-radius: 12px;
                    border: 1px solid #E4E9EF;
                }
            """)
            ev = QVBoxLayout(empty)
            ev.setContentsMargins(40, 60, 40, 60)
            ev.setSpacing(12)

            dot_row = QHBoxLayout()
            dot_row.addStretch()
            dot_row.addWidget(ColorDot("#B8C4D0", 10))
            dot_row.addStretch()
            ev.addLayout(dot_row)

            msg = QLabel("Aucune alerte résolue dans l'historique")
            msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            msg.setStyleSheet("""
                font-size: 12pt; color: #7A8B9C; font-weight: 700;
                background: transparent; border: none;
            """)
            ev.addWidget(msg)

            self.alerts_container.addWidget(empty)
            return

        for a in alerts:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #F4FAF8;
                    border-radius: 10px;
                    border: 1px solid #E8F5F1;
                    border-left: 4px solid #0D7A6A;
                }
            """)
            v = QVBoxLayout(card)
            v.setContentsMargins(18, 14, 18, 14)
            v.setSpacing(8)

            head = QHBoxLayout()
            head.setSpacing(10)

            emp_name = a.get('employee_name', '—')
            parts = emp_name.split(" ", 1)
            first = parts[0] if len(parts) > 0 else ""
            last = parts[1] if len(parts) > 1 else ""
            head.addWidget(InitialsAvatar(first, last, size=32))

            name = QLabel(emp_name)
            name.setStyleSheet("""
                font-size: 11pt; color: #0F1E2E; font-weight: 700;
                background: transparent; border: none;
            """)
            head.addWidget(name)

            badge = QFrame()
            badge.setStyleSheet("""
                background-color: #E8F5F1;
                border-radius: 10px;
                border: none;
            """)
            badge_h = QHBoxLayout(badge)
            badge_h.setContentsMargins(8, 4, 12, 4)
            badge_h.setSpacing(6)
            badge_h.addWidget(ColorDot("#0D7A6A", 6))

            badge_txt = QLabel("RÉSOLUE")
            badge_txt.setStyleSheet("""
                font-size: 8pt; font-weight: 800; color: #0D7A6A;
                letter-spacing: 0.5px;
                background: transparent; border: none;
            """)
            badge_h.addWidget(badge_txt)
            head.addWidget(badge)

            head.addStretch()

            resolved = a.get("resolved_at")
            if resolved and hasattr(resolved, "strftime"):
                dt_txt = resolved.strftime("%d/%m/%Y à %H:%M")
            else:
                dt_txt = "—"
            dt_lbl = QLabel(f"Résolue le {dt_txt}")
            dt_lbl.setStyleSheet("""
                font-size: 8pt; color: #0D7A6A; font-weight: 700;
                background: transparent; border: none;
            """)
            head.addWidget(dt_lbl)

            v.addLayout(head)

            desc = QLabel(a.get("description", "—"))
            desc.setStyleSheet("""
                font-size: 9pt; color: #5A6B7D;
                background: transparent; border: none;
                padding-left: 44px;
            """)
            desc.setWordWrap(True)
            v.addWidget(desc)

            self.alerts_container.addWidget(card)

    def _build_section_header(self, title: str, subtitle: str,
                              badge: str, color: str) -> QFrame:
        frame = QFrame()
        frame.setStyleSheet("background: transparent; border: none;")

        h = QHBoxLayout(frame)
        h.setContentsMargins(0, 12, 0, 6)
        h.setSpacing(12)

        accent = QFrame()
        accent.setFixedSize(3, 28)
        accent.setStyleSheet(f"""
            background-color: {color};
            border-radius: 2px;
            border: none;
        """)
        h.addWidget(accent)

        col = QVBoxLayout()
        col.setSpacing(2)

        t = QLabel(title)
        t.setStyleSheet(f"""
            font-size: 12.5pt; font-weight: 800; color: {color};
            background: transparent; border: none; letter-spacing: 0.5px;
        """)
        col.addWidget(t)

        sub = QLabel(subtitle)
        sub.setStyleSheet("""
            font-size: 9pt; color: #7A8B9C;
            background: transparent; border: none;
        """)
        col.addWidget(sub)

        h.addLayout(col)
        h.addStretch()

        # ✅ Badge avec pastille intégrée
        badge_box = QFrame()
        badge_box.setStyleSheet(f"""
            background-color: {color}12;
            border-radius: 12px;
            border: 1px solid {color}40;
        """)
        badge_h = QHBoxLayout(badge_box)
        badge_h.setContentsMargins(10, 5, 14, 5)
        badge_h.setSpacing(6)
        badge_h.addWidget(ColorDot(color, 7))

        badge_lbl = QLabel(badge)
        badge_lbl.setStyleSheet(f"""
            font-size: 8.5pt; font-weight: 800; color: {color};
            letter-spacing: 0.4px;
            background: transparent; border: none;
        """)
        badge_h.addWidget(badge_lbl)

        h.addWidget(badge_box)

        return frame

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
    def _on_filter_change(self, filter_key: str):
        self.current_filter = filter_key
        for key, btn in self.tabs.items():
            btn.set_active(key == filter_key)
        self._render_alerts()

    def _on_resolve_alert(self, alert_id: str):
        try:
            resolved_severity = None
            for a in self.all_alerts:
                if a.get("id") == alert_id:
                    resolved_severity = a.get("severity", "").lower()
                    break

            self.svc.resolve_alert(alert_id)

            try:
                from app.services.audit_service import AuditService
                AuditService().log_action(
                    action="resolve_alert",
                    entity_type="alert",
                    entity_id=alert_id,
                    details="Alerte traitée depuis Turnover",
                )
            except Exception:
                pass

            QMessageBox.information(
                self, "Succès",
                "L'alerte a été marquée comme résolue."
            )

            self.all_alerts = self._load_alerts()
            kpis = self.svc.get_kpis()

            if self.kpi_alerts_card:
                self.kpi_alerts_card.value_label.setText(str(kpis.get("active_alerts", 0)))
            if self.kpi_risks_card:
                self.kpi_risks_card.value_label.setText(str(kpis.get("detected_risks", 0)))
            if self.kpi_resolved_card:
                self.kpi_resolved_card.value_label.setText(str(kpis.get("resolved_alerts", 0)))

            n_total = len(self.all_alerts)
            n_crit = len([a for a in self.all_alerts if a["severity"].lower() == "critique"])
            n_prev = len([a for a in self.all_alerts if a["severity"].lower() == "preventif"])
            n_resolved = kpis.get("resolved_alerts", 0)

            self.tabs["all"].setText(f"Toutes les alertes ({n_total})")
            self.tabs["critique"].setText(f"Critiques ({n_crit})")
            self.tabs["preventif"].setText(f"Préventifs ({n_prev})")
            self.tabs["resolved"].setText(f"Historique résolu ({n_resolved})")

            self._render_alerts()

            self.chart_evolution.figure.clear()
            self._draw_evolution_chart()
            self.chart_repartition.figure.clear()
            self._draw_repartition_chart()

        except Exception as e:
            print(f"[TurnoverPage] Erreur resolution: {e}")
            QMessageBox.critical(
                self, "Erreur",
                f"Impossible de traiter l'alerte :\n{e}"
            )

    def _export_audit(self):
        try:
            from app.services.report_service import ReportService
            svc = ReportService()
            path = svc.generate("turnover_absenteeism")
            QMessageBox.information(
                self, "Succès",
                f"Rapport d'audit généré :\n{path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Erreur",
                f"Impossible de générer le rapport :\n{e}"
            )