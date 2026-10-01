"""Titre de section avec badge optionnel.

Utilisation :
    st = SectionTitle("Alertes & Activites", badge_text="3 situations", badge_variant="danger")
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from app.ui.widgets.badge import Badge


class SectionTitle(QWidget):
    def __init__(
        self,
        title: str,
        badge_text: str = "",
        badge_variant: str = "danger",
        parent=None,
    ):
        super().__init__(parent)
        h = QHBoxLayout(self)
        h.setContentsMargins(0, 12, 0, 0)
        h.setSpacing(12)

        t = QLabel(title)
        t.setObjectName("sectionTitle")
        h.addWidget(t)

        if badge_text:
            h.addWidget(Badge(badge_text, variant=badge_variant))

        h.addStretch()