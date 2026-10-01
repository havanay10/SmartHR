"""Page Recrutement — Recrutement & Scoring IA (Module 4 du CDC)."""

import csv
from pathlib import Path
from math import ceil

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QScrollArea, QFrame, QLabel, QPushButton, QProgressBar,
    QLineEdit, QMenu, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QCursor

from app.ui.widgets import Badge
from app.ui.dialogs import CreateOfferDialog
from app.ui.dialogs.import_cv_dialog import ImportCVDialog
from app.ui.dialogs.candidate_dialog import CandidateDialog
from app.services.recruitment_service import RecruitmentService
from app.services.stats_service import StatsService
from app.services.audit_service import AuditService


PAGE_SIZE = 5
TOP_MATCHES_LIMIT = 5


# =====================================================
# HELPERS
# =====================================================
def extract_candidate_id(candidate) -> str:
    """Extrait l'ID d'un candidat peu importe la clé utilisée."""
    if not candidate:
        return ""
    if isinstance(candidate, (str, int)):
        return str(candidate)
    if not isinstance(candidate, dict):
        if hasattr(candidate, "id"):
            return str(candidate.id)
        return ""

    for key in ["id", "ID", "Id", "candidate_id", "candidateId",
                "_id", "uuid", "UUID", "applicant_id"]:
        val = candidate.get(key)
        if val is not None and val != "":
            return str(val)

    for key, val in candidate.items():
        if "id" in key.lower() and val is not None and val != "":
            return str(val)
    return ""


# =====================================================
# WIDGETS CUSTOM
# =====================================================
class ScoreRing(QLabel):
    """Cercle avec score en pourcentage (couleur dynamique)."""

    def __init__(self, score: int, size: int = 56):
        super().__init__()
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText(f"{score}%")

        if score >= 95:
            bg = "#0D7A6A"
        elif score >= 85:
            bg = "#1F9D8A"
        elif score >= 75:
            bg = "#F39C12"
        else:
            bg = "#94A3B8"

        self.setStyleSheet(f"""
            background-color: {bg};
            color: #FFFFFF;
            border-radius: {size // 2}px;
            font-size: 13pt;
            font-weight: 800;
            border: none;
        """)


class ColorDot(QFrame):
    """Pastille colorée (remplace les emojis)."""

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

    def __init__(self, letter: str, color: str, bg: str, size: int = 34):
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
# PAGE PRINCIPALE
# =====================================================
class RecruitmentPage(QWidget):

    navigate_to = pyqtSignal(str)
    offer_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.recruitment_svc = RecruitmentService()
        self.stats_svc = StatsService()

        self.selected_offer_id = None
        self.active_filter = "Tous"
        self.search_query = ""
        self.sort_mode = "pertinence"

        self.current_page = 1
        self.total_pages = 1
        self.all_filtered_candidates = []

        self._offers_stats_cache = {}

        self.offers_badge = None
        self.candidates_badge = None
        self.offers_layout = None
        self.candidates_layout = None
        self.top_matches_layout = None
        self.pagination_info = None
        self.pagination_layout = None
        self.search_input = None
        self.sort_button = None

        self._setup_ui()
        self._load_data()

    # =====================================================
    # UI
    # =====================================================
    def _setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { background-color: #F4F6F9; border: none; }")

        inner = QWidget()
        inner.setStyleSheet("background-color: #F4F6F9;")
        scroll.setWidget(inner)
        outer.addWidget(scroll)

        layout = QVBoxLayout(inner)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(20)

        layout.addLayout(self._build_header())
        layout.addLayout(self._build_kpi_section())
        layout.addWidget(self._build_offers_section())
        layout.addWidget(self._build_candidates_section())
        layout.addWidget(self._build_top_matches_section())
        layout.addStretch()

    # =====================================================
    # HEADER
    # =====================================================
    def _build_header(self):
        header = QHBoxLayout()
        header.setSpacing(12)

        # Titre + badge
        left_head = QVBoxLayout()
        left_head.setSpacing(6)

        title_row = QHBoxLayout()
        title_row.setSpacing(12)

        title = QLabel("Recrutement & Scoring IA")
        title.setStyleSheet("""
            font-size: 18pt; font-weight: 800; color: #0F1E2E;
            background: transparent; border: none; padding: 0;
        """)
        title_row.addWidget(title)

        # Badge avec pastille
        badge_algo = QFrame()
        badge_algo.setStyleSheet("""
            background-color: #E8F5F1;
            border-radius: 11px;
            border: none;
        """)
        badge_layout = QHBoxLayout(badge_algo)
        badge_layout.setContentsMargins(10, 3, 14, 3)
        badge_layout.setSpacing(6)
        badge_layout.addWidget(ColorDot("#0D7A6A", 7))

        badge_txt = QLabel("Algorithme v2.4 Actif")
        badge_txt.setStyleSheet("""
            background: transparent; color: #0D7A6A;
            font-size: 8pt; font-weight: 800;
            letter-spacing: 0.5px; border: none;
        """)
        badge_layout.addWidget(badge_txt)

        title_row.addWidget(badge_algo, 0, Qt.AlignmentFlag.AlignVCenter)
        title_row.addStretch()
        left_head.addLayout(title_row)

        subtitle = QLabel("Gestion des candidatures avec matching IA intelligent et vivier dynamique")
        subtitle.setStyleSheet("""
            font-size: 10pt; color: #7A8B9C;
            background: transparent; border: none; padding: 0;
        """)
        left_head.addWidget(subtitle)

        header.addLayout(left_head, 1)

        # Bouton Importer CV
        btn_import = QPushButton("Importer un CV")
        btn_import.setObjectName("secondaryButton")
        btn_import.setMinimumHeight(42)
        btn_import.setMinimumWidth(140)
        btn_import.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_import.clicked.connect(self._show_import_cv_dialog)
        header.addWidget(btn_import, 0, Qt.AlignmentFlag.AlignTop)

        # Bouton Nouvelle offre
        btn_create = QPushButton("+  Nouvelle offre")
        btn_create.setObjectName("primaryButton")
        btn_create.setMinimumHeight(42)
        btn_create.setMinimumWidth(150)
        btn_create.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_create.setStyleSheet("""
            QPushButton {
                background-color: #0D7A6A;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 10pt;
                font-weight: 700;
                min-height: 42px;
            }
            QPushButton:hover { background-color: #0A6456; }
            QPushButton:pressed { background-color: #084C41; }
        """)
        btn_create.clicked.connect(self._show_create_offer_dialog)
        header.addWidget(btn_create, 0, Qt.AlignmentFlag.AlignTop)

        return header

    # =====================================================
    # KPIs
    # =====================================================
    def _build_kpi_section(self):
        kpi_row = QGridLayout()
        kpi_row.setSpacing(16)

        try:
            kpis = self.recruitment_svc.get_recruitment_kpis()
        except Exception:
            kpis = {'total_candidates': 0, 'preselected_count': 0, 'interviews_count': 0}

        total = max(kpis['total_candidates'], 1)
        preselected_pct = int(kpis['preselected_count'] / total * 100)

        kpi_row.addWidget(self._build_kpi_card(
            title="Candidatures vivier",
            value=str(kpis['total_candidates']),
            subtitle="Profils en base",
            letter="C", accent="blue",
            progress_pct=min(100, int(kpis['total_candidates'] / 50 * 100)) if kpis['total_candidates'] else 0,
        ), 0, 0)

        kpi_row.addWidget(self._build_kpi_card(
            title="Présélectionnés IA",
            value=str(kpis['preselected_count']),
            subtitle="Matchs ≥ 80%",
            letter="P", accent="green",
            progress_pct=preselected_pct,
        ), 0, 1)

        kpi_row.addWidget(self._build_kpi_card(
            title="Entretiens",
            value=str(kpis['interviews_count']),
            subtitle="Planifiés cette semaine",
            letter="E", accent="orange",
            progress_pct=min(100, int(kpis['interviews_count'] / 10 * 100)) if kpis['interviews_count'] else 0,
        ), 0, 2)

        return kpi_row

    def _build_kpi_card(self, title, value, subtitle, letter, accent, progress_pct=0):
        card = QFrame()
        card.setObjectName("kpiCard")
        card.setProperty("accentColor", accent)
        card.setMinimumHeight(120)

        accent_map = {
            "blue": ("#E0F0FF", "#2E86DE", "#2E86DE"),
            "green": ("#E8F5F1", "#0D7A6A", "#0D7A6A"),
            "orange": ("#FEF3C7", "#F39C12", "#F39C12"),
        }
        bg, fg, bar_color = accent_map.get(accent, ("#F1F5F9", "#475569", "#475569"))

        v = QVBoxLayout(card)
        v.setContentsMargins(22, 18, 22, 18)
        v.setSpacing(10)

        top_row = QHBoxLayout()
        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet("""
            font-size: 8.5pt; color: #5A6B7D; font-weight: 700;
            letter-spacing: 0.8px; background: transparent; border: none;
        """)
        top_row.addWidget(title_lbl)
        top_row.addStretch()

        # Carré coloré avec lettre (remplace l'emoji)
        top_row.addWidget(IconSquare(letter, fg, bg, size=34))
        v.addLayout(top_row)

        val_row = QHBoxLayout()
        val_lbl = QLabel(value)
        val_lbl.setStyleSheet("""
            font-size: 24pt; font-weight: 800; color: #0F1E2E;
            background: transparent; border: none;
        """)
        val_row.addWidget(val_lbl)

        sub_lbl = QLabel(subtitle)
        sub_lbl.setStyleSheet("""
            font-size: 9pt; color: #7A8B9C;
            background: transparent; border: none; padding-left: 10px;
        """)
        val_row.addWidget(sub_lbl, 0, Qt.AlignmentFlag.AlignBottom)
        val_row.addStretch()
        v.addLayout(val_row)
        v.addStretch()

        bar = QProgressBar()
        bar.setValue(progress_pct)
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
                background-color: {bar_color};
                border-radius: 3px;
            }}
        """)
        v.addWidget(bar)

        return card

    # =====================================================
    # SECTION OFFRES
    # =====================================================
    def _build_offers_section(self):
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
            }
        """)
        v = QVBoxLayout(section)
        v.setContentsMargins(24, 20, 24, 20)
        v.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Postes ouverts & En cours")
        title.setStyleSheet("""
            font-size: 14pt; font-weight: 700; color: #0F1E2E;
            background: transparent; border: none;
        """)
        header.addWidget(title)

        self.offers_badge = Badge("0 postes", variant="info")
        header.addWidget(self.offers_badge)
        header.addStretch()

        self.sort_button = QPushButton("Trier par pertinence ▾")
        self.sort_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sort_button.setStyleSheet("""
            QPushButton {
                background: transparent; color: #7A8B9C;
                border: none; font-size: 9pt;
                padding: 4px 8px; text-align: right;
            }
            QPushButton:hover { color: #0D7A6A; }
        """)
        self.sort_button.clicked.connect(self._show_sort_menu)
        header.addWidget(self.sort_button)

        v.addLayout(header)

        self.offers_container = QWidget()
        self.offers_container.setStyleSheet("background-color: transparent;")
        self.offers_layout = QVBoxLayout(self.offers_container)
        self.offers_layout.setContentsMargins(0, 0, 0, 0)
        self.offers_layout.setSpacing(12)
        v.addWidget(self.offers_container)

        return section

    def _show_sort_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 6px;
                min-width: 200px;
            }
            QMenu::item {
                background-color: transparent;
                color: #0F172A;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 10pt;
            }
            QMenu::item:selected {
                background-color: #ECFDF5;
                color: #0D7A6A;
            }
        """)

        for label, key in [
            ("Trier par pertinence", "pertinence"),
            ("Trier par plus récent", "recent"),
            ("Trier par score", "score"),
        ]:
            action = QAction(label, self)
            action.triggered.connect(lambda _, k=key: self._on_sort_change(k))
            menu.addAction(action)

        menu.exec(QCursor.pos())

    def _on_sort_change(self, sort_key: str):
        self.sort_mode = sort_key
        labels = {
            "pertinence": "Trier par pertinence ▾",
            "recent": "Trier par plus récent ▾",
            "score": "Trier par score ▾",
        }
        if self.sort_button:
            self.sort_button.setText(labels.get(sort_key, "Trier ▾"))
        self._load_offers()

    # =====================================================
    # SECTION CANDIDATS
    # =====================================================
    def _build_candidates_section(self):
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
            }
        """)
        v = QVBoxLayout(section)
        v.setContentsMargins(24, 20, 24, 20)
        v.setSpacing(14)

        title_row = QHBoxLayout()
        c_title = QLabel("Candidatures filtrées")
        c_title.setStyleSheet("""
            font-size: 14pt; font-weight: 700; color: #0F1E2E;
            background: transparent; border: none;
        """)
        title_row.addWidget(c_title)
        title_row.addStretch()

        v.addLayout(title_row)

        sub_row = QHBoxLayout()
        sub_row.setSpacing(12)

        self.candidates_badge = QLabel("0 candidats pré-sélectionnés sur 0 profils analysés")
        self.candidates_badge.setStyleSheet("""
            font-size: 9pt; color: #7A8B9C;
            background: transparent; border: none;
        """)
        sub_row.addWidget(self.candidates_badge)
        sub_row.addStretch()

        self.filter_buttons = {}
        for label in ["Tous", "Top Matchs > 90%", "Disponibles"]:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setChecked(label == "Tous")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(32)
            self._apply_filter_style(btn, label == "Tous")
            btn.clicked.connect(lambda _, l=label: self._on_filter_click(l))
            sub_row.addWidget(btn)
            self.filter_buttons[label] = btn

        v.addLayout(sub_row)

        self.candidates_container = QWidget()
        self.candidates_container.setStyleSheet("background-color: transparent;")
        self.candidates_layout = QVBoxLayout(self.candidates_container)
        self.candidates_layout.setContentsMargins(0, 0, 0, 0)
        self.candidates_layout.setSpacing(10)
        v.addWidget(self.candidates_container)

        footer = QHBoxLayout()
        self.pagination_info = QLabel("Affichage de 0 sur 0 profils")
        self.pagination_info.setStyleSheet("""
            font-size: 9pt; color: #7A8B9C; font-style: italic;
            background: transparent; border: none;
        """)
        footer.addWidget(self.pagination_info)
        footer.addStretch()

        self.pagination_layout = QHBoxLayout()
        self.pagination_layout.setSpacing(4)
        footer.addLayout(self.pagination_layout)

        v.addLayout(footer)

        return section

    def _render_pagination(self):
        while self.pagination_layout.count():
            item = self.pagination_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if self.total_pages <= 1:
            return

        btn_prev = QPushButton("‹")
        btn_prev.setFixedSize(28, 28)
        btn_prev.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_prev.setEnabled(self.current_page > 1)
        btn_prev.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #7A8B9C;
                border: none; border-radius: 6px; font-size: 11pt;
            }
            QPushButton:hover:enabled { background-color: #F4F6F9; }
            QPushButton:disabled { color: #CBD5E1; }
        """)
        btn_prev.clicked.connect(lambda: self._go_to_page(self.current_page - 1))
        self.pagination_layout.addWidget(btn_prev)

        for i in range(1, self.total_pages + 1):
            btn = QPushButton(str(i))
            btn.setFixedSize(28, 28)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            if i == self.current_page:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #0D7A6A; color: #FFFFFF;
                        border: none; border-radius: 6px;
                        font-size: 9pt; font-weight: 700;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent; color: #7A8B9C;
                        border: none; border-radius: 6px; font-size: 9pt;
                    }
                    QPushButton:hover { background-color: #F4F6F9; }
                """)
            btn.clicked.connect(lambda _, p=i: self._go_to_page(p))
            self.pagination_layout.addWidget(btn)

        btn_next = QPushButton("›")
        btn_next.setFixedSize(28, 28)
        btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_next.setEnabled(self.current_page < self.total_pages)
        btn_next.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #7A8B9C;
                border: none; border-radius: 6px; font-size: 11pt;
            }
            QPushButton:hover:enabled { background-color: #F4F6F9; }
            QPushButton:disabled { color: #CBD5E1; }
        """)
        btn_next.clicked.connect(lambda: self._go_to_page(self.current_page + 1))
        self.pagination_layout.addWidget(btn_next)

    def _go_to_page(self, page: int):
        if page < 1 or page > self.total_pages:
            return
        self.current_page = page
        self._render_candidates_page()

    def _render_candidates_page(self):
        self._clear_layout(self.candidates_layout)

        start = (self.current_page - 1) * PAGE_SIZE
        end = start + PAGE_SIZE
        page_items = self.all_filtered_candidates[start:end]

        if not page_items:
            self.candidates_layout.addWidget(self._build_empty_state(
                "Aucun candidat trouvé",
                "Essayez de modifier vos filtres ou votre recherche"
            ))
            return

        for candidate in page_items:
            card = self._build_candidate_card(candidate)
            self.candidates_layout.addWidget(card)

        if self.pagination_info:
            total = len(self.all_filtered_candidates)
            self.pagination_info.setText(
                f"Affichage de {start + 1}-{min(end, total)} sur {total} profils préqualifiés"
            )

        self._render_pagination()

    # =====================================================
    # SECTION TOP MATCHS
    # =====================================================
    def _build_top_matches_section(self):
        section = QFrame()
        section.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
            }
        """)
        v = QVBoxLayout(section)
        v.setContentsMargins(24, 20, 24, 20)
        v.setSpacing(14)

        header = QHBoxLayout()
        title = QLabel("Top Matchs IA & Profils Recommandés")
        title.setStyleSheet("""
            font-size: 13pt; font-weight: 700; color: #0F1E2E;
            background: transparent; border: none;
        """)
        header.addWidget(title)
        header.addStretch()

        self.top_matches_badge = Badge("Top 10", variant="success")
        header.addWidget(self.top_matches_badge)
        v.addLayout(header)

        self.top_matches_sub = QLabel("Chargement des meilleurs profils...")
        self.top_matches_sub.setStyleSheet("""
            font-size: 9pt; color: #7A8B9C;
            background: transparent; border: none;
        """)
        v.addWidget(self.top_matches_sub)

        self.top_matches_container = QWidget()
        self.top_matches_container.setStyleSheet("background-color: transparent;")
        self.top_matches_layout = QVBoxLayout(self.top_matches_container)
        self.top_matches_layout.setContentsMargins(0, 0, 0, 0)
        self.top_matches_layout.setSpacing(10)
        v.addWidget(self.top_matches_container)

        return section

    def _load_top_matches(self):
        try:
            top_matches = self.recruitment_svc.get_top_matches(limit=TOP_MATCHES_LIMIT)
        except Exception as e:
            print(f"[RecruitmentPage] Erreur top matches: {e}")
            top_matches = []

        self._clear_layout(self.top_matches_layout)

        if not top_matches:
            self.top_matches_layout.addWidget(self._build_empty_state(
                "Aucun top match disponible",
                "Importez des CV pour alimenter le scoring IA"
            ))
            if self.top_matches_badge:
                self.top_matches_badge.setText("Top 0")
            if self.top_matches_sub:
                self.top_matches_sub.setText("Aucun profil recommandé pour le moment")
            return

        enriched_matches = [
            self._enrich_candidate_with_offer(m) for m in top_matches
        ]

        if self.top_matches_badge:
            self.top_matches_badge.setText(f"Top {len(enriched_matches)}")

        if self.top_matches_sub:
            self.top_matches_sub.setText(
                f"{len(enriched_matches)} profils recommandés par l'IA (score ≥ 80%)"
            )

        for candidate in enriched_matches:
            card = self._build_candidate_card(candidate)
            self.top_matches_layout.addWidget(card)

    # =====================================================
    # CARTE CANDIDAT
    # =====================================================
    def _build_candidate_card(self, candidate: dict):
        cand_id = extract_candidate_id(candidate)

        card = QFrame()
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setMinimumHeight(100)
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                border: 1px solid #E4E9EF;
            }
            QFrame:hover {
                border: 1px solid #0D7A6A;
                background-color: #FAFDFB;
            }
        """)

        h = QHBoxLayout(card)
        h.setContentsMargins(16, 14, 16, 14)
        h.setSpacing(16)

        score = int(candidate.get("match_score", 0) or 0)
        score_badge = ScoreRing(score)
        h.addWidget(score_badge, 0, Qt.AlignmentFlag.AlignVCenter)

        main = QVBoxLayout()
        main.setSpacing(4)

        name_row = QHBoxLayout()
        name_row.setSpacing(8)

        first = candidate.get("first_name", "") or ""
        last = candidate.get("last_name", "") or ""
        name_lbl = QLabel(f"{first} {last}".strip() or "—")
        name_lbl.setStyleSheet("""
            font-size: 11.5pt; font-weight: 700; color: #0F1E2E;
            background: transparent; border: none;
        """)
        name_row.addWidget(name_lbl)

        sep = QLabel("•")
        sep.setStyleSheet("color: #CBD5E1; background: transparent; border: none;")
        name_row.addWidget(sep)

        title_lbl = QLabel(candidate.get("current_title", "—") or "—")
        title_lbl.setStyleSheet("""
            font-size: 9.5pt; color: #5A6B7D;
            background: transparent; border: none;
        """)
        name_row.addWidget(title_lbl)
        name_row.addStretch()
        main.addLayout(name_row)

        # Recommandé (sans étoiles emoji - utilise des caractères unicode)
        rec_row = QHBoxLayout()
        rec_row.setSpacing(6)

        if score >= 90:
            rec_row.addWidget(ColorDot("#F39C12", 8))

            rec_lbl = QLabel("Recommandé")
            rec_lbl.setStyleSheet("""
                font-size: 8.5pt; color: #B9770E; font-weight: 800;
                letter-spacing: 0.4px;
                background: transparent; border: none;
            """)
            rec_row.addWidget(rec_lbl)

        rec_row.addStretch()
        main.addLayout(rec_row)

        skills = candidate.get("skills", []) or []
        if skills:
            skills_row = QHBoxLayout()
            skills_row.setSpacing(4)

            for skill in skills[:4]:
                chip = QLabel(str(skill))
                chip.setStyleSheet("""
                    background-color: #EFF6FF;
                    color: #2E86DE;
                    padding: 2px 8px;
                    border-radius: 8px;
                    font-size: 8pt;
                    font-weight: 600;
                    border: none;
                """)
                skills_row.addWidget(chip)

            skills_row.addStretch()
            main.addLayout(skills_row)

        summary = candidate.get("ai_summary") or candidate.get("summary") or ""
        if summary:
            short = summary[:90] + ("..." if len(summary) > 90 else "")
            sum_lbl = QLabel(f"Profil : {short}")
            sum_lbl.setStyleSheet("""
                font-size: 8.5pt; color: #94A3B8;
                background: transparent; border: none;
            """)
            sum_lbl.setWordWrap(True)
            main.addWidget(sum_lbl)

        h.addLayout(main, 1)

        right = QVBoxLayout()
        right.setSpacing(6)
        right.setAlignment(Qt.AlignmentFlag.AlignTop)

        available = candidate.get("is_available", True)
        if available:
            avail = QLabel("● Disponible maintenant")
            avail.setStyleSheet("""
                background-color: #E8F5F1; color: #0D7A6A;
                padding: 4px 10px; border-radius: 10px;
                font-size: 8pt; font-weight: 700; border: none;
            """)
            right.addWidget(avail, 0, Qt.AlignmentFlag.AlignRight)

        offer_title = candidate.get("offer_title") or ""
        if offer_title:
            short_offer = offer_title[:28] + ("..." if len(offer_title) > 28 else "")
            offer_lbl = QLabel(f"Offre : {short_offer}")
            offer_lbl.setStyleSheet("""
                background-color: #F1F5F9; color: #64748B;
                padding: 3px 10px; border-radius: 8px;
                font-size: 8pt; font-weight: 600; border: none;
            """)
            right.addWidget(offer_lbl, 0, Qt.AlignmentFlag.AlignRight)

        right.addStretch()

        btn_voir = QPushButton("Voir  ›")
        btn_voir.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_voir.setStyleSheet("""
            QPushButton {
                background: transparent; color: #0D7A6A;
                border: none; font-size: 9pt;
                font-weight: 700; padding: 0;
            }
            QPushButton:hover { color: #0A6456; }
        """)
        btn_voir.clicked.connect(lambda _, cid=cand_id: self._on_candidate_clicked(cid))
        right.addWidget(btn_voir, 0, Qt.AlignmentFlag.AlignRight)

        h.addLayout(right)

        card.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        card.customContextMenuRequested.connect(
            lambda pos, c=candidate: self._show_candidate_context_menu(c, pos, card)
        )

        def mouse_press(e, cid=cand_id):
            if e.button() == Qt.MouseButton.LeftButton:
                self._on_candidate_clicked(cid)
        card.mousePressEvent = mouse_press

        return card

    def _show_candidate_context_menu(self, candidate: dict, pos, parent_widget):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 6px;
                min-width: 180px;
            }
            QMenu::item {
                background-color: transparent;
                color: #0F172A;
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 10pt;
            }
            QMenu::item:selected {
                background-color: #ECFDF5;
                color: #0D7A6A;
            }
        """)

        cand_id = extract_candidate_id(candidate)

        action_view = QAction("Voir la fiche", self)
        action_view.triggered.connect(lambda: self._on_candidate_clicked(cand_id))
        menu.addAction(action_view)

        action_export = QAction("Exporter ce candidat", self)
        action_export.triggered.connect(lambda: self._export_single_candidate(candidate))
        menu.addAction(action_export)

        menu.exec(parent_widget.mapToGlobal(pos))

    # =====================================================
    # ETAT VIDE
    # =====================================================
    def _build_empty_state(self, title: str, subtitle: str) -> QFrame:
        empty = QFrame()
        empty.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border-radius: 10px;
                border: 1px dashed #E4E9EF;
            }
        """)
        v = QVBoxLayout(empty)
        v.setContentsMargins(40, 40, 40, 40)
        v.setSpacing(8)

        # Pastille au lieu de l'emoji
        dot_row = QHBoxLayout()
        dot_row.addStretch()
        dot_row.addWidget(ColorDot("#B8C4D0", 12))
        dot_row.addStretch()
        v.addLayout(dot_row)

        t = QLabel(title)
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        t.setStyleSheet("""
            font-size: 12pt; font-weight: 700; color: #0F1E2E;
            background: transparent; border: none;
        """)
        v.addWidget(t)

        s = QLabel(subtitle)
        s.setAlignment(Qt.AlignmentFlag.AlignCenter)
        s.setStyleSheet("""
            font-size: 9.5pt; color: #7A8B9C;
            background: transparent; border: none;
        """)
        v.addWidget(s)

        return empty

    # =====================================================
    # HELPERS
    # =====================================================
    def _apply_filter_style(self, btn, is_active):
        if is_active:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #0D7A6A; color: #FFFFFF;
                    border: none; padding: 6px 14px;
                    border-radius: 6px; font-size: 9pt; font-weight: 700;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F4F6F9; color: #5A6B7D;
                    border: 1px solid #E4E9EF; padding: 6px 14px;
                    border-radius: 6px; font-size: 9pt; font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #E8F5F1;
                    color: #0D7A6A;
                    border-color: #0D7A6A;
                }
            """)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    # =====================================================
    # ENRICHISSEMENT
    # =====================================================
    def _enrich_offer_with_stats(self, offer: dict) -> dict:
        enriched = dict(offer)
        offer_id = offer.get("id")

        if not offer_id:
            return enriched

        if offer_id in self._offers_stats_cache:
            enriched.update(self._offers_stats_cache[offer_id])
            return enriched

        try:
            candidates_data = self.recruitment_svc.get_candidates_of_offer(offer_id)

            candidates = []
            if isinstance(candidates_data, dict):
                candidates = candidates_data.get("received", [])
            elif isinstance(candidates_data, list):
                candidates = candidates_data

            candidates_count = len(candidates)
            ia_matches = 0
            scores = []

            for c in candidates:
                score = c.get("match_score") or 0
                try:
                    score = float(score)
                except (ValueError, TypeError):
                    score = 0
                if score > 0:
                    scores.append(score)
                if score >= 80:
                    ia_matches += 1

            avg_score = (sum(scores) / len(scores)) if scores else 0.0

            stats = {
                "candidates_count": candidates_count,
                "candidates": candidates_count,
                "ia_matches": ia_matches,
                "matches_ia": ia_matches,
                "avg_score": round(avg_score, 1),
                "score_moyen": round(avg_score, 1),
            }

            self._offers_stats_cache[offer_id] = stats
            enriched.update(stats)

        except Exception as e:
            print(f"[RecruitmentPage] Erreur enrich offre {offer_id}: {e}")

        return enriched

    def _enrich_candidate_with_offer(self, candidate: dict) -> dict:
        enriched = dict(candidate)

        try:
            offer_title = candidate.get("offer_title") or candidate.get("matched_offer")
            if offer_title:
                enriched["offer_title"] = offer_title
                return enriched

            candidate_id = extract_candidate_id(candidate)
            if candidate_id:
                try:
                    details = self.recruitment_svc.get_candidate_details(candidate_id)
                    if details:
                        applications = details.get("applications", [])
                        if applications:
                            first = applications[0]
                            enriched["offer_title"] = (
                                first.get("job_title")
                                or first.get("offer_title")
                                or "—"
                            )
                except Exception:
                    pass

        except Exception as e:
            print(f"[RecruitmentPage] Erreur enrich candidat: {e}")

        return enriched

    # =====================================================
    # CHARGEMENT
    # =====================================================
    def _load_data(self):
        try:
            self._offers_stats_cache.clear()
            self._load_offers()
            self._load_top_matches()
            self._load_filtered_candidates()
        except Exception as e:
            print(f"[RecruitmentPage] Erreur chargement donnees: {e}")

    def _load_offers(self):
        offers = self.recruitment_svc.get_all_job_offers()

        if self.sort_mode == "recent":
            offers.sort(key=lambda o: o.get("created_at") or "", reverse=True)
        elif self.sort_mode == "score":
            offers = [self._enrich_offer_with_stats(o) for o in offers]
            offers.sort(key=lambda o: o.get("avg_score", 0), reverse=True)

        self._clear_layout(self.offers_layout)

        if self.offers_badge:
            self.offers_badge.setText(f"{len(offers)} postes")

        if not offers:
            self.offers_layout.addWidget(self._build_empty_state(
                "Aucune offre active",
                "Cliquez sur '+ Nouvelle offre' pour commencer"
            ))
            return

        for i, offer in enumerate(offers):
            enriched = self._enrich_offer_with_stats(offer)
            is_active = (i == 0)
            row = self._build_offer_row(enriched, is_active=is_active)
            self.offers_layout.addWidget(row)

    def _build_offer_row(self, offer: dict, is_active: bool = False):
        row = QFrame()
        row.setCursor(Qt.CursorShape.PointingHandCursor)
        row.setMinimumHeight(80)

        if is_active:
            row.setStyleSheet("""
                QFrame {
                    background-color: #F4FAF8;
                    border-radius: 10px;
                    border: 1px solid #0D7A6A;
                    border-left: 4px solid #0D7A6A;
                }
            """)
        else:
            row.setStyleSheet("""
                QFrame {
                    background-color: #FFFFFF;
                    border-radius: 10px;
                    border: 1px solid #E4E9EF;
                }
                QFrame:hover { border: 1px solid #0D7A6A; }
            """)

        h = QHBoxLayout(row)
        h.setContentsMargins(18, 14, 18, 14)
        h.setSpacing(20)

        left = QVBoxLayout()
        left.setSpacing(6)

        title_lbl = QLabel(offer.get("title", "—"))
        title_lbl.setStyleSheet("""
            font-size: 11.5pt; font-weight: 700; color: #0F1E2E;
            background: transparent; border: none;
        """)
        left.addWidget(title_lbl)

        tags_row = QHBoxLayout()
        tags_row.setSpacing(6)

        dept = offer.get("department", "—")
        if dept and dept != "—":
            dept_badge = QLabel(dept)
            dept_badge.setStyleSheet("""
                background-color: #EFF6FF; color: #2E86DE;
                padding: 3px 10px; border-radius: 10px;
                font-size: 8pt; font-weight: 600; border: none;
            """)
            tags_row.addWidget(dept_badge)

        status = offer.get("status", "active")
        status_map = {
            "active": ("Active", "#E8F5F1", "#0D7A6A"),
            "en_entretien": ("En entretien", "#FEF3C7", "#B45309"),
            "closed": ("Fermée", "#F1F5F9", "#64748B"),
        }
        s_txt, s_bg, s_fg = status_map.get(status, ("Active", "#E8F5F1", "#0D7A6A"))
        status_badge = QLabel(s_txt)
        status_badge.setStyleSheet(f"""
            background-color: {s_bg}; color: {s_fg};
            padding: 3px 10px; border-radius: 10px;
            font-size: 8pt; font-weight: 700; border: none;
        """)
        tags_row.addWidget(status_badge)

        if offer.get("priority") == "high" or offer.get("is_priority"):
            prio = QLabel("Prioritaire")
            prio.setStyleSheet("""
                background-color: #FEE2E2; color: #C0392B;
                padding: 3px 10px; border-radius: 10px;
                font-size: 8pt; font-weight: 700; border: none;
            """)
            tags_row.addWidget(prio)

        tags_row.addStretch()
        left.addLayout(tags_row)
        h.addLayout(left, 2)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(18)
        stats_row.addLayout(self._stat_block(offer.get("candidates_count", 0), "candidats"))
        stats_row.addLayout(self._stat_block(offer.get("ia_matches", 0), "IA matchs"))
        avg = offer.get("avg_score", 0)
        stats_row.addLayout(self._stat_block(f"{avg:.1f}%", "score moy.", color="#0D7A6A"))
        h.addLayout(stats_row, 2)

        actions = QHBoxLayout()
        actions.setSpacing(8)
        offer_id = offer.get("id", "")

        btn_view = QPushButton("Voir les candidats")
        btn_view.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_view.setMinimumHeight(34)
        btn_view.setStyleSheet("""
            QPushButton {
                background-color: #0D7A6A; color: #FFFFFF;
                border: none; padding: 8px 16px; border-radius: 6px;
                font-size: 9pt; font-weight: 700;
            }
            QPushButton:hover { background-color: #0A6456; }
        """)
        btn_view.clicked.connect(lambda _, oid=offer_id: self._on_offer_clicked(oid))
        actions.addWidget(btn_view)

        btn_detail = QPushButton("Voir détail poste")
        btn_detail.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_detail.setMinimumHeight(34)
        btn_detail.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF; color: #5A6B7D;
                border: 1px solid #E4E9EF; padding: 8px 16px;
                border-radius: 6px; font-size: 9pt; font-weight: 600;
            }
            QPushButton:hover {
                background-color: #F4F6F9;
                border-color: #94A3B8;
            }
        """)
        btn_detail.clicked.connect(lambda _, oid=offer_id: self._on_offer_details_clicked(oid))
        actions.addWidget(btn_detail)

        h.addLayout(actions)

        def mouse_press(e):
            self._on_offer_clicked(offer_id)
        row.mousePressEvent = mouse_press

        return row

    def _stat_block(self, value, label, color="#0F1E2E"):
        v = QVBoxLayout()
        v.setSpacing(1)
        v.setAlignment(Qt.AlignmentFlag.AlignCenter)

        val_lbl = QLabel(str(value))
        val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        val_lbl.setStyleSheet(f"""
            font-size: 14pt; font-weight: 800; color: {color};
            background: transparent; border: none;
        """)
        v.addWidget(val_lbl)

        lbl = QLabel(label)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("""
            font-size: 8pt; color: #7A8B9C;
            background: transparent; border: none;
        """)
        v.addWidget(lbl)

        return v

    def _load_filtered_candidates(self, min_score: float = 80):
        candidates = self.recruitment_svc.get_filtered_candidates(
            min_score=min_score, max_score=100,
        )

        try:
            total = self.recruitment_svc.get_recruitment_kpis()['total_candidates']
        except Exception:
            total = len(candidates)

        if self.candidates_badge:
            self.candidates_badge.setText(
                f"{len(candidates)} candidats pré-sélectionnés sur {total} profils analysés"
            )

        top90 = len([c for c in candidates if (c.get("match_score") or 0) >= 90])
        available = len([c for c in candidates if c.get("is_available", True)])

        if "Tous" in self.filter_buttons:
            self.filter_buttons["Tous"].setText(f"Tous ({len(candidates)})")
        if "Top Matchs > 90%" in self.filter_buttons:
            self.filter_buttons["Top Matchs > 90%"].setText(f"Top Matchs > 90% ({top90})")
        if "Disponibles" in self.filter_buttons:
            self.filter_buttons["Disponibles"].setText(f"Disponibles ({available})")

        filtered = candidates
        if self.active_filter == "Top Matchs > 90%":
            filtered = [c for c in candidates if (c.get("match_score") or 0) >= 90]
        elif self.active_filter == "Disponibles":
            filtered = [c for c in candidates if c.get("is_available", True)]

        if self.search_query:
            q = self.search_query.lower()
            filtered = [
                c for c in filtered
                if q in (c.get("first_name", "") or "").lower()
                or q in (c.get("last_name", "") or "").lower()
                or q in (c.get("current_title", "") or "").lower()
            ]

        self.all_filtered_candidates = [
            self._enrich_candidate_with_offer(c) for c in filtered
        ]

        self.current_page = 1
        self.total_pages = max(1, ceil(len(self.all_filtered_candidates) / PAGE_SIZE))

        self._render_candidates_page()

    # =====================================================
    # INTERACTIONS
    # =====================================================
    def _on_search_change(self, text: str):
        self.search_query = text
        self._load_filtered_candidates()

    def _on_filter_click(self, filter_name: str):
        self.active_filter = filter_name
        for name, btn in self.filter_buttons.items():
            btn.setChecked(name == filter_name)
            self._apply_filter_style(btn, name == filter_name)
        self._load_filtered_candidates()

    def _on_offer_clicked(self, offer_id: str):
        self.selected_offer_id = offer_id
        self._load_offers()

        candidates_data = self.recruitment_svc.get_candidates_of_offer(offer_id)

        if isinstance(candidates_data, dict):
            candidates_list = candidates_data.get("received", [])
        elif isinstance(candidates_data, list):
            candidates_list = candidates_data
        else:
            candidates_list = []

        self.all_filtered_candidates = [
            self._enrich_candidate_with_offer(c) for c in candidates_list
        ]
        self.current_page = 1
        self.total_pages = max(1, ceil(len(self.all_filtered_candidates) / PAGE_SIZE))

        self._render_candidates_page()

    def _on_candidate_clicked(self, candidate_id):
        if not candidate_id or candidate_id == "" or candidate_id == "None":
            QMessageBox.warning(
                self, "ID manquant",
                "L'ID du candidat est vide."
            )
            return

        cand_id_str = str(candidate_id)
        candidate_data = None

        try:
            candidate_data = self.recruitment_svc.get_candidate_details(cand_id_str)
        except Exception as e1:
            print(f"[RecruitmentPage] Tentative 1 échouée : {e1}")

        if not candidate_data:
            try:
                import uuid
                uuid_obj = uuid.UUID(cand_id_str)
                candidate_data = self.recruitment_svc.get_candidate_details(uuid_obj)
            except Exception as e2:
                print(f"[RecruitmentPage] Tentative 2 échouée : {e2}")

        if not candidate_data:
            QMessageBox.warning(
                self, "Introuvable",
                f"Aucun candidat trouvé pour l'ID :\n{cand_id_str}"
            )
            return

        try:
            dialog = CandidateDialog(candidate_data, self)
            dialog.exec()
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir la fiche :\n{e}")

    def _on_offer_details_clicked(self, offer_id: str):
        self.offer_selected.emit(offer_id)
        self.navigate_to.emit("job_offer_detail")

    # =====================================================
    # ACTIONS : IMPORT CV, NOUVELLE OFFRE
    # =====================================================
    def _show_import_cv_dialog(self):
        """Ouvre le dialogue d'import CV (mode candidat)."""
        try:
            dialog = ImportCVDialog(mode="candidate", parent=self)
            dialog.cv_imported.connect(self._on_cv_imported)
            dialog.exec()
        except Exception as e:
            print(f"[RecruitmentPage] Erreur import CV: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir l'import :\n{e}")

    def _on_cv_imported(self, data: dict):
        print(f"[RecruitmentPage] CV importe: {data.get('first_name')} {data.get('last_name')}")
        self._offers_stats_cache.clear()
        self._load_data()

    def _show_create_offer_dialog(self):
        """Ouvre le dialogue de creation d'offre."""
        try:
            departments = self.stats_svc.get_all_departments()
            dialog = CreateOfferDialog(departments, self)
            dialog.offer_created.connect(self._on_offer_created)
            dialog.exec()
        except Exception as e:
            print(f"[RecruitmentPage] Erreur dialogue création offre: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le formulaire :\n{e}")

    def _on_offer_created(self, offer_data: dict):
        try:
            offer_id = self.recruitment_svc.create_job_offer(**offer_data)
            AuditService().log_action(
                action="create_job_offer",
                entity_type="job_offer",
                entity_id=offer_id,
                details=offer_data.get("title", "—"),
            )
            print(f"[RecruitmentPage] Offre créée : {offer_id}")
            self._offers_stats_cache.clear()
            self._load_data()
        except Exception as e:
            print(f"[RecruitmentPage] Erreur création offre: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible de créer l'offre :\n{e}")

    # =====================================================
    # EXPORT CSV
    # =====================================================
    def _export_candidates_csv(self):
        if not self.all_filtered_candidates:
            QMessageBox.information(self, "Export", "Aucun candidat à exporter.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer le CSV",
            str(Path.home() / "candidats_smartrh.csv"),
            "Fichiers CSV (*.csv)",
        )
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Nom", "Prénom", "Poste", "Email", "Téléphone",
                    "Ville", "Score", "Offre", "Disponible"
                ])
                for c in self.all_filtered_candidates:
                    writer.writerow([
                        c.get("last_name", ""),
                        c.get("first_name", ""),
                        c.get("current_title", ""),
                        c.get("email", ""),
                        c.get("phone", ""),
                        c.get("city", ""),
                        c.get("match_score", 0),
                        c.get("offer_title", ""),
                        "Oui" if c.get("is_available", True) else "Non",
                    ])

            QMessageBox.information(
                self, "Export réussi",
                f"{len(self.all_filtered_candidates)} candidats exportés.\n\n{path}"
            )
            AuditService().log_action(
                action="export_candidates_csv",
                entity_type="candidate",
                entity_id="bulk",
                details=f"{len(self.all_filtered_candidates)} candidats",
            )
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Export impossible :\n{e}")

    def _export_single_candidate(self, candidate: dict):
        name = f"{candidate.get('first_name', '')}_{candidate.get('last_name', '')}".strip("_") or "candidat"
        path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer le CSV",
            str(Path.home() / f"{name}.csv"),
            "Fichiers CSV (*.csv)",
        )
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Nom", "Prénom", "Poste", "Email", "Téléphone",
                    "Ville", "Score", "Offre", "Disponible"
                ])
                writer.writerow([
                    candidate.get("last_name", ""),
                    candidate.get("first_name", ""),
                    candidate.get("current_title", ""),
                    candidate.get("email", ""),
                    candidate.get("phone", ""),
                    candidate.get("city", ""),
                    candidate.get("match_score", 0),
                    candidate.get("offer_title", ""),
                    "Oui" if candidate.get("is_available", True) else "Non",
                ])
            QMessageBox.information(self, "Export réussi", f"Candidat exporté :\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Export impossible :\n{e}")