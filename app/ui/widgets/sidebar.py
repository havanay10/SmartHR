"""Widgets communs pour SmartRH (Sidebar, TopBar, etc.)."""

from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QIcon

from app.ui.icons import resolve_icon_path


# =====================================================
# HELPER : trouver la racine du projet
# =====================================================
def find_project_root() -> Path:
    """Remonte depuis __file__ jusqu'à trouver le dossier qui contient 'assets/'.

    Cette methode est robuste : elle fonctionne peu importe la profondeur
    du fichier dans l'arborescence du projet.
    """
    current = Path(__file__).resolve().parent

    for _ in range(6):  # Maximum 6 niveaux de remontee
        # Si on trouve le dossier assets/ OU le fichier main.py → c'est la racine
        if (current / "assets").exists() or (current / "main.py").exists():
            return current

        parent = current.parent
        if parent == current:  # Atteint la racine du disque → stop
            break
        current = parent

    # Fallback : 3 niveaux au-dessus (cas standard app/ui/widgets.py)
    return Path(__file__).resolve().parent.parent.parent


# =====================================================
# SIDEBAR
# =====================================================
class Sidebar(QFrame):
    """Barre laterale de navigation avec logo image + menu avec icones."""

    navigate = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(240)

        # Container principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ============================================
        # LOGO : image unique (rh.png ou autre)
        # ============================================
        logo_container = QFrame()
        logo_container.setObjectName("sidebarLogo")
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(16, 20, 16, 20)
        logo_layout.setSpacing(0)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Recherche l'image avec plusieurs chemins et extensions possibles
        logo_pixmap = self._find_logo_pixmap()

        if logo_pixmap is not None:
            logo_img = QLabel()
            logo_img.setPixmap(logo_pixmap)
            logo_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_img.setStyleSheet("background: transparent; border: none;")
            logo_layout.addWidget(logo_img)
            print(f"[Sidebar] Logo charge OK ({logo_pixmap.width()}x{logo_pixmap.height()})")
        else:
            # Fallback : texte
            fallback = QLabel("SmartRH")
            fallback.setStyleSheet("""
                color: #FFFFFF;
                font-size: 18pt;
                font-weight: 800;
                letter-spacing: 0.5px;
                background: transparent;
                border: none;
            """)
            fallback.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_layout.addWidget(fallback)
            print("[Sidebar] Logo non trouve, fallback texte utilise")

        main_layout.addWidget(logo_container)

        # ============================================
        # MENU DE NAVIGATION (avec icones)
        # ============================================
        nav_container = QFrame()
        nav_container.setStyleSheet("background: transparent; border: none;")
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(8, 8, 8, 8)
        nav_layout.setSpacing(4)

        # Items : (icon_name, label, page_key)
        self.nav_items = [
            ("sidebar-home", "Accueil", "accueil"),
            ("sidebar-users", "Employés", "employees"),
            ("sidebar-recruit", "Recrutement IA", "recruitment"),
            ("status-match", "SmartMatch IA", "smartmatch"),
            ("sidebar-chart", "Rapports & Analytics", "reports"),
            ("sidebar-warning", "Risques & Turnover", "turnover"),
            ("sidebar-link", "Liens & Relations", "links"),
            ("audi", "Journal d'audit", "audit"),
            ("sidebar-settings", "Paramètres", "settings"),
        ]

        self.buttons = {}

        for icon_name, label, page_key in self.nav_items:
            btn = QPushButton(f"  {label}")
            btn.setObjectName("navButton")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setIconSize(QSize(18, 18))

            # Charge l'icone si elle existe
            icon_path = resolve_icon_path(icon_name)
            if icon_path and icon_path.exists():
                btn.setIcon(QIcon(str(icon_path)))

            btn.clicked.connect(
                lambda _, k=page_key: self._on_nav_click(k)
            )
            nav_layout.addWidget(btn)
            self.buttons[page_key] = btn

        nav_layout.addStretch()
        main_layout.addWidget(nav_container, 1)

        # ============================================
        # FOOTER : IA Connectée
        # ============================================
        footer = QFrame()
        footer.setStyleSheet("background: transparent; border: none;")
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(16, 12, 16, 16)
        footer_layout.setSpacing(0)

        ai_status = QLabel("●  IA Connectée          v2.4")
        ai_status.setObjectName("aiStatus")
        ai_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.addWidget(ai_status)

        main_layout.addWidget(footer)

        # État par défaut
        self.active_key = None
        self.set_active("accueil")

    # =====================================================
    # RECHERCHE DU LOGO (multi-chemins, multi-extensions)
    # =====================================================
    def _find_logo_pixmap(self):
        """Cherche le logo dans plusieurs emplacements possibles."""
        # ✅ Utilise la methode robuste pour trouver la racine
        root = find_project_root()

        print(f"[Sidebar] Racine projet detectee : {root}")

        # Tous les chemins et noms possibles à essayer
        candidates = [
            # Chemin principal
            root / "assets" / "icons" / "rh.png",
            root / "assets" / "icons" / "rh.PNG",
            root / "assets" / "icons" / "RH.png",
            root / "assets" / "icons" / "rh.svg",
            root / "assets" / "icons" / "rh.jpg",
            root / "assets" / "icons" / "rh.jpeg",
            root / "assets" / "icons" / "rh.webp",
            # Variantes dans icons
            root / "assets" / "icons" / "logo.png",
            root / "assets" / "icons" / "smartrh.png",
            # Dossier assets direct
            root / "assets" / "rh.png",
            root / "assets" / "logo.png",
            root / "assets" / "smartrh.png",
            # Dossier images
            root / "assets" / "images" / "rh.png",
            root / "assets" / "images" / "logo.png",
        ]

        for path in candidates:
            if path.exists():
                pix = QPixmap(str(path))
                if not pix.isNull():
                    # Contrainte largeur 208px (240 - 2*16) et hauteur 60px
                    pix = pix.scaled(
                        208, 60,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    print(f"[Sidebar] Logo trouve : {path}")
                    return pix
                else:
                    print(f"[Sidebar] Fichier trouve mais image invalide : {path}")

        # Si rien n'est trouve
        return None

    # =====================================================
    # GESTION ACTIVE/DISABLED
    # =====================================================
    def set_active(self, key: str):
        """Met le bouton correspondant en surbrillance."""
        self.active_key = key
        for k, btn in self.buttons.items():
            btn.setChecked(k == key)

    def set_disabled(self, keys: list):
        """Desactive une liste de pages."""
        for k, btn in self.buttons.items():
            btn.setEnabled(k not in keys)

    # =====================================================
    # NAVIGATION
    # =====================================================
    def _on_nav_click(self, key: str):
        """Emet le signal de navigation."""
        self.set_active(key)
        self.navigate.emit(key)