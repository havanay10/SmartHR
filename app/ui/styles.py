"""Theme QSS de SmartRH.

Palette alignee maquettes Executive Slate & Deep Teal.
"""

# =====================================================
# PALETTE (reutilisable dans le code Python)
# =====================================================
COLORS = {
    "bg_app": "#F4F6F9",
    "bg_card": "#FFFFFF",
    "bg_sidebar": "#0F172A",
    "bg_sidebar_hover": "#1A2E44",
    "bg_sidebar_active": "#0D7A6A",
    "bg_sidebar_item": "#1E293B",

    "primary": "#0D7A6A",
    "primary_hover": "#0A6456",
    "primary_light": "#ECFDF5",

    "text_primary": "#0F172A",
    "text_secondary": "#5A6B7D",
    "text_muted": "#7A8B9C",
    "text_light": "#EAF1FF",
    "text_sidebar": "#94A3B8",
    "text_white": "#FFFFFF",

    "border": "#E2E8F0",
    "border_light": "#F1F5F9",
    "grid": "#F1F5F9",

    "danger": "#C0392B",
    "danger_light": "#FEE2E2",
    "warning": "#F39C12",
    "warning_light": "#FEF3C7",
    "success": "#0D7A6A",
    "success_light": "#D1FAE5",
    "purple": "#7C3AED",
    "purple_light": "#EDE9FE",
    "blue": "#2E86DE",
    "blue_light": "#D8DEFF",
}


# =====================================================
# QSS GLOBAL
# =====================================================
APP_STYLE = """
/* ================= BASE ================= */
QMainWindow, QWidget {
    background-color: #F4F6F9;
    font-family: 'Inter', 'Segoe UI', 'Helvetica', sans-serif;
    font-size: 11pt;
    color: #0F172A;
}

/* ================= SIDEBAR ================= */
QFrame#sidebar {
    background-color: #0F172A;
    border: none;
}

QFrame#sidebarLogo {
    background-color: transparent;
    border: none;
}

QLabel#sidebarLogoBadge {
    background-color: #0D7A6A;
    color: #FFFFFF;
    border-radius: 10px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    font-size: 16pt;
    font-weight: 800;
    qproperty-alignment: AlignCenter;
}

QLabel#sidebarTitle {
    color: #FFFFFF;
    font-size: 14pt;
    font-weight: 800;
    padding: 0 0 0 10px;
    letter-spacing: -0.3px;
    background: transparent;
}

QLabel#sidebarSubtitle {
    color: #AAFFE9;
    font-size: 8pt;
    letter-spacing: 1.5px;
    padding: 3px 10px;
    font-weight: 700;
    background-color: #0D7A6A;
    border-radius: 4px;
}

/* ===== NAV BUTTONS (COMPACT - style maquette) ===== */
QPushButton#navButton {
    background: transparent;
    color: #E2E8F0;
    text-align: left;
    padding: 8px 12px;
    border: none;
    border-radius: 8px;
    font-size: 10.5pt;
    font-weight: 500;
    min-height: 38px;
    margin: 1px 6px;
}

QPushButton#navButton:hover {
    background-color: #1A2E44;
    color: #FFFFFF;
}

/* ACTIF : fond vert uni avec coins arrondis sur TOUS les côtés */
QPushButton#navButton:checked {
    background-color: #0D7A6A;
    color: #FFFFFF;
    font-weight: 700;
    border: none;
    border-radius: 8px;
}

QLabel#aiStatus {
    color: #FFFFFF;
    font-size: 9pt;
    padding: 8px 14px;
    background-color: rgba(13, 122, 106, 0.2);
    border-radius: 8px;
    font-weight: 700;
    border: 1px solid rgba(13, 122, 106, 0.3);
}

QLabel#userInfo {
    color: #E2E8F0;
    font-size: 11pt;
    padding: 10px 14px;
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    font-weight: 500;
}

/* ================= PAGE HEADER ================= */
QLabel#pageTitle {
    color: #0F172A;
    font-size: 19pt;
    font-weight: 800;
    padding: 4px 0;
    background: transparent;
}

QLabel#pageSubtitle {
    color: #5A6B7D;
    font-size: 11pt;
    padding: 2px 0;
    background: transparent;
}

QLabel#sectionTitle {
    color: #0F172A;
    font-size: 14pt;
    font-weight: 700;
    padding: 6px 0;
    background: transparent;
}

QLabel#sectionSubtitle {
    color: #7A8B9C;
    font-size: 10pt;
    background: transparent;
}

/* ================= KPI CARDS ================= */
QFrame#kpiCard {
    background-color: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
}

QFrame#kpiCard:hover {
    border: 1px solid #CBD5E1;
}

QLabel#kpiTitle {
    color: #5A6B7D;
    font-size: 9pt;
    font-weight: 700;
    letter-spacing: 0.8px;
    background: transparent;
}

QLabel#kpiValue {
    color: #0F172A;
    font-size: 24pt;
    font-weight: 800;
    padding: 4px 0;
    background: transparent;
}

QLabel#kpiSubtitle {
    color: #7A8B9C;
    font-size: 10pt;
    background: transparent;
}

QLabel#kpiIcon {
    font-size: 16pt;
    color: #0D7A6A;
    background: transparent;
}

QLabel#kpiValueAlert {
    color: #C0392B;
    font-size: 24pt;
    font-weight: 800;
    background: transparent;
}

/* ================= BOUTONS ================= */
QPushButton#primaryButton {
    background-color: #0D7A6A;
    color: #FFFFFF;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 10pt;
    border: none;
    min-height: 24px;
}

QPushButton#primaryButton:hover {
    background-color: #0A6456;
}

QPushButton#primaryButton:pressed {
    background-color: #084C41;
}

QPushButton#actionButton {
    background-color: #FFFFFF;
    color: #0F172A;
    padding: 10px 18px;
    border-radius: 8px;
    border: 1px solid #CBD5E1;
    font-size: 10pt;
    font-weight: 600;
    text-align: left;
}

QPushButton#actionButton:hover {
    background-color: #F8FAFC;
    border-color: #94A3B8;
}

QPushButton#secondaryButton {
    background-color: #FFFFFF;
    color: #0F172A;
    padding: 10px 20px;
    border-radius: 6px;
    border: 1px solid #CBD5E1;
    font-size: 10pt;
    font-weight: 600;
}

QPushButton#secondaryButton:hover {
    background-color: #F1F5F9;
    border-color: #94A3B8;
}

QPushButton#dangerButton {
    background-color: #C0392B;
    color: #FFFFFF;
    padding: 10px 20px;
    border-radius: 6px;
    font-weight: 600;
    border: none;
}

QPushButton#dangerButton:hover {
    background-color: #A93226;
}

/* ================= TABLES ================= */
QTableView, QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    gridline-color: #F1F5F9;
    selection-background-color: #ECFDF5;
    selection-color: #0F172A;
    alternate-background-color: #F8FAFC;
}

QTableView::item, QTableWidget::item {
    padding: 10px 10px;
    border-bottom: 1px solid #F1F5F9;
}

QHeaderView::section {
    background-color: #F8FAFC;
    color: #64748B;
    padding: 12px 12px;
    border: none;
    border-bottom: 1px solid #E2E8F0;
    font-weight: 700;
    font-size: 8pt;
    letter-spacing: 0.8px;
}

QHeaderView::section:first {
    border-top-left-radius: 12px;
}

QHeaderView::section:last {
    border-top-right-radius: 12px;
}

/* ================= GROUP BOX ================= */
QGroupBox {
    font-weight: 700;
    font-size: 11pt;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 24px 20px 20px 20px;
    margin-top: 16px;
    background-color: #FFFFFF;
    color: #0F172A;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 20px;
    padding: 0 10px;
    color: #0F172A;
    background-color: #FFFFFF;
}

/* ================= INPUTS ================= */
QLineEdit, QComboBox, QSpinBox, QDateEdit {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 10pt;
    color: #0F172A;
    min-height: 24px;
}

QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus {
    border: 2px solid #0D7A6A;
    background-color: #F8FAFC;
}

QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #64748B;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    selection-background-color: #ECFDF5;
    selection-color: #0F172A;
    padding: 6px;
    border-radius: 8px;
}

/* ================= RADIO / CHECK ================= */
QRadioButton, QCheckBox {
    font-size: 10pt;
    color: #0F172A;
    padding: 4px 8px;
    spacing: 8px;
}

QRadioButton::indicator, QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 9px;
    border: 2px solid #CBD5E1;
    background-color: #FFFFFF;
}

QRadioButton::indicator:checked, QCheckBox::indicator:checked {
    background-color: #0D7A6A;
    border-color: #0D7A6A;
}

/* ================= SCROLLBARS ================= */
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #CBD5E1;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #94A3B8;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
    background: none;
}

QScrollBar:horizontal {
    background: transparent;
    height: 8px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background: #CBD5E1;
    border-radius: 4px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover {
    background: #94A3B8;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
    background: none;
}

/* ================= SCROLL AREA ================= */
QScrollArea {
    background-color: transparent;
    border: none;
}

QScrollArea > QWidget > QWidget {
    background-color: transparent;
}

/* ================= SEPARATOR ================= */
QFrame[frameShape="4"] {
    color: #E2E8F0;
    max-height: 1px;
}
"""


# =====================================================
# STYLES ADDITIONNELS
# =====================================================
EXTRA_STYLE = """
/* ================= BANDE DE COULEUR HAUT DES CARTES KPI ================= */
QFrame#kpiCard[accentColor="green"] { border-top: 4px solid #0D7A6A; }
QFrame#kpiCard[accentColor="red"] { border-top: 4px solid #C0392B; }
QFrame#kpiCard[accentColor="orange"] { border-top: 4px solid #F39C12; }
QFrame#kpiCard[accentColor="blue"] { border-top: 4px solid #2E86DE; }
QFrame#kpiCard[accentColor="purple"] { border-top: 4px solid #7C3AED; }
QFrame#kpiCard[accentColor="gray"] { border-top: 4px solid #94A3B8; }

/* ================= ICONES SIDEBAR ================= */
QLabel#sidebarIconActive {
    background-color: rgba(255, 255, 255, 0.15);
    border-radius: 6px;
    padding: 2px;
}

QLabel#sidebarIconInactive {
    background-color: transparent;
    border-radius: 6px;
    padding: 2px;
}

/* ================= BADGES ================= */
QLabel#badgeSuccess {
    background-color: #D1FAE5;
    color: #065F46;
    padding: 4px 10px;
    border-radius: 999px;
    border: 1px solid #A7F3D0;
    font-size: 8pt;
    font-weight: 700;
}

QLabel#badgeDanger {
    background-color: #FEE2E2;
    color: #991B1B;
    padding: 4px 10px;
    border-radius: 999px;
    border: 1px solid #FECACA;
    font-size: 8pt;
    font-weight: 700;
}

QLabel#badgeWarning {
    background-color: #FEF3C7;
    color: #92400E;
    padding: 4px 10px;
    border-radius: 999px;
    border: 1px solid #FDE68A;
    font-size: 8pt;
    font-weight: 700;
}

QLabel#badgeInfo {
    background-color: #F1F5F9;
    color: #475569;
    padding: 4px 10px;
    border-radius: 999px;
    border: 1px solid #E2E8F0;
    font-size: 8pt;
    font-weight: 700;
}

QLabel#badgeMatch {
    background-color: #0D7A6A;
    color: #FFFFFF;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 8pt;
    font-weight: 800;
}

QLabel#badgePriority {
    background-color: #FEE2E2;
    color: #991B1B;
    padding: 4px 10px;
    border-radius: 999px;
    border: 1px solid #FECACA;
    font-size: 8pt;
    font-weight: 700;
}

/* ================= ICONES KPI (medaillons carres arrondis 36px) ================= */
QLabel#iconCircleGreen {
    background-color: #ECFDF5;
    color: #0D7A6A;
    border-radius: 8px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    font-size: 14pt;
    qproperty-alignment: AlignCenter;
}

QLabel#iconCircleBlue {
    background-color: #D8DEFF;
    color: #565D79;
    border-radius: 8px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    font-size: 14pt;
    qproperty-alignment: AlignCenter;
}

QLabel#iconCircleRed {
    background-color: #FEE2E2;
    color: #C0392B;
    border-radius: 8px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    font-size: 14pt;
    qproperty-alignment: AlignCenter;
}

QLabel#iconCircleOrange {
    background-color: #FEF3C7;
    color: #F39C12;
    border-radius: 8px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    font-size: 14pt;
    qproperty-alignment: AlignCenter;
}

QLabel#iconSquarePurple {
    background-color: #EDE9FE;
    color: #7C3AED;
    border-radius: 8px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    font-size: 14pt;
    qproperty-alignment: AlignCenter;
}

QLabel#iconSquareGray {
    background-color: #F1F5F9;
    color: #475569;
    border-radius: 8px;
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    font-size: 14pt;
    qproperty-alignment: AlignCenter;
}

/* ================= BARRE DE PROGRESSION ================= */
QProgressBar {
    background-color: #F1F5F9;
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: center;
    color: transparent;
}

QProgressBar::chunk {
    background-color: #0D7A6A;
    border-radius: 4px;
}

QProgressBar#progressDanger::chunk { background-color: #C0392B; }
QProgressBar#progressWarning::chunk { background-color: #F39C12; }
QProgressBar#progressInfo::chunk { background-color: #2E86DE; }

QLabel#progressLabel {
    color: #64748B;
    font-size: 9pt;
    font-weight: 600;
    background: transparent;
}

/* ================= BREADCRUMB ================= */
QLabel#breadcrumb {
    color: #64748B;
    font-size: 9pt;
    font-weight: 500;
    padding: 2px 0;
    background: transparent;
}

QLabel#breadcrumbCurrent {
    color: #0D7A68;
    font-size: 9pt;
    font-weight: 700;
    padding: 2px 0;
    background: transparent;
}

/* ================= TOP BAR ================= */
QFrame#topBar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E2E8F0;
    min-height: 72px;
    max-height: 72px;
}

QLabel#topBarBrand {
    color: #0F172A;
    font-size: 13pt;
    font-weight: 800;
    background: transparent;
}

QLabel#topBarSubtitle {
    color: #64748B;
    font-size: 10pt;
    font-weight: 500;
    background: transparent;
    padding-left: 12px;
}

QLabel#topBarDate {
    color: #5A6B7D;
    font-size: 10pt;
    font-weight: 500;
    padding: 4px 0;
    background-color: transparent;
}

QLabel#topBarIcon {
    font-size: 14pt;
    padding: 6px 8px;
    background-color: transparent;
    border-radius: 8px;
}

QLabel#topBarIcon:hover {
    background-color: #EFF4FF;
}

/* BADGE DE NOTIFICATION (rouge sur la cloche) */
QLabel#notificationBadge {
    background-color: #C0392B;
    color: #FFFFFF;
    border-radius: 8px;
    font-size: 7pt;
    font-weight: 800;
    min-width: 16px;
    max-width: 16px;
    min-height: 16px;
    max-height: 16px;
    qproperty-alignment: AlignCenter;
}

QLabel#avatar {
    background-color: #0D7A68;
    color: #FFFFFF;
    border-radius: 16px;
    min-width: 32px;
    max-width: 32px;
    min-height: 32px;
    max-height: 32px;
    font-size: 11pt;
    font-weight: 700;
    qproperty-alignment: AlignCenter;
}

/* ================= CARTE D'ACTIVITE ================= */
QFrame#activityCard {
    background-color: #FFFFFF;
    border-radius: 12px;
    border: 1px solid #E2E8F0;
    padding: 16px;
}

QFrame#activityItem {
    background-color: #F8FAFC;
    border-radius: 10px;
    border: 1px solid #F1F5F9;
    padding: 12px;
}

QLabel#activityTime {
    color: #94A3B8;
    font-size: 9pt;
    background: transparent;
}

QLabel#activityTitle {
    color: #0F172A;
    font-size: 11pt;
    font-weight: 600;
    background: transparent;
}

QLabel#activityDesc {
    color: #64748B;
    font-size: 10pt;
    background: transparent;
}

QFrame#activityIconWarning {
    background-color: #FEF3C7;
    color: #B45309;
    border-radius: 16px;
    min-width: 32px;
    max-width: 32px;
    min-height: 32px;
    max-height: 32px;
    font-size: 14pt;
    qproperty-alignment: AlignCenter;
}

QFrame#activityIconDanger {
    background-color: #FEE2E2;
    color: #C0392B;
    border-radius: 16px;
    min-width: 32px;
    max-width: 32px;
    min-height: 32px;
    max-height: 32px;
    font-size: 14pt;
    qproperty-alignment: AlignCenter;
}
"""

APP_STYLE = APP_STYLE + EXTRA_STYLE