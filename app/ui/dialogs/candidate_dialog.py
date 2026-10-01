"""Dialogue de detail d'un candidat (fiche complete).

⚠️ Toutes les donnees affichees viennent UNIQUEMENT de la base de donnees.
    Les champs manquants affichent "—" au lieu de valeurs par defaut inventees.
"""

from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QScrollArea, QFrame, QLabel, QPushButton,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal

from app.services.audit_service import AuditService


# =====================================================
# HELPERS
# =====================================================
def fmt_date(value, fmt="%d/%m/%Y"):
    """Formate une date en toute securite."""
    if not value:
        return "—"
    if hasattr(value, "strftime"):
        return value.strftime(fmt)
    return str(value)


def safe_str(value, default="—"):
    """Retourne une string sure, ou le defaut si vide."""
    if value is None or value == "":
        return default
    return str(value)


def val_or_dash(value, default="—"):
    """Retourne la valeur ou '—'."""
    if value is None or value == "" or value == 0:
        return default
    return value


# =====================================================
# AVATAR
# =====================================================
class BigAvatar(QLabel):
    def __init__(self, first_name: str, last_name: str, size: int = 80):
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


# =====================================================
# SCORE RING
# =====================================================
class BigScoreRing(QLabel):
    def __init__(self, score: int, size: int = 90):
        super().__init__()
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText(f"{score}%")

        if score >= 90:
            bg = "#0D7A6A"
        elif score >= 75:
            bg = "#F39C12"
        else:
            bg = "#94A3B8"

        self.setStyleSheet(f"""
            background-color: {bg};
            color: #FFFFFF;
            border-radius: {size // 2}px;
            font-size: 20pt;
            font-weight: 800;
            border: 4px solid #E8F5F1;
        """)


# =====================================================
# CARTE INFO (petit bloc)
# =====================================================
class InfoTile(QFrame):
    def __init__(self, label: str, value: str, color: str = "#0F1E2E"):
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
            font-size: 7.5pt; color: #7A8B9C; font-weight: 700;
            letter-spacing: 0.5px; background: transparent; border: none;
        """)
        v.addWidget(lbl)

        val = QLabel(value)
        val.setStyleSheet(f"""
            font-size: 11pt; font-weight: 700; color: {color};
            background: transparent; border: none;
        """)
        val.setWordWrap(True)
        v.addWidget(val)


# =====================================================
# DIALOGUE
# =====================================================
class CandidateDialog(QDialog):
    """Fiche candidat complete - donnees STRICTEMENT issues de la base."""

    candidate_updated = pyqtSignal(str)
    interview_requested = pyqtSignal(str)

    def __init__(self, candidate_data: dict, parent=None):
        super().__init__(parent)
        self.data = candidate_data or {}
        self.candidate_id = str(self.data.get("id", ""))

        # DEBUG : affiche les cles disponibles
        print(f"\n[CandidateDialog] ========== DONNEES RECUES ==========")
        print(f"[CandidateDialog] Cles : {list(self.data.keys())}")
        for key in list(self.data.keys())[:20]:
            val = self.data.get(key)
            val_str = str(val)[:60] if val is not None else "None"
            print(f"[CandidateDialog]   {key} = {val_str}")

        # Titre
        full_name = f"{self.data.get('first_name', '')} {self.data.get('last_name', '')}".strip()
        self.setWindowTitle(f"Détail candidat — {full_name or 'Inconnu'}")
        self.setMinimumSize(820, 800)
        self.setStyleSheet("QDialog { background-color: #F4F6F9; }")

        self._setup_ui()

    # =====================================================
    # UI PRINCIPALE
    # =====================================================
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_header())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: #F4F6F9; border: none; }")

        inner = QWidget()
        inner.setStyleSheet("background-color: #F4F6F9;")
        scroll.setWidget(inner)
        layout.addWidget(scroll, 1)

        body = QVBoxLayout(inner)
        body.setContentsMargins(28, 24, 28, 24)
        body.setSpacing(16)

        body.addWidget(self._build_identity_card())
        body.addWidget(self._build_quick_stats())
        body.addWidget(self._build_skills_card())
        body.addWidget(self._build_summary_card())
        body.addWidget(self._build_application_card())
        body.addWidget(self._build_timeline_card())
        body.addStretch()

        layout.addWidget(self._build_footer())

    # =====================================================
    # HEADER
    # =====================================================
    def _build_header(self):
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-bottom: 1px solid #E4E9EF;
            }
        """)
        h = QHBoxLayout(header)
        h.setContentsMargins(28, 18, 28, 18)
        h.setSpacing(16)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        t = QLabel("Fiche candidat")
        t.setStyleSheet("""
            font-size: 15pt; font-weight: 800; color: #0F1E2E;
            background: transparent; border: none;
        """)
        title_col.addWidget(t)

        # Badge de statut (depuis la base uniquement)
        status = self.data.get("status", "")
        if status:
            status_map = {
                "recu": ("Reçu", "#EFF6FF", "#2E86DE"),
                "preselectionne": ("Présélectionné", "#E8F5F1", "#0D7A6A"),
                "entretien": ("Entretien planifié", "#FEF3C7", "#B45309"),
                "embauche": ("Embauché", "#E8F5F1", "#0D7A6A"),
                "refuse": ("Refusé", "#FEE2E2", "#C0392B"),
            }
            s_txt, s_bg, s_fg = status_map.get(
                status.lower(),
                (status.capitalize(), "#F1F5F9", "#64748B")
            )

            status_badge = QLabel(f"● {s_txt}")
            status_badge.setStyleSheet(f"""
                background-color: {s_bg};
                color: {s_fg};
                padding: 3px 12px;
                border-radius: 10px;
                font-size: 8.5pt;
                font-weight: 700;
                border: none;
            """)
            title_col.addWidget(status_badge, 0, Qt.AlignmentFlag.AlignLeft)

        h.addLayout(title_col, 1)

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(32, 32)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #7A8B9C;
                border: none;
                border-radius: 6px;
                font-size: 14pt;
            }
            QPushButton:hover {
                background-color: #F4F6F9;
                color: #0F1E2E;
            }
        """)
        btn_close.clicked.connect(self.reject)
        h.addWidget(btn_close, 0, Qt.AlignmentFlag.AlignTop)

        return header

    # =====================================================
    # CARTE IDENTITE
    # =====================================================
    def _build_identity_card(self):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
            }
        """)
        v = QVBoxLayout(card)
        v.setContentsMargins(24, 22, 24, 22)
        v.setSpacing(18)

        # Ligne 1 : Avatar + Nom/Poste + Score
        top = QHBoxLayout()
        top.setSpacing(20)

        # Avatar
        avatar = BigAvatar(
            self.data.get("first_name", ""),
            self.data.get("last_name", ""),
            size=80,
        )
        top.addWidget(avatar, 0, Qt.AlignmentFlag.AlignTop)

        # Infos
        info_col = QVBoxLayout()
        info_col.setSpacing(6)

        # Nom (depuis la base)
        full_name = f"{self.data.get('first_name', '')} {self.data.get('last_name', '')}".strip()
        name_lbl = QLabel(full_name if full_name else "—")
        name_lbl.setStyleSheet("""
            font-size: 20pt; font-weight: 800; color: #0F1E2E;
            background: transparent; border: none;
        """)
        info_col.addWidget(name_lbl)

        # Poste (depuis la base, pas de fallback)
        title = self.data.get("current_title")
        if title:
            title_lbl = QLabel(str(title))
            title_lbl.setStyleSheet("""
                font-size: 11pt; color: #5A6B7D;
                background: transparent; border: none;
            """)
            info_col.addWidget(title_lbl)

        # Années d'expérience (depuis la base uniquement)
        years = self.data.get("years_experience")
        if years is not None and years > 0:
            exp_lbl = QLabel(f"{years} ans d'expérience")
            exp_lbl.setStyleSheet("""
                font-size: 9.5pt; color: #0D7A6A; font-weight: 700;
                background: transparent; border: none;
            """)
            info_col.addWidget(exp_lbl)

        top.addLayout(info_col, 1)

        # Score (depuis la base)
        score = self.data.get("match_score")
        if score is not None:
            try:
                score_int = int(float(score))
            except (ValueError, TypeError):
                score_int = 0

            score_col = QVBoxLayout()
            score_col.setSpacing(4)
            score_col.setAlignment(Qt.AlignmentFlag.AlignCenter)

            score_ring = BigScoreRing(score_int, size=90)
            score_col.addWidget(score_ring, 0, Qt.AlignmentFlag.AlignCenter)

            match_lbl = QLabel("MATCH IA")
            match_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            match_lbl.setStyleSheet("""
                font-size: 8pt; color: #7A8B9C; font-weight: 700;
                letter-spacing: 1px; background: transparent; border: none;
            """)
            score_col.addWidget(match_lbl)

            top.addLayout(score_col)

        v.addLayout(top)

        # Ligne 2 : Contacts (grille)
        contacts_grid = QGridLayout()
        contacts_grid.setSpacing(10)

        # Seulement les contacts présents dans la base
        contacts = []
        if self.data.get("email"):
            contacts.append(("EMAIL", str(self.data["email"])))
        if self.data.get("phone"):
            contacts.append(("TÉLÉPHONE", str(self.data["phone"])))
        if self.data.get("city"):
            contacts.append(("VILLE", str(self.data["city"])))

        # Ajouter les tuiles
        for idx, (label, value) in enumerate(contacts[:3]):
            contacts_grid.addWidget(InfoTile(label, value), 0, idx)

        # Si aucun contact, afficher un message
        if not contacts:
            no_contact = QLabel("Aucune coordonnée renseignée")
            no_contact.setStyleSheet("""
                font-size: 9pt; color: #94A3B8; font-style: italic;
                background: transparent; border: none;
            """)
            contacts_grid.addWidget(no_contact, 0, 0, 1, 3)

        v.addLayout(contacts_grid)

        return card

    # =====================================================
    # QUICK STATS
    # =====================================================
    def _build_quick_stats(self):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
            }
        """)
        h = QHBoxLayout(card)
        h.setContentsMargins(24, 18, 24, 18)
        h.setSpacing(20)

        # Stats STRICTEMENT issues de la base
        stats = []

        # Score
        score = self.data.get("match_score")
        if score is not None:
            try:
                stats.append(("SCORE MATCH", f"{int(float(score))}%", "#0D7A6A"))
            except (ValueError, TypeError):
                pass

        # Années d'expérience
        years = self.data.get("years_experience")
        if years is not None:
            stats.append(("EXPÉRIENCE", f"{years} ans", "#2E86DE"))

        # Nombre de compétences
        skills = self.data.get("skills") or []
        if skills:
            stats.append(("COMPÉTENCES", str(len(skills)), "#7C3AED"))

        # Statut (depuis la base)
        status = self.data.get("status")
        if status:
            stats.append(("STATUT", status.capitalize(), "#0D7A6A"))

        # Si aucune stat, ne pas afficher la carte
        if not stats:
            return self._build_empty_card(
                "Informations",
                "Aucune statistique disponible"
            )

        for i, (label, value, color) in enumerate(stats):
            v = QVBoxLayout()
            v.setSpacing(2)
            v.setAlignment(Qt.AlignmentFlag.AlignCenter)

            val_lbl = QLabel(value)
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            val_lbl.setStyleSheet(f"""
                font-size: 16pt; font-weight: 800; color: {color};
                background: transparent; border: none;
            """)
            v.addWidget(val_lbl)

            lbl = QLabel(label)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("""
                font-size: 7.5pt; color: #7A8B9C; font-weight: 700;
                letter-spacing: 0.8px; background: transparent; border: none;
            """)
            v.addWidget(lbl)

            h.addLayout(v, 1)

            if i < len(stats) - 1:
                sep = QFrame()
                sep.setFixedWidth(1)
                sep.setStyleSheet("background-color: #EEF2F6; border: none;")
                h.addWidget(sep)

        return card

    # =====================================================
    # COMPETENCES
    # =====================================================
    def _build_skills_card(self):
        skills = self.data.get("skills") or []
        if not skills:
            return self._build_empty_card(
                "Compétences",
                "Aucune compétence renseignée"
            )

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
            }
        """)
        v = QVBoxLayout(card)
        v.setContentsMargins(24, 20, 24, 20)
        v.setSpacing(14)

        title_row = QHBoxLayout()
        title = QLabel("Compétences")
        title.setStyleSheet("""
            font-size: 12pt; font-weight: 700; color: #0F1E2E;
            background: transparent; border: none;
        """)
        title_row.addWidget(title)
        title_row.addStretch()

        count_badge = QLabel(f"{len(skills)} compétence{'s' if len(skills) > 1 else ''}")
        count_badge.setStyleSheet("""
            background-color: #E8F5F1;
            color: #0D7A6A;
            padding: 3px 10px;
            border-radius: 10px;
            font-size: 8.5pt;
            font-weight: 700;
            border: none;
        """)
        title_row.addWidget(count_badge)
        v.addLayout(title_row)

        chips_container = QWidget()
        chips_container.setStyleSheet("background: transparent;")
        chips_layout = QGridLayout(chips_container)
        chips_layout.setContentsMargins(0, 0, 0, 0)
        chips_layout.setSpacing(6)

        MAX_COLS = 4
        for idx, skill in enumerate(skills):
            chip = QLabel(str(skill))
            chip.setStyleSheet("""
                background-color: #E8F5F1;
                color: #0D7A6A;
                padding: 6px 14px;
                border-radius: 12px;
                font-size: 9pt;
                font-weight: 600;
                border: none;
            """)
            chip.setAlignment(Qt.AlignmentFlag.AlignCenter)

            row_idx = idx // MAX_COLS
            col_idx = idx % MAX_COLS
            chips_layout.addWidget(chip, row_idx, col_idx)

        chips_layout.setColumnStretch(MAX_COLS, 1)
        v.addWidget(chips_container)

        return card

    # =====================================================
    # SYNTHESE IA
    # =====================================================
    def _build_summary_card(self):
        # Depuis la base uniquement (ai_summary)
        summary = self.data.get("ai_summary")

        if not summary:
            return self._build_empty_card(
                "Synthèse IA",
                "Aucune synthèse générée par l'IA"
            )

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
            }
        """)
        v = QVBoxLayout(card)
        v.setContentsMargins(24, 20, 24, 20)
        v.setSpacing(12)

        title = QLabel("Synthèse IA")
        title.setStyleSheet("""
            font-size: 12pt; font-weight: 700; color: #0F1E2E;
            background: transparent; border: none;
        """)
        v.addWidget(title)

        box = QFrame()
        box.setStyleSheet("""
            QFrame {
                background-color: #F0FDF4;
                border-radius: 10px;
                border-left: 4px solid #0D7A6A;
            }
        """)
        bv = QVBoxLayout(box)
        bv.setContentsMargins(16, 14, 16, 14)

        summary_lbl = QLabel(str(summary))
        summary_lbl.setStyleSheet("""
            font-size: 10pt; color: #0F1E2E;
            background: transparent; border: none;
        """)
        summary_lbl.setWordWrap(True)
        bv.addWidget(summary_lbl)

        v.addWidget(box)
        return card

    # =====================================================
    # CANDIDATURE
    # =====================================================
    def _build_application_card(self):
        # Applications depuis la base
        applications = self.data.get("applications") or []
        app = applications[0] if applications else {}

        # Titre offre - STRICTEMENT depuis la base
        offer_title = (
            app.get("job_title")
            or app.get("offer_title")
            or self.data.get("offer_title")
        )

        # Departement
        dept = app.get("department") or self.data.get("department")

        # Type de contrat - seulement si en base
        contract = app.get("contract_type") or self.data.get("contract_type")

        # Lieu
        location = (
            app.get("location")
            or app.get("city")
            or self.data.get("city")
        )

        # Date
        applied_at = (
            app.get("applied_at")
            or app.get("created_at")
            or self.data.get("created_at")
        )

        # Si aucune donnee de candidature, ne pas afficher
        if not any([offer_title, dept, contract, location, applied_at]):
            return self._build_empty_card(
                "Candidature",
                "Aucune candidature enregistrée"
            )

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
            }
        """)
        v = QVBoxLayout(card)
        v.setContentsMargins(24, 20, 24, 20)
        v.setSpacing(12)

        title = QLabel("Candidature")
        title.setStyleSheet("""
            font-size: 12pt; font-weight: 700; color: #0F1E2E;
            background: transparent; border: none;
        """)
        v.addWidget(title)

        # Titre de l'offre
        if offer_title:
            offer_lbl = QLabel(str(offer_title))
            offer_lbl.setStyleSheet("""
                font-size: 13pt; font-weight: 700; color: #0D7A6A;
                background: transparent; border: none;
            """)
            offer_lbl.setWordWrap(True)
            v.addWidget(offer_lbl)

        # Tags
        tags_row = QHBoxLayout()
        tags_row.setSpacing(8)

        if dept:
            dept_badge = QLabel(str(dept))
            dept_badge.setStyleSheet("""
                background-color: #EFF6FF; color: #2E86DE;
                padding: 4px 12px; border-radius: 10px;
                font-size: 8.5pt; font-weight: 600; border: none;
            """)
            tags_row.addWidget(dept_badge)

        if contract:
            contract_badge = QLabel(str(contract))
            contract_badge.setStyleSheet("""
                background-color: #F1F5F9; color: #475569;
                padding: 4px 12px; border-radius: 10px;
                font-size: 8.5pt; font-weight: 600; border: none;
            """)
            tags_row.addWidget(contract_badge)

        if location:
            loc_badge = QLabel(str(location))
            loc_badge.setStyleSheet("""
                background-color: #F1F5F9; color: #475569;
                padding: 4px 12px; border-radius: 10px;
                font-size: 8.5pt; font-weight: 600; border: none;
            """)
            tags_row.addWidget(loc_badge)

        tags_row.addStretch()
        v.addLayout(tags_row)

        # Date
        if applied_at:
            date_lbl = QLabel(f"Candidature déposée le {fmt_date(applied_at)}")
            date_lbl.setStyleSheet("""
                font-size: 9pt; color: #94A3B8; font-style: italic;
                background: transparent; border: none;
            """)
            v.addWidget(date_lbl)

        return card

    # =====================================================
    # TIMELINE (basée sur le statut réel en base)
    # =====================================================
    def _build_timeline_card(self):
        # Statut depuis la base uniquement
        status = self.data.get("status", "").lower()

        if not status:
            return self._build_empty_card(
                "Progression",
                "Aucun statut renseigné"
            )

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
            }
        """)
        v = QVBoxLayout(card)
        v.setContentsMargins(24, 20, 24, 20)
        v.setSpacing(14)

        title = QLabel("Progression du recrutement")
        title.setStyleSheet("""
            font-size: 12pt; font-weight: 700; color: #0F1E2E;
            background: transparent; border: none;
        """)
        v.addWidget(title)

        # Étapes standards du processus
        stages = [
            ("recu", "Candidature reçue"),
            ("preselectionne", "Présélection IA"),
            ("entretien", "Entretien"),
            ("embauche", "Décision finale"),
        ]

        status_order = {s[0]: i for i, s in enumerate(stages)}
        current_idx = status_order.get(status, 0)

        timeline_row = QHBoxLayout()
        timeline_row.setSpacing(0)

        for i, (key, label) in enumerate(stages):
            dot_col = QVBoxLayout()
            dot_col.setSpacing(6)
            dot_col.setAlignment(Qt.AlignmentFlag.AlignCenter)

            if i < current_idx:
                dot = QLabel("✓")
                dot.setFixedSize(28, 28)
                dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
                dot.setStyleSheet("""
                    background-color: #0D7A6A;
                    color: #FFFFFF;
                    border-radius: 14px;
                    font-size: 11pt;
                    font-weight: 700;
                    border: none;
                """)
            elif i == current_idx:
                dot = QLabel("●")
                dot.setFixedSize(28, 28)
                dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
                dot.setStyleSheet("""
                    background-color: #F39C12;
                    color: #FFFFFF;
                    border-radius: 14px;
                    font-size: 11pt;
                    font-weight: 700;
                    border: none;
                """)
            else:
                dot = QLabel("○")
                dot.setFixedSize(28, 28)
                dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
                dot.setStyleSheet("""
                    background-color: #F1F5F9;
                    color: #94A3B8;
                    border-radius: 14px;
                    font-size: 11pt;
                    font-weight: 700;
                    border: none;
                """)
            dot_col.addWidget(dot, 0, Qt.AlignmentFlag.AlignCenter)

            lbl = QLabel(label)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(f"""
                font-size: 8pt; font-weight: 600;
                color: {'#0D7A6A' if i <= current_idx else '#94A3B8'};
                background: transparent; border: none;
            """)
            dot_col.addWidget(lbl)

            timeline_row.addLayout(dot_col, 1)

            if i < len(stages) - 1:
                connector = QFrame()
                connector.setFixedHeight(2)
                connector.setStyleSheet(f"""
                    background-color: {'#0D7A6A' if i < current_idx else '#E4E9EF'};
                    border: none;
                    margin-top: 13px;
                """)
                timeline_row.addWidget(connector, 1)

        v.addLayout(timeline_row)
        return card

    # =====================================================
    # CARTE VIDE
    # =====================================================
    def _build_empty_card(self, title: str, message: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
            }
        """)
        v = QVBoxLayout(card)
        v.setContentsMargins(24, 20, 24, 20)
        v.setSpacing(8)

        t = QLabel(title)
        t.setStyleSheet("""
            font-size: 12pt; font-weight: 700; color: #0F1E2E;
            background: transparent; border: none;
        """)
        v.addWidget(t)

        msg = QLabel(message)
        msg.setStyleSheet("""
            font-size: 9.5pt; color: #94A3B8; font-style: italic;
            background: transparent; border: none;
        """)
        v.addWidget(msg)

        return card

    # =====================================================
    # FOOTER
    # =====================================================
    def _build_footer(self):
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-top: 1px solid #E4E9EF;
            }
        """)
        h = QHBoxLayout(footer)
        h.setContentsMargins(28, 16, 28, 16)
        h.setSpacing(10)

        # Télécharger CV (seulement si en base)
        cv_url = self.data.get("cv_file_url")
        if cv_url:
            btn_download = QPushButton("Télécharger le CV")
            btn_download.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_download.setMinimumHeight(40)
            btn_download.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    color: #5A6B7D;
                    border: 1px solid #E4E9EF;
                    border-radius: 6px;
                    padding: 10px 18px;
                    font-size: 9.5pt;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #F4F6F9;
                    border-color: #94A3B8;
                }
            """)
            btn_download.clicked.connect(self._on_download_cv)
            h.addWidget(btn_download)

        h.addStretch()

        btn_close = QPushButton("Fermer")
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setMinimumHeight(40)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #5A6B7D;
                border: 1px solid #E4E9EF;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 9.5pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #F4F6F9;
            }
        """)
        btn_close.clicked.connect(self.reject)
        h.addWidget(btn_close)

        # Planifier entretien (seulement si statut permet)
        status = self.data.get("status", "").lower()
        if status in ("preselectionne", "recu", "entretien"):
            btn_interview = QPushButton("Planifier un entretien")
            btn_interview.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_interview.setMinimumHeight(40)
            btn_interview.setStyleSheet("""
                QPushButton {
                    background-color: #0D7A6A;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 6px;
                    padding: 10px 24px;
                    font-size: 9.5pt;
                    font-weight: 700;
                }
                QPushButton:hover { background-color: #0A6456; }
            """)
            btn_interview.clicked.connect(self._on_schedule_interview)
            h.addWidget(btn_interview)

        return footer

    # =====================================================
    # ACTIONS
    # =====================================================
    def _on_download_cv(self):
        cv_url = self.data.get("cv_file_url")
        if not cv_url:
            return

        try:
            from pathlib import Path
            cv_path = Path(str(cv_url))
            if not cv_path.exists():
                QMessageBox.warning(
                    self, "Introuvable",
                    f"Le fichier n'existe pas :\n{cv_url}"
                )
                return

            import subprocess, sys, os
            if sys.platform == "win32":
                os.startfile(cv_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", cv_path])
            else:
                subprocess.Popen(["xdg-open", cv_path])

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le CV :\n{e}")

    def _on_schedule_interview(self):
        """Affiche un message - fonctionnalite a implementer cote service."""
        QMessageBox.information(
            self, "Planifier un entretien",
            "Fonctionnalité à venir : planification d'entretien.\n\n"
            "Elle nécessite une table 'interviews' dans la base."
        )