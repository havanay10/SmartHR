"""Page Accueil — Tableau de bord RH (Module 1 du CDC)."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QScrollArea, QFrame, QLabel, QPushButton, QProgressBar,
    QMenu, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QCursor, QIcon

from app.ui.widgets import KpiCard, Badge
from app.ui.icons import IconLabel, is_emoji, resolve_icon_path
from app.services.stats_service import StatsService
from app.services.alert_service import AlertService


# =====================================================
# SOUS-WIDGETS SPECIFIQUES A L'ACCUEIL
# =====================================================

class RepartitionRow(QFrame):
    """Ligne de repartition : nom + % + count + barre horizontale."""

    def __init__(self, name, percentage, count, color="#0D7A6A"):
        super().__init__()
        self.setStyleSheet("background: transparent;")

        v = QVBoxLayout(self)
        v.setContentsMargins(0, 4, 0, 4)
        v.setSpacing(6)

        # --- Ligne 1 : pastille + nom + % + count ---
        top = QHBoxLayout()
        top.setSpacing(6)

        # Pastille colorée (au lieu de "●")
        dot = QFrame()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
        top.addWidget(dot)

        name_lbl = QLabel(f"<b>{name}</b>")
        name_lbl.setStyleSheet("font-size: 10pt; color: #0F172A; background: transparent;")
        top.addWidget(name_lbl)

        pct_lbl = QLabel(f"({percentage}%)")
        pct_lbl.setStyleSheet("font-size: 9pt; color: #64748B; background: transparent;")
        top.addWidget(pct_lbl)

        top.addStretch()

        count_lbl = QLabel(f"<b>{count} pers.</b>")
        count_lbl.setStyleSheet("font-size: 10pt; color: #0F172A; background: transparent;")
        top.addWidget(count_lbl)

        v.addLayout(top)

        # --- Ligne 2 : barre de progression ---
        bar = QProgressBar()
        bar.setValue(int(min(100, percentage)))
        bar.setMaximum(100)
        bar.setTextVisible(False)
        bar.setFixedHeight(6)
        bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #F1F5F9;
                border-radius: 3px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
        v.addWidget(bar)


class ActivityItem(QFrame):
    """Carte d'activite stylee (compacte, badge à droite - style maquette)."""

    def __init__(self, icon, title, desc, time_ago,
                 badge_text="", badge_variant="info"):
        super().__init__()
        self.setObjectName("activityItem")
        # Empêche l'étirement vertical
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.setStyleSheet("""
            QFrame#activityItem {
                background-color: #F8FAFC;
                border-radius: 10px;
                border: 1px solid #F1F5F9;
            }
        """)

        # Layout horizontal principal : [icône] [contenu] [badge à droite]
        h = QHBoxLayout(self)
        h.setContentsMargins(14, 12, 14, 12)
        h.setSpacing(12)

        # --- Icone ronde pastel (à gauche) ---
        if badge_variant == "danger":
            bg_icon = "#FEE2E2"
            fg_icon = "#C0392B"
        elif badge_variant == "warning":
            bg_icon = "#FEF3C7"
            fg_icon = "#B45309"
        else:
            bg_icon = "#E8F5F1"
            fg_icon = "#0D7A6A"

        ic = IconLabel(icon, size=13)
        ic.setFixedSize(34, 34)
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ic.setStyleSheet(f"""
            background-color: {bg_icon};
            color: {fg_icon};
            border-radius: 17px;
        """)
        h.addWidget(ic, 0, Qt.AlignmentFlag.AlignVCenter)

        # --- Contenu central (nom + desc + temps) ---
        v = QVBoxLayout()
        v.setSpacing(2)

        # Ligne 1 : Nom (bold) + description courte (gris)
        line1 = QHBoxLayout()
        line1.setSpacing(6)

        name = QLabel(f"<b>{title}</b>")
        name.setStyleSheet(
            "font-size: 10.5pt; color: #0F172A; background: transparent;"
        )
        line1.addWidget(name)

        short_desc = desc[:40] + ("..." if len(desc) > 40 else "")
        tag = QLabel(short_desc)
        tag.setStyleSheet(
            "font-size: 9pt; color: #94A3B8; background: transparent;"
        )
        line1.addWidget(tag)
        line1.addStretch()

        v.addLayout(line1)

        # Ligne 2 : Description complète (gris foncé)
        if len(desc) > 40:
            desc_lbl = QLabel(desc)
            desc_lbl.setStyleSheet(
                "font-size: 9pt; color: #64748B; background: transparent;"
            )
            desc_lbl.setWordWrap(True)
            v.addWidget(desc_lbl)

        # Ligne 3 : Temps écoulé
        time_lbl = QLabel(time_ago)
        time_lbl.setStyleSheet(
            "font-size: 8.5pt; color: #94A3B8; background: transparent;"
        )
        v.addWidget(time_lbl)

        h.addLayout(v, 1)

        # --- Badge à droite, centré verticalement ---
        if badge_text:
            badge = Badge(badge_text.upper(), variant=badge_variant)
            h.addWidget(badge, 0, Qt.AlignmentFlag.AlignVCenter)


# =====================================================
# PAGE ACCUEIL
# =====================================================

class AccueilPage(QWidget):
    navigate_to = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stats_svc = StatsService()
        self.alert_svc = AlertService()

        # === Layout racine ===
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background-color: #F4F6F9; border: none; }")

        inner = QWidget()
        scroll.setWidget(inner)
        outer.addWidget(scroll)

        layout = QVBoxLayout(inner)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(18)

        # ============================================
        # CHARGEMENT DES DONNEES
        # ============================================
        kpis = self._load_kpis()
        repart = self._load_repartition()
        alerts = self._load_alerts()

        # ============================================
        # HEADER
        # ============================================
        header = QHBoxLayout()
        left_head = QVBoxLayout()
        left_head.setSpacing(2)

        bc = QLabel("SMARTRH  /  ACCUEIL")
        bc.setObjectName("breadcrumb")
        left_head.addWidget(bc)

        t = QLabel("Tableau de bord RH")
        t.setObjectName("pageTitle")
        left_head.addWidget(t)

        s = QLabel("Vue d'ensemble stratégique et indicateurs clés des effectifs")
        s.setObjectName("pageSubtitle")
        left_head.addWidget(s)
        header.addLayout(left_head, 1)

        # Bouton "Action rapide"
        btn_action = QPushButton("  Action rapide  ▾")
        btn_action.setObjectName("actionButton")
        btn_action.setMinimumHeight(40)
        btn_action.setCursor(Qt.CursorShape.PointingHandCursor)

        icon_path = resolve_icon_path("action-play")
        if icon_path and icon_path.exists():
            btn_action.setIcon(QIcon(str(icon_path)))

        btn_action.clicked.connect(self._show_quick_actions_menu)
        header.addWidget(btn_action, 0, Qt.AlignmentFlag.AlignTop)

        layout.addLayout(header)

        # ============================================
        # 5 KPI CARDS
        # ============================================
        kpi_row = QGridLayout()
        kpi_row.setSpacing(14)

        kpi_row.addWidget(KpiCard(
            title="Total employés", value=str(kpis["total_employees"]),
            subtitle=f"{kpis['active_employees']} en poste actif",
            icon="kpi-employees", accent="green",
        ), 0, 0)

        kpi_row.addWidget(KpiCard(
            title="Absences & congés", value=str(kpis["absences_this_month"]),
            subtitle=f"Taux : {round(100 * kpis['absences_this_month'] / max(kpis['total_employees'], 1), 1)}% ce mois",
            icon="kpi-calendar", accent="red",
        ), 0, 1)

        kpi_row.addWidget(KpiCard(
            title="Recrutement IA", value=str(kpis["open_positions"]),
            subtitle=f"{kpis['total_candidates']} candidats en base",
            icon="kpi-target", accent="blue",
        ), 0, 2)

        kpi_row.addWidget(KpiCard(
            title="Turnover annuel", value=f"{kpis['annual_turnover_rate']}%",
            subtitle=f"{kpis.get('turnover_label', 'Zone maîtrisée')}",
            icon="kpi-turnover", accent="green",
        ), 0, 3)

        kpi_row.addWidget(KpiCard(
            title="Présélectionnés IA", value=str(kpis["selected_candidates"]),
            subtitle="Candidats retenus",
            icon="kpi-interview", accent="blue",
        ), 0, 4)

        layout.addLayout(kpi_row)

        # ============================================
        # SECTION : Vigilance & Analyse
        # ============================================
        vigilance_card = self._build_vigilance_section(alerts)
        layout.addWidget(vigilance_card)

        # ============================================
        # SECTION : Repartition + Activites (2 colonnes)
        # ============================================
        middle = QHBoxLayout()
        middle.setSpacing(16)
        middle.setAlignment(Qt.AlignmentFlag.AlignTop)

        # --- Colonne gauche : Repartition ---
        left_col = QVBoxLayout()
        left_col.setSpacing(14)
        left_col.setAlignment(Qt.AlignmentFlag.AlignTop)
        left_col.addWidget(self._build_repartition_card(repart, kpis))
        middle.addLayout(left_col, 3)

        # --- Colonne droite : Activites ---
        right_col = QVBoxLayout()
        right_col.setSpacing(10)
        right_col.setAlignment(Qt.AlignmentFlag.AlignTop)
        right_col.addWidget(self._build_activities_card(alerts))
        middle.addLayout(right_col, 2)

        layout.addLayout(middle)
        layout.addStretch()

    # =====================================================
    # CONSTRUCTION DES SECTIONS
    # =====================================================

    def _build_vigilance_section(self, alerts) -> QFrame:
        card = QFrame()
        card.setObjectName("kpiCard")
        v = QVBoxLayout(card)
        v.setContentsMargins(24, 18, 24, 18)
        v.setSpacing(12)

        head = QHBoxLayout()
        head.setSpacing(12)

        # Utilisation de l'émoji 🤖 qui va chercher app-ia.png
        icon = IconLabel("🤖", fallback="🛡", size=18)
        icon.setFixedSize(40, 40)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("background-color: #ECFDF5; border-radius: 10px;")
        head.addWidget(icon)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        title = QLabel("Vigilance & Analyse")
        title.setStyleSheet("font-size: 14pt; font-weight: 700; color: #0F172A; background: transparent;")
        title_col.addWidget(title)

        sub = QLabel("Détection anticipée des tensions, surcharge et risques de désengagement")
        sub.setStyleSheet("font-size: 10pt; color: #64748B; background: transparent;")
        title_col.addWidget(sub)

        head.addLayout(title_col, 1)

        n_crit = len([a for a in alerts if a["severity"].lower() == "critique"])
        badge_variant = "danger" if n_crit > 0 else "success"
        head.addWidget(Badge(f"{n_crit} Alertes Actives", variant=badge_variant))
        v.addLayout(head)

        row = QHBoxLayout()
        row.setSpacing(14)
        row.addWidget(self._build_pred_card(alerts, kind="danger"))
        row.addWidget(self._build_pred_card(alerts, kind="success"))
        v.addLayout(row)

        return card

    def _build_pred_card(self, alerts, kind="danger") -> QFrame:
        card = QFrame()
        card.setMinimumHeight(140)

        if kind == "danger":
            border_color = "#C0392B"
            bg_card = "#FEF2F2"
            tag = "RISQUE DE SURCHARGE"
            tag_color = "#C0392B"
        else:
            border_color = "#0D7A6A"
            bg_card = "#F0FDF4"
            tag = "RISQUE RÉSOLU"
            tag_color = "#0D7A6A"

        card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_card};
                border-radius: 12px;
                border: 1px solid {border_color};
                border-top: 4px solid {border_color};
            }}
        """)

        v = QVBoxLayout(card)
        v.setContentsMargins(20, 14, 20, 14)
        v.setSpacing(6)

        tag_lbl = QLabel(tag)
        tag_lbl.setStyleSheet(
            f"color: {tag_color}; font-size: 9pt; font-weight: 800; "
            "letter-spacing: 1px; background: transparent; border: none;"
        )
        v.addWidget(tag_lbl)

        if kind == "danger":
            n_crit = len([a for a in alerts if a["severity"].lower() == "critique"])
            title = f"{n_crit} Alerte(s) critique(s) à traiter"
            desc = "Anomalies détectées nécessitant une intervention rapide."
        else:
            n_resolved = self._load_resolved_count()
            title = f"{n_resolved} Alerte(s) résolue(s)"
            desc = ("Les anomalies précédemment détectées ont été traitées. "
                    "Le risque de démission a été neutralisé grâce aux actions correctives.")

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(
            "font-size: 12pt; font-weight: 700; color: #0F172A; "
            "background: transparent; border: none;"
        )
        title_lbl.setWordWrap(True)
        v.addWidget(title_lbl)

        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet(
            "font-size: 9.5pt; color: #64748B; background: transparent; border: none;"
        )
        desc_lbl.setWordWrap(True)
        v.addWidget(desc_lbl)

        v.addStretch()

        footer = QHBoxLayout()
        footer.addStretch()
        btn = QPushButton("Consulter alerte →")
        btn.setObjectName("secondaryButton")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        # CORRECTION : Navigation vers la page Turnover au clic
        btn.clicked.connect(lambda: self.navigate_to.emit("turnover"))
        footer.addWidget(btn)
        v.addLayout(footer)

        return card

    def _build_repartition_card(self, repart, kpis) -> QFrame:
        card = QFrame()
        card.setObjectName("kpiCard")
        # Empêche l'étirement vertical
        card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        v = QVBoxLayout(card)
        v.setContentsMargins(24, 20, 24, 20)
        v.setSpacing(6)

        head = QHBoxLayout()
        head.setSpacing(10)
        title = QLabel("Répartition des Effectifs")
        title.setStyleSheet("font-size: 14pt; font-weight: 700; color: #0F172A; background: transparent;")
        head.addWidget(title)
        head.addStretch()

        total_emp = sum(d["count"] for d in repart) or 1
        head.addWidget(Badge(f"{total_emp} Collaborateurs", variant="info"))
        v.addLayout(head)

        sub = QLabel("par Pôle")
        sub.setStyleSheet(
            "font-size: 11pt; font-weight: 600; color: #0F172A; "
            "background: transparent; padding-top: 4px;"
        )
        v.addWidget(sub)

        sub2 = QLabel("Effectifs consolidés, ratio de parité et enveloppe budgétaire")
        sub2.setStyleSheet("font-size: 9pt; color: #64748B; background: transparent;")
        v.addWidget(sub2)

        v.addSpacing(12)

        if repart:
            # Barre multicolore avec des QFrame
            bar_container = QFrame()
            bar_container.setFixedHeight(10)
            bar_container.setStyleSheet("background-color: #F1F5F9; border-radius: 5px;")
            bar_layout = QHBoxLayout(bar_container)
            bar_layout.setContentsMargins(0, 0, 0, 0)
            bar_layout.setSpacing(0)

            colors_grad = ["#0D7A6A", "#1F4E5F", "#7A8B9C", "#4CD7B0", "#C0392B"]

            for i, d in enumerate(repart):
                pct = 100 * d["count"] / total_emp
                color = colors_grad[i % len(colors_grad)]
                segment = QFrame()
                segment.setStyleSheet(f"background-color: {color}; border: none;")
                segment.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                bar_layout.addWidget(segment, int(pct))

            v.addWidget(bar_container)

            # Labels 0% 50% 100%
            lbl_row = QHBoxLayout()
            lbl_row.setContentsMargins(0, 2, 0, 0)
            lbl_left = QLabel("0%")
            lbl_left.setStyleSheet("color: #94A3B8; font-size: 8pt; font-weight: 600; background: transparent;")
            lbl_mid = QLabel("50%")
            lbl_mid.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_mid.setStyleSheet("color: #94A3B8; font-size: 8pt; font-weight: 600; background: transparent;")
            lbl_right = QLabel("100%")
            lbl_right.setAlignment(Qt.AlignmentFlag.AlignRight)
            lbl_right.setStyleSheet("color: #94A3B8; font-size: 8pt; font-weight: 600; background: transparent;")

            lbl_row.addWidget(lbl_left, 1)
            lbl_row.addWidget(lbl_mid, 1)
            lbl_row.addWidget(lbl_right, 1)
            v.addLayout(lbl_row)

            v.addSpacing(16)

            colors = ["#0D7A6A", "#1F4E5F", "#4CD7B0", "#7A8B9C", "#C0392B"]
            for i, d in enumerate(repart):
                pct = round(100 * d["count"] / total_emp, 1)
                v.addWidget(RepartitionRow(
                    name=d["name"], percentage=pct, count=d["count"],
                    color=colors[i % len(colors)],
                ))
        else:
            empty = QLabel("Aucune donnée disponible")
            empty.setStyleSheet("color: #7A8B9C; font-style: italic; padding: 12px; background: transparent;")
            v.addWidget(empty)

        # Empêche le contenu de s'étirer verticalement
        v.addStretch()
        return card

    def _build_activities_card(self, alerts) -> QFrame:
        card = QFrame()
        card.setObjectName("kpiCard")
        card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        v = QVBoxLayout(card)
        v.setContentsMargins(20, 18, 20, 18)
        v.setSpacing(10)

        head = QHBoxLayout()
        head.setSpacing(8)

        dot = QFrame()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet("background-color: #C0392B; border-radius: 4px;")
        head.addWidget(dot)

        title = QLabel("Dernières Activités RH")
        title.setStyleSheet(
            "font-size: 13pt; font-weight: 700; color: #0F172A; background: transparent;"
        )
        head.addWidget(title)

        sub = QLabel("/ Alertes actives à traiter")
        sub.setStyleSheet("font-size: 9pt; color: #94A3B8; background: transparent;")
        head.addWidget(sub)

        head.addStretch()

        btn_see = QPushButton("Tout voir")
        btn_see.setStyleSheet(
            "color: #0D7A6A; font-size: 9pt; font-weight: 600; "
            "background: transparent; border: none; text-decoration: underline;"
        )
        btn_see.setCursor(Qt.CursorShape.PointingHandCursor)
        head.addWidget(btn_see)

        v.addLayout(head)

        activities = self._build_activities_from_alerts(alerts)
        if activities:
            for act in activities:
                v.addWidget(ActivityItem(
                    icon=act.get("icon", "🔔"),
                    title=act.get("title", ""),
                    desc=act.get("description", ""),
                    time_ago=act.get("time_ago", ""),
                    badge_text=act.get("severity", "info"),
                    badge_variant=act.get("badge_variant", "info"),
                ))
        else:
            empty = QLabel("Aucune activité récente")
            empty.setStyleSheet(
                "color: #7A8B9C; font-style: italic; padding: 12px; background: transparent;"
            )
            v.addWidget(empty)

        v.addStretch()
        return card

    # =====================================================
    # CHARGEMENT DES DONNEES
    # =====================================================

    def _load_kpis(self) -> dict:
        try:
            return self.stats_svc.get_dashboard_kpis()
        except Exception as e:
            print(f"[AccueilPage] Erreur KPIs: {e}")
            return {
                "total_employees": 0, "active_employees": 0,
                "absences_this_month": 0, "annual_turnover_rate": 0.0,
                "turnover_label": "—", "turnover_alert": False,
                "open_positions": 0, "total_candidates": 0,
                "selected_candidates": 0, "annual_payroll": 0.0,
                "average_seniority_years": 0.0,
            }

    def _load_repartition(self) -> list:
        try:
            return self.stats_svc.get_headcount_by_department()
        except Exception as e:
            print(f"[AccueilPage] Erreur repartition: {e}")
            return []

    def _load_alerts(self) -> list:
        try:
            return self.alert_svc.get_active_alerts()
        except Exception as e:
            print(f"[AccueilPage] Erreur alertes: {e}")
            return []

    def _load_resolved_count(self) -> int:
        try:
            kpis = self.alert_svc.get_kpis()
            return kpis.get("resolved_alerts", 0)
        except Exception as e:
            print(f"[AccueilPage] Erreur resolved: {e}")
            return 0

    def _build_activities_from_alerts(self, alerts) -> list:
        from datetime import datetime
        activities = []
        now = datetime.now()

        for a in alerts[:6]:
            sev = a["severity"].lower()
            icon = "⚠️" if sev == "critique" else "🔔"
            title = a.get("employee_name", "Alerte")
            desc = a.get("description", "")

            if sev == "critique":
                badge_variant = "danger"
            elif sev == "preventif":
                badge_variant = "warning"
            else:
                badge_variant = "info"

            detected = a.get("detected_at")
            if detected:
                delta = now - detected
                seconds = int(delta.total_seconds())
                if seconds < 60:
                    time_ago = "à l'instant"
                elif seconds < 3600:
                    time_ago = f"il y a {seconds // 60}min"
                elif seconds < 86400:
                    time_ago = f"il y a {seconds // 3600}h"
                else:
                    time_ago = f"il y a {seconds // 86400}j"
            else:
                time_ago = "—"

            activities.append({
                "icon": icon, "title": title, "description": desc,
                "time_ago": time_ago, "severity": sev,
                "badge_variant": badge_variant,
            })
        return activities

    # =====================================================
    # ACTIONS
    # =====================================================

    def _show_quick_actions_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 6px;
                min-width: 260px;
            }
            QMenu::item {
                background-color: transparent;
                color: #0F172A;
                padding: 10px 16px;
                border-radius: 6px;
                font-size: 10pt;
            }
            QMenu::item:selected {
                background-color: #ECFDF5;
                color: #0D7A6A;
            }
        """)

        actions_config = [
            ("   Ajouter un employé", "action-add"),
            ("   Lancer un recrutement IA", "sidebar-recruit"),
            ("   Analyse SmartMatch binôme", "status-match"),
        ]

        for label, icon_name in actions_config:
            action = QAction(label, self)
            icon_path = resolve_icon_path(icon_name)
            if icon_path and icon_path.exists():
                action.setIcon(QIcon(str(icon_path)))

            action.triggered.connect(lambda _, k=icon_name: self.navigate_to.emit(k))
            menu.addAction(action)

        menu.exec(QCursor.pos())