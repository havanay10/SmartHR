"""Test : utilisation des icones (emoji OU image)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
)
from app.ui.styles import APP_STYLE
from app.ui.icons import IconLabel, IMAGES_DIR, is_emoji, resolve_icon_path
from app.ui.widgets import KpiCard, Sidebar, TopBar, AlertCard


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test - Icones emoji / images")
        self.resize(1200, 800)
        self.setStyleSheet(APP_STYLE)

        container = QWidget()
        self.setCentralWidget(container)

        h = QHBoxLayout(container)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        # Sidebar (avec emojis par defaut)
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
        info = QLabel(f"Dossier des images : {IMAGES_DIR}")
        info.setStyleSheet("color: #7A8B9C; font-size: 9pt;")
        cv.addWidget(info)

        info2 = QLabel(f"Existe ? {IMAGES_DIR.exists()}")
        info2.setStyleSheet("color: #7A8B9C; font-size: 9pt;")
        cv.addWidget(info2)

        # Test KPI avec emoji
        cv.addWidget(QLabel("<b>KPI avec emoji :</b>"))
        kpi1 = KpiCard(
            title="Test emoji",
            value="42",
            subtitle="Utilise un emoji",
            icon="👥",
            accent="green",
        )
        cv.addWidget(kpi1)

        # Test KPI avec nom d'image (si existe)
        cv.addWidget(QLabel("<b>KPI avec image (nom court) :</b>"))
        kpi2 = KpiCard(
            title="Test image",
            value="99",
            subtitle="Utilise une image (si elle existe)",
            icon="user",       # cherchera assets/images/user.png
            accent="blue",
        )
        cv.addWidget(kpi2)

        # Test KPI avec chemin complet
        cv.addWidget(QLabel("<b>KPI avec chemin complet :</b>"))
        kpi3 = KpiCard(
            title="Test chemin",
            value="77",
            subtitle="assets/images/user.png",
            icon="assets/images/user.png",
            accent="orange",
        )
        cv.addWidget(kpi3)

        cv.addStretch()
        v.addWidget(content, 1)

        h.addWidget(right, 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)

    print("=" * 65)
    print("  TEST 7.2b : Icones emoji / images")
    print("=" * 65)
    print(f"\n  Dossier images : {IMAGES_DIR}")
    print(f"  Existe ?       : {IMAGES_DIR.exists()}")

    if IMAGES_DIR.exists():
        files = list(IMAGES_DIR.glob("*"))
        print(f"  {len(files)} fichier(s) :")
        for f in files[:10]:
            print(f"    - {f.name}")
    else:
        print("  [INFO] Creez le dossier assets/images/ et ajoutez vos icones")

    print("\n  Test emoji      : '👥' ->", "emoji" if is_emoji("👥") else "chemin")
    print("  Test chemin     : 'user.png' ->", "emoji" if is_emoji("user.png") else "chemin")
    print("  Test nom court  : 'user' ->", "emoji" if is_emoji("user") else "chemin")

    win = TestWindow()
    win.show()
    sys.exit(app.exec())