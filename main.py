"""Point d'entree de l'application SmartRH."""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from pathlib import Path

from app.ui.main_window import MainWindow
from config import settings


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(settings.APP_NAME)
    app.setApplicationVersion(settings.APP_VERSION)

    # Icone de l'application (si existe)
    logo = Path(__file__).parent / "assets" / "images" / "app-logo.png"
    if logo.exists():
        app.setWindowIcon(QIcon(str(logo)))

    # Police par defaut
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)

    # Fenetre principale
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()