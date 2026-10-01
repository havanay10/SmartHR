"""Carte KPI reutilisable (avec support images).

Icone acceptee :
- emoji         : icon="👥"
- chemin image  : icon="assets/icons/user.png"
- nom image     : icon="user"  (cherche dans assets/icons/)
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from app.ui.icons import IconLabel, is_emoji, resolve_icon_path


ACCENT_TO_ICON_STYLE = {
    "green":  "iconCircleGreen",
    "red":    "iconCircleRed",
    "orange": "iconCircleOrange",
    "blue":   "iconCircleBlue",
    "purple": "iconSquarePurple",
    "gray":   "iconSquareGray",
}

# Fallback emoji selon l'accent (utilise si aucune image trouvee)
ACCENT_FALLBACK = {
    "green":  "📊",
    "red":    "⚠️",
    "orange": "📅",
    "blue":   "🎯",
    "purple": "🤖",
    "gray":   "📈",
}


class KpiCard(QFrame):
    def __init__(
        self,
        title: str,
        value: str,
        subtitle: str = "",
        icon: str = "",
        accent: str = "green",
        trend: str = "",
        trend_positive: bool = True,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("kpiCard")
        self.setProperty("accentColor", accent)
        self.setMinimumHeight(140)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(6)

        # ===== Ligne 1 : Titre + Icone carre arrondi =====
        top = QHBoxLayout()
        top.setSpacing(10)

        title_lbl = QLabel(title.upper())
        title_lbl.setObjectName("kpiTitle")
        title_lbl.setWordWrap(True)
        top.addWidget(title_lbl, 1)

        if icon:
            # Determine la source (emoji vs image)
            icon_style = ACCENT_TO_ICON_STYLE.get(accent, "iconCircleGreen")
            fallback = ACCENT_FALLBACK.get(accent, "•")

            if is_emoji(icon):
                # Emoji direct
                icon_lbl = IconLabel(icon, size=14, object_name=icon_style)
            else:
                # Nom d'icone : verifie si le PNG existe
                path = resolve_icon_path(icon)
                if path and path.exists():
                    # Image trouvee : on garde le fond pastel
                    icon_lbl = IconLabel(icon, fallback=fallback, size=20,
                                          object_name=icon_style)
                else:
                    # Image manquante : emoji dans le carre
                    icon_lbl = IconLabel(fallback, size=14, object_name=icon_style)

            icon_lbl.setFixedSize(40, 40)
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            top.addWidget(icon_lbl, 0, Qt.AlignmentFlag.AlignTop)

        layout.addLayout(top)

        # ===== Ligne 2 : Valeur + Trend =====
        mid = QHBoxLayout()
        mid.setSpacing(8)

        value_lbl = QLabel(value)
        value_lbl.setObjectName("kpiValueAlert" if accent == "red" else "kpiValue")
        mid.addWidget(value_lbl)

        if trend:
            color = "#0D7A6A" if trend_positive else "#C0392B"
            trend_lbl = QLabel(trend)
            trend_lbl.setStyleSheet(
                f"color: {color}; font-size: 10pt; font-weight: 700;"
            )
            mid.addWidget(trend_lbl)

        mid.addStretch()
        layout.addLayout(mid)

        # ===== Ligne 3 : Sous-titre =====
        if subtitle:
            sub_lbl = QLabel(subtitle)
            sub_lbl.setObjectName("kpiSubtitle")
            sub_lbl.setWordWrap(True)
            layout.addWidget(sub_lbl)

        layout.addStretch()