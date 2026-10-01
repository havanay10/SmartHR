"""Widget JobOfferRow - Ligne pour afficher une offre d'emploi.

Affiche les informations clés d'une offre avec ses statistiques :
- Titre et département
- Statut et priorité
- Nombre de candidats et pré-sélectionnés
- Score moyen de matching
- 2 boutons d'action : Voir les candidats, Voir détail poste
"""
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from app.ui.widgets import Badge


class JobOfferRow(QFrame):
    """Ligne cliquable pour une offre d'emploi."""

    clicked = pyqtSignal(str)  # Signal émis avec l'ID de l'offre
    view_candidates = pyqtSignal(str)  # Signal pour voir les candidats
    view_details = pyqtSignal(str)  # Signal pour voir les détails de l'offre

    def __init__(self, offer_data: dict, is_active: bool = False, parent=None):
        super().__init__(parent)
        self.offer_data = offer_data
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(70)

        # Style de la ligne
        if is_active:
            self.setStyleSheet("""
                QFrame {
                    background-color: #F8FAFC;
                    border-radius: 12px;
                    border: 2px solid #0D7A6A;
                    border-left: 4px solid #0D7A6A;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #FFFFFF;
                    border-radius: 12px;
                    border: 1px solid #E4E9EF;
                    border-left: 4px solid transparent;
                }
                QFrame:hover {
                    border: 2px solid #0D7A6A;
                    border-left: 4px solid #0D7A6A;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
                }
            """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # ===== Colonne gauche : Informations principales =====
        left_col = QVBoxLayout()
        left_col.setSpacing(2)

        # Titre de l'offre
        title_lbl = QLabel(f"<b>{offer_data.get('title', '—')}</b>")
        title_lbl.setStyleSheet(
            "font-size: 10pt; color: #0F1E2E; background: transparent;"
        )
        title_lbl.setWordWrap(True)
        left_col.addWidget(title_lbl)

        # Département + Badges statut/priorité
        info_row = QHBoxLayout()
        info_row.setSpacing(6)

        dept_lbl = QLabel(offer_data.get('department', '—'))
        dept_lbl.setStyleSheet(
            "font-size: 8pt; color: #5A6B7D; background: transparent;"
        )
        info_row.addWidget(dept_lbl)

        # Badge statut
        status = offer_data.get('status', 'active')
        status_variant = "success" if status == "active" else "info"
        info_row.addWidget(Badge(status.capitalize(), variant=status_variant))

        # Badge priorité si prioritaire
        priority = offer_data.get('priority')
        if priority == "prioritaire":
            info_row.addWidget(Badge("Prioritaire", variant="danger"))

        info_row.addStretch()
        left_col.addLayout(info_row)

        layout.addLayout(left_col, 2)

        # ===== Colonne centre : Statistiques compactes =====
        stats_col = QVBoxLayout()
        stats_col.setSpacing(1)

        # Ligne statistiques : candidats + pré-sélectionnés + score
        stats_row = QHBoxLayout()
        stats_row.setSpacing(8)

        # Candidats
        total_candidates = offer_data.get('total_candidates', 0)
        candidates_lbl = QLabel(f"<b>{total_candidates}</b> candidats")
        candidates_lbl.setStyleSheet(
            "font-size: 8pt; color: #0F1E2E; background: transparent;"
        )
        stats_row.addWidget(candidates_lbl)

        # Pré-sélectionnés
        preselected = offer_data.get('preselected_count', 0)
        if preselected > 0:
            preselected_lbl = QLabel(f"<b>{preselected}</b> IA matchs")
            preselected_lbl.setStyleSheet(
                "font-size: 8pt; color: #0D7A6A; background: transparent;"
            )
            stats_row.addWidget(preselected_lbl)

        # Score moyen
        avg_score = offer_data.get('avg_match_score', 0)
        score_color = "#0D7A6A" if avg_score >= 80 else "#F39C12" if avg_score >= 60 else "#C0392B"
        score_lbl = QLabel(f"<span style='color:{score_color}; font-weight:700;'>{avg_score}%</span>")
        score_lbl.setStyleSheet(
            "font-size: 8pt; color: #7A8B9C; background: transparent;"
        )
        stats_row.addWidget(score_lbl)

        stats_row.addStretch()
        stats_col.addLayout(stats_row)

        layout.addLayout(stats_col, 1)

        # ===== Colonne droite : 2 boutons d'action =====
        right_col = QVBoxLayout()
        right_col.setSpacing(4)

        # Bouton 1 : Voir les candidats
        btn_candidates = QPushButton("Voir les candidats")
        btn_candidates.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_candidates.setFixedHeight(28)
        btn_candidates.setStyleSheet("""
            QPushButton {
                background-color: #0D7A6A;
                color: #FFFFFF;
                border: none;
                border-radius: 4px;
                font-size: 8pt;
                font-weight: 600;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #0A6456;
            }
        """)
        btn_candidates.clicked.connect(lambda: self.view_candidates.emit(offer_data['id']))
        right_col.addWidget(btn_candidates)

        # Bouton 2 : Voir détail poste
        btn_details = QPushButton("Voir détail poste")
        btn_details.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_details.setFixedHeight(28)
        btn_details.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #0D7A6A;
                border: 1px solid #0D7A6A;
                border-radius: 4px;
                font-size: 8pt;
                font-weight: 600;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #E8F5F1;
            }
        """)
        btn_details.clicked.connect(lambda: self.view_details.emit(offer_data['id']))
        right_col.addWidget(btn_details)

        layout.addLayout(right_col)

    def mousePressEvent(self, event):
        """Émet le signal clicked lors du clic sur la ligne."""
        self.clicked.emit(self.offer_data['id'])
        super().mousePressEvent(event)
