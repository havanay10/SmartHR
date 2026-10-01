"""Fenetre principale de SmartRH.

Structure :
- Sidebar fixe a gauche (240px)
- Colonne de droite : TopBar + QStackedWidget (pages)

Les pages sont ajoutees UNE PAR UNE au fur et a mesure.
"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget
)

from app.ui.styles import APP_STYLE
from app.ui.widgets import Sidebar, TopBar
from app.ui.pages import (
    AccueilPage, EmployeesPage, RecruitmentPage, JobOfferDetailPage,
    SmartMatchPage, ReportsPage, TurnoverPage, LinksPage, SettingsPage,
    AuditPage,
)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SmartRH — Enterprise Suite")
        self.resize(1500, 900)
        self.setMinimumSize(1200, 700)
        self.setStyleSheet(APP_STYLE)

        # ============ LAYOUT RACINE ============
        container = QWidget()
        self.setCentralWidget(container)

        h_root = QHBoxLayout(container)
        h_root.setContentsMargins(0, 0, 0, 0)
        h_root.setSpacing(0)

        # ============ SIDEBAR ============
        self.sidebar = Sidebar()
        self.sidebar.navigate.connect(self.navigate)
        h_root.addWidget(self.sidebar)

        # ============ COLONNE DROITE ============
        right = QWidget()
        v_right = QVBoxLayout(right)
        v_right.setContentsMargins(0, 0, 0, 0)
        v_right.setSpacing(0)

        self.topbar = TopBar(user_name="Rakoto")
        v_right.addWidget(self.topbar)

        self.stack = QStackedWidget()
        v_right.addWidget(self.stack, 1)

        h_root.addWidget(right, 1)

        # ============ PAGES ============
        self.pages = {}

        # Stockage pour passer des données entre pages
        self.selected_offer_id = None

        # --- Pages actuellement disponibles ---
        self._register_page("accueil", AccueilPage)
        self._register_page("employees", EmployeesPage)
        self._register_page("recruitment", RecruitmentPage)
        self._register_page("job_offer_detail", JobOfferDetailPage)
        self._register_page("smartmatch", SmartMatchPage)
        self._register_page("reports", ReportsPage)
        self._register_page("turnover", TurnoverPage)
        self._register_page("links", LinksPage)
        self._register_page("settings", SettingsPage)
        self._register_page("audit", AuditPage)
                
        # Connecter le signal offer_selected de la page recrutement
        recruitment_page = self.pages.get("recruitment")
        if recruitment_page:
            page, _ = recruitment_page
            if hasattr(page, 'offer_selected'):
                page.offer_selected.connect(self._on_offer_selected)

        # ============ PAGE PAR DEFAUT ============
        self.navigate("accueil")

        # Desactiver les boutons des pages non encore disponibles
        not_ready = []
        if hasattr(self.sidebar, "set_disabled"):
            self.sidebar.set_disabled(not_ready)
    
    def _register_page(self, key: str, PageClass):
        """Enregistre une page dans le QStackedWidget."""
        try:
            page = PageClass()
            idx = self.stack.addWidget(page)
            self.pages[key] = (page, idx)

            # Si la page expose un signal navigate_to, on le connecte
            if hasattr(page, "navigate_to"):
                page.navigate_to.connect(self.navigate)

            print(f"[NAV] Page chargee : {key}")
        except Exception as e:
            print(f"[ERREUR] Impossible de charger la page '{key}': {e}")

    def navigate(self, key: str):
        """Change la page affichee et met a jour la sidebar."""
        if key not in self.pages:
            print(f"[NAV] Page non encore disponible : {key}")
            return

        _, idx = self.pages[key]
        self.stack.setCurrentIndex(idx)
        self.sidebar.set_active(key)
        print(f"[NAV] Navigation vers : {key}")

        # Cas spécial : page de détail d'offre
        if key == "job_offer_detail" and hasattr(self, 'selected_offer_id'):
            page, _ = self.pages[key]
            if hasattr(page, 'set_offer_id'):
                page.set_offer_id(self.selected_offer_id)

    def _on_offer_selected(self, offer_id: str):
        """Gère la sélection d'une offre pour les détails."""
        self.selected_offer_id = offer_id
        print(f"[MainWindow] Offre sélectionnée pour détail : {offer_id}")