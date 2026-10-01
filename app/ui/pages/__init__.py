"""Pages de l'application SmartRH.

On ajoute les pages AU FUR ET A MESURE.
Actuellement : Accueil + Employes + Recrutement + Détails.
"""
from app.ui.pages.accueil_page import AccueilPage
from app.ui.pages.employees_page import EmployeesPage
from app.ui.pages.recruitment_page import RecruitmentPage
from app.ui.pages.job_offer_detail_page import JobOfferDetailPage
from app.ui.pages.smartmatch_page import SmartMatchPage
from app.ui.pages.reports_page import ReportsPage
from app.ui.pages.turnover_page import TurnoverPage
from app.ui.pages.links_page import LinksPage
from app.ui.pages.settings_page import SettingsPage
from app.ui.pages.audit_page import AuditPage

__all__ = [
    "AccueilPage",
    "EmployeesPage",
    "RecruitmentPage",
    "JobOfferDetailPage",
    "SmartMatchPage",
    "ReportsPage",
    "TurnoverPage",
    "LinksPage",
    "SettingsPage",
    "AuditPage",
]