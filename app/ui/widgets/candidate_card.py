"""Widget CandidateCard - Carte pour afficher un candidat.

Affiche les informations d'un candidat avec son score de matching :
- Nom et poste actuel
- Compétences techniques
- Score de matching IA avec étoiles
- Résumé IA
- Localisation et disponibilité
"""
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from app.ui.widgets import Badge


class CandidateCard(QFrame):
    """Carte cliquable pour un candidat."""

    clicked = pyqtSignal(str)  # Signal émis avec l'ID du candidat

    def __init__(self, candidate_data: dict, parent=None):
        super().__init__(parent)
        self.candidate_data = candidate_data
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(100)

        # Style de la carte
        score = candidate_data.get('match_score', 0)
        border_color = "#0D7A6A" if score >= 80 else "#F39C12" if score >= 60 else "#C0392B"

        self.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
                border-left: 4px solid {border_color};
            }}
            QFrame:hover {{
                border: 2px solid {border_color};
                border-left: 4px solid {border_color};
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # ===== Colonne gauche : Score de matching + étoiles =====
        score_col = QVBoxLayout()
        score_col.setSpacing(2)

        # Score en cercle
        score_circle = QLabel(f"{int(score)}%")
        score_circle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_circle.setFixedSize(45, 45)
        score_circle.setStyleSheet(f"""
            background-color: {border_color};
            color: #FFFFFF;
            border-radius: 22px;
            font-size: 11pt;
            font-weight: 800;
        """)
        score_col.addWidget(score_circle, 0, Qt.AlignmentFlag.AlignCenter)

        # Étoiles de notation
        stars = self._get_stars(score)
        stars_lbl = QLabel(stars)
        stars_lbl.setStyleSheet(
            "font-size: 9pt; color: #F39C12; background: transparent;"
        )
        stars_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_col.addWidget(stars_lbl)

        layout.addLayout(score_col)

        # ===== Colonne centre : Informations du candidat =====
        info_col = QVBoxLayout()
        info_col.setSpacing(2)

        # Nom + étoiles
        name_row = QHBoxLayout()
        name_row.setSpacing(6)

        name_lbl = QLabel(f"<b>{candidate_data.get('name', '—')}</b>")
        name_lbl.setStyleSheet(
            "font-size: 10pt; color: #0F1E2E; background: transparent;"
        )
        name_row.addWidget(name_lbl)

        info_col.addLayout(name_row)

        # Poste actuel
        title_lbl = QLabel(candidate_data.get('current_title', '—'))
        title_lbl.setStyleSheet(
            "font-size: 8pt; color: #5A6B7D; background: transparent;"
        )
        title_lbl.setWordWrap(True)
        info_col.addWidget(title_lbl)

        # Compétences (limitées)
        skills = candidate_data.get('skills', [])
        if skills:
            skills_text = ", ".join(skills[:3])  # Afficher max 3 compétences
            if len(skills) > 3:
                skills_text += f" (+{len(skills) - 3})"
            skills_lbl = QLabel(f"🎯 {skills_text}")
            skills_lbl.setStyleSheet(
                "font-size: 8pt; color: #7A8B9C; background: transparent;"
            )
            skills_lbl.setWordWrap(True)
            info_col.addWidget(skills_lbl)

        # Résumé IA (si disponible)
        ai_summary = candidate_data.get('ai_summary', '')
        if ai_summary:
            summary_lbl = QLabel(f"📝 {ai_summary[:60]}...")
            summary_lbl.setStyleSheet(
                "font-size: 7pt; color: #7A8B9C; background: transparent;"
            )
            summary_lbl.setWordWrap(True)
            info_col.addWidget(summary_lbl)

        layout.addLayout(info_col, 2)

        # ===== Colonne droite : Disponibilité et action =====
        right_col = QVBoxLayout()
        right_col.setSpacing(4)

        # Disponibilité
        availability = "Disponible maintenant"  # Valeur par défaut
        avail_lbl = QLabel(f"🟢 {availability}")
        avail_lbl.setStyleSheet(
            "font-size: 8pt; color: #0D7A6A; background: transparent;"
        )
        right_col.addWidget(avail_lbl, 0, Qt.AlignmentFlag.AlignRight)

        # Badge offre
        offer_title = candidate_data.get('offer_title', '—')
        if offer_title and offer_title != "—":
            # Tronquer si trop long
            display_offer = offer_title[:25] + "..." if len(offer_title) > 25 else offer_title
            offer_badge = Badge(display_offer, variant="info")
            right_col.addWidget(offer_badge, 0, Qt.AlignmentFlag.AlignRight)

        # Bouton voir profil
        btn_view = QPushButton("Voir ›")
        btn_view.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_view.setFixedWidth(50)
        btn_view.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #0D7A6A;
                border: none;
                font-size: 9pt;
                font-weight: 700;
                padding: 0;
            }
            QPushButton:hover {
                color: #0A6456;
                text-decoration: underline;
            }
        """)
        btn_view.clicked.connect(lambda: self.clicked.emit(candidate_data['candidate_id']))
        right_col.addWidget(btn_view, 0, Qt.AlignmentFlag.AlignRight)

        layout.addLayout(right_col)

    def _get_stars(self, score: float) -> str:
        """Retourne les étoiles en fonction du score."""
        if score >= 95:
            return "★★★★★"
        elif score >= 85:
            return "★★★★☆"
        elif score >= 75:
            return "★★★☆☆"
        elif score >= 65:
            return "★★☆☆☆"
        else:
            return "★☆☆☆☆"

    def mousePressEvent(self, event):
        """Émet le signal clicked lors du clic sur la carte."""
        self.clicked.emit(self.candidate_data['candidate_id'])
        super().mousePressEvent(event)
