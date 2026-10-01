"""Test : systeme hybride (image si existe, sinon emoji).

Ce test montre 3 cas :
1. Emoji direct (toujours affiche)
2. Nom d'image qui N'EXISTE PAS -> fallback emoji
3. Nom d'image qui EXISTE -> image
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QGridLayout
)
from app.ui.styles import APP_STYLE
from app.ui.icons import IconLabel, IMAGES_DIR, image_exists
from app.ui.widgets import KpiCard, Sidebar, TopBar


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test - Systeme hybride icones")
        self.resize(1300, 850)
        self.setStyleSheet(APP_STYLE)

        container = QWidget()
        self.setCentralWidget(container)

        h = QHBoxLayout(container)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        # Sidebar (utilise les nouveaux noms d'images + fallback emoji)
        sidebar = Sidebar()
        h.addWidget(sidebar)

        right = QWidget()
        v = QVBoxLayout(right)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        topbar = TopBar()
        v.addWidget(topbar)

        content = QWidget()
        cv = QVBoxLayout(content)
        cv.setContentsMargins(30, 30, 30, 30)
        cv.setSpacing(20)

        # Info
        info = QLabel(f"Dossier images : {IMAGES_DIR}")
        info.setStyleSheet("color: #7A8B9C; font-size: 9pt;")
        cv.addWidget(info)

        exist_txt = "OUI" if IMAGES_DIR.exists() else "NON"
        info2 = QLabel(f"Existe ? {exist_txt}")
        info2.setStyleSheet("color: #7A8B9C; font-size: 9pt;")
        cv.addWidget(info2)

        if IMAGES_DIR.exists():
            files = list(IMAGES_DIR.glob("*"))
            info3 = QLabel(f"{len(files)} fichier(s) dans assets/images/")
            info3.setStyleSheet("color: #7A8B9C; font-size: 9pt;")
            cv.addWidget(info3)
            for f in files[:5]:
                cv.addWidget(QLabel(f"  • {f.name}"))

        # Test 1 : Emoji direct
        cv.addWidget(QLabel("<b>Test 1 : Emoji direct</b>"))
        t1 = QWidget()
        l1 = QHBoxLayout(t1)
        for emoji in ["🏠", "👥", "🎯", "📊", "⚠️", "🔗", "⚙️"]:
            l1.addWidget(IconLabel(emoji, size=24))
        l1.addStretch()
        cv.addWidget(t1)

        # Test 2 : Noms d'images (fallback si absentes)
        cv.addWidget(QLabel("<b>Test 2 : Noms d'images (fallback si absentes)</b>"))
        t2 = QWidget()
        l2 = QHBoxLayout(t2)
        icons = [
            ("sidebar-home", "🏠"),
            ("sidebar-users", "👥"),
            ("sidebar-recruit", "🎯"),
            ("kpi-money", "💰"),
            ("kpi-calendar", "📅"),
        ]
        for name, fallback in icons:
            widget = QWidget()
            wl = QVBoxLayout(widget)
            wl.setSpacing(4)

            exists = image_exists(name)
            status = "IMG" if exists else "EMOJI"

            wl.addWidget(IconLabel(name, fallback=fallback, size=28))
            lbl = QLabel(status)
            lbl.setStyleSheet("font-size: 8pt; color: #7A8B9C;")
            lbl.setAlignment(__import__("PyQt6.QtCore", fromlist=["Qt"]).Qt.AlignmentFlag.AlignCenter)
            wl.addWidget(lbl)

            l2.addWidget(widget)
        l2.addStretch()
        cv.addWidget(t2)

        # Test 3 : KPI cards completes
        cv.addWidget(QLabel("<b>Test 3 : Cartes KPI (avec fallback)</b>"))
        grid = QGridLayout()
        grid.setSpacing(16)
        kpis = [
            ("Total employes", "108", "96% en poste", "kpi-employees", "👥", "green"),
            ("Absences", "3", "Aujourd'hui", "kpi-calendar", "📅", "red"),
            ("Recrutement IA", "2", "Postes ouverts", "kpi-target", "🎯", "blue"),
            ("Turnover", "5.0%", "Zone maitrisee", "kpi-turnover", "🔄", "green"),
        ]
        for i, (t, vv, s, icon, fallback, acc) in enumerate(kpis):
            grid.addWidget(
                KpiCard(t, vv, s, icon=icon, accent=acc),
                0, i,
            )
        cv.addLayout(grid)

        cv.addStretch()
        v.addWidget(content, 1)

        h.addWidget(right, 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)

    print("=" * 65)
    print("  TEST 7.2c : Systeme hybride (image OU emoji)")
    print("=" * 65)
    print(f"\n  Dossier images : {IMAGES_DIR}")
    print(f"  Existe ?       : {IMAGES_DIR.exists()}")

    if IMAGES_DIR.exists():
        files = list(IMAGES_DIR.glob("*"))
        print(f"  {len(files)} fichier(s) :")
        for f in files[:10]:
            print(f"    - {f.name}")
    else:
        print("  [INFO] Toutes les icones seront des emojis (fallback)")
        print("  [INFO] Creez assets/images/ et copiez vos icones pour les voir")

    # Test existence
    print("\n  Verification des images attendues :")
    expected = [
        "sidebar-home", "sidebar-users", "sidebar-recruit",
        "kpi-calendar", "kpi-money", "app-bell",
    ]
    for name in expected:
        exists = image_exists(name)
        status = "TROUVEE" if exists else "absente -> emoji"
        print(f"    {name:25} : {status}")

    win = TestWindow()
    win.show()
    sys.exit(app.exec())