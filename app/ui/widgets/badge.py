"""Badge colore reutilisable.

Utilisation :
    b = Badge("Prioritaire", variant="danger")
    b = Badge("Match 96%", variant="match")
"""
from PyQt6.QtWidgets import QLabel


VARIANTS = {
    "success": "badgeSuccess",
    "danger": "badgeDanger",
    "warning": "badgeWarning",
    "info": "badgeInfo",
    "match": "badgeMatch",
    "priority": "badgePriority",
}


class Badge(QLabel):
    def __init__(self, text: str, variant: str = "info", parent=None):
        super().__init__(text, parent)
        self.setObjectName(VARIANTS.get(variant, "badgeInfo"))
        self.setAlignment(
            __import__("PyQt6.QtCore", fromlist=["Qt"]).Qt.AlignmentFlag.AlignCenter
        )