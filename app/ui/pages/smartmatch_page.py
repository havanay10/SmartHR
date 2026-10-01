"""Page SmartMatch — Analyse de compatibilite (Module 5 du CDC)."""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QScrollArea, QFrame, QLabel, QPushButton, QComboBox,
    QRadioButton, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal

from app.services.smartmatch_service import SmartMatchService
from app.services.audit_service import AuditService


# Mapping DISC -> texte complet
DISC_LABELS = {
    "D": "Dominant",
    "I": "Influent",
    "S": "Stable",
    "C": "Consciencieux",
}


def disc_label(code: str) -> str:
    if not code:
        return "Non renseigné"
    return DISC_LABELS.get(code.upper(), code)


# =====================================================
# AVATAR
# =====================================================
class AvatarBig(QLabel):
    def __init__(self, first_name: str, last_name: str, size: int = 64):
        super().__init__()
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        initials = f"{(first_name or '?')[:1]}{(last_name or '?')[:1]}".upper()
        colors = ["#0D7A6A", "#1F4E5F", "#2E86DE", "#8E44AD", "#B9770E"]
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
# PASTILLE COULEUR
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


# =====================================================
# CARTE MODE D'ANALYSE
# =====================================================
class ModeCard(QFrame):
    mode_selected = pyqtSignal(str)

    def __init__(self, mode_key: str, title: str, description: str, is_active: bool = False):
        super().__init__()
        self.mode_key = mode_key
        self.is_active = is_active
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(150)

        self._apply_style()

        h = QHBoxLayout(self)
        h.setContentsMargins(22, 18, 22, 18)
        h.setSpacing(16)

        self.radio = QRadioButton()
        self.radio.setChecked(is_active)
        self.radio.setStyleSheet("""
            QRadioButton::indicator {
                width: 18px; height: 18px;
                border: 2px solid #D6DEE8;
                border-radius: 10px;
                background: #FFFFFF;
            }
            QRadioButton::indicator:checked {
                background-color: #0D7A6A;
                border-color: #0D7A6A;
            }
        """)
        h.addWidget(self.radio, 0, Qt.AlignmentFlag.AlignTop)

        v = QVBoxLayout()
        v.setSpacing(8)

        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("""
            font-size: 11pt; font-weight: 700; color: #0F1E2E;
            background: transparent; border: none;
        """)
        title_row.addWidget(title_lbl)

        if is_active:
            active_badge = QLabel("Actif")
            active_badge.setStyleSheet("""
                background-color: #0D7A6A;
                color: #FFFFFF;
                padding: 3px 10px;
                border-radius: 10px;
                font-size: 8pt;
                font-weight: 700;
                border: none;
            """)
            title_row.addWidget(active_badge)

        title_row.addStretch()
        v.addLayout(title_row)

        desc_lbl = QLabel(description)
        desc_lbl.setStyleSheet("""
            font-size: 9pt; color: #5A6B7D; line-height: 1.5;
            background: transparent; border: none;
        """)
        desc_lbl.setWordWrap(True)
        v.addWidget(desc_lbl)

        h.addLayout(v, 1)

    def _apply_style(self):
        if self.is_active:
            self.setStyleSheet("""
                QFrame {
                    background-color: #F4FAF8;
                    border-radius: 14px;
                    border: 2px solid #0D7A6A;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #FFFFFF;
                    border-radius: 14px;
                    border: 1px solid #E4E9EF;
                }
                QFrame:hover {
                    border: 2px solid #0D7A6A;
                    background-color: #FAFDFB;
                }
            """)

    def set_active(self, active: bool):
        self.is_active = active
        self.radio.setChecked(active)
        self._apply_style()

    def mousePressEvent(self, event):
        self.mode_selected.emit(self.mode_key)
        super().mousePressEvent(event)


# =====================================================
# CARTE COLLABORATEUR
# =====================================================
class CollaboratorCard(QFrame):
    def __init__(self, employee: dict, role: str, score_data: dict = None, other_id: str = None):
        super().__init__()
        self.employee = employee
        self.other_id = other_id
        self.setMinimumHeight(260)

        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 14px;
                border: 1px solid #E4E9EF;
            }
        """)

        v = QVBoxLayout(self)
        v.setContentsMargins(20, 18, 20, 18)
        v.setSpacing(16)

        head = QHBoxLayout()
        head.setSpacing(8)

        role_badge = QLabel(role.upper())
        role_badge.setStyleSheet("""
            background-color: #E8F5F1; color: #0D7A6A;
            padding: 4px 12px; border-radius: 12px;
            font-size: 8pt; font-weight: 800; letter-spacing: 0.5px;
            border: none;
        """)
        head.addWidget(role_badge)
        head.addStretch()

        disc = employee.get("disc", "") or ""
        if disc:
            disc_badge = QLabel(f"DISC {disc}")
            disc_badge.setStyleSheet("""
                background-color: #F4F6F9; color: #5A6B7D;
                padding: 4px 12px; border-radius: 12px;
                font-size: 8pt; font-weight: 700;
                border: none;
            """)
            head.addWidget(disc_badge)

        v.addLayout(head)

        main = QHBoxLayout()
        main.setSpacing(14)

        name = employee.get("name", "—")
        parts = name.split(" ", 1)
        first = parts[0] if len(parts) > 0 else ""
        last = parts[1] if len(parts) > 1 else ""

        avatar = AvatarBig(first, last, size=64)
        main.addWidget(avatar, 0, Qt.AlignmentFlag.AlignTop)

        info_col = QVBoxLayout()
        info_col.setSpacing(4)

        name_lbl = QLabel(name)
        name_lbl.setStyleSheet("""
            font-size: 14pt; font-weight: 800; color: #0F1E2E;
            background: transparent; border: none;
        """)
        info_col.addWidget(name_lbl)

        title_lbl = QLabel(employee.get("job_title", "—"))
        title_lbl.setStyleSheet("""
            font-size: 10pt; color: #5A6B7D;
            background: transparent; border: none;
        """)
        title_lbl.setWordWrap(True)
        info_col.addWidget(title_lbl)

        dept = employee.get("department", "—")
        sub_lbl = QLabel(f"Département : {dept}")
        sub_lbl.setStyleSheet("""
            font-size: 9pt; color: #7A8B9C;
            background: transparent; border: none;
        """)
        info_col.addWidget(sub_lbl)

        main.addLayout(info_col, 1)
        v.addLayout(main)

        # Bloc RELATION
        if self.other_id:
            try:
                from app.services.relationship_service import RelationshipService
                relation = RelationshipService().get_relation_between(
                    employee.get("id", ""), self.other_id
                )

                if relation:
                    rel_label = relation.get("relation_label", "Relation")
                    rel_color = relation.get("relation_color", "#7A8B9C")
                    rel_notes = relation.get("notes")

                    rel_box = QFrame()
                    rel_box.setStyleSheet(f"""
                        QFrame {{
                            background-color: {rel_color}12;
                            border-radius: 10px;
                            border: 1px solid {rel_color}40;
                            border-left: 4px solid {rel_color};
                        }}
                    """)
                    rb = QVBoxLayout(rel_box)
                    rb.setContentsMargins(14, 12, 14, 12)
                    rb.setSpacing(4)

                    top = QHBoxLayout()
                    top.setSpacing(8)
                    top.addWidget(ColorDot(rel_color, 8))

                    lbl_rel = QLabel("RELATION AVEC L'AUTRE")
                    lbl_rel.setStyleSheet("""
                        font-size: 7.5pt; color: #7A8B9C; font-weight: 800;
                        letter-spacing: 0.5px; background: transparent; border: none;
                    """)
                    top.addWidget(lbl_rel)
                    top.addStretch()
                    rb.addLayout(top)

                    val_rel = QLabel(rel_label)
                    val_rel.setStyleSheet(f"""
                        font-size: 11pt; color: {rel_color}; font-weight: 700;
                        background: transparent; border: none;
                    """)
                    rb.addWidget(val_rel)

                    if rel_notes:
                        notes_lbl = QLabel(rel_notes)
                        notes_lbl.setStyleSheet("""
                            font-size: 8pt; color: #7A8B9C; font-style: italic;
                            background: transparent; border: none;
                        """)
                        notes_lbl.setWordWrap(True)
                        rb.addWidget(notes_lbl)

                    v.addWidget(rel_box)
            except Exception as e:
                print(f"[CollaboratorCard] Erreur relation: {e}")

        # Grille de details
        if score_data is not None or role == "Collaborateur Pivot":
            grid = QGridLayout()
            grid.setSpacing(8)

            disc_full = disc_label(disc)
            grid.addWidget(self._info_block(
                "Profil comportemental",
                disc_full,
                f"DISC {disc or '—'}"
            ), 0, 0)

            work_mode_raw = (employee.get("work_mode") or "").lower()
            if "hybride" in work_mode_raw:
                mode_label = "Hybride"
            elif "télétravail" in work_mode_raw or "teletravail" in work_mode_raw:
                mode_label = "Télétravail"
            elif "présentiel" in work_mode_raw or "presentiel" in work_mode_raw:
                mode_label = "Présentiel"
            else:
                mode_label = "Non renseigné"

            remote_days = employee.get("remote_days_per_week", 0)
            presence_sub = f"{remote_days}j/sem. à distance" if remote_days > 0 else "100% sur site"

            grid.addWidget(self._info_block(
                "Rythme & Mode",
                mode_label,
                presence_sub
            ), 0, 1)

            if self.other_id:
                try:
                    stats = SmartMatchService().get_collaboration_stats(
                        employee.get("id", ""), self.other_id
                    )
                    n_proj = stats.get("n_projects", 0)
                    n_months = stats.get("n_months", 0)

                    if n_proj == 0:
                        hist_val = "Aucun projet commun"
                        hist_sub = "Première collaboration"
                    elif n_proj == 1:
                        hist_val = f"{n_proj} projet commun"
                        hist_sub = f"{n_months} mois de collaboration"
                    else:
                        hist_val = f"{n_proj} projets communs"
                        hist_sub = f"{n_months} mois de collaboration"
                except Exception:
                    hist_val = "—"
                    hist_sub = ""
            else:
                hist_val = "—"
                hist_sub = ""

            grid.addWidget(self._info_block(
                "Historique co-travail",
                hist_val,
                hist_sub
            ), 1, 0, 1, 2)

            v.addLayout(grid)

        v.addStretch()

    def _info_block(self, label, value, subtitle=""):
        box = QFrame()
        box.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border-radius: 8px;
                border: 1px solid #EEF2F6;
            }
        """)
        bv = QVBoxLayout(box)
        bv.setContentsMargins(12, 10, 12, 10)
        bv.setSpacing(3)

        lbl = QLabel(label.upper())
        lbl.setStyleSheet("""
            font-size: 7pt; color: #7A8B9C; font-weight: 800;
            letter-spacing: 0.5px; background: transparent; border: none;
        """)
        bv.addWidget(lbl)

        val = QLabel(value)
        val.setStyleSheet("""
            font-size: 10pt; font-weight: 700; color: #0F1E2E;
            background: transparent; border: none;
        """)
        val.setWordWrap(True)
        bv.addWidget(val)

        if subtitle:
            sub = QLabel(subtitle)
            sub.setStyleSheet("""
                font-size: 8pt; color: #7A8B9C;
                background: transparent; border: none;
            """)
            sub.setWordWrap(True)
            bv.addWidget(sub)

        return box


# =====================================================
# CARTE VS
# =====================================================
class VsBadge(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedSize(120, 150)

        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(8)

        v.addStretch()

        vs_lbl = QLabel("VS")
        vs_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vs_lbl.setFixedSize(64, 64)
        vs_lbl.setStyleSheet("""
            background-color: #0D7A6A;
            color: #FFFFFF;
            border-radius: 32px;
            font-size: 20pt;
            font-weight: 800;
            border: 4px solid #E8F5F1;
        """)
        v.addWidget(vs_lbl, 0, Qt.AlignmentFlag.AlignCenter)

        txt = QLabel("CROISEMENT IA")
        txt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        txt.setStyleSheet("""
            font-size: 7pt; color: #7A8B9C; font-weight: 800;
            letter-spacing: 1.5px; background: transparent; border: none;
        """)
        v.addWidget(txt)

        v.addStretch()


# =====================================================
# CARTE SCORE SECONDAIRE
# =====================================================
class ScoreCard(QFrame):
    def __init__(self, label: str, value: float, description: str, is_risk: bool = False):
        super().__init__()
        self.setMinimumHeight(130)

        if is_risk:
            if value < 20:
                color = "#0D7A6A"
            elif value < 40:
                color = "#F39C12"
            else:
                color = "#C0392B"
        else:
            if value >= 80:
                color = "#0D7A6A"
            elif value >= 60:
                color = "#F39C12"
            else:
                color = "#C0392B"

        self.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
                border-top: 3px solid {color};
            }}
        """)

        v = QVBoxLayout(self)
        v.setContentsMargins(16, 14, 16, 14)
        v.setSpacing(8)

        head = QHBoxLayout()
        head.setSpacing(8)

        head.addWidget(ColorDot(color, 8), 0, Qt.AlignmentFlag.AlignVCenter)

        lbl = QLabel(label)
        lbl.setStyleSheet("""
            font-size: 9.5pt; font-weight: 700; color: #0F1E2E;
            background: transparent; border: none;
        """)
        head.addWidget(lbl)
        head.addStretch()

        val = QLabel(f"{value:.0f}%")
        val.setStyleSheet(f"""
            font-size: 14pt; font-weight: 800; color: {color};
            background: transparent; border: none;
        """)
        head.addWidget(val)
        v.addLayout(head)

        bar = QProgressBar()
        bar.setValue(int(value))
        bar.setMaximum(100)
        bar.setTextVisible(False)
        bar.setFixedHeight(6)
        bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #EEF2F6;
                border-radius: 3px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
        v.addWidget(bar)

        if description:
            desc = QLabel(description)
            desc.setStyleSheet("""
                font-size: 8.5pt; color: #7A8B9C;
                background: transparent; border: none;
            """)
            desc.setWordWrap(True)
            v.addWidget(desc)

        v.addStretch()


# =====================================================
# CARTE HISTORIQUE BINOME
# =====================================================
class BinomeHistoryCard(QFrame):
    delete_requested = pyqtSignal(str)

    def __init__(self, binome: dict):
        super().__init__()
        self.binome = binome
        self.setMinimumHeight(90)

        self.setStyleSheet("""
            QFrame {
                background-color: #FAFBFC;
                border-radius: 10px;
                border: 1px solid #EEF2F6;
            }
            QFrame:hover {
                background-color: #F4F9F7;
                border: 1px solid #0D7A6A;
            }
        """)

        h = QHBoxLayout(self)
        h.setContentsMargins(14, 12, 14, 12)
        h.setSpacing(14)

        score = binome.get("score", 0)
        if score >= 80:
            color = "#0D7A6A"
            bg = "#E8F5F1"
        elif score >= 60:
            color = "#B9770E"
            bg = "#FEF9E7"
        else:
            color = "#C0392B"
            bg = "#FADBD8"

        score_box = QLabel(f"{score:.0f}%")
        score_box.setFixedSize(56, 56)
        score_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_box.setStyleSheet(f"""
            background-color: {bg};
            color: {color};
            border-radius: 28px;
            font-size: 13pt;
            font-weight: 800;
            border: 2px solid {color};
        """)
        h.addWidget(score_box)

        v = QVBoxLayout()
        v.setSpacing(3)

        names = f"{binome.get('employee_a_name', '—')} + {binome.get('employee_b_name', '—')}"
        names_lbl = QLabel(names)
        names_lbl.setStyleSheet("""
            font-size: 11pt; font-weight: 700; color: #0F1E2E;
            background: transparent; border: none;
        """)
        v.addWidget(names_lbl)

        diag = QLabel(binome.get("diagnosis", "—"))
        diag.setStyleSheet("""
            font-size: 9pt; color: #7A8B9C;
            background: transparent; border: none;
        """)
        diag.setWordWrap(True)
        v.addWidget(diag)

        created = binome.get("created_at")
        if created:
            dt_txt = created.strftime("%d/%m/%Y à %H:%M") if hasattr(created, "strftime") else str(created)
        else:
            dt_txt = "—"
        date_lbl = QLabel(f"Assigné le {dt_txt}")
        date_lbl.setStyleSheet("""
            font-size: 8pt; color: #B8C4D0;
            background: transparent; border: none;
        """)
        v.addWidget(date_lbl)

        h.addLayout(v, 1)

        btn_del = QPushButton("✕")
        btn_del.setFixedSize(30, 30)
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setToolTip("Archiver ce binôme")
        btn_del.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #B8C4D0;
                border: none;
                border-radius: 15px;
                font-size: 13pt;
            }
            QPushButton:hover {
                background-color: #FADBD8;
                color: #C0392B;
            }
        """)
        btn_del.clicked.connect(
            lambda: self.delete_requested.emit(binome.get("id", ""))
        )
        h.addWidget(btn_del)


# =====================================================
# PAGE PRINCIPALE
# =====================================================
class SmartMatchPage(QWidget):
    navigate_to = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.svc = SmartMatchService()
        self.current_mode = "duo"

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

        self.main_layout = QVBoxLayout(inner)
        self.main_layout.setContentsMargins(28, 22, 28, 24)
        self.main_layout.setSpacing(20)

        # HEADER
        header = QHBoxLayout()
        header.setSpacing(16)

        left = QVBoxLayout()
        left.setSpacing(6)

        bc_row = QHBoxLayout()
        bc_row.setSpacing(8)

        bc = QLabel("SMARTRH  /  SMARTMATCH IA")
        bc.setStyleSheet("""
            color: #7A8B9C; font-size: 8pt; font-weight: 800;
            letter-spacing: 1.2px; background: transparent; border: none;
        """)
        bc_row.addWidget(bc)

        bc_row.addWidget(ColorDot("#0D7A6A", 6))

        ia_status = QLabel("MOTEUR IA v2.4")
        ia_status.setStyleSheet("""
            color: #0D7A6A; font-size: 8pt; font-weight: 800;
            letter-spacing: 1.2px; background: transparent; border: none;
        """)
        bc_row.addWidget(ia_status)
        bc_row.addStretch()
        left.addLayout(bc_row)

        t = QLabel("SmartMatch IA — Analyse de Compatibilité")
        t.setStyleSheet("""
            font-size: 20pt; font-weight: 800; color: #0F1E2E;
            background: transparent; border: none;
        """)
        t.setWordWrap(True)
        left.addWidget(t)

        s = QLabel("Sélectionnez deux employés pour croiser leurs données professionnelles, styles de travail et évaluer leur compatibilité globale")
        s.setStyleSheet("""
            font-size: 10pt; color: #7A8B9C;
            background: transparent; border: none;
        """)
        s.setWordWrap(True)
        left.addWidget(s)

        header.addLayout(left, 1)

        btn_new = QPushButton("Nouvelle Comparaison")
        btn_new.setMinimumHeight(44)
        btn_new.setMinimumWidth(200)
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
        btn_new.clicked.connect(self._reset_page)
        header.addWidget(btn_new, 0, Qt.AlignmentFlag.AlignTop)

        self.main_layout.addLayout(header)

        # SECTION MODE
        mode_title = QLabel("MODE D'ANALYSE IA SOUHAITÉ")
        mode_title.setStyleSheet("""
            font-size: 10pt; font-weight: 800; color: #5A6B7D;
            letter-spacing: 1.2px; padding-top: 10px;
            background: transparent; border: none;
        """)
        self.main_layout.addWidget(mode_title)

        mode_row = QHBoxLayout()
        mode_row.setSpacing(20)

        self.card_duo = ModeCard(
            "duo",
            "Mode A : Duo Intra-Département (1 contre 1)",
            "Sélectionnez deux collaborateurs appartenant obligatoirement au même département pour confronter leurs données.",
            is_active=True,
        )
        self.card_duo.mode_selected.connect(self._on_mode_click)
        mode_row.addWidget(self.card_duo, 1)

        self.card_multi = ModeCard(
            "multi",
            "Mode B : Analyse 1-vers-Tous (Département complet)",
            "Choisissez un collaborateur pivot et l'IA analyse et compare ses données face à chacun des collaborateurs de son département.",
            is_active=False,
        )
        self.card_multi.mode_selected.connect(self._on_mode_click)
        mode_row.addWidget(self.card_multi, 1)

        self.main_layout.addLayout(mode_row)

        # SECTION SELECTION
        self.sel_card = QFrame()
        self.sel_card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 14px;
                border: 1px solid #E4E9EF;
            }
        """)
        self.sel_v = QVBoxLayout(self.sel_card)
        self.sel_v.setContentsMargins(24, 20, 24, 20)
        self.sel_v.setSpacing(20)

        sel_title = QLabel("Configuration de l'analyse")
        sel_title.setStyleSheet("""
            font-size: 13pt; font-weight: 800; color: #0F1E2E;
            background: transparent; border: none;
        """)
        self.sel_v.addWidget(sel_title)

        grid = QGridLayout()
        grid.setSpacing(14)

        grid.addWidget(self._make_label("Département cible"), 0, 0)
        self.combo_dept = QComboBox()
        self._style_combo(self.combo_dept)
        grid.addWidget(self.combo_dept, 0, 1)

        grid.addWidget(self._make_label("Collaborateur pivot"), 0, 2)
        self.combo_pivot = QComboBox()
        self._style_combo(self.combo_pivot)
        grid.addWidget(self.combo_pivot, 0, 3)

        self.lbl_target = self._make_label("2ème collaborateur")
        grid.addWidget(self.lbl_target, 1, 0)
        self.combo_target = QComboBox()
        self._style_combo(self.combo_target)
        grid.addWidget(self.combo_target, 1, 1)

        self.sel_v.addLayout(grid)

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        self.btn_run = QPushButton("Lancer l'analyse IA")
        self.btn_run.setMinimumHeight(44)
        self.btn_run.setMinimumWidth(220)
        self.btn_run.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_run.setStyleSheet("""
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
        self.btn_run.clicked.connect(self._run_analysis)
        btn_row.addWidget(self.btn_run)

        self.sel_v.addLayout(btn_row)
        self.main_layout.addWidget(self.sel_card)

        # SECTION HISTORIQUE
        history_title_row = QHBoxLayout()
        history_title_row.setSpacing(10)

        hist_title = QLabel("BINÔMES ASSIGNÉS RÉCEMMENT")
        hist_title.setStyleSheet("""
            font-size: 10pt; font-weight: 800; color: #5A6B7D;
            letter-spacing: 1.2px; padding-top: 10px;
            background: transparent; border: none;
        """)
        history_title_row.addWidget(hist_title)
        history_title_row.addStretch()

        btn_refresh = QPushButton("Rafraîchir")
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #5A6B7D;
                border: 1px solid #E4E9EF;
                border-radius: 8px;
                padding: 6px 14px;
                font-size: 9pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #F4F6F9;
                color: #0D7A6A;
                border-color: #0D7A6A;
            }
        """)
        btn_refresh.clicked.connect(self._load_binome_history)
        history_title_row.addWidget(btn_refresh)

        self.main_layout.addLayout(history_title_row)

        self.history_card = QFrame()
        self.history_card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 14px;
                border: 1px solid #E4E9EF;
            }
        """)
        self.history_v = QVBoxLayout(self.history_card)
        self.history_v.setContentsMargins(18, 18, 18, 18)
        self.history_v.setSpacing(10)

        self.main_layout.addWidget(self.history_card)

        # SECTION RESULTATS
        self.results_container = QVBoxLayout()
        self.results_container.setSpacing(20)
        self.main_layout.addLayout(self.results_container)

        self.main_layout.addStretch()

        self._load_departments()
        self.combo_dept.currentIndexChanged.connect(self._reload_employees)
        self._load_binome_history()

    # =====================================================
    # HISTORIQUE
    # =====================================================
    def _load_binome_history(self):
        while self.history_v.count():
            item = self.history_v.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

        try:
            binomes = self.svc.get_all_binomes(limit=20)
        except Exception as e:
            print(f"[SmartMatchPage] Erreur binomes: {e}")
            binomes = []

        if not binomes:
            empty = QLabel("Aucun binôme assigné pour le moment")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet("""
                color: #7A8B9C; font-style: italic; padding: 40px;
                font-size: 10pt; background: transparent; border: none;
            """)
            self.history_v.addWidget(empty)
            return

        for b in binomes:
            card = BinomeHistoryCard(b)
            card.delete_requested.connect(self._on_delete_binome)
            self.history_v.addWidget(card)

    def _on_delete_binome(self, binome_id: str):
        reply = QMessageBox.question(
            self, "Confirmation",
            "Voulez-vous vraiment archiver ce binôme ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            success = self.svc.delete_binome(binome_id)
            if success:
                AuditService().log_action(
                    action="delete_binome",
                    entity_type="binome",
                    entity_id=binome_id,
                    details="Binôme archivé",
                )
                QMessageBox.information(self, "Succès", "Le binôme a été archivé.")
                self._load_binome_history()
            else:
                QMessageBox.warning(self, "Erreur", "Binôme introuvable.")
        except Exception as e:
            QMessageBox.critical(self, "Erreur", str(e))

    # =====================================================
    # HELPERS UI
    # =====================================================
    def _make_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet("""
            font-size: 9.5pt; color: #5A6B7D; font-weight: 700;
            background: transparent; border: none;
        """)
        return lbl

    def _style_combo(self, combo: QComboBox):
        combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #E4E9EF;
                border-radius: 8px;
                padding: 10px 14px;
                font-size: 9.5pt;
                background-color: #FFFFFF;
                min-width: 220px;
                color: #0F1E2E;
            }
            QComboBox:focus { border: 1px solid #0D7A6A; }
            QComboBox::drop-down { border: none; padding-right: 8px; }
        """)

    # =====================================================
    # CHARGEMENT
    # =====================================================
    def _load_departments(self):
        try:
            self.combo_dept.clear()
            for d in self.svc.get_departments():
                self.combo_dept.addItem(d["name"], d["id"])
            self._reload_employees()
        except Exception as e:
            print(f"[SmartMatchPage] Erreur chargement depts: {e}")

    def _reload_employees(self):
        dept_id = self.combo_dept.currentData()
        if not dept_id:
            return
        try:
            emps = self.svc.get_employees_by_department(dept_id)
            self.combo_pivot.clear()
            self.combo_target.clear()
            for e in emps:
                label = f"{e['name']} — {e['job_title']}"
                self.combo_pivot.addItem(label, e["id"])
                self.combo_target.addItem(label, e["id"])
        except Exception as e:
            print(f"[SmartMatchPage] Erreur chargement emps: {e}")

    # =====================================================
    # ACTIONS
    # =====================================================
    def _on_mode_click(self, mode: str):
        self.current_mode = mode
        self.card_duo.set_active(mode == "duo")
        self.card_multi.set_active(mode == "multi")

        is_duo = (mode == "duo")
        self.lbl_target.setVisible(is_duo)
        self.combo_target.setVisible(is_duo)

    def _reset_page(self):
        while self.results_container.count():
            item = self.results_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _run_analysis(self):
        pivot_id = self.combo_pivot.currentData()
        if not pivot_id:
            QMessageBox.warning(self, "Attention", "Sélectionnez un pivot.")
            return

        try:
            self.btn_run.setEnabled(False)
            self.btn_run.setText("Analyse en cours...")

            pivot_emp = self._get_employee_by_id(pivot_id)

            if self.current_mode == "duo":
                target_id = self.combo_target.currentData()
                if not target_id:
                    QMessageBox.warning(self, "Attention", "Sélectionnez une cible.")
                    return
                if target_id == pivot_id:
                    QMessageBox.warning(
                        self, "Attention",
                        "Le pivot et la cible doivent être différents."
                    )
                    return

                target_emp = self._get_employee_by_id(target_id)
                session = self.svc.run_duo(pivot_id, target_id)
                self._display_duo_results(pivot_emp, target_emp, session["results"][0])
            else:
                session = self.svc.run_multi_scan(pivot_id)
                self._display_multi_results(pivot_emp, session["results"])

        except Exception as e:
            print(f"[SmartMatchPage] Erreur analyse: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible de lancer l'analyse :\n{e}")
        finally:
            self.btn_run.setEnabled(True)
            self.btn_run.setText("Lancer l'analyse IA")

    def _get_employee_by_id(self, emp_id: str) -> dict:
        dept_id = self.combo_dept.currentData()
        emps = self.svc.get_employees_by_department(dept_id)
        for e in emps:
            if e["id"] == emp_id:
                return e
        return {}

    # =====================================================
    # ASSIGNER UN BINOME
    # =====================================================
    def _on_assign_binome(self, pivot: dict, target: dict, score: float, diagnosis: str):
        pivot_id = pivot.get("id")
        target_id = target.get("id")

        if not pivot_id or not target_id:
            QMessageBox.warning(self, "Erreur", "Impossible d'identifier les employes.")
            return

        try:
            success, message = self.svc.create_binome(
                employee_a_id=pivot_id,
                employee_b_id=target_id,
                score=score,
                diagnosis=diagnosis,
            )

            if success:
                AuditService().log_action(
                    action="create_binome",
                    entity_type="binome",
                    entity_id=None,
                    details=f"{pivot.get('name', '?')} + {target.get('name', '?')} (score {score:.0f}%)",
                )

                QMessageBox.information(
                    self, "Succès",
                    f"{message}\n\n"
                    f"Binôme : {pivot.get('name', '—')} + {target.get('name', '—')}\n"
                    f"Score : {score:.0f}%"
                )
                self._load_binome_history()
            else:
                QMessageBox.warning(self, "Attention", message)

        except Exception as e:
            print(f"[SmartMatchPage] Erreur assignation: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible de créer le binôme :\n{e}")

    # =====================================================
    # AFFICHAGE - MODE A (DUO)
    # =====================================================
    def _display_duo_results(self, pivot: dict, target: dict, result: dict):
        self._reset_page()

        # 2 cartes + VS
        duo_row = QHBoxLayout()
        duo_row.setSpacing(20)

        pivot_card = CollaboratorCard(
            pivot, role="Collaborateur 1",
            score_data=result, other_id=target.get("id"),
        )
        duo_row.addWidget(pivot_card, 1)

        duo_row.addWidget(VsBadge(), 0)

        target_card = CollaboratorCard(
            target, role="Collaborateur 2",
            score_data=result, other_id=pivot.get("id"),
        )
        duo_row.addWidget(target_card, 1)

        duo_container = QWidget()
        duo_container.setLayout(duo_row)
        self.results_container.addWidget(duo_container)

        # Diagnostic global
        global_score = result.get("global_score", 0)
        diagnosis = result.get("diagnosis", "—")

        if global_score >= 80:
            bg_color = "#F4FAF8"
            border_color = "#0D7A6A"
            score_color = "#0D7A6A"
            badge_txt = "Forte Synergie Opérationnelle"
            badge_style = "background-color: #E8F5F1; color: #0D7A6A;"
        elif global_score >= 60:
            bg_color = "#FEF9E7"
            border_color = "#F39C12"
            score_color = "#B9770E"
            badge_txt = "Synergie modérée"
            badge_style = "background-color: #FDEBD0; color: #B9770E;"
        else:
            bg_color = "#FADBD8"
            border_color = "#C0392B"
            score_color = "#C0392B"
            badge_txt = "Vigilance requise"
            badge_style = "background-color: #FADBD8; color: #C0392B;"

        diag_card = QFrame()
        diag_card.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 14px;
                border: 1px solid {border_color}40;
                border-top: 4px solid {border_color};
            }}
        """)
        diag_v = QVBoxLayout(diag_card)
        diag_v.setContentsMargins(28, 24, 28, 24)
        diag_v.setSpacing(20)

        head = QHBoxLayout()
        head.setSpacing(24)

        score_box = QFrame()
        score_box.setFixedSize(130, 130)
        score_box.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border-radius: 65px;
                border: 4px solid {border_color};
            }}
        """)
        sv = QVBoxLayout(score_box)
        sv.setContentsMargins(4, 4, 4, 4)
        sv.setSpacing(0)

        sv.addStretch()
        score_lbl = QLabel(f"{global_score:.0f}%")
        score_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_lbl.setStyleSheet(f"""
            font-size: 26pt; font-weight: 800; color: {score_color};
            background: transparent; border: none;
        """)
        sv.addWidget(score_lbl)

        sm_lbl = QLabel("SMARTMATCH")
        sm_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sm_lbl.setStyleSheet("""
            font-size: 7pt; font-weight: 800; letter-spacing: 1.2px;
            color: #7A8B9C; background: transparent; border: none;
        """)
        sv.addWidget(sm_lbl)
        sv.addStretch()

        head.addWidget(score_box)

        txt_col = QVBoxLayout()
        txt_col.setSpacing(8)

        badge_row = QHBoxLayout()
        badge_row.setSpacing(8)

        badge_row.addWidget(ColorDot(score_color, 8), 0, Qt.AlignmentFlag.AlignVCenter)

        badge = QLabel(badge_txt)
        badge.setStyleSheet(f"""
            {badge_style} padding: 5px 14px; border-radius: 12px;
            font-size: 9pt; font-weight: 700; border: none;
        """)
        badge_row.addWidget(badge)
        badge_row.addStretch()
        txt_col.addLayout(badge_row)

        diag_title = QLabel(f"Diagnostic Global : {diagnosis}")
        diag_title.setStyleSheet("""
            font-size: 16pt; font-weight: 800; color: #0F1E2E;
            background: transparent; border: none;
        """)
        diag_title.setWordWrap(True)
        txt_col.addWidget(diag_title)

        desc = QLabel(
            "L'alliance des compétences et styles de travail de ces deux "
            "collaborateurs crée une synergie opérationnelle basée sur la "
            "complémentarité de leurs profils."
        )
        desc.setStyleSheet("""
            font-size: 10pt; color: #5A6B7D; line-height: 1.5;
            background: transparent; border: none;
        """)
        desc.setWordWrap(True)
        txt_col.addWidget(desc)

        relation = result.get("relation")
        if relation:
            rel_color = relation.get("relation_color", "#7A8B9C")
            rel_label = relation.get("relation_label", "Relation")
            rel_notes = relation.get("notes")

            rel_box = QFrame()
            rel_box.setStyleSheet(f"""
                QFrame {{
                    background-color: {rel_color}12;
                    border-radius: 10px;
                    border: 1px solid {rel_color}40;
                    border-left: 4px solid {rel_color};
                }}
            """)
            rb = QVBoxLayout(rel_box)
            rb.setContentsMargins(14, 12, 14, 12)
            rb.setSpacing(4)

            t_lbl = QLabel(rel_label)
            t_lbl.setStyleSheet(f"""
                font-size: 11pt; font-weight: 700; color: {rel_color};
                background: transparent; border: none;
            """)
            rb.addWidget(t_lbl)

            detail = QLabel("Relation déclarée entre ces deux collaborateurs")
            detail.setStyleSheet("""
                font-size: 9pt; color: #5A6B7D;
                background: transparent; border: none;
            """)
            detail.setWordWrap(True)
            rb.addWidget(detail)

            if rel_notes:
                notes_lbl = QLabel(rel_notes)
                notes_lbl.setStyleSheet("""
                    font-size: 8.5pt; color: #7A8B9C; font-style: italic;
                    background: transparent; border: none;
                """)
                notes_lbl.setWordWrap(True)
                rb.addWidget(notes_lbl)

            txt_col.addWidget(rel_box)

        head.addLayout(txt_col, 1)

        btns_col = QVBoxLayout()
        btns_col.setSpacing(8)
        btns_col.setAlignment(Qt.AlignmentFlag.AlignTop)

        btn_assign = QPushButton("Assigner en Binôme")
        btn_assign.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_assign.setMinimumHeight(40)
        btn_assign.setStyleSheet("""
            QPushButton {
                background-color: #0D7A6A;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 9.5pt;
                font-weight: 700;
            }
            QPushButton:hover { background-color: #0A6456; }
        """)
        btn_assign.clicked.connect(
            lambda: self._on_assign_binome(pivot, target, global_score, diagnosis)
        )
        btns_col.addWidget(btn_assign)

        btn_share = QPushButton("Partager au CODIR")
        btn_share.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_share.setMinimumHeight(40)
        btn_share.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #0F1E2E;
                border: 1px solid #D6DEE8;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 9.5pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #F4F6F9;
                border-color: #0D7A6A;
            }
        """)
        btns_col.addWidget(btn_share)

        head.addLayout(btns_col)

        diag_v.addLayout(head)

        # 4 cartes de scores (approche SIMPLE comme l'original)
        scores_row = QGridLayout()
        scores_row.setSpacing(20)

        skills = result.get("skills_score", 0)
        comm = result.get("communication_score", 0)
        friction = result.get("friction_risk", 0)
        hierarchy = result.get("hierarchy_risk", 0)

        scores_row.addWidget(ScoreCard(
            "Complémentarité Compétences",
            skills,
            "Balance technique entre les deux profils",
            is_risk=False,
        ), 0, 0)

        scores_row.addWidget(ScoreCard(
            "Méthodes & Communication",
            comm,
            "Communication directe et réactive entre les profils",
            is_risk=False,
        ), 0, 1)

        scores_row.addWidget(ScoreCard(
            "Risque de Friction Relationnelle",
            friction,
            "Risque faible : bonne entente attendue",
            is_risk=True,
        ), 1, 0)

        scores_row.addWidget(ScoreCard(
            "Risque Hiérarchique",
            hierarchy,
            "Attention aux enjeux de gouvernance",
            is_risk=True,
        ), 1, 1)

        diag_v.addLayout(scores_row)

        self.results_container.addWidget(diag_card)

    # =====================================================
    # AFFICHAGE - MODE B (MULTI-SCAN)
    # =====================================================
    def _display_multi_results(self, pivot: dict, results: list):
        self._reset_page()

        pivot_card = CollaboratorCard(pivot, role="Collaborateur Pivot", score_data=None)
        self.results_container.addWidget(pivot_card)

        sec_row = QHBoxLayout()
        sec_row.setSpacing(10)

        sec_title = QLabel("Multi-Scan")
        sec_title.setStyleSheet("""
            font-size: 14pt; font-weight: 800; color: #0F1E2E;
            padding-top: 8px; background: transparent; border: none;
        """)
        sec_row.addWidget(sec_title)

        sec_row.addWidget(ColorDot("#0D7A6A", 6))

        sec_count = QLabel(f"{len(results)} comparaisons effectuées")
        sec_count.setStyleSheet("""
            font-size: 10pt; color: #0D7A6A; font-weight: 700;
            background: transparent; border: none;
        """)
        sec_row.addWidget(sec_count)
        sec_row.addStretch()

        sec_wrapper = QWidget()
        sec_wrapper.setLayout(sec_row)
        self.results_container.addWidget(sec_wrapper)

        grid = QGridLayout()
        grid.setSpacing(20)

        for i, r in enumerate(results):
            card = self._build_multi_result_card(r)
            grid.addWidget(card, i // 2, i % 2)

        grid_container = QWidget()
        grid_container.setLayout(grid)
        self.results_container.addWidget(grid_container)

    def _build_multi_result_card(self, result: dict) -> QFrame:
        card = QFrame()

        # Approche SIMPLE comme l'original
        global_score = result.get("global_score", 0)
        skills = result.get("skills_score", 0)
        comm = result.get("communication_score", 0)
        friction = result.get("friction_risk", 0)

        if global_score >= 80:
            color = "#0D7A6A"
        elif global_score >= 60:
            color = "#B9770E"
        else:
            color = "#C0392B"

        card.setStyleSheet(f"""
            QFrame {{
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
                border-left: 4px solid {color};
            }}
        """)
        card.setMinimumHeight(160)

        v = QVBoxLayout(card)
        v.setContentsMargins(18, 16, 18, 16)
        v.setSpacing(10)

        head = QHBoxLayout()
        name_lbl = QLabel(result.get('target_name', '—'))
        name_lbl.setStyleSheet("""
            font-size: 12.5pt; font-weight: 800; color: #0F1E2E;
            background: transparent; border: none;
        """)
        head.addWidget(name_lbl)
        head.addStretch()

        score_lbl = QLabel(f"{global_score:.0f}%")
        score_lbl.setStyleSheet(f"""
            font-size: 18pt; font-weight: 800; color: {color};
            background: transparent; border: none;
        """)
        head.addWidget(score_lbl)
        v.addLayout(head)

        diag = QLabel(result.get("diagnosis", "—"))
        diag.setStyleSheet("""
            font-size: 10pt; color: #5A6B7D;
            background: transparent; border: none;
        """)
        diag.setWordWrap(True)
        v.addWidget(diag)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #EEF2F6; border: none;")
        v.addWidget(sep)

        mini = QHBoxLayout()
        mini.setSpacing(12)

        mini.addWidget(self._mini_score("SKILLS", skills, is_risk=False), 1)
        mini.addWidget(self._mini_score("COMM.", comm, is_risk=False), 1)
        mini.addWidget(self._mini_score("FRICTION", friction, is_risk=True), 1)

        v.addLayout(mini)

        return card

    def _mini_score(self, label: str, value: float, is_risk: bool = False) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(4)

        h = QHBoxLayout()
        h.setSpacing(4)

        lbl = QLabel(label)
        lbl.setStyleSheet("""
            font-size: 7pt; color: #7A8B9C; font-weight: 800;
            letter-spacing: 0.5px; background: transparent; border: none;
        """)
        h.addWidget(lbl)
        h.addStretch()

        val = QLabel(f"{value:.0f}%")
        val.setStyleSheet("""
            font-size: 9pt; font-weight: 800; color: #0F1E2E;
            background: transparent; border: none;
        """)
        h.addWidget(val)
        v.addLayout(h)

        bar = QProgressBar()
        bar.setValue(int(value))
        bar.setMaximum(100)
        bar.setTextVisible(False)
        bar.setFixedHeight(4)

        if is_risk:
            bar_color = "#0D7A6A" if value < 20 else ("#F39C12" if value < 40 else "#C0392B")
        else:
            bar_color = "#0D7A6A" if value >= 80 else ("#F39C12" if value >= 60 else "#C0392B")

        bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #EEF2F6;
                border-radius: 2px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {bar_color};
                border-radius: 2px;
            }}
        """)
        v.addWidget(bar)

        return w