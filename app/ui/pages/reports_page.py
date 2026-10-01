import os
import platform
import subprocess
from pathlib import Path

from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.services.audit_service import AuditService
from app.services.report_service import REPORT_TYPES, ReportService


# =====================================================
# UTILITAIRE POUR ICÔNES SVG (Remplacement des émojis)
# =====================================================
def get_svg_icon(svg_content: str, color: str = "#0D7A6A", size: int = 24) -> QIcon:
    """Convertit une chaîne SVG en QIcon vectoriel à la couleur spécifiée."""
    colored_svg = svg_content.replace('currentColor', color)
    renderer = QSvgRenderer(colored_svg.encode('utf-8'))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    from PyQt6.QtGui import QPainter
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    
    return QIcon(pixmap)


# Icônes SVG professionnelles
SVG_ICONS = {
    "remuneration_by_dept": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/></svg>""",
    "turnover_absenteeism": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/><polyline points="17 18 23 18 23 12"/></svg>""",
    "age_pyramid": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>""",
    "salary_projection": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="20" x2="12" y2="10"/><line x1="18" y1="20" x2="18" y2="4"/><line x1="6" y1="20" x2="6" y2="16"/></svg>""",
    "file_pdf": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>""",
    "bolt": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>""",
    "refresh": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/></svg>"""
}


# =====================================================
# CARTE DE RAPPORT (Grille d'action)
# =====================================================
class ReportTypeCard(QFrame):
    """Carte cliquable pour un type de rapport."""

    generate_requested = pyqtSignal(str)

    def __init__(self, report_type: str, label: str, svg_data: str, subtitle: str):
        super().__init__()
        self.report_type = report_type
        self.setMinimumHeight(160)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                border: 1px solid #E2E8F0;
            }
            QFrame:hover {
                border: 1px solid #0D7A6A;
                background-color: #FAFCFB;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # En-tête : Icône SVG + Titre
        top_layout = QHBoxLayout()
        top_layout.setSpacing(14)

        icon_label = QLabel()
        icon_label.setFixedSize(42, 42)
        icon_label.setStyleSheet("""
            background-color: #E8F5F1;
            border-radius: 8px;
            border: none;
        """)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Application de l'icône SVG
        icon = get_svg_icon(svg_data, color="#0D7A6A", size=22)
        icon_label.setPixmap(icon.pixmap(22, 22))
        top_layout.addWidget(icon_label)

        title_label = QLabel(label)
        title_label.setStyleSheet("""
            font-size: 11pt;
            font-weight: 700;
            color: #1E293B;
            background: transparent;
            border: none;
        """)
        title_label.setWordWrap(True)
        top_layout.addWidget(title_label, 1)

        layout.addLayout(top_layout)

        # Description
        sub_label = QLabel(subtitle)
        sub_label.setStyleSheet("""
            font-size: 8.5pt;
            color: #64748B;
            background: transparent;
            border: none;
            line-height: 1.3;
        """)
        sub_label.setWordWrap(True)
        layout.addWidget(sub_label)

        layout.addStretch()

        # Bouton Action
        btn_generate = QPushButton(" Générer le rapport")
        btn_generate.setIcon(get_svg_icon(SVG_ICONS["bolt"], color="#FFFFFF", size=14))
        btn_generate.setIconSize(QSize(14, 14))
        btn_generate.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_generate.setStyleSheet("""
            QPushButton {
                background-color: #0D7A6A;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 8px 14px;
                font-size: 8.5pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0A6456;
            }
        """)
        btn_generate.clicked.connect(lambda: self.generate_requested.emit(self.report_type))
        layout.addWidget(btn_generate)

    def mousePressEvent(self, event):
        """Permet au clic sur l'ensemble du conteneur de déclencher l'action."""
        self.generate_requested.emit(self.report_type)
        super().mousePressEvent(event)


# =====================================================
# LIGNE D'HISTORIQUE DES RAPPORTS
# =====================================================
class ReportHistoryRow(QFrame):
    """Composant représentant un document généré dans l'historique."""

    def __init__(self, report: dict):
        super().__init__()
        self.report = report
        self.setFixedHeight(60)
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 6px;
                border: 1px solid #F1F5F9;
            }
            QFrame:hover {
                background-color: #F8FAFC;
                border-color: #CBD5E1;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(14)

        # Icône Fichier PDF
        pdf_icon = QLabel()
        pdf_icon.setFixedSize(32, 32)
        pdf_icon.setStyleSheet("background: transparent; border: none;")
        pdf_icon.setPixmap(get_svg_icon(SVG_ICONS["file_pdf"], color="#64748B", size=20).pixmap(20, 20))
        layout.addWidget(pdf_icon)

        # Meta-données
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        title = QLabel(report.get("title", "Rapport sans titre"))
        title.setStyleSheet("""
            font-size: 9.5pt;
            font-weight: 600;
            color: #0F172A;
            background: transparent;
            border: none;
        """)
        info_layout.addWidget(title)

        created_at = report.get("created_at")
        date_str = created_at.strftime("%d/%m/%Y à %H:%M") if hasattr(created_at, "strftime") else str(created_at)
        file_info = QLabel(f"Généré le {date_str}  •  {report.get('format', 'PDF')}  •  {report.get('size_kb', 0)} Ko")
        file_info.setStyleSheet("""
            font-size: 8pt;
            color: #64748B;
            background: transparent;
            border: none;
        """)
        info_layout.addWidget(file_info)

        layout.addLayout(info_layout, 1)

        # Bouton d'ouverture
        btn_open = QPushButton("Ouvrir")
        btn_open.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_open.setFixedWidth(80)
        btn_open.setStyleSheet("""
            QPushButton {
                background-color: #F1F5F9;
                color: #334155;
                border: 1px solid #E2E8F0;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 8.5pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #E2E8F0;
                color: #0F172A;
            }
        """)
        btn_open.clicked.connect(self._open_pdf)
        layout.addWidget(btn_open)

    def _open_pdf(self):
        file_url = self.report.get("file_url")
        if not file_url:
            QMessageBox.warning(self, "Erreur", "Lien de fichier non valide.")
            return

        path = Path(file_url)
        if not path.exists():
            QMessageBox.warning(self, "Erreur", f"Le fichier source est introuvable :\n{path}")
            return

        try:
            sys_name = platform.system()
            if sys_name == "Windows":
                os.startfile(str(path))
            elif sys_name == "Darwin":
                subprocess.run(["open", str(path)])
            else:
                subprocess.run(["xdg-open", str(path)])
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Échec lors de l'ouverture du fichier :\n{e}")


# =====================================================
# VUE PRINCIPALE : REPORTS & ANALYTICS
# =====================================================
class ReportsPage(QWidget):
    """Page d'administration et génération des rapports analytiques."""

    navigate_to = pyqtSignal(str)

    SUBTITLES = {
        "remuneration_by_dept": "Analyse de la masse salariale, répartition par service et égalité.",
        "turnover_absenteeism": "Indicateurs de renouvellement et suivi de l'assiduité globale.",
        "age_pyramid": "Structure démographique et projections des départs à la retraite.",
        "salary_projection": "Modélisation budgétaire et simulations de masse salariale.",
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.svc = ReportService()

        # Conteneur principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { background-color: #F8FAFC; border: none; }")

        container = QWidget()
        container.setStyleSheet("background-color: #F8FAFC;")
        scroll_area.setWidget(container)
        main_layout.addWidget(scroll_area)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(24)

        # -------------------------------------------------
        # HEADER DE LA PAGE
        # -------------------------------------------------
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)

        breadcrumb = QLabel("SMARTRH  /  RAPPORTS & ANALYTICS")
        breadcrumb.setStyleSheet("""
            color: #64748B;
            font-size: 8.5pt;
            font-weight: 700;
            letter-spacing: 0.8px;
        """)
        header_layout.addWidget(breadcrumb)

        title = QLabel("Rapports & Analyses Décisionnelles")
        title.setStyleSheet("font-size: 18pt; font-weight: 800; color: #0F172A;")
        header_layout.addWidget(title)

        subtitle = QLabel("Générez, consultez et exportez vos états réglementaires et tableaux de bord.")
        subtitle.setStyleSheet("font-size: 9.5pt; color: #475569;")
        header_layout.addWidget(subtitle)

        layout.addLayout(header_layout)

        # -------------------------------------------------
        # SECTION 1 : GRILLE DES RAPPORTS
        # -------------------------------------------------
        sec1_title = QLabel("MODÈLES DE RAPPORTS DISPONIBLES")
        sec1_title.setStyleSheet("""
            font-size: 9pt;
            font-weight: 700;
            color: #64748B;
            letter-spacing: 1px;
            padding-top: 8px;
        """)
        layout.addWidget(sec1_title)

        grid = QGridLayout()
        grid.setSpacing(16)

        for idx, (rtype, label) in enumerate(REPORT_TYPES.items()):
            svg_data = SVG_ICONS.get(rtype, SVG_ICONS["file_pdf"])
            sub = self.SUBTITLES.get(rtype, "")
            
            card = ReportTypeCard(rtype, label, svg_data, sub)
            card.generate_requested.connect(self._generate_report)
            grid.addWidget(card, idx // 2, idx % 2)

        layout.addLayout(grid)

        # -------------------------------------------------
        # SECTION 2 : HISTORIQUE
        # -------------------------------------------------
        sec2_layout = QHBoxLayout()
        
        sec2_title = QLabel("HISTORIQUE DES RAPPORTS GÉNÉRÉS")
        sec2_title.setStyleSheet("""
            font-size: 9pt;
            font-weight: 700;
            color: #64748B;
            letter-spacing: 1px;
        """)
        sec2_layout.addWidget(sec2_title)
        sec2_layout.addStretch()

        btn_refresh = QPushButton(" Actualiser")
        btn_refresh.setIcon(get_svg_icon(SVG_ICONS["refresh"], color="#475569", size=14))
        btn_refresh.setIconSize(QSize(14, 14))
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #475569;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 8.5pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #F1F5F9;
                color: #0F172A;
            }
        """)
        btn_refresh.clicked.connect(self._load_history)
        sec2_layout.addWidget(btn_refresh)

        layout.addLayout(sec2_layout)

        # Card de fond pour le tableau / l'historique
        self.history_card = QFrame()
        self.history_card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 8px;
                border: 1px solid #E2E8F0;
            }
        """)
        self.history_v = QVBoxLayout(self.history_card)
        self.history_v.setContentsMargins(12, 12, 12, 12)
        self.history_v.setSpacing(8)

        layout.addWidget(self.history_card)
        layout.addStretch()

        # Chargement des données
        self._load_history()

    # -------------------------------------------------
    # LOGIQUE MÉTIER
    # -------------------------------------------------
    def _load_history(self):
        """Récupère et rafraîchit la liste des récents rapports générés."""
        while self.history_v.count():
            item = self.history_v.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            reports = self.svc.get_latest(10)
        except Exception as e:
            print(f"[ReportsPage] Erreur au chargement de l'historique : {e}")
            reports = []

        if not reports:
            empty = QLabel("Aucun rapport n'a été généré pour le moment.")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("""
                color: #94A3B8;
                font-style: italic;
                padding: 30px;
                font-size: 9pt;
                background: transparent;
                border: none;
            """)
            self.history_v.addWidget(empty)
            return

        for r in reports:
            self.history_v.addWidget(ReportHistoryRow(r))

    def _generate_report(self, report_type: str):
        """Déclenche la génération d'un rapport PDF."""
        label = REPORT_TYPES.get(report_type, report_type)

        try:
            path = self.svc.generate(report_type)

            AuditService().log_action(
                action="generate_report",
                entity_type="report",
                entity_id=None,
                details=label,
            )

            QMessageBox.information(
                self,
                "Génération réussie",
                f"Le rapport suivant a été généré avec succès :\n\n"
                f"• Type : {label}\n"
                f"• Fichier : {Path(path).name}"
            )

            self._load_history()

        except Exception as e:
            print(f"[ReportsPage] Échec de la génération : {e}")
            QMessageBox.critical(
                self,
                "Erreur de génération",
                f"Une erreur est survenue lors de la création du document PDF :\n{e}"
            )