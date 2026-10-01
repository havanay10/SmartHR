"""Page Liens — Relations entre employes.

Palette couleurs coherente par type de relation :
- Ami(e)            → Bleu ciel      (#2E86DE)
- Ancien collegue   → Gris ardoise   (#64748B)
- Collegue          → Teal           (#0D7A6A)
- En couple         → Rose/Rouge     (#E91E63)
- Famille           → Orange        (#F39C12)
- Mentor/Mentore    → Violet         (#7C3AED)
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QScrollArea, QFrame, QLabel, QPushButton, QMessageBox,
    QDialog, QComboBox, QLineEdit, QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSignal

from app.services.relationship_service import RelationshipService, RELATION_TYPES
from app.services.audit_service import AuditService


# =====================================================
# PALETTE COULEURS PAR TYPE DE RELATION
# =====================================================
# Format : (background, foreground)
RELATION_PALETTE = {
    "ami": {
        "color": "#2E86DE",
        "bg": "#E0F0FF",
        "letter": "A",
        "label": "Ami(e)",
    },
    "amie": {
        "color": "#2E86DE",
        "bg": "#E0F0FF",
        "letter": "A",
        "label": "Ami(e)",
    },
    "collegue": {
        "color": "#0D7A6A",
        "bg": "#E8F5F1",
        "letter": "C",
        "label": "Collègue",
    },
    "ancien_collegue": {
        "color": "#64748B",
        "bg": "#F1F5F9",
        "letter": "C",
        "label": "Ancien collègue",
    },
    "couple": {
        "color": "#E91E63",
        "bg": "#FCE7F0",
        "letter": "C",
        "label": "En couple",
    },
    "famille": {
        "color": "#F39C12",
        "bg": "#FEF3C7",
        "letter": "F",
        "label": "Famille",
    },
    "mentor": {
        "color": "#7C3AED",
        "bg": "#EDE9FE",
        "letter": "M",
        "label": "Mentor / Mentoré",
    },
    "mentore": {
        "color": "#7C3AED",
        "bg": "#EDE9FE",
        "letter": "M",
        "label": "Mentor / Mentoré",
    },
}


def get_relation_style(rel_type: str) -> dict:
    """Retourne le style (color, bg, letter, label) pour un type donne."""
    key = (rel_type or "").lower().strip()
    if key in RELATION_PALETTE:
        return RELATION_PALETTE[key]
    # Fallback neutre
    return {
        "color": "#64748B",
        "bg": "#F1F5F9",
        "letter": "•",
        "label": (rel_type or "Relation").capitalize(),
    }


# =====================================================
# HELPERS VISUELS
# =====================================================
class ColorDot(QFrame):
    def __init__(self, color: str, size: int = 8):
        super().__init__()
        self.setFixedSize(size, size)
        self.setStyleSheet(f"""
            background-color: {color};
            border-radius: {size // 2}px;
            border: none;
        """)


class IconSquare(QLabel):
    def __init__(self, letter: str, color: str, bg: str, size: int = 36):
        super().__init__()
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText(letter)
        self.setStyleSheet(f"""
            background-color: {bg};
            color: {color};
            border-radius: {size // 3}px;
            font-size: {size // 3}pt;
            font-weight: 800;
            border: none;
        """)


class TypeIndicator(QLabel):
    def __init__(self, letter: str, color: str, bg: str, size: int = 44):
        super().__init__()
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText(letter)
        self.setStyleSheet(f"""
            background-color: {bg};
            color: {color};
            border-radius: 10px;
            font-size: {size // 3}pt;
            font-weight: 800;
            border: none;
        """)


class InitialsAvatar(QLabel):
    """Avatar rond avec initiales (couleur déterministe)."""

    def __init__(self, name: str, size: int = 32):
        super().__init__()
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        parts = (name or "?").split(" ", 1)
        first = parts[0] if len(parts) > 0 else "?"
        last = parts[1] if len(parts) > 1 else ""

        initials = f"{first[:1]}{last[:1]}".upper() if last else first[:2].upper()

        # Palette plus sobre et moderne pour les avatars
        colors = ["#0D7A6A", "#1F4E5F", "#2E86DE", "#7C3AED", "#B9770E", "#64748B"]
        idx = sum(ord(c) for c in initials) % len(colors)
        color = colors[idx]

        self.setText(initials)
        self.setStyleSheet(f"""
            background-color: {color};
            color: white;
            border-radius: {size // 2}px;
            font-size: {size // 3}pt;
            font-weight: 800;
            border: none;
        """)


# =====================================================
# DIALOGUE NOUVELLE RELATION
# =====================================================
class AddRelationDialog(QDialog):
    def __init__(self, employees: list, parent=None):
        super().__init__(parent)
        self.employees = employees
        self.result_data = None

        self.setWindowTitle("Nouvelle relation")
        self.setFixedSize(520, 400)
        self.setStyleSheet("QDialog { background-color: #FFFFFF; }")

        self._setup_ui()

    def _setup_ui(self):
        v = QVBoxLayout(self)
        v.setContentsMargins(28, 24, 28, 24)
        v.setSpacing(18)

        title = QLabel("Créer une nouvelle relation")
        title.setStyleSheet("""
            font-size: 15pt; font-weight: 800; color: #0F1E2E;
            background: transparent; border: none;
        """)
        v.addWidget(title)

        sub = QLabel("Associez deux collaborateurs et définissez la nature du lien")
        sub.setStyleSheet("""
            font-size: 9.5pt; color: #7A8B9C;
            background: transparent; border: none;
        """)
        v.addWidget(sub)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #EEF2F6; border: none;")
        v.addWidget(sep)

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)

        self.combo_a = QComboBox()
        for e in self.employees:
            self.combo_a.addItem(f"{e['name']} — {e['job_title']}", e["id"])
        self.combo_a.setStyleSheet(self._input_style())
        form.addRow(self._form_label("Employé 1"), self.combo_a)

        self.combo_b = QComboBox()
        for e in self.employees:
            self.combo_b.addItem(f"{e['name']} — {e['job_title']}", e["id"])
        self.combo_b.setStyleSheet(self._input_style())
        form.addRow(self._form_label("Employé 2"), self.combo_b)

        self.combo_type = QComboBox()
        for key in RELATION_PALETTE.keys():
            style = RELATION_PALETTE[key]
            # Évite les doublons ami/amie
            if key == "amie":
                continue
            self.combo_type.addItem(style["label"], key)
        self.combo_type.setStyleSheet(self._input_style())
        form.addRow(self._form_label("Type de relation"), self.combo_type)

        self.line_notes = QLineEdit()
        self.line_notes.setPlaceholderText("Notes (optionnel)")
        self.line_notes.setStyleSheet(self._input_style())
        form.addRow(self._form_label("Notes"), self.line_notes)

        v.addLayout(form)
        v.addStretch()

        btns = QHBoxLayout()
        btns.addStretch()

        btn_cancel = QPushButton("Annuler")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setMinimumHeight(40)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #5A6B7D;
                border: 1px solid #E4E9EF;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 9.5pt;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #F4F6F9; }
        """)
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)

        btn_save = QPushButton("Créer la relation")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setMinimumHeight(40)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #0D7A6A;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 9.5pt;
                font-weight: 700;
            }
            QPushButton:hover { background-color: #0A6456; }
        """)
        btn_save.clicked.connect(self._on_submit)
        btns.addWidget(btn_save)

        v.addLayout(btns)

    def _form_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("""
            font-size: 9.5pt; color: #5A6B7D; font-weight: 700;
            background: transparent; border: none;
        """)
        return lbl

    def _input_style(self):
        return """
            QComboBox, QLineEdit {
                border: 1px solid #E4E9EF;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 9.5pt;
                background-color: #FFFFFF;
                color: #0F1E2E;
                min-height: 24px;
            }
            QComboBox:focus, QLineEdit:focus {
                border: 1px solid #0D7A6A;
            }
            QComboBox::drop-down { border: none; padding-right: 8px; }
        """

    def _on_submit(self):
        a = self.combo_a.currentData()
        b = self.combo_b.currentData()

        if a == b:
            QMessageBox.warning(self, "Attention",
                                "Les 2 employés doivent être différents.")
            return

        self.result_data = {
            "employee_a_id": a,
            "employee_b_id": b,
            "relation_type": self.combo_type.currentData(),
            "notes": self.line_notes.text().strip() or None,
        }
        self.accept()


# =====================================================
# LIGNE DE RELATION
# =====================================================
class RelationRow(QFrame):
    """Ligne pour une relation avec couleurs coherentes par type."""

    delete_requested = pyqtSignal(str)

    def __init__(self, relation: dict):
        super().__init__()
        self.relation = relation
        self.setMinimumHeight(100)

        rel_type = relation.get("relation_type", "")
        style = get_relation_style(rel_type)

        color = style["color"]
        bg = style["bg"]
        letter = style["letter"]
        label = style["label"]

        # Détection conflit
        dept_a = relation.get("employee_a_dept", "")
        dept_b = relation.get("employee_b_dept", "")
        is_conflict = (
            rel_type.lower() in ("couple", "famille")
            and dept_a and dept_b and dept_a == dept_b
        )

        border_left = color
        if is_conflict:
            border_left = "#C0392B"

        self.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border-radius: 10px;
                border: 1px solid #E4E9EF;
                border-left: 4px solid {border_left};
            }}
            QFrame:hover {{
                background-color: #FAFDFB;
                border: 1px solid #0D7A6A;
                border-left: 4px solid {border_left};
            }}
        """)

        h = QHBoxLayout(self)
        h.setContentsMargins(18, 14, 18, 14)
        h.setSpacing(16)

        # Indicateur de type (carré coloré avec lettre)
        indicator = TypeIndicator(letter, color, bg, size=44)
        h.addWidget(indicator, 0, Qt.AlignmentFlag.AlignVCenter)

        # Bloc central
        center = QVBoxLayout()
        center.setSpacing(6)

        # Ligne 1 : avatars + noms
        name_row = QHBoxLayout()
        name_row.setSpacing(10)

        name_a = relation.get("employee_a_name", "—")
        name_b = relation.get("employee_b_name", "—")

        name_row.addWidget(InitialsAvatar(name_a, size=32))

        name_a_lbl = QLabel(name_a)
        name_a_lbl.setStyleSheet("""
            font-size: 11pt; font-weight: 700; color: #0F1E2E;
            background: transparent; border: none;
        """)
        name_row.addWidget(name_a_lbl)

        sep_lbl = QLabel("—")
        sep_lbl.setStyleSheet("""
            font-size: 11pt; color: #B8C4D0; font-weight: 700;
            background: transparent; border: none;
            padding: 0 6px;
        """)
        name_row.addWidget(sep_lbl)

        name_row.addWidget(InitialsAvatar(name_b, size=32))

        name_b_lbl = QLabel(name_b)
        name_b_lbl.setStyleSheet("""
            font-size: 11pt; font-weight: 700; color: #0F1E2E;
            background: transparent; border: none;
        """)
        name_row.addWidget(name_b_lbl)

        if is_conflict:
            conflict_badge = QLabel("CONFLIT D'INTÉRÊTS")
            conflict_badge.setStyleSheet("""
                background-color: #FEE2E2;
                color: #C0392B;
                padding: 3px 10px;
                border-radius: 8px;
                font-size: 7.5pt;
                font-weight: 800;
                letter-spacing: 0.5px;
                border: 1px solid #FECACA;
            """)
            name_row.addWidget(conflict_badge)

        name_row.addStretch()
        center.addLayout(name_row)

        # Ligne 2 : départements
        dept_txt = f"{dept_a or '—'}  •  {dept_b or '—'}"
        sub_lbl = QLabel(dept_txt)
        sub_lbl.setStyleSheet("""
            font-size: 9pt; color: #7A8B9C;
            background: transparent; border: none;
            padding-left: 42px;
        """)
        center.addWidget(sub_lbl)

        # Ligne 3 : notes
        notes = relation.get("notes")
        if notes:
            notes_lbl = QLabel(notes)
            notes_lbl.setStyleSheet("""
                font-size: 8.5pt; color: #B8C4D0; font-style: italic;
                background: transparent; border: none;
                padding-left: 42px;
            """)
            notes_lbl.setWordWrap(True)
            center.addWidget(notes_lbl)

        h.addLayout(center, 1)

        # Badge type (avec pastille + texte)
        type_badge = QFrame()
        type_badge.setStyleSheet(f"""
            background-color: {bg};
            border-radius: 10px;
            border: 1px solid {color}60;
        """)
        tb_layout = QHBoxLayout(type_badge)
        tb_layout.setContentsMargins(12, 6, 16, 6)
        tb_layout.setSpacing(8)
        tb_layout.addWidget(ColorDot(color, 8))

        type_lbl = QLabel(label.upper())
        type_lbl.setStyleSheet(f"""
            background: transparent;
            color: {color};
            font-size: 8pt;
            font-weight: 800;
            letter-spacing: 0.8px;
            border: none;
        """)
        tb_layout.addWidget(type_lbl)

        h.addWidget(type_badge, 0, Qt.AlignmentFlag.AlignVCenter)

        # Bouton supprimer
        btn_del = QPushButton("✕")
        btn_del.setFixedSize(32, 32)
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setToolTip("Supprimer cette relation")
        btn_del.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #B8C4D0;
                border: none;
                border-radius: 16px;
                font-size: 13pt;
            }
            QPushButton:hover {
                background-color: #FADBD8;
                color: #C0392B;
            }
        """)
        btn_del.clicked.connect(
            lambda: self.delete_requested.emit(relation.get("id", ""))
        )
        h.addWidget(btn_del, 0, Qt.AlignmentFlag.AlignVCenter)


# =====================================================
# KPI CARD
# =====================================================
class KpiCardCustom(QFrame):
    def __init__(self, title: str, value: str, subtitle: str,
                 letter: str, accent: str):
        super().__init__()
        self.setMinimumHeight(130)

        # Palette cohérente avec la liste
        accent_map = {
            "green": ("#E8F5F1", "#0D7A6A"),      # Total
            "blue": ("#E0F0FF", "#2E86DE"),       # Amis
            "pink": ("#FCE7F0", "#E91E63"),       # Couples
            "orange": ("#FEF3C7", "#F39C12"),     # Familles
            "purple": ("#EDE9FE", "#7C3AED"),
            "gray": ("#F1F5F9", "#64748B"),
        }
        bg, fg = accent_map.get(accent, ("#F1F5F9", "#475569"))

        self.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
                border-top: 3px solid {fg};
            }}
        """)

        v = QVBoxLayout(self)
        v.setContentsMargins(20, 16, 20, 18)
        v.setSpacing(10)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        title_lbl = QLabel(title.upper())
        title_lbl.setStyleSheet("""
            font-size: 8.5pt; color: #5A6B7D; font-weight: 800;
            letter-spacing: 0.8px; background: transparent; border: none;
        """)
        top_row.addWidget(title_lbl)
        top_row.addStretch()

        top_row.addWidget(IconSquare(letter, fg, bg, size=34))
        v.addLayout(top_row)

        val_lbl = QLabel(value)
        val_lbl.setStyleSheet("""
            font-size: 26pt; font-weight: 800; color: #0F1E2E;
            background: transparent; border: none;
        """)
        v.addWidget(val_lbl)

        sub_lbl = QLabel(subtitle)
        sub_lbl.setStyleSheet("""
            font-size: 9pt; color: #7A8B9C;
            background: transparent; border: none;
        """)
        v.addWidget(sub_lbl)

        v.addStretch()


# =====================================================
# BOUTON FILTRE
# =====================================================
class FilterTab(QPushButton):
    def __init__(self, label: str, count: int, is_active: bool = False):
        super().__init__(f"{label} ({count})")
        self.setCheckable(True)
        self.setChecked(is_active)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(36)
        self._apply_style(is_active)

    def _apply_style(self, is_active: bool):
        if is_active:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #0F1E2E;
                    color: #FFFFFF;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 8px;
                    font-size: 9pt;
                    font-weight: 700;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    color: #5A6B7D;
                    border: 1px solid #E4E9EF;
                    padding: 8px 16px;
                    border-radius: 8px;
                    font-size: 9pt;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #F4F6F9;
                    color: #0D7A6A;
                    border-color: #0D7A6A;
                }
            """)

    def set_active(self, active: bool):
        self.setChecked(active)
        self._apply_style(active)


# =====================================================
# PAGE PRINCIPALE
# =====================================================
class LinksPage(QWidget):
    navigate_to = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.svc = RelationshipService()
        self.all_relations = []
        self.all_employees = []

        self.active_filter = "all"

        # Layout racine
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: #F4F6F9; border: none; }")

        inner = QWidget()
        inner.setStyleSheet("background-color: #F4F6F9;")
        scroll.setWidget(inner)
        outer.addWidget(scroll)

        layout = QVBoxLayout(inner)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(20)

        # HEADER
        header = QHBoxLayout()

        left = QVBoxLayout()
        left.setSpacing(6)

        bc = QLabel("SMARTRH  /  GOUVERNANCE & LIENS")
        bc.setStyleSheet("""
            color: #7A8B9C; font-size: 9pt; font-weight: 800;
            letter-spacing: 1px;
            background: transparent; border: none;
        """)
        left.addWidget(bc)

        t = QLabel("Liens & Relations entre Collaborateurs")
        t.setStyleSheet("""
            font-size: 20pt; font-weight: 800; color: #0F1E2E;
            background: transparent; border: none;
        """)
        left.addWidget(t)

        s = QLabel(
            "Cartographiez le réseau social de l'entreprise : amitiés, couples, "
            "familles, mentorat. Utile pour éviter les conflits d'intérêts en SmartMatch."
        )
        s.setStyleSheet("""
            font-size: 10pt; color: #7A8B9C;
            background: transparent; border: none;
        """)
        s.setWordWrap(True)
        left.addWidget(s)

        header.addLayout(left, 1)

        btn_new = QPushButton("Nouvelle relation")
        btn_new.setMinimumHeight(44)
        btn_new.setMinimumWidth(180)
        btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new.setStyleSheet("""
            QPushButton {
                background-color: #0D7A6A;
                color: #FFFFFF;
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
                font-size: 10pt;
                font-weight: 700;
            }
            QPushButton:hover { background-color: #0A6456; }
            QPushButton:pressed { background-color: #084C41; }
        """)
        btn_new.clicked.connect(self._show_add_relation)
        header.addWidget(btn_new, 0, Qt.AlignmentFlag.AlignTop)

        layout.addLayout(header)

        # Ligne gradient
        gradient = QFrame()
        gradient.setFixedHeight(3)
        gradient.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2E86DE, stop:1 #0D7A6A
                );
                border: none;
                border-radius: 2px;
            }
        """)
        layout.addWidget(gradient)

        # CHARGEMENT
        try:
            kpis = self.svc.get_kpis()
        except Exception:
            kpis = {"total_relations": 0, "by_type": {}, "employees_with_rel": 0}

        self.all_relations = self._load_relations()
        self.all_employees = self._load_employees()

        # KPI CARDS
        self.kpi_row = QGridLayout()
        self.kpi_row.setSpacing(16)
        self._build_kpis(kpis)
        layout.addLayout(self.kpi_row)

        # BARRE DE FILTRES
        filter_card = QFrame()
        filter_card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
            }
        """)
        filter_v = QVBoxLayout(filter_card)
        filter_v.setContentsMargins(16, 14, 16, 14)
        filter_v.setSpacing(12)

        # Ligne 1 : titre + badge + rafraîchir
        title_row = QHBoxLayout()
        title_row.setSpacing(10)

        title_row.addWidget(ColorDot("#0D7A6A", 8))

        title_lbl = QLabel("TOUTES LES RELATIONS")
        title_lbl.setStyleSheet("""
            font-size: 10.5pt; font-weight: 800; color: #5A6B7D;
            letter-spacing: 1.2px;
            background: transparent; border: none;
        """)
        title_row.addWidget(title_lbl)

        self.relations_count_badge = QLabel(f"{len(self.all_relations)} enregistrées")
        self.relations_count_badge.setStyleSheet("""
            background-color: #F1F5F9;
            color: #475569;
            padding: 4px 12px;
            border-radius: 10px;
            font-size: 8.5pt;
            font-weight: 700;
            border: none;
        """)
        title_row.addWidget(self.relations_count_badge)

        title_row.addStretch()

        btn_refresh = QPushButton("Rafraîchir")
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setMinimumHeight(34)
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #5A6B7D;
                border: 1px solid #E4E9EF;
                border-radius: 8px;
                padding: 6px 16px;
                font-size: 9pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #F4F6F9;
                color: #0D7A6A;
                border-color: #0D7A6A;
            }
        """)
        btn_refresh.clicked.connect(self._reload)
        title_row.addWidget(btn_refresh)

        filter_v.addLayout(title_row)

        # Ligne 2 : filtres par type (avec pastilles colorées cohérentes)
        filters_row = QHBoxLayout()
        filters_row.setSpacing(6)

        # Calcule les compteurs depuis all_relations (source de vérité)
        total = len(self.all_relations)
        n_ami = len([r for r in self.all_relations
                     if r.get("relation_type", "").lower() in ("ami", "amie")])
        n_couple = len([r for r in self.all_relations
                        if r.get("relation_type", "").lower() == "couple"])
        n_famille = len([r for r in self.all_relations
                         if r.get("relation_type", "").lower() == "famille"])

        self.filter_tabs = {}
        for key, label, count in [
            ("all", "Tous", total),
            ("ami", "Amis", n_ami),
            ("couple", "Couples", n_couple),
            ("famille", "Familles", n_famille),
        ]:
            tab = FilterTab(label, count, is_active=(key == "all"))
            tab.clicked.connect(lambda _, k=key: self._on_filter_change(k))
            filters_row.addWidget(tab)
            self.filter_tabs[key] = tab

        filters_row.addStretch()
        filter_v.addLayout(filters_row)

        layout.addWidget(filter_card)

        # CONTENEUR DES RELATIONS
        self.relations_card = QFrame()
        self.relations_card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
            }
        """)
        self.relations_v = QVBoxLayout(self.relations_card)
        self.relations_v.setContentsMargins(16, 16, 16, 16)
        self.relations_v.setSpacing(10)

        layout.addWidget(self.relations_card)

        # FOOTER INFO
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background-color: #EFF6FF;
                border-radius: 10px;
                border: none;
            }
        """)
        footer_v = QHBoxLayout(footer)
        footer_v.setContentsMargins(18, 14, 18, 14)
        footer_v.setSpacing(12)

        footer_v.addWidget(ColorDot("#0D7A6A", 10), 0, Qt.AlignmentFlag.AlignTop)

        footer_txt = QLabel(
            "Les liens recensés alimentent l'algorithme SmartMatch IA afin de "
            "garantir une neutralité totale dans les évaluations croisées et la "
            "constitution d'équipes de revue de code."
        )
        footer_txt.setStyleSheet("""
            font-size: 9.5pt; color: #5A6B7D;
            background: transparent; border: none;
        """)
        footer_txt.setWordWrap(True)
        footer_v.addWidget(footer_txt, 1)

        layout.addWidget(footer)
        layout.addStretch()

        self._render_relations()

    # =====================================================
    # CHARGEMENT
    # =====================================================
    def _load_relations(self) -> list:
        try:
            return self.svc.get_all_relations()
        except Exception as e:
            print(f"[LinksPage] Erreur relations: {e}")
            return []

    def _load_employees(self) -> list:
        try:
            return self.svc.get_all_employees()
        except Exception as e:
            print(f"[LinksPage] Erreur employes: {e}")
            return []

    # =====================================================
    # FILTRAGE
    # =====================================================
    def _filter_relations(self) -> list:
        if self.active_filter == "all":
            return self.all_relations

        return [
            r for r in self.all_relations
            if r.get("relation_type", "").lower() == self.active_filter
            or (self.active_filter == "ami" and
                r.get("relation_type", "").lower() == "amie")
        ]

    def _on_filter_change(self, filter_key: str):
        self.active_filter = filter_key
        for key, tab in self.filter_tabs.items():
            tab.set_active(key == filter_key)
        self._render_relations()

    # =====================================================
    # RENDU
    # =====================================================
    def _render_relations(self):
        while self.relations_v.count():
            item = self.relations_v.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

        filtered = self._filter_relations()

        # Mise à jour du badge
        if hasattr(self, "relations_count_badge"):
            if self.active_filter == "all":
                self.relations_count_badge.setText(
                    f"{len(filtered)} enregistrées"
                )
            else:
                self.relations_count_badge.setText(
                    f"{len(filtered)} / {len(self.all_relations)}"
                )

        # État vide
        if not filtered:
            empty = QFrame()
            empty.setStyleSheet("""
                QFrame {
                    background-color: #F8FAFC;
                    border-radius: 10px;
                    border: 1px dashed #E4E9EF;
                }
            """)
            ev = QVBoxLayout(empty)
            ev.setContentsMargins(40, 60, 40, 60)
            ev.setSpacing(10)

            dot_row = QHBoxLayout()
            dot_row.addStretch()
            dot_row.addWidget(ColorDot("#B8C4D0", 10))
            dot_row.addStretch()
            ev.addLayout(dot_row)

            if self.active_filter != "all":
                msg_txt = "Aucun résultat pour ce filtre"
                sub_txt = "Essayez un autre type de relation"
            else:
                msg_txt = "Aucune relation enregistrée pour le moment"
                sub_txt = "Cliquez sur 'Nouvelle relation' pour cartographier le réseau"

            msg = QLabel(msg_txt)
            msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
            msg.setStyleSheet("""
                font-size: 11pt; color: #7A8B9C; font-weight: 700;
                background: transparent; border: none;
            """)
            ev.addWidget(msg)

            sub = QLabel(sub_txt)
            sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sub.setStyleSheet("""
                font-size: 9.5pt; color: #B8C4D0;
                background: transparent; border: none;
            """)
            ev.addWidget(sub)

            self.relations_v.addWidget(empty)
            return

        for rel in filtered:
            row = RelationRow(rel)
            row.delete_requested.connect(self._on_delete_relation)
            self.relations_v.addWidget(row)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    # =====================================================
    # ACTIONS
    # =====================================================
    def _show_add_relation(self):
        if len(self.all_employees) < 2:
            QMessageBox.warning(
                self, "Erreur",
                "Il faut au moins 2 employés pour créer une relation."
            )
            return

        dialog = AddRelationDialog(self.all_employees, self)
        if dialog.exec() and dialog.result_data:
            data = dialog.result_data
            success, message = self.svc.create_relation(
                employee_a_id=data["employee_a_id"],
                employee_b_id=data["employee_b_id"],
                relation_type=data["relation_type"],
                notes=data["notes"],
            )
            if success:
                try:
                    a_name = next((e["name"] for e in self.all_employees
                                   if e["id"] == data["employee_a_id"]), "?")
                    b_name = next((e["name"] for e in self.all_employees
                                   if e["id"] == data["employee_b_id"]), "?")
                    style = get_relation_style(data["relation_type"])

                    AuditService().log_action(
                        action="create_relation",
                        entity_type="relation",
                        entity_id=None,
                        details=f"{a_name} + {b_name} ({style['label']})",
                    )
                except Exception as e:
                    print(f"[LinksPage] Erreur log relation: {e}")

                QMessageBox.information(self, "Succès", message)
                self._reload()
            else:
                QMessageBox.warning(self, "Attention", message)

    def _on_delete_relation(self, relation_id: str):
        reply = QMessageBox.question(
            self, "Confirmation",
            "Voulez-vous vraiment supprimer cette relation ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            if self.svc.delete_relation(relation_id):
                AuditService().log_action(
                    action="delete_relation",
                    entity_type="relation",
                    entity_id=relation_id,
                    details="Relation supprimée",
                )

                QMessageBox.information(self, "Succès", "Relation supprimée.")
                self._reload()
            else:
                QMessageBox.warning(self, "Erreur", "Relation introuvable.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    def _reload(self):
        try:
            kpis = self.svc.get_kpis()
            self._build_kpis(kpis)
        except Exception as e:
            print(f"[LinksPage] Erreur reload KPIs: {e}")

        self.all_relations = self._load_relations()
        self._update_filter_counts()
        self._render_relations()

    def _update_filter_counts(self):
        total = len(self.all_relations)
        n_ami = len([r for r in self.all_relations
                     if r.get("relation_type", "").lower() in ("ami", "amie")])
        n_couple = len([r for r in self.all_relations
                        if r.get("relation_type", "").lower() == "couple"])
        n_famille = len([r for r in self.all_relations
                         if r.get("relation_type", "").lower() == "famille"])

        if "all" in self.filter_tabs:
            self.filter_tabs["all"].setText(f"Tous ({total})")
        if "ami" in self.filter_tabs:
            self.filter_tabs["ami"].setText(f"Amis ({n_ami})")
        if "couple" in self.filter_tabs:
            self.filter_tabs["couple"].setText(f"Couples ({n_couple})")
        if "famille" in self.filter_tabs:
            self.filter_tabs["famille"].setText(f"Familles ({n_famille})")

    # =====================================================
    # KPI BUILD
    # =====================================================
    def _build_kpis(self, kpis: dict):
        while self.kpi_row.count():
            item = self.kpi_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Compte depuis all_relations (source de vérité) pour cohérence
        n_ami = len([r for r in self.all_relations
                     if r.get("relation_type", "").lower() in ("ami", "amie")])
        n_couple = len([r for r in self.all_relations
                        if r.get("relation_type", "").lower() == "couple"])
        n_famille = len([r for r in self.all_relations
                         if r.get("relation_type", "").lower() == "famille"])

        self.kpi_row.addWidget(KpiCardCustom(
            title="Total relations",
            value=str(kpis.get("total_relations", len(self.all_relations))),
            subtitle=f"{kpis.get('employees_with_rel', 0)} employés concernés",
            letter="R",
            accent="green",
        ), 0, 0)

        self.kpi_row.addWidget(KpiCardCustom(
            title="Amis",
            value=str(n_ami),
            subtitle="Relations amicales",
            letter="A",
            accent="blue",
        ), 0, 1)

        self.kpi_row.addWidget(KpiCardCustom(
            title="Couples",
            value=str(n_couple),
            subtitle="Attention conflits",
            letter="C",
            accent="pink",
        ), 0, 2)

        self.kpi_row.addWidget(KpiCardCustom(
            title="Familles",
            value=str(n_famille),
            subtitle="Liens de sang",
            letter="F",
            accent="orange",
        ), 0, 3)