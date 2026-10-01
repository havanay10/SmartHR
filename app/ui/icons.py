# ============================================================
# SmartRH 2.0
# app/ui/icons.py
#
# Gestion centralisée des icônes SVG
# Aligné sur la maquette de référence "Executive Slate & Deep Teal"
# (Material Symbols Outlined, palette Material 3 exacte de la maquette)
# ============================================================

from pathlib import Path
import re

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import (
    QPixmap,
    QPainter,
    QIcon,
    QColor,
)
from PyQt6.QtWidgets import QLabel

try:
    from PyQt6.QtSvg import QSvgRenderer
    SVG_AVAILABLE = True
except ImportError:
    QSvgRenderer = None
    SVG_AVAILABLE = False


# ============================================================
# CHEMINS
# ============================================================

# app/ui/icons.py
# parents[0] = ui
# parents[1] = app
# parents[2] = smartRh_2.0

BASE_DIR = Path(__file__).resolve().parents[2]

ICONS_DIR = BASE_DIR / "assets" / "icons"

# Préfixe utilisé sur les 77 icônes extraites de la maquette
# (ic_add.svg, ic_groups.svg, ic_person_search.svg, ...)
# pour éviter tout conflit avec d'anciens fichiers du même nom.
MOCKUP_ICON_PREFIX = "ic_"


# ============================================================
# PALETTE SMART RH
#
# Reprend fidèlement les tokens Material 3 de la maquette
# ("Executive Slate & Deep Teal") — ce sont les couleurs
# hexadécimales réellement utilisées dans le code des écrans,
# pas seulement une description de style.
# ============================================================

class IconColors:
    """
    Palette utilisée par l'interface SmartRH — copie exacte
    des tokens Material 3 de la maquette de référence.
    """

    # --- Neutres / texte ---
    WHITE = "#FFFFFF"                      # on-primary / on-secondary / on-error / on-tertiary
    LIGHT = "#EAF1FF"                      # inverse-on-surface
    ON_SURFACE = "#0B1C30"                 # texte principal sombre (= on-background)
    ON_SURFACE_VARIANT = "#3E4946"         # gris de texte secondaire
    OUTLINE = "#6E7A75"                    # icônes discrètes / bordures
    OUTLINE_VARIANT = "#BDC9C4"            # bordures très discrètes
    INVERSE_SURFACE = "#213145"

    # --- Primaire (teal) ---
    PRIMARY = "#005F50"                    # teal foncé — icônes/actions principales
    ON_PRIMARY = "#FFFFFF"                 # icône blanche sur fond teal (ex: avatar rond)
    PRIMARY_CONTAINER = "#0D7A68"          # teal plus clair — accents IA, boutons
    ON_PRIMARY_CONTAINER = "#AAFFE9"       # = ACTIVE (nav active, badges sur fond teal)
    PRIMARY_FIXED = "#99F3DD"
    PRIMARY_FIXED_DIM = "#7CD7C1"          # = INVERSE_PRIMARY
    ON_PRIMARY_FIXED = "#00201A"
    ON_PRIMARY_FIXED_VARIANT = "#005144"

    # Alias historiques conservés (mêmes valeurs que ci-dessus)
    ACTIVE = ON_PRIMARY_CONTAINER          # élément actif (sidebar)

    # --- Secondaire (violet/gris) ---
    SECONDARY = "#565D79"                  # icônes secondaires (mail, historique, appel...)
    ON_SECONDARY = "#FFFFFF"
    SECONDARY_CONTAINER = "#D8DEFF"
    ON_SECONDARY_CONTAINER = "#5A627E"
    SECONDARY_FIXED = "#DBE1FF"
    SECONDARY_FIXED_DIM = "#BEC5E5"        # = INACTIVE (sidebar inactive)
    ON_SECONDARY_FIXED = "#131A33"
    ON_SECONDARY_FIXED_VARIANT = "#3E4660"

    INACTIVE = SECONDARY_FIXED_DIM         # élément inactif (sidebar)

    # --- Tertiaire (corail — alertes) ---
    TERTIARY = "#9E2622"                   # icônes d'alerte (notifications, PDF, warning)
    ON_TERTIARY = "#FFFFFF"
    TERTIARY_CONTAINER = "#C03F37"
    ON_TERTIARY_CONTAINER = "#FFEAE8"
    TERTIARY_FIXED = "#FFDAD6"
    TERTIARY_FIXED_DIM = "#FFB4AB"
    ON_TERTIARY_FIXED = "#410002"
    ON_TERTIARY_FIXED_VARIANT = "#8B1817"

    # --- Erreur ---
    ERROR = "#BA1A1A"
    ON_ERROR = "#FFFFFF"
    ERROR_CONTAINER = "#FFDAD6"
    ON_ERROR_CONTAINER = "#93000A"

    # --- Surfaces (fonds, pas des couleurs d'icônes, mais utiles
    #     pour les widgets qui s'appuient sur icons.py) ---
    SURFACE = "#F8F9FF"
    BACKGROUND = "#F8F9FF"
    SURFACE_DIM = "#CBDBF5"
    SURFACE_BRIGHT = "#F8F9FF"
    SURFACE_CONTAINER_LOWEST = "#FFFFFF"
    SURFACE_CONTAINER_LOW = "#EFF4FF"
    SURFACE_CONTAINER = "#E5EEFF"
    SURFACE_CONTAINER_HIGH = "#DCE9FF"
    SURFACE_CONTAINER_HIGHEST = "#D3E4FE"
    SURFACE_VARIANT = "#D3E4FE"


# ============================================================
# COULEURS NOMMÉES
# ============================================================

COLOR_MAP = {
    "white": IconColors.WHITE,
    "light": IconColors.LIGHT,
    "active": IconColors.ACTIVE,
    "inactive": IconColors.INACTIVE,

    "on_surface": IconColors.ON_SURFACE,
    "on_surface_variant": IconColors.ON_SURFACE_VARIANT,
    "outline": IconColors.OUTLINE,
    "outline_variant": IconColors.OUTLINE_VARIANT,
    "inverse_surface": IconColors.INVERSE_SURFACE,

    "primary": IconColors.PRIMARY,
    "on_primary": IconColors.ON_PRIMARY,
    "primary_container": IconColors.PRIMARY_CONTAINER,
    "on_primary_container": IconColors.ON_PRIMARY_CONTAINER,
    "primary_fixed": IconColors.PRIMARY_FIXED,
    "primary_fixed_dim": IconColors.PRIMARY_FIXED_DIM,

    "secondary": IconColors.SECONDARY,
    "on_secondary": IconColors.ON_SECONDARY,
    "secondary_container": IconColors.SECONDARY_CONTAINER,
    "on_secondary_container": IconColors.ON_SECONDARY_CONTAINER,
    "secondary_fixed": IconColors.SECONDARY_FIXED,
    "secondary_fixed_dim": IconColors.SECONDARY_FIXED_DIM,

    "tertiary": IconColors.TERTIARY,
    "on_tertiary": IconColors.ON_TERTIARY,
    "tertiary_container": IconColors.TERTIARY_CONTAINER,
    "on_tertiary_container": IconColors.ON_TERTIARY_CONTAINER,

    "error": IconColors.ERROR,
    "on_error": IconColors.ON_ERROR,
    "error_container": IconColors.ERROR_CONTAINER,
    "on_error_container": IconColors.ON_ERROR_CONTAINER,

    "dark": IconColors.ON_SURFACE,
    "surface": IconColors.ON_SURFACE_VARIANT,
}


# ============================================================
# ICÔNES SÉMANTIQUES SMART RH
#
# Le code peut utiliser :
#
# IconLabel("dashboard")
# IconLabel("employees")
# IconLabel("recruitment")
#
# sans dépendre directement du nom du fichier SVG.
#
# Les 77 icônes issues de la maquette sont référencées avec le
# préfixe "ic_" (nom réel des fichiers dans assets/icons).
# Les anciens noms sans préfixe sont conservés en dernier recours,
# au cas où d'autres icônes (hors maquette) existeraient déjà
# dans le dossier.
# ============================================================

ICON_ALIASES = {

    # --------------------------------------------------------
    # NAVIGATION PRINCIPALE (identique à la sidebar de la maquette)
    # --------------------------------------------------------

    "dashboard": ["ic_space_dashboard.svg", "space_dashboard.svg", "dashboard.svg", "home.svg"],
    "accueil": ["ic_space_dashboard.svg", "space_dashboard.svg", "dashboard.svg", "home.svg"],

    "employees": ["ic_groups.svg", "groups.svg", "ic_group.svg", "group.svg", "people.svg", "person.svg"],
    "employes": ["ic_groups.svg", "groups.svg", "ic_group.svg", "group.svg", "people.svg", "person.svg"],

    "recruitment": ["ic_person_search.svg", "person_search.svg", "ic_person_add.svg", "person_add.svg", "ic_groups.svg", "groups.svg"],
    "recrutement": ["ic_person_search.svg", "person_search.svg", "ic_person_add.svg", "person_add.svg", "ic_groups.svg", "groups.svg"],
    "recruitment_ai": ["ic_person_search.svg", "person_search.svg", "ic_psychology.svg", "psychology.svg", "ic_psychology_alt.svg", "psychology_alt.svg"],
    "recrutement_ia": ["ic_person_search.svg", "person_search.svg", "ic_psychology.svg", "psychology.svg", "ic_psychology_alt.svg", "psychology_alt.svg"],

    "smartmatch": ["ic_auto_awesome.svg", "auto_awesome.svg", "ic_psychology.svg", "psychology.svg", "ic_psychology_alt.svg", "psychology_alt.svg"],
    "smartmatch_ai": ["ic_auto_awesome.svg", "auto_awesome.svg", "ic_psychology.svg", "psychology.svg", "ic_psychology_alt.svg", "psychology_alt.svg"],
    "smartmatch_ia": ["ic_auto_awesome.svg", "auto_awesome.svg", "ic_psychology.svg", "psychology.svg", "ic_psychology_alt.svg", "psychology_alt.svg"],

    "analytics": ["ic_insights.svg", "insights.svg", "analytics.svg", "bar_chart.svg"],
    "rapports": ["ic_insights.svg", "insights.svg", "analytics.svg", "bar_chart.svg"],

    "turnover": ["ic_sync_alt.svg", "sync_alt.svg", "ic_trending_up.svg", "trending_up.svg", "autorenew.svg"],
    "risques": ["ic_warning.svg", "warning.svg", "warning_amber.svg", "error.svg"],

    "relations": ["ic_hub.svg", "hub.svg", "account_tree.svg", "ic_share.svg", "share.svg"],

    "settings": ["ic_tune.svg", "tune.svg", "settings.svg"],

    # --------------------------------------------------------
    # EMPLOYÉS / COLLABORATEURS
    # --------------------------------------------------------

    "person": ["ic_person.svg", "person.svg"],
    "employee": ["ic_person.svg", "person.svg", "person_outline.svg"],

    "group": ["ic_group.svg", "group.svg", "ic_groups.svg", "groups.svg"],
    "groups": ["ic_groups.svg", "groups.svg", "ic_group.svg", "group.svg"],

    "add_employee": ["ic_person_add.svg", "person_add.svg", "ic_add.svg", "add.svg"],
    "person_add": ["ic_person_add.svg", "person_add.svg", "ic_add.svg", "add.svg"],

    "supervisor": ["ic_supervisor_account.svg", "supervisor_account.svg"],
    "diversity": ["ic_diversity_3.svg", "diversity_3.svg", "ic_diversity_1.svg", "diversity_1.svg"],
    "badge": ["ic_badge.svg", "badge.svg"],
    "shield_person": ["ic_shield_person.svg", "shield_person.svg"],

    "delete": ["delete.svg", "delete_outline.svg"],
    "edit": ["edit.svg", "edit_square.svg", "ic_edit_document.svg", "edit_document.svg"],
    "search": ["search.svg"],
    "filter": ["ic_filter_list.svg", "filter_list.svg", "filter_alt.svg"],
    "sort": ["ic_sort.svg", "sort.svg"],

    # --------------------------------------------------------
    # RECRUTEMENT
    # --------------------------------------------------------

    "cv": ["ic_description.svg", "description.svg", "article.svg", "contact_page.svg"],
    "pdf": ["ic_picture_as_pdf.svg", "picture_as_pdf.svg"],

    "candidate": ["ic_person_search.svg", "person_search.svg", "ic_person.svg", "person.svg"],
    "candidates": ["ic_groups.svg", "groups.svg", "ic_person_search.svg", "person_search.svg"],

    "upload": ["upload.svg", "file_upload.svg"],
    "download": ["download.svg", "file_download.svg"],

    "screening": ["ic_psychology.svg", "psychology.svg", "ic_person_search.svg", "person_search.svg"],

    "ai": ["ic_psychology.svg", "psychology.svg", "ic_psychology_alt.svg", "psychology_alt.svg", "ic_auto_awesome.svg", "auto_awesome.svg", "ic_smart_toy.svg", "smart_toy.svg"],
    "psychology": ["ic_psychology.svg", "psychology.svg"],
    "psychology_alt": ["ic_psychology_alt.svg", "psychology_alt.svg", "ic_psychology.svg", "psychology.svg"],
    "auto_awesome": ["ic_auto_awesome.svg", "auto_awesome.svg", "stars.svg"],
    "smart_toy": ["ic_smart_toy.svg", "smart_toy.svg", "ic_psychology.svg", "psychology.svg"],

    "school": ["ic_school.svg", "school.svg"],
    "handshake": ["ic_handshake.svg", "handshake.svg"],
    "corporate_fare": ["ic_corporate_fare.svg", "corporate_fare.svg"],
    "domain": ["ic_domain.svg", "domain.svg"],
    "apartment": ["ic_apartment.svg", "apartment.svg"],

    # --------------------------------------------------------
    # KPI / TABLEAU DE BORD
    # --------------------------------------------------------

    "total_employees": ["ic_group.svg", "group.svg", "ic_groups.svg", "groups.svg", "ic_person.svg", "person.svg"],

    "absences": ["ic_calendar_month.svg", "calendar_month.svg", "ic_event_busy.svg", "event_busy.svg"],
    "calendar": ["ic_calendar_month.svg", "calendar_month.svg", "calendar_today.svg"],
    "event_busy": ["ic_event_busy.svg", "event_busy.svg", "ic_calendar_month.svg", "calendar_month.svg"],

    "recruitment_kpi": ["ic_track_changes.svg", "track_changes.svg", "ic_person_search.svg", "person_search.svg"],
    "track_changes": ["ic_track_changes.svg", "track_changes.svg", "ic_target.svg", "target.svg"],
    "target": ["ic_target.svg", "target.svg"],

    "turnover_kpi": ["ic_sync_alt.svg", "sync_alt.svg", "ic_trending_up.svg", "trending_up.svg"],
    "sync_alt": ["ic_sync_alt.svg", "sync_alt.svg", "ic_sync.svg", "sync.svg"],
    "sync": ["ic_sync.svg", "sync.svg"],

    "preselection": ["ic_psychology_alt.svg", "psychology_alt.svg", "ic_psychology.svg", "psychology.svg"],

    "stacked_line_chart": ["ic_stacked_line_chart.svg", "stacked_line_chart.svg"],
    "dataset": ["ic_dataset.svg", "dataset.svg"],
    "trending_up": ["ic_trending_up.svg", "trending_up.svg"],
    "trending_down": ["ic_trending_down.svg", "trending_down.svg"],
    "bolt": ["ic_bolt.svg", "bolt.svg"],
    "flash_on": ["ic_flash_on.svg", "flash_on.svg"],
    "local_fire_department": ["ic_local_fire_department.svg", "local_fire_department.svg"],
    "priority_high": ["ic_priority_high.svg", "priority_high.svg"],
    "hourglass": ["ic_hourglass_empty.svg", "hourglass_empty.svg"],
    "history": ["ic_history.svg", "history.svg"],

    # --------------------------------------------------------
    # ALERTES / STATUTS
    # --------------------------------------------------------

    "warning": ["ic_warning.svg", "warning.svg", "warning_amber.svg"],
    "error": ["error.svg", "error_outline.svg"],

    "notification": ["ic_notifications.svg", "notifications.svg", "notifications_none.svg"],
    "notifications": ["ic_notifications.svg", "notifications.svg", "notifications_none.svg"],
    "notifications_active": ["ic_notifications_active.svg", "notifications_active.svg", "ic_notifications.svg", "notifications.svg"],
    "notification_important": ["ic_notification_important.svg", "notification_important.svg", "ic_notifications_active.svg", "notifications_active.svg"],

    "verified": ["ic_verified.svg", "verified.svg"],
    "verified_user": ["ic_verified_user.svg", "verified_user.svg", "ic_verified.svg", "verified.svg"],
    "info": ["ic_info.svg", "info.svg"],
    "star": ["ic_star.svg", "star.svg"],
    "favorite": ["ic_favorite.svg", "favorite.svg"],

    # --------------------------------------------------------
    # ACTIONS
    # --------------------------------------------------------

    "add": ["ic_add.svg", "add.svg"],
    "add_circle": ["ic_add_circle.svg", "add_circle.svg"],
    "close": ["ic_close.svg", "close.svg"],

    "check": ["ic_check.svg", "check.svg", "done.svg"],
    "check_circle": ["ic_check_circle.svg", "check_circle.svg", "ic_check.svg", "check.svg"],
    "done": ["done.svg", "ic_check.svg", "check.svg"],
    "done_all": ["ic_done_all.svg", "done_all.svg", "ic_check_circle.svg", "check_circle.svg"],

    "refresh": ["ic_refresh.svg", "refresh.svg", "ic_sync.svg", "sync.svg"],
    "restart": ["ic_restart_alt.svg", "restart_alt.svg", "ic_refresh.svg", "refresh.svg"],

    "arrow_forward": ["ic_arrow_forward.svg", "arrow_forward.svg", "ic_chevron_right.svg", "chevron_right.svg"],
    "arrow_back": ["ic_arrow_back.svg", "arrow_back.svg", "ic_chevron_left.svg", "chevron_left.svg"],
    "chevron_left": ["ic_chevron_left.svg", "chevron_left.svg"],
    "chevron_right": ["ic_chevron_right.svg", "chevron_right.svg"],

    "expand_more": ["ic_expand_more.svg", "expand_more.svg", "keyboard_arrow_down.svg"],
    "expand_less": ["expand_less.svg", "keyboard_arrow_up.svg"],

    "send": ["ic_send.svg", "send.svg"],
    "share": ["ic_share.svg", "share.svg"],
    "link": ["ic_link.svg", "link.svg"],
    "visibility": ["ic_visibility.svg", "visibility.svg"],

    # --------------------------------------------------------
    # CONTACT / COMMUNICATION
    # --------------------------------------------------------

    "mail": ["ic_mail.svg", "mail.svg"],
    "call": ["ic_call.svg", "call.svg"],
    "chat": ["ic_chat.svg", "chat.svg"],
    "chat_bubble": ["ic_chat_bubble_outline.svg", "chat_bubble_outline.svg", "ic_chat.svg", "chat.svg"],
    "location": ["ic_location_on.svg", "location_on.svg"],
    "cake": ["ic_cake.svg", "cake.svg"],
    "payments": ["ic_payments.svg", "payments.svg"],

    # --------------------------------------------------------
    # ANALYSE
    # --------------------------------------------------------

    "insights": ["ic_insights.svg", "insights.svg", "analytics.svg"],
    "hub": ["ic_hub.svg", "hub.svg", "account_tree.svg"],
}


# ============================================================
# COMPATIBILITÉ AVEC LES ANCIENS EMOJIS
#
# Aucun emoji n'est affiché.
# Si l'ancien code fait :
#
# IconLabel("👥")
#
# il sera automatiquement transformé en l'alias "groups".
# ============================================================

LEGACY_EMOJI_MAP = {

    "👥": "groups",
    "👤": "person",
    "➕": "add",
    "✏️": "edit",
    "🗑️": "delete",
    "🔍": "search",
    "⚠️": "warning",
    "🔔": "notifications",
    "📅": "calendar",
    "🧠": "psychology",
    "✨": "auto_awesome",
    "📊": "analytics",
    "🔄": "sync_alt",
    "✓": "check",
    "✔": "check_circle",
    "→": "arrow_forward",
    "←": "arrow_back",
    "⚙️": "settings",
    "📄": "cv",
    "⬆️": "upload",
    "⬇️": "download",
}


# ============================================================
# is_emoji
#
# Conservée pour ne pas casser les anciens imports.
# ============================================================

def is_emoji(value):
    """
    Détermine approximativement si une chaîne correspond
    à un ancien emoji utilisé par l'application.

    Important :
    cette fonction ne provoque jamais l'affichage de l'emoji.
    """

    if not isinstance(value, str):
        return False

    return value in LEGACY_EMOJI_MAP


# ============================================================
# NORMALISATION
# ============================================================

def normalize_icon_name(icon_name):
    """
    Transforme un nom d'icône en nom utilisable (sans .svg,
    sans chemin, sans préfixe "ic_").
    """

    if icon_name is None:
        return None

    if not isinstance(icon_name, str):
        return str(icon_name)

    icon_name = icon_name.strip()

    # Ancien emoji
    if icon_name in LEGACY_EMOJI_MAP:
        return LEGACY_EMOJI_MAP[icon_name]

    # Supprime éventuellement le chemin
    icon_name = Path(icon_name).name

    # Supprime .svg
    if icon_name.lower().endswith(".svg"):
        icon_name = icon_name[:-4]

    # Normalise le préfixe "ic_" pour que "ic_person" et "person"
    # pointent vers la même icône
    if icon_name.lower().startswith(MOCKUP_ICON_PREFIX):
        icon_name = icon_name[len(MOCKUP_ICON_PREFIX):]

    return icon_name.lower()


# ============================================================
# RECHERCHE D'ICÔNE
# ============================================================

def resolve_icon_path(icon_name):
    """
    Retourne le fichier SVG correspondant à l'icône.

    Ordre de résolution :
        1. ic_{nom}.svg   (fichier réel issu de la maquette)
        2. {nom}.svg       (ancien nom sans préfixe, compatibilité)
        3. Alias déclarés dans ICON_ALIASES
        4. Recherche insensible à la casse dans le dossier
    """

    if not icon_name:
        return None

    normalized = normalize_icon_name(icon_name)

    if not normalized:
        return None

    # --------------------------------------------------------
    # 1. Fichier de la maquette (préfixe ic_)
    # --------------------------------------------------------

    prefixed_path = ICONS_DIR / f"{MOCKUP_ICON_PREFIX}{normalized}.svg"

    if prefixed_path.exists():
        return prefixed_path

    # --------------------------------------------------------
    # 2. Nom direct, sans préfixe (compatibilité anciens fichiers)
    # --------------------------------------------------------

    direct_path = ICONS_DIR / f"{normalized}.svg"

    if direct_path.exists():
        return direct_path

    # --------------------------------------------------------
    # 3. Recherche dans les alias
    # --------------------------------------------------------

    aliases = ICON_ALIASES.get(normalized, [])

    for filename in aliases:

        path = ICONS_DIR / filename

        if path.exists():
            return path

    # --------------------------------------------------------
    # 4. Recherche insensible à la casse
    # --------------------------------------------------------

    if ICONS_DIR.exists():

        targets = {
            f"{MOCKUP_ICON_PREFIX}{normalized}.svg".lower(),
            f"{normalized}.svg".lower(),
        }

        for file in ICONS_DIR.iterdir():

            if file.is_file() and file.name.lower() in targets:
                return file

    return None


# ============================================================
# EXISTENCE
# ============================================================

def icon_exists(icon_name):
    """
    Vérifie si une icône existe.
    """

    return resolve_icon_path(icon_name) is not None


def image_exists(icon_name):
    """
    Alias historique.
    """

    return icon_exists(icon_name)


# ============================================================
# COULEUR
# ============================================================

def resolve_color(color):
    """
    Transforme :
        "white"
        "primary"
        "#FFFFFF"

    en couleur hexadécimale.
    """

    if isinstance(color, QColor):
        return color.name()

    if color is None:
        return IconColors.WHITE

    if not isinstance(color, str):
        return IconColors.WHITE

    color = color.strip()

    return COLOR_MAP.get(color.lower(), color)


# ============================================================
# COLORATION SVG
# ============================================================

def _recolor_svg(svg_data, color):
    """
    Recolore les éléments SVG.

    Les couleurs courantes :
        fill="#..."
        stroke="#..."
        fill="..."
        stroke="..."

    sont remplacées par la couleur demandée.

    Cela permet notamment de rendre les icônes blanches
    sans modifier physiquement les fichiers SVG — la couleur
    de base du fichier (ex: le teal de la maquette) n'a donc
    aucune importance : elle est toujours écrasée ici.
    """

    color = resolve_color(color)

    text = svg_data.decode("utf-8", errors="ignore")

    # --------------------------------------------------------
    # Remplacement des fill
    # --------------------------------------------------------

    text = re.sub(
        r'fill\s*=\s*["\'][^"\']*["\']',
        f'fill="{color}"',
        text,
        flags=re.IGNORECASE
    )

    # --------------------------------------------------------
    # Remplacement des stroke
    # --------------------------------------------------------

    text = re.sub(
        r'stroke\s*=\s*["\'][^"\']*["\']',
        f'stroke="{color}"',
        text,
        flags=re.IGNORECASE
    )

    # --------------------------------------------------------
    # Cas des styles CSS internes
    # --------------------------------------------------------

    text = re.sub(
        r'fill\s*:\s*#[0-9a-fA-F]{3,8}',
        f'fill:{color}',
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r'stroke\s*:\s*#[0-9a-fA-F]{3,8}',
        f'stroke:{color}',
        text,
        flags=re.IGNORECASE
    )

    return text.encode("utf-8")


# ============================================================
# RENDU SVG
# ============================================================

def svg_to_pixmap(path, size=24, color=IconColors.WHITE):
    """
    Transforme un SVG en QPixmap avec la couleur demandée.
    """

    if not path:
        return QPixmap()

    if not Path(path).exists():
        return QPixmap()

    if not SVG_AVAILABLE:
        return QPixmap()

    try:

        with open(path, "rb") as file:
            svg_data = file.read()

        # Recoloration
        svg_data = _recolor_svg(
            svg_data,
            color
        )

        renderer = QSvgRenderer(svg_data)

        if not renderer.isValid():
            return QPixmap()

        pixmap = QPixmap(size, size)

        pixmap.fill(
            Qt.GlobalColor.transparent
        )

        painter = QPainter(pixmap)

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        renderer.render(
            painter
        )

        painter.end()

        return pixmap

    except Exception:
        return QPixmap()


# ============================================================
# ICONLABEL
# ============================================================

class IconLabel(QLabel):
    def __init__(
        self,
        icon_name=None,
        size=24,
        parent=None,
        color=IconColors.WHITE,
        tooltip=None,
        fallback=None,
        object_name=None
    ):
        super().__init__(parent)

        self.icon_name = icon_name
        self.icon_size = size
        self.icon_color = color
        self.fallback = fallback

        # Compatibilité avec les widgets existants
        if object_name:
            self.setObjectName(object_name)

        self.setFixedSize(QSize(size, size))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                padding: 0;
                margin: 0;
            }
        """)

        if tooltip:
            self.setToolTip(tooltip)

        if icon_name:
            self.set_icon(
                icon_name,
                color=color,
                size=size,
                fallback=fallback
            )

    def set_icon(
        self,
        icon_name,
        color=None,
        size=None,
        fallback=None
    ):
        if color is None:
            color = self.icon_color

        if size is None:
            size = self.icon_size

        if fallback is None:
            fallback = self.fallback

        self.icon_name = icon_name
        self.icon_color = color
        self.icon_size = size
        self.fallback = fallback

        path = resolve_icon_path(icon_name)

        # Utilise le fallback si l'icône principale n'existe pas
        if path is None and fallback:
            path = resolve_icon_path(fallback)

        if path is None:
            self.clear()
            return False

        pixmap = svg_to_pixmap(
            path,
            size=size,
            color=color
        )

        if pixmap.isNull():
            self.clear()
            return False

        self.setPixmap(pixmap)
        return True

    def set_color(self, color):
        self.icon_color = color

        return self.set_icon(
            self.icon_name,
            color=color,
            size=self.icon_size,
            fallback=self.fallback
        )

    def set_icon_size(self, size):
        self.icon_size = size
        self.setFixedSize(QSize(size, size))

        return self.set_icon(
            self.icon_name,
            color=self.icon_color,
            size=size,
            fallback=self.fallback
        )


# ============================================================
# QICON
# ============================================================

def get_icon(
    icon_name,
    color=IconColors.WHITE,
    size=24
):
    """
    Retourne un QIcon coloré.

    Exemple :

        icon = get_icon(
            "groups",
            "white",
            24
        )

        button.setIcon(icon)
    """

    path = resolve_icon_path(
        icon_name
    )

    if path is None:
        return QIcon()

    pixmap = svg_to_pixmap(
        path,
        size=size,
        color=color
    )

    if pixmap.isNull():
        return QIcon()

    return QIcon(
        pixmap
    )


# ============================================================
# get_icon_path
# ============================================================

def get_icon_path(icon_name):

    path = resolve_icon_path(
        icon_name
    )

    if path is None:
        return None

    return str(path)


# ============================================================
# NAVIGATION — reproduit exactement la sidebar de la maquette
#
# 7 écrans, dans l'ordre où ils apparaissent, avec la même
# icône et le même libellé que dans le code des maquettes.
# ============================================================

SIDEBAR_NAV_ITEMS = [
    {"key": "accueil",         "icon": "space_dashboard", "label": "Accueil"},
    {"key": "employes",        "icon": "groups",          "label": "Employés"},
    {"key": "recrutement_ia",  "icon": "person_search",   "label": "Recrutement IA"},
    {"key": "smartmatch_ia",   "icon": "auto_awesome",    "label": "SmartMatch IA"},
    {"key": "rapports",        "icon": "insights",        "label": "Rapports & Analytics"},
    {"key": "risques",         "icon": "warning",         "label": "Risques & Turnover"},
    {"key": "relations",       "icon": "hub",             "label": "Liens & Relations"},
]


# ============================================================
# CONFIGURATION RAPIDE DES ICÔNES
#
# Ces fonctions reprennent les rôles de couleur réellement
# utilisés sur les icônes dans la maquette (relevés dans le
# code des 8 écrans) :
#   - primary          : action/état principal (le plus fréquent)
#   - on_primary        : icône blanche sur médaillon/avatar teal
#   - secondary         : icônes discrètes (mail, historique, appel...)
#   - outline           : icônes très discrètes (badge, chevrons...)
#   - tertiary          : alertes (notifications, PDF, warning)
# ============================================================

def sidebar_icon(
    icon_name,
    active=False,
    size=20
):
    """
    Icône spécialement destinée à la sidebar.

    Actif :
        #AAFFE9  (on-primary-container)

    Inactif :
        #BEC5E5  (secondary-fixed-dim)
    """

    color = (
        IconColors.ACTIVE
        if active
        else IconColors.INACTIVE
    )

    return IconLabel(
        icon_name,
        size=size,
        color=color
    )


def white_icon(
    icon_name,
    size=20
):
    """
    Icône blanche.
    """

    return IconLabel(
        icon_name,
        size=size,
        color=IconColors.WHITE
    )


def primary_icon(
    icon_name,
    size=20
):
    """
    Icône teal principale — rôle de couleur le plus utilisé
    dans la maquette (psychology, verified, trending_up, target,
    sync, send, refresh, person_add, info, description...).
    """

    return IconLabel(
        icon_name,
        size=size,
        color=IconColors.PRIMARY
    )


def on_primary_icon(
    icon_name,
    size=20
):
    """
    Icône blanche destinée à être posée sur un médaillon/avatar
    de couleur teal (ex: icône "person" dans un cercle plein).
    """

    return IconLabel(
        icon_name,
        size=size,
        color=IconColors.ON_PRIMARY
    )


def secondary_icon(
    icon_name,
    size=20
):
    """
    Icône secondaire (violet-gris) — utilisée pour les éléments
    de contact et de métadonnées : mail, call, chat, history,
    location_on, event_busy, hourglass_empty, supervisor_account...
    """

    return IconLabel(
        icon_name,
        size=size,
        color=IconColors.SECONDARY
    )


def outline_icon(
    icon_name,
    size=20
):
    """
    Icône très discrète (badge, expand_more, share...).
    """

    return IconLabel(
        icon_name,
        size=size,
        color=IconColors.OUTLINE
    )


def ai_icon(
    icon_name="psychology",
    size=20
):
    """
    Icône IA — teal container.
    """

    return IconLabel(
        icon_name,
        size=size,
        color=IconColors.PRIMARY_CONTAINER
    )


def warning_icon(
    icon_name="warning",
    size=20
):
    """
    Icône d'alerte / signal préventif (tertiary — corail sombre).
    Utilisée dans la maquette pour : notifications, notification_important,
    picture_as_pdf, warning.
    """

    return IconLabel(
        icon_name,
        size=size,
        color=IconColors.TERTIARY
    )


def error_icon(
    icon_name="warning",
    size=20
):
    """
    Icône d'erreur critique.
    """

    return IconLabel(
        icon_name,
        size=size,
        color=IconColors.ERROR
    )


# ============================================================
# DEBUG
# ============================================================

def debug_icons():
    """
    Diagnostic complet des icônes.

    À lancer avec :

        python -c "from app.ui.icons import debug_icons; debug_icons()"
    """

    print()
    print("=" * 60)
    print("SMART RH - DIAGNOSTIC DES ICONES")
    print("=" * 60)

    print()
    print("BASE_DIR :")
    print(BASE_DIR)

    print()
    print("ICONS_DIR :")
    print(ICONS_DIR)

    print()
    print("Dossier existe :")

    if ICONS_DIR.exists():
        print("[OK] Oui")
    else:
        print("[ERREUR] Dossier introuvable")

    print()
    print("SVG trouvés :")

    if ICONS_DIR.exists():

        svg_files = list(
            ICONS_DIR.glob("*.svg")
        )

        if not svg_files:

            print("[ERREUR] Aucun fichier SVG")

        else:

            for file in sorted(svg_files):
                print(
                    f"  [OK] {file.name}"
                )

    print()
    print("TEST DES ICONES DE LA MAQUETTE (sidebar + usages courants) :")

    tests = [
        "accueil",
        "employes",
        "recrutement_ia",
        "smartmatch_ia",
        "rapports",
        "risques",
        "relations",
        "person",
        "person_search",
        "psychology",
        "auto_awesome",
        "insights",
        "warning",
        "hub",
        "calendar",
        "notifications",
        "notification_important",
        "verified_user",
        "trending_up",
        "trending_down",
        "target",
        "sync_alt",
        "badge",
        "mail",
        "call",
        "history",
        "settings",
        "add",
        "edit",
        "delete",
        "search",
    ]

    for name in tests:

        path = resolve_icon_path(
            name
        )

        if path:

            print(
                f"  [OK] {name:<20} -> {path.name}"
            )

        else:

            print(
                f"  [ERREUR] {name:<20} -> introuvable"
            )

    print()
    print("=" * 60)
    print("FIN DU DIAGNOSTIC")
    print("=" * 60)
    print()


# ============================================================
# FIN
# ============================================================