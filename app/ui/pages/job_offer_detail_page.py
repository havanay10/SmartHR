"""Page JobOfferDetail — Détails d'une offre d'emploi."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QScrollArea, QFrame, QLabel, QPushButton, QMessageBox,
    QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal

from app.ui.widgets import Badge
from app.ui.dialogs.candidate_dialog import CandidateDialog
from app.services.recruitment_service import RecruitmentService


# =====================================================
# WIDGETS UTILITAIRES
# =====================================================
class InfoTile(QFrame):
    def __init__(self, label: str, value: str, value_color: str = "#0F1E2E"):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border-radius: 8px;
                border: 1px solid #EEF2F6;
            }
        """)
        v = QVBoxLayout(self)
        v.setContentsMargins(14, 10, 14, 10)
        v.setSpacing(3)

        lbl = QLabel(label.upper())
        lbl.setStyleSheet("""
            font-size: 7.5pt; color: #7A8B9C; font-weight: 800;
            letter-spacing: 0.8px; background: transparent; border: none;
        """)
        v.addWidget(lbl)

        val = QLabel(value)
        val.setStyleSheet(f"""
            font-size: 11pt; font-weight: 700; color: {value_color};
            background: transparent; border: none;
        """)
        val.setWordWrap(True)
        v.addWidget(val)


class ListBlock(QFrame):
    def __init__(self, title: str, items: list, empty_msg: str):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #EFF6FF;
                border-radius: 10px;
                border: none;
            }
        """)
        v = QVBoxLayout(self)
        v.setContentsMargins(18, 14, 18, 14)
        v.setSpacing(10)

        t = QLabel(title)
        t.setStyleSheet("""
            font-size: 10pt; font-weight: 700; color: #1E40AF;
            background: transparent; border: none;
        """)
        v.addWidget(t)

        if items:
            chips_container = QWidget()
            chips_container.setStyleSheet("background: transparent;")
            chips_layout = QHBoxLayout(chips_container)
            chips_layout.setContentsMargins(0, 0, 0, 0)
            chips_layout.setSpacing(6)

            for item in items[:8]:
                chip = QLabel(str(item))
                chip.setStyleSheet("""
                    background-color: #FFFFFF;
                    color: #1E40AF;
                    padding: 4px 12px;
                    border-radius: 10px;
                    font-size: 8.5pt;
                    font-weight: 600;
                    border: none;
                """)
                chips_layout.addWidget(chip)

            chips_layout.addStretch()
            v.addWidget(chips_container)
        else:
            empty = QLabel(empty_msg)
            empty.setStyleSheet("""
                font-size: 9pt; color: #7A8B9C; font-style: italic;
                background: transparent; border: none;
                padding: 8px 0;
            """)
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            v.addWidget(empty)


class ScoreRing(QLabel):
    def __init__(self, score: int, size: int = 52):
        super().__init__()
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText(f"{score}%")
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

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
            font-size: 12pt;
            font-weight: 800;
            border: none;
        """)


# =====================================================
# PAGE
# =====================================================
class JobOfferDetailPage(QWidget):

    navigate_to = pyqtSignal(str)

    def __init__(self, offer_id: str = None, parent=None):
        super().__init__(parent)

        self.offer_id = offer_id
        self.recruitment_svc = RecruitmentService()
        self.offer_data = {}

        self._setup_ui()

        if offer_id:
            self._load_offer_data(offer_id)

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
        layout.setContentsMargins(28, 20, 28, 24)
        layout.setSpacing(14)

        # Header simplifié : seulement "Retour aux offres"
        layout.addWidget(self._build_top_header())

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

        self.content_container = QWidget()
        self.content_container.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(16)
        layout.addWidget(self.content_container)

        layout.addStretch()

    def _build_top_header(self):
        """Header simplifié : uniquement le bouton Retour."""
        header = QFrame()
        header.setStyleSheet("background: transparent;")
        h = QHBoxLayout(header)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(10)

        btn_back = QPushButton("←  Retour aux offres")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #5A6B7D;
                border: none;
                font-size: 10pt;
                font-weight: 600;
                padding: 6px 0;
                text-align: left;
            }
            QPushButton:hover { color: #0D7A6A; }
        """)
        btn_back.clicked.connect(lambda: self.navigate_to.emit("recruitment"))
        h.addWidget(btn_back)
        h.addStretch()

        return header

    # =====================================================
    # CHARGEMENT
    # =====================================================
    def set_offer_id(self, offer_id: str):
        self.offer_id = offer_id
        self._load_offer_data(offer_id)

    def _load_offer_data(self, offer_id: str):
        try:
            offers = self.recruitment_svc.get_all_job_offers()
            offer = next((o for o in offers if o.get("id") == offer_id), None)

            if not offer:
                self._show_error("Offre non trouvée")
                return

            self.offer_data = offer
            self._clear_layout(self.content_layout)

            self._build_offer_details(offer)
            self._build_candidates_section(offer_id)

        except Exception as e:
            print(f"[JobOfferDetailPage] Erreur chargement offre: {e}")
            self._show_error("Erreur lors du chargement de l'offre")

    # =====================================================
    # CARTE OFFRE
    # =====================================================
    def _build_offer_details(self, offer: dict):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 14px;
                border: 1px solid #E4E9EF;
            }
        """)
        v = QVBoxLayout(card)
        v.setContentsMargins(28, 22, 28, 22)
        v.setSpacing(18)

        dept = offer.get("department") or "—"
        ref = offer.get("reference") or offer.get("code") or "—"
        breadcrumb = QLabel(f"🏢  PÔLE {dept.upper()}  •  REF: {ref}")
        breadcrumb.setStyleSheet("""
            font-size: 8pt; color: #7A8B9C; font-weight: 800;
            letter-spacing: 0.8px; background: transparent; border: none;
        """)
        v.addWidget(breadcrumb)

        title_row = QHBoxLayout()
        title_row.setSpacing(12)

        title = QLabel(offer.get("title") or "—")
        title.setStyleSheet("""
            font-size: 22pt; font-weight: 800; color: #0F1E2E;
            background: transparent; border: none;
        """)
        title_row.addWidget(title)
        title_row.addStretch()

        status = (offer.get("status") or "").lower()
        if status in ("active", "ouverte"):
            title_row.addWidget(Badge("Active", variant="success"))
        elif status:
            title_row.addWidget(Badge(status.capitalize(), variant="info"))

        priority = (offer.get("priority") or "").lower()
        if priority in ("prioritaire", "high", "haute"):
            title_row.addWidget(Badge("Prioritaire", variant="danger"))

        v.addLayout(title_row)

        info_grid = QGridLayout()
        info_grid.setSpacing(10)

        sal_min = offer.get("salary_min")
        sal_max = offer.get("salary_max")
        if sal_min and sal_max:
            salary_txt = f"{int(sal_min)}k€ - {int(sal_max)}k€ / an"
        elif sal_min:
            salary_txt = f"À partir de {int(sal_min)}k€ / an"
        else:
            salary_txt = "—"

        tiles = [
            ("DÉPARTEMENT", dept, "#0F1E2E"),
            ("TYPE DE CONTRAT", offer.get("contract_type") or "—", "#0F1E2E"),
            ("LOCALISATION", offer.get("location") or "—", "#0F1E2E"),
            ("EXPÉRIENCE REQUISE", offer.get("experience_level") or "—", "#0F1E2E"),
            ("FOURCHETTE SALARIALE", salary_txt, "#0D7A6A"),
            ("RÉFÉRENCE", ref, "#0F1E2E"),
        ]

        for idx, (label, value, color) in enumerate(tiles):
            info_grid.addWidget(InfoTile(label, value, color), 0, idx)

        v.addLayout(info_grid)

        blocks_row = QHBoxLayout()
        blocks_row.setSpacing(14)

        hard_skills = offer.get("hard_skills") or []
        soft_skills = offer.get("soft_skills") or []

        blocks_row.addWidget(ListBlock(
            title="Compétences techniques requises",
            items=hard_skills,
            empty_msg="Aucune compétence spécifiée",
        ), 1)
        blocks_row.addWidget(ListBlock(
            title="Soft skills & Culture fit",
            items=soft_skills,
            empty_msg="Aucun soft skill spécifié",
        ), 1)

        v.addLayout(blocks_row)

        self.content_layout.addWidget(card)

    # =====================================================
    # SECTION CANDIDATS
    # =====================================================
    def _build_candidates_section(self, offer_id: str):
        try:
            candidates_data = self.recruitment_svc.get_candidates_of_offer(offer_id)
        except Exception as e:
            print(f"[JobOfferDetailPage] Erreur candidats: {e}")
            return

        if isinstance(candidates_data, dict):
            received = candidates_data.get("received", []) or []
            preselected = candidates_data.get("preselected", []) or []
        else:
            received = []
            preselected = []

        section = QWidget()
        section.setStyleSheet("background: transparent;")
        v = QVBoxLayout(section)
        v.setContentsMargins(0, 8, 0, 0)
        v.setSpacing(14)

        header = QHBoxLayout()
        header.setSpacing(10)

        title = QLabel("Candidats associés")
        title.setStyleSheet("""
            font-size: 15pt; font-weight: 800; color: #0F1E2E;
            background: transparent; border: none;
        """)
        header.addWidget(title)

        total = len(received) + len(preselected)
        count_badge = QLabel(f"{total} candidats ({len(preselected)} pré-sél.)")
        count_badge.setStyleSheet("""
            background-color: #F1F5F9;
            color: #475569;
            padding: 4px 12px;
            border-radius: 10px;
            font-size: 8.5pt;
            font-weight: 700;
            border: none;
        """)
        header.addWidget(count_badge)
        header.addStretch()

        v.addLayout(header)

        # QGridLayout pour aligner les 2 colonnes en haut
        cols = QGridLayout()
        cols.setSpacing(20)
        cols.setContentsMargins(0, 0, 0, 0)

        left_col = self._build_candidates_column(
            title="Reçus / À trier",
            candidates=received,
            dot_color="#475569",
            extra_badge="",
        )
        cols.addWidget(left_col, 0, 0, Qt.AlignmentFlag.AlignTop)

        right_col = self._build_candidates_column(
            title="Présélection IA",
            candidates=preselected,
            dot_color="#0D7A6A",
            extra_badge="SmartMatch actif",
        )
        cols.addWidget(right_col, 0, 1, Qt.AlignmentFlag.AlignTop)

        cols.setRowStretch(1, 1)
        cols.setColumnStretch(0, 1)
        cols.setColumnStretch(1, 1)

        v.addLayout(cols)

        self.content_layout.addWidget(section)

    def _build_candidates_column(
        self,
        title: str,
        candidates: list,
        dot_color: str,
        extra_badge: str = "",
    ) -> QFrame:
        col = QFrame()
        col.setStyleSheet("background: transparent;")
        col.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        v = QVBoxLayout(col)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(10)
        v.setAlignment(Qt.AlignmentFlag.AlignTop)

        header = QHBoxLayout()
        header.setSpacing(8)

        dot = QLabel("●")
        dot.setStyleSheet(f"""
            color: {dot_color}; font-size: 12pt; font-weight: 800;
            background: transparent; border: none;
        """)
        header.addWidget(dot)

        t = QLabel(title)
        t.setStyleSheet(f"""
            font-size: 11pt; font-weight: 700; color: {dot_color};
            background: transparent; border: none;
        """)
        header.addWidget(t)

        count_badge = QLabel(f"{len(candidates)} profils")
        count_badge.setStyleSheet("""
            background-color: #F1F5F9;
            color: #64748B;
            padding: 3px 10px;
            border-radius: 10px;
            font-size: 8pt;
            font-weight: 700;
            border: none;
        """)
        header.addWidget(count_badge)

        if extra_badge:
            eb = QLabel(extra_badge)
            eb.setStyleSheet("""
                background-color: #E8F5F1;
                color: #0D7A6A;
                padding: 3px 10px;
                border-radius: 10px;
                font-size: 8pt;
                font-weight: 700;
                border: none;
            """)
            header.addWidget(eb)

        header.addStretch()
        v.addLayout(header)

        if not candidates:
            empty = QLabel("Aucun candidat dans cette catégorie")
            empty.setStyleSheet("""
                font-size: 9pt; color: #94A3B8; font-style: italic;
                background-color: #F8FAFC;
                border-radius: 10px;
                border: 1px dashed #E4E9EF;
                padding: 30px;
            """)
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            empty.setFixedHeight(120)
            v.addWidget(empty)
            return col

        for candidate in candidates[:8]:
            card = self._build_candidate_card(candidate)
            v.addWidget(card)

        return col

    # =====================================================
    # CARTE CANDIDAT
    # =====================================================
    def _build_candidate_card(self, candidate: dict):
        card = QFrame()
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        card.setMinimumHeight(105)
        card.setMaximumHeight(140)

        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                border: 1px solid #E4E9EF;
                border-left: 4px solid #0D7A6A;
            }
            QFrame:hover {
                background-color: #FAFDFB;
                border: 1px solid #0D7A6A;
                border-left: 4px solid #0D7A6A;
            }
        """)

        h = QHBoxLayout(card)
        h.setContentsMargins(14, 12, 14, 12)
        h.setSpacing(14)

        score = int(candidate.get("match_score", 0) or 0)
        score_ring = ScoreRing(score, size=52)
        h.addWidget(score_ring, 0, Qt.AlignmentFlag.AlignTop)

        main = QVBoxLayout()
        main.setSpacing(4)
        main.setContentsMargins(0, 0, 0, 0)

        top = QHBoxLayout()
        top.setSpacing(8)

        first = candidate.get("first_name", "") or ""
        last = candidate.get("last_name", "") or ""
        name_lbl = QLabel(f"{first} {last}".strip() or "—")
        name_lbl.setStyleSheet("""
            font-size: 11pt; font-weight: 800; color: #0F1E2E;
            background: transparent; border: none;
        """)
        top.addWidget(name_lbl)

        stars_count = max(1, min(5, round(score / 20))) if score else 1
        stars = "★" * stars_count + "☆" * (5 - stars_count)
        stars_lbl = QLabel(stars)
        stars_lbl.setStyleSheet("""
            font-size: 10pt; color: #F39C12;
            background: transparent; border: none;
        """)
        top.addWidget(stars_lbl)
        top.addStretch()

        if candidate.get("is_available", True):
            avail = QLabel("● Disponible maintenant")
            avail.setStyleSheet("""
                background-color: #E8F5F1;
                color: #0D7A6A;
                padding: 3px 10px;
                border-radius: 10px;
                font-size: 8pt;
                font-weight: 700;
                border: none;
            """)
            avail.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            top.addWidget(avail)

        main.addLayout(top)

        title_lbl = QLabel(candidate.get("current_title", "—") or "—")
        title_lbl.setStyleSheet("""
            font-size: 9.5pt; color: #5A6B7D;
            background: transparent; border: none;
        """)
        main.addWidget(title_lbl)

        skills = candidate.get("skills", []) or []
        if skills:
            skills_row = QHBoxLayout()
            skills_row.setSpacing(4)

            for skill in skills[:3]:
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
                chip.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                chip.setMaximumHeight(20)
                skills_row.addWidget(chip)

            skills_row.addStretch()
            main.addLayout(skills_row)

        bottom = QHBoxLayout()
        bottom.setSpacing(6)

        summary = candidate.get("ai_summary") or ""
        if summary:
            short = summary[:55] + ("..." if len(summary) > 55 else "")
            sum_lbl = QLabel(f"Profil : {short}")
            sum_lbl.setStyleSheet("""
                font-size: 8.5pt; color: #94A3B8;
                background: transparent; border: none;
            """)
            sum_lbl.setWordWrap(False)
            bottom.addWidget(sum_lbl, 1)

        bottom.addStretch()

        btn_voir = QPushButton("Voir  ›")
        btn_voir.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_voir.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #0D7A6A;
                border: none;
                font-size: 9pt;
                font-weight: 700;
                padding: 0;
            }
            QPushButton:hover { color: #0A6456; }
        """)
        btn_voir.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        cand_id = (
            candidate.get("candidate_id")
            or candidate.get("id")
            or ""
        )
        cand_id = str(cand_id)
        btn_voir.clicked.connect(lambda _, cid=cand_id: self._on_candidate_clicked(cid))
        bottom.addWidget(btn_voir)

        main.addLayout(bottom)
        h.addLayout(main, 1)

        def mouse_press(e, cid=cand_id):
            if e.button() == Qt.MouseButton.LeftButton:
                self._on_candidate_clicked(cid)
        card.mousePressEvent = mouse_press

        return card

    # =====================================================
    # ACTIONS
    # =====================================================
    def _on_candidate_clicked(self, candidate_id_or_dict):
        if isinstance(candidate_id_or_dict, dict):
            candidate_id = (
                candidate_id_or_dict.get("candidate_id")
                or candidate_id_or_dict.get("id")
            )
        else:
            candidate_id = candidate_id_or_dict

        if not candidate_id:
            QMessageBox.warning(self, "Erreur", "Impossible d'identifier le candidat.")
            return

        candidate_id = str(candidate_id)

        try:
            candidate_data = self.recruitment_svc.get_candidate_details(candidate_id)
            if not candidate_data:
                QMessageBox.warning(self, "Introuvable",
                                    "Ce candidat n'existe plus dans le systeme.")
                return
            dialog = CandidateDialog(candidate_data, self)
            dialog.exec()
        except Exception as e:
            print(f"[JobOfferDetailPage] Erreur fiche candidat: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir la fiche :\n{e}")

    # =====================================================
    # HELPERS
    # =====================================================
    def _show_error(self, message: str):
        error_lbl = QLabel(f"❌ {message}")
        error_lbl.setStyleSheet("""
            font-size: 12pt; color: #C0392B;
            background: transparent; padding: 40px;
        """)
        error_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(error_lbl)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())