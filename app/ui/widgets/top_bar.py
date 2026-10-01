"""Top bar : logo + date + notifications + avatar.

Reproduit fidèlement la barre du haut de la maquette
"Executive Slate & Deep Teal" :

    [ logo  SmartRH Suite   Lundi 21 Septembre 2026 ]   ...   [ (5)  (avatar) ]

Icones acceptees : emoji, chemin, nom de fichier (voir app.ui.icons).
"""
from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QWidget

from app.ui.icons import BASE_DIR, IconLabel


MOIS_FR = [
    "", "Janvier", "Fevrier", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Aout", "Septembre", "Octobre", "Novembre", "Decembre",
]
JOURS_FR = [
    "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche",
]

# Logo affiché en haut a gauche, a la place du nom du logiciel en texte
LOGO_PATH = BASE_DIR / "assets" / "fonts" / "logoIspm.png"

# Taille cible du logo dans la barre (hauteur en pixels, largeur proportionnelle)
LOGO_HEIGHT = 50


class NotificationBell(QWidget):
    """Cloche de notification avec pastille de comptage (badge tertiary)
    posee en haut a droite de l'icone, comme dans la maquette.
    """

    def __init__(self, icon_name="notifications", fallback="🔔",
                 count=0, size=22, parent=None):
        super().__init__(parent)
        self.setFixedSize(size + 10, size + 10)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._icon = IconLabel(
            icon_name,
            fallback=fallback,
            size=size,
            object_name="topBarBellIcon",
            parent=self,
        )
        self._icon.move(5, 5)

        self._badge = QLabel(str(count), self)
        self._badge.setObjectName("topBarBellBadge")
        self._badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._badge.setFixedSize(16, 16)
        self._badge.move(self.width() - 16, 0)
        self._badge.setStyleSheet(
            """
            QLabel#topBarBellBadge {{
                border-radius: 8px;
                font-size: 10px;
                font-weight: 600;
            }}
            """
        )
        self.set_count(count)

    def set_count(self, count: int):
        self._badge.setText(str(count))
        self._badge.setVisible(count > 0)


class Avatar(QLabel):
    """Medaillon rond teal avec icone/initiale blanche, comme dans
    la maquette (w-8 h-8 rounded-full bg-primary).
    """

    def __init__(self, icon_name="person", fallback="U", size=32, parent=None):
        super().__init__(parent)
        self.setObjectName("avatar")
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            f"""
            QLabel#avatar {{
                border-radius: {size // 2}px;
                font-weight: 600;
            }}
            """
        )

        from app.ui.icons import resolve_icon_path, svg_to_pixmap

        path = resolve_icon_path(icon_name)
        if path is not None:
            pixmap = svg_to_pixmap(path, size=int(size * 0.55))
            if not pixmap.isNull():
                self.setPixmap(pixmap)
                return

        self.setText((fallback or "U")[0].upper())


class TopBar(QFrame):
    def __init__(
        self,
        user_name: str = "Rakoto",
        software_name: str = "SmartRH Suite",
        notif_icon: str = "notifications",
        notif_fallback: str = "🔔",
        notif_count: int = 0,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("topBar")
        self.setFixedHeight(64)

        h = QHBoxLayout(self)
        h.setContentsMargins(24, 0, 24, 0)
        h.setSpacing(16)

        # --------------------------------------------------------
        # Bloc gauche : logo + nom du logiciel (image) + date
        # --------------------------------------------------------

        left = QWidget()
        left_layout = QHBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(12)

        logo = QLabel()
        logo.setObjectName("topBarLogo")
        # Fond explicitement transparent : sans ceci, un QLabel herite
        # souvent d'un fond blanc du style global de l'appli, ce qui
        # masque la transparence du PNG.
        logo.setStyleSheet("background: transparent; border: none;")
        logo.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        pixmap = QPixmap(str(LOGO_PATH))
        if not pixmap.isNull():
            pixmap = pixmap.scaledToHeight(
                LOGO_HEIGHT, Qt.TransformationMode.SmoothTransformation
            )
            logo.setPixmap(pixmap)
        else:
            # Repli si l'image est introuvable : on garde le nom en texte
            logo.setText(software_name)
            logo.setObjectName("topBarSoftwareName")
        left_layout.addWidget(logo)

        now = datetime.now()
        jour = JOURS_FR[now.weekday()]
        mois = MOIS_FR[now.month]
        date_txt = f"{jour} {now.day} {mois} {now.year}"
        date = QLabel(date_txt)
        date.setObjectName("topBarDate")
        left_layout.addWidget(date)

        h.addWidget(left)
        h.addStretch()

        # --------------------------------------------------------
        # Bloc droit : notifications + avatar
        # --------------------------------------------------------

        notif = NotificationBell(
            notif_icon,
            fallback=notif_fallback,
            count=notif_count,
        )
        h.addWidget(notif)

        initial = (user_name or "U")[0].upper()
        avatar = Avatar("person", fallback=initial, size=32)
        h.addWidget(avatar)