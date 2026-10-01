"""Page Employes — Repertoire des Collaborateurs (Module 2 du CDC)."""

from datetime import date
from PyQt6.QtWidgets import (
    QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QScrollArea, QFrame, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from app.ui.widgets import Badge
from app.services.stats_service import StatsService
from app.ui.dialogs.employee_dialog import EmployeeDialog
from app.ui.dialogs.import_cv_dialog import ImportCVDialog
from app.services.audit_service import AuditService


# =====================================================
# AVATAR ROND
# =====================================================
class AvatarLabel(QLabel):
    """Avatar rond affichant les initiales (couleur deterministe)."""

    def __init__(self, first_name: str, last_name: str, size: int = 44):
        super().__init__()
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        initials = f"{(first_name or '?')[0]}{(last_name or '?')[0]}".upper()

        colors = ["#0D7A6A", "#1F4E5F", "#2E86DE", "#8E44AD", "#B9770E"]
        idx = sum(ord(c) for c in initials) % len(colors)
        color = colors[idx]

        self.setText(initials)
        self.setStyleSheet(f"""
            background-color: {color};
            color: white;
            border-radius: {size // 2}px;
            font-size: {size // 3}pt;
            font-weight: 700;
            border: none;
        """)


# =====================================================
# ONGLET DE FILTRE
# =====================================================
class TabButton(QPushButton):
    """Onglet pour filtrer par departement (compact)."""

    def __init__(self, label: str, count: int = None, is_active: bool = False):
        display = f"{label} ({count})" if count is not None else label
        super().__init__(display)
        self.setCheckable(True)
        self.setChecked(is_active)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(36)
        self._apply_style(is_active)

    def _apply_style(self, is_active: bool):
        if is_active:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #0D7A6A;
                    color: #FFFFFF;
                    border: none;
                    padding: 7px 14px;
                    border-radius: 6px;
                    font-size: 9pt;
                    font-weight: 700;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #F4F6F9;
                    color: #5A6B7D;
                    border: 1px solid #E4E9EF;
                    padding: 7px 14px;
                    border-radius: 6px;
                    font-size: 9pt;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #E8F5F1;
                    color: #0D7A6A;
                    border-color: #0D7A6A;
                }
            """)

    def set_active(self, active: bool):
        self.setChecked(active)
        self._apply_style(active)


# =====================================================
# CARTE EMPLOYE
# =====================================================
class EmployeeCard(QFrame):
    """Carte cliquable d'un employe dans la liste (compacte)."""

    clicked = pyqtSignal(dict)
    view_requested = pyqtSignal(dict)

    def __init__(self, employee: dict, is_active: bool = False):
        super().__init__()
        self.employee = employee
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(100)
        self.setMaximumHeight(115)

        if is_active:
            self.setStyleSheet("""
                QFrame {
                    background-color: #F4FAF8;
                    border-radius: 10px;
                    border: 1.5px solid #0D7A6A;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #FFFFFF;
                    border-radius: 10px;
                    border: 1px solid #E4E9EF;
                }
                QFrame:hover {
                    border: 1px solid #0D7A6A;
                }
            """)

        h = QHBoxLayout(self)
        h.setContentsMargins(14, 12, 14, 12)
        h.setSpacing(12)

        # === Avatar ===
        avatar = AvatarLabel(
            employee.get("first_name", ""),
            employee.get("last_name", ""),
            size=42,
        )
        h.addWidget(avatar, 0, Qt.AlignmentFlag.AlignVCenter)

        # === Colonne centrale ===
        v = QVBoxLayout()
        v.setSpacing(3)
        v.setContentsMargins(0, 0, 0, 0)

        # Ligne 1 : Nom + badge statut inline
        name_row = QHBoxLayout()
        name_row.setSpacing(6)

        name_lbl = QLabel(
            f"<b>{employee.get('first_name', '')} {employee.get('last_name', '')}</b>"
        )
        name_lbl.setStyleSheet(
            "font-size: 10.5pt; color: #0F1E2E; background: transparent; "
            "border: none; padding: 0;"
        )
        name_row.addWidget(name_lbl)

        work_mode = (employee.get("work_mode") or "").lower()
        status = employee.get("status", "actif").lower()
        city = employee.get("city") or ""

        if status == "actif":
            if "remote" in work_mode or "hybride" in work_mode:
                name_row.addWidget(Badge("Télétravail", variant="info"))
            else:
                if city:
                    name_row.addWidget(Badge(f"Présent {city}", variant="success"))
                else:
                    name_row.addWidget(Badge("Présent", variant="success"))

        name_row.addStretch()
        v.addLayout(name_row)

        # Ligne 2 : Poste
        title_lbl = QLabel(employee.get("job_title", "—"))
        title_lbl.setStyleSheet(
            "font-size: 9pt; color: #5A6B7D; background: transparent; "
            "border: none; padding: 0;"
        )
        v.addWidget(title_lbl)

        # Ligne 3 : Email
        email_lbl = QLabel(employee.get("email", "—"))
        email_lbl.setStyleSheet(
            "font-size: 8.5pt; color: #B8C4D0; background: transparent; "
            "border: none; padding: 0;"
        )
        v.addWidget(email_lbl)

        # Ligne 4 : Anciennete + departement (sans emoji)
        info_lbl = QLabel(
            f"Ancienneté : {employee.get('seniority_years', 0):.2f} ans  •  "
            f"{employee.get('department', '—')}"
        )
        info_lbl.setStyleSheet(
            "font-size: 8.5pt; color: #7A8B9C; background: transparent; "
            "border: none; padding: 0;"
        )
        v.addWidget(info_lbl)

        h.addLayout(v, 1)

        # === Colonne droite : bouton Voir dossier ===
        right_col = QVBoxLayout()
        right_col.setSpacing(0)
        right_col.setContentsMargins(0, 0, 0, 0)

        btn_view = QPushButton("Voir dossier ›")
        btn_view.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_view.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #0D7A6A;
                border: none;
                font-size: 9pt;
                font-weight: 700;
                padding: 4px 0;
                text-align: right;
            }
            QPushButton:hover { color: #0A6456; }
        """)
        btn_view.clicked.connect(lambda: self.view_requested.emit(self.employee))
        right_col.addStretch()
        right_col.addWidget(btn_view, 0, Qt.AlignmentFlag.AlignRight)
        right_col.addStretch()

        h.addLayout(right_col)

    def mousePressEvent(self, event):
        self.clicked.emit(self.employee)
        super().mousePressEvent(event)


# =====================================================
# PANNEAU DETAIL
# =====================================================
class DetailPanel(QWidget):
    """Panneau de detail avec 2 onglets : Contrat & Conges."""

    def __init__(self):
        super().__init__()

        self.active_tab = "contrat"
        self.current_employee = None

        self.v = QVBoxLayout(self)
        self.v.setContentsMargins(0, 0, 0, 0)
        self.v.setSpacing(16)

        self._show_empty()

    def _clear(self):
        while self.v.count():
            item = self.v.takeAt(0)
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

    def _show_empty(self):
        empty = QLabel("Sélectionnez un employé pour voir son dossier")
        empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty.setStyleSheet(
            "color: #7A8B9C; font-style: italic; padding: 60px; font-size: 11pt;"
            "background: #FFFFFF; border-radius: 12px; border: 1px solid #E4E9EF;"
        )
        self.v.addWidget(empty)

    def show_employee(self, employee: dict):
        self.current_employee = employee
        self._clear()
        self._build_layout()

    def _on_tab_click(self, tab_name: str):
        self.active_tab = tab_name
        self._clear()
        self._build_layout()

    def _build_layout(self):
        employee = self.current_employee

        # CARTE HEADER
        header_card = QFrame()
        header_card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
            }
        """)
        hv = QVBoxLayout(header_card)
        hv.setContentsMargins(20, 16, 20, 16)
        hv.setSpacing(14)

        # Ligne ID
        id_lbl = QLabel(f"ID: {employee.get('employee_code', '—')}")
        id_lbl.setStyleSheet("""
            font-size: 8.5pt; color: #7A8B9C; font-weight: 600;
            background-color: #F4F6F9; border: none;
            padding: 3px 10px; border-radius: 4px;
        """)
        id_row = QHBoxLayout()
        id_row.addWidget(id_lbl)
        id_row.addStretch()
        hv.addLayout(id_row)

        # Avatar + infos
        main_row = QHBoxLayout()
        main_row.setSpacing(16)

        avatar = AvatarLabel(
            employee.get("first_name", ""),
            employee.get("last_name", ""),
            size=72,
        )
        main_row.addWidget(avatar, 0, Qt.AlignmentFlag.AlignTop)

        info_col = QVBoxLayout()
        info_col.setSpacing(5)

        name_row = QHBoxLayout()
        name_row.setSpacing(10)

        name_lbl = QLabel(
            f"<b>{employee.get('first_name', '')} {employee.get('last_name', '')}</b>"
        )
        name_lbl.setStyleSheet(
            "font-size: 16pt; font-weight: 800; color: #0F1E2E; "
            "background: transparent; border: none; padding: 0;"
        )
        name_row.addWidget(name_lbl)

        dept_full = employee.get("department", "")
        if dept_full and dept_full != "—":
            dept_clean = dept_full.replace("R&D / Ingenierie Produit", "R&D / Tech")
            dept_clean = dept_clean.replace("Support & Succes Client", "Support")
            dept_clean = dept_clean.replace("Commercial & Partenariats", "Commercial")
            dept_clean = dept_clean.replace("Ressources Humaines & RSE", "RH & RSE")
            name_row.addWidget(Badge(dept_clean, variant="info"))

        name_row.addStretch()
        info_col.addLayout(name_row)

        title_lbl = QLabel(employee.get("job_title", "—"))
        title_lbl.setStyleSheet(
            "font-size: 10pt; color: #5A6B7D; "
            "background: transparent; border: none; padding: 0;"
        )
        info_col.addWidget(title_lbl)

        # Contacts 1 : email + tél + ville (avec préfixes textuels)
        contacts1 = QHBoxLayout()
        contacts1.setSpacing(16)

        email_lbl = QLabel(f"Email : {employee.get('email', '—')}")
        email_lbl.setStyleSheet(
            "font-size: 9pt; color: #7A8B9C; "
            "background: transparent; border: none; padding: 0;"
        )
        contacts1.addWidget(email_lbl)

        phone = employee.get("phone") or "—"
        phone_lbl = QLabel(f"Tél : {phone}")
        phone_lbl.setStyleSheet(
            "font-size: 9pt; color: #7A8B9C; "
            "background: transparent; border: none; padding: 0;"
        )
        contacts1.addWidget(phone_lbl)

        city_lbl = QLabel(f"Ville : {employee.get('city', '—')}")
        city_lbl.setStyleSheet(
            "font-size: 9pt; color: #7A8B9C; "
            "background: transparent; border: none; padding: 0;"
        )
        contacts1.addWidget(city_lbl)
        contacts1.addStretch()
        info_col.addLayout(contacts1)

        # Contacts 2 : âge + N+1 (avec préfixes textuels)
        contacts2 = QHBoxLayout()
        contacts2.setSpacing(16)

        age_txt = "—"
        bd = employee.get("birth_date")
        if bd and hasattr(bd, "year"):
            today = date.today()
            age = today.year - bd.year
            if (today.month, today.day) < (bd.month, bd.day):
                age -= 1
            age_txt = f"{age} ans ({bd.strftime('%d/%m/%Y')})"

        age_lbl = QLabel(f"Âge : {age_txt}")
        age_lbl.setStyleSheet(
            "font-size: 9pt; color: #7A8B9C; "
            "background: transparent; border: none; padding: 0;"
        )
        contacts2.addWidget(age_lbl)

        from app.db.connection import get_session
        from app.models.employee import Employee as EmpModel
        manager_name = "—"
        if employee.get("manager_id"):
            try:
                with get_session() as db:
                    mgr = db.get(EmpModel, employee["manager_id"])
                    if mgr:
                        manager_name = mgr.full_name
            except Exception:
                pass

        mgr_lbl = QLabel(f"N+1 : {manager_name}")
        mgr_lbl.setStyleSheet(
            "font-size: 9pt; color: #7A8B9C; "
            "background: transparent; border: none; padding: 0;"
        )
        contacts2.addWidget(mgr_lbl)
        contacts2.addStretch()
        info_col.addLayout(contacts2)

        main_row.addLayout(info_col, 1)
        hv.addLayout(main_row)

        # Onglets
        tabs_row = QHBoxLayout()
        tabs_row.setSpacing(20)

        is_contrat = (self.active_tab == "contrat")
        tab_contrat = QPushButton("Contrat Poste")
        tab_contrat.setCursor(Qt.CursorShape.PointingHandCursor)
        if is_contrat:
            tab_contrat.setStyleSheet("""
                QPushButton {
                    background: transparent; color: #0F1E2E;
                    font-size: 10pt; font-weight: 700; border: none;
                    border-bottom: 2px solid #0D7A6A; padding: 6px 4px;
                }
            """)
        else:
            tab_contrat.setStyleSheet("""
                QPushButton {
                    background: transparent; color: #7A8B9C;
                    font-size: 10pt; font-weight: 500; border: none;
                    padding: 6px 4px;
                }
                QPushButton:hover { color: #0D7A6A; }
            """)
        tab_contrat.clicked.connect(lambda: self._on_tab_click("contrat"))
        tabs_row.addWidget(tab_contrat)

        is_conges = (self.active_tab == "conges")
        tab_conges = QPushButton("Congés Absences")
        tab_conges.setCursor(Qt.CursorShape.PointingHandCursor)
        if is_conges:
            tab_conges.setStyleSheet("""
                QPushButton {
                    background: transparent; color: #0F1E2E;
                    font-size: 10pt; font-weight: 700; border: none;
                    border-bottom: 2px solid #0D7A6A; padding: 6px 4px;
                }
            """)
        else:
            tab_conges.setStyleSheet("""
                QPushButton {
                    background: transparent; color: #7A8B9C;
                    font-size: 10pt; font-weight: 500; border: none;
                    padding: 6px 4px;
                }
                QPushButton:hover { color: #0D7A6A; }
            """)
        tab_conges.clicked.connect(lambda: self._on_tab_click("conges"))
        tabs_row.addWidget(tab_conges)

        tabs_row.addStretch()
        hv.addLayout(tabs_row)

        self.v.addWidget(header_card)

        if self.active_tab == "contrat":
            self._build_contrat_tab()
        else:
            self._build_conges_tab()

        self.v.addStretch()

    # =====================================================
    # ONGLET CONTRAT
    # =====================================================
    def _build_contrat_tab(self):
        employee = self.current_employee

        bloc = QFrame()
        bloc.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
            }
        """)
        bv = QVBoxLayout(bloc)
        bv.setContentsMargins(20, 16, 20, 16)
        bv.setSpacing(16)

        t_row = QHBoxLayout()
        t = QLabel("Contrat & Rémunération")
        t.setStyleSheet(
            "font-size: 11.5pt; font-weight: 700; color: #0F1E2E; "
            "background: transparent; border: none; padding: 0;"
        )
        t_row.addWidget(t)
        t_row.addStretch()

        contract = employee.get("contract_type", "—")
        if contract and contract != "—":
            t_row.addWidget(Badge(contract, variant="info"))

        status = employee.get("status", "—")
        if status and status != "—":
            status_variant = "success" if status == "actif" else "info"
            t_row.addWidget(Badge(status.capitalize(), variant=status_variant))

        bv.addLayout(t_row)

        grid = QGridLayout()
        grid.setSpacing(10)

        hire = employee.get("hire_date")
        hire_txt = hire.strftime("%d/%m/%Y") if hasattr(hire, "strftime") else str(hire) if hire else "—"

        grid.addWidget(self._info_block(
            "DATE D'EMBAUCHE", hire_txt,
            f"{employee.get('seniority_years', 0):.2f} ans d'ancienneté"
        ), 0, 0)

        grid.addWidget(self._info_block(
            "TYPE DE CONTRAT",
            employee.get("contract_type", "—"),
            "Temps Plein" if employee.get("contract_type") else "—"
        ), 0, 1)

        work_mode = employee.get("work_mode", "—")
        work_mode_txt = work_mode.capitalize() if work_mode and work_mode != "—" else "—"
        grid.addWidget(self._info_block(
            "MODE DE TRAVAIL", work_mode_txt, "—"
        ), 1, 0)

        grid.addWidget(self._info_block(
            "DÉPARTEMENT",
            employee.get("department", "—"),
            f"Code: {employee.get('employee_code', '—')}"
        ), 1, 1)

        bv.addLayout(grid)

        salaire = float(employee.get("salary_base", 0))
        salaire_var = float(employee.get("salary_variable", 0) or 0)

        rem_block = QFrame()
        rem_block.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border-radius: 8px;
                border: 1px solid #EEF2F6;
            }
        """)
        rv = QHBoxLayout(rem_block)
        rv.setContentsMargins(14, 10, 14, 10)

        rl = QLabel("Rémunération annuelle brute")
        rl.setStyleSheet(
            "font-size: 9pt; color: #7A8B9C; font-weight: 600; "
            "background: transparent; border: none; padding: 0;"
        )
        rv.addWidget(rl)
        rv.addStretch()

        salary_txt = f"<b>{salaire:,.0f} €</b>"
        if salaire_var > 0:
            salary_txt += f" + {salaire_var:,.0f} € variable"
        sl = QLabel(salary_txt)
        sl.setStyleSheet(
            "font-size: 12pt; color: #0F1E2E; "
            "background: transparent; border: none; padding: 0;"
        )
        rv.addWidget(sl)

        bv.addWidget(rem_block)
        self.v.addWidget(bloc)

    # =====================================================
    # ONGLET CONGES
    # =====================================================
    def _build_conges_tab(self):
        employee = self.current_employee
        emp_id = employee.get("id")

        history = []
        try:
            history = StatsService().get_employee_leave_history(emp_id)
        except Exception as e:
            print(f"[DetailPanel] Erreur conges: {e}")

        DROIT_CP = 25.0
        DROIT_RTT = 10.0

        used_cp = sum(
            float(h.get("duration", 0)) for h in history
            if h.get("type", "").lower() in ["conge paye", "congé payé", "conges payes"]
            and h.get("status") == "valide"
        )
        used_rtt = sum(
            float(h.get("duration", 0)) for h in history
            if h.get("type", "").lower() == "rtt"
            and h.get("status") == "valide"
        )

        solde_cp = max(0.0, DROIT_CP - used_cp)
        solde_rtt = max(0.0, DROIT_RTT - used_rtt)

        bloc = QFrame()
        bloc.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
            }
        """)
        bv = QVBoxLayout(bloc)
        bv.setContentsMargins(20, 16, 20, 16)
        bv.setSpacing(14)

        t_row = QHBoxLayout()
        t = QLabel("Congés & Absences")
        t.setStyleSheet(
            "font-size: 11.5pt; font-weight: 700; color: #0F1E2E; "
            "background: transparent; border: none; padding: 0;"
        )
        t_row.addWidget(t)
        t_row.addStretch()

        t_row.addWidget(Badge(f"{len(history)} demande(s)", variant="warning"))

        badge_solde = QLabel(f"Solde CP : {solde_cp:.1f}j")
        badge_solde.setStyleSheet(
            "background-color: #E8F5F1; color: #0D7A6A; "
            "padding: 4px 10px; border-radius: 10px; "
            "font-size: 8pt; font-weight: 700; border: none;"
        )
        t_row.addWidget(badge_solde)
        bv.addLayout(t_row)

        soldes_row = QHBoxLayout()
        soldes_row.setSpacing(10)

        soldes_row.addWidget(self._info_block(
            "SOLDE CONGÉS PAYÉS", f"{solde_cp:.1f} jours",
            f"sur {DROIT_CP:.0f} jours annuels"
        ))
        soldes_row.addWidget(self._info_block(
            "SOLDE RTT", f"{solde_rtt:.1f} jours",
            f"sur {DROIT_RTT:.0f} jours annuels"
        ))
        bv.addLayout(soldes_row)

        hist_title = QLabel("Historique des demandes et absences")
        hist_title.setStyleSheet(
            "font-size: 10.5pt; font-weight: 700; color: #0F1E2E; padding-top: 4px; "
            "background: transparent; border: none;"
        )
        bv.addWidget(hist_title)

        if not history:
            empty = QLabel("Aucun congé enregistré pour cet employé")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet(
                "color: #7A8B9C; font-style: italic; padding: 24px; "
                "background: #F8FAFC; border-radius: 8px; border: 1px dashed #E4E9EF;"
            )
            bv.addWidget(empty)
        else:
            header_row = QHBoxLayout()
            header_row.setSpacing(8)
            for txt, w in [("TYPE", 2), ("PÉRIODE", 3), ("DURÉE", 1), ("STATUT", 2)]:
                lbl = QLabel(txt)
                lbl.setStyleSheet(
                    "font-size: 7.5pt; color: #7A8B9C; font-weight: 700; "
                    "letter-spacing: 0.5px; background: transparent; border: none;"
                )
                header_row.addWidget(lbl, w)
            bv.addLayout(header_row)

            for h in history:
                row = QHBoxLayout()
                row.setSpacing(8)

                type_lbl = QLabel(h.get("type", "—"))
                type_lbl.setStyleSheet(
                    "font-size: 9pt; color: #0F1E2E; font-weight: 600; "
                    "background: transparent; border: none;"
                )
                row.addWidget(type_lbl, 2)

                start = h.get("start")
                end = h.get("end")
                if start and end:
                    s = start.strftime("%d/%m/%Y") if hasattr(start, "strftime") else str(start)
                    e = end.strftime("%d/%m/%Y") if hasattr(end, "strftime") else str(end)
                    period_txt = f"{s} → {e}"
                elif start:
                    s = start.strftime("%d/%m/%Y") if hasattr(start, "strftime") else str(start)
                    period_txt = s
                else:
                    period_txt = "—"
                per_lbl = QLabel(period_txt)
                per_lbl.setStyleSheet(
                    "font-size: 9pt; color: #5A6B7D; "
                    "background: transparent; border: none;"
                )
                row.addWidget(per_lbl, 3)

                dur = h.get("duration", 0)
                dur_lbl = QLabel(f"{float(dur):.1f} j")
                dur_lbl.setStyleSheet(
                    "font-size: 9pt; color: #0F1E2E; font-weight: 600; "
                    "background: transparent; border: none;"
                )
                row.addWidget(dur_lbl, 1)

                status_val = h.get("status", "—")
                # ✅ Emojis "✓" retirés → texte simple
                status_map = {
                    "valide": ("Validé", "success"),
                    "validé": ("Validé", "success"),
                    "en_attente": ("En attente", "warning"),
                    "refuse": ("Refusé", "danger"),
                    "refusé": ("Refusé", "danger"),
                }
                if status_val in status_map:
                    txt, variant = status_map[status_val]
                else:
                    txt, variant = status_val.capitalize(), "info"

                if status_val in ("en_attente", "En attente"):
                    # ✅ Emoji "✓" retiré → texte simple
                    btn_validate = QPushButton("Valider (RH)")
                    btn_validate.setCursor(Qt.CursorShape.PointingHandCursor)
                    btn_validate.setStyleSheet("""
                        QPushButton {
                            background-color: #0D7A6A;
                            color: #FFFFFF;
                            border: none;
                            padding: 6px 14px;
                            border-radius: 6px;
                            font-size: 8.5pt;
                            font-weight: 700;
                        }
                        QPushButton:hover { background-color: #0A6456; }
                    """)
                    leave_id = h.get("id")
                    btn_validate.clicked.connect(
                        lambda _, lid=leave_id: self._on_validate_leave(lid)
                    )
                    row.addWidget(btn_validate, 2, Qt.AlignmentFlag.AlignRight)
                else:
                    row.addWidget(Badge(txt, variant=variant), 2)

                bv.addLayout(row)

        actions = QHBoxLayout()
        actions.addStretch()

        btn_demande = QPushButton("+  Poser une demande")
        btn_demande.setObjectName("primaryButton")
        btn_demande.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_demande.clicked.connect(self._on_new_leave)
        actions.addWidget(btn_demande)

        bv.addLayout(actions)
        self.v.addWidget(bloc)

    # =====================================================
    # ACTIONS
    # =====================================================
    def _on_validate_leave(self, leave_id: str):
        success = StatsService().validate_leave(leave_id)
        if success:
            AuditService().log_action(
                action="validate_leave",
                entity_type="leave",
                entity_id=leave_id,
                details="Validation d'une demande de congé",
            )
            QMessageBox.information(self, "Succès", "Le congé a été validé.")
            self._on_tab_click("conges")
        else:
            QMessageBox.warning(self, "Erreur", "Impossible de valider le congé.")

    def _on_new_leave(self):
        from app.ui.dialogs.leave_dialog import LeaveDialog

        employee = self.current_employee
        if not employee:
            return

        emp_name = f"{employee.get('first_name', '')} {employee.get('last_name', '')}"

        dialog = LeaveDialog(emp_name, self)
        if dialog.exec():
            data = dialog.result_data
            if not data:
                return

            success = StatsService().create_leave_request(
                employee_id=employee.get("id"),
                leave_type=data["leave_type"],
                start_date=data["start_date"],
                end_date=data["end_date"],
                reason=data["reason"],
            )

            if success:
                AuditService().log_action(
                    action="create_leave",
                    entity_type="leave",
                    entity_id=employee.get("id"),
                    details=f"{data['leave_type']} : {data['start_date']} → {data['end_date']}",
                )
                QMessageBox.information(
                    self, "Succès",
                    f"Demande de {data['leave_type']} créée avec succès."
                )
                self._on_tab_click("conges")
            else:
                QMessageBox.warning(self, "Erreur", "Impossible de créer la demande.")

    # =====================================================
    # HELPER
    # =====================================================
    def _info_block(self, label, value, subtitle=""):
        box = QFrame()
        box.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border-radius: 8px;
                border: 1px solid #EEF2F6;
            }
        """)
        v = QVBoxLayout(box)
        v.setContentsMargins(14, 12, 14, 12)
        v.setSpacing(3)

        lbl = QLabel(label.upper())
        lbl.setStyleSheet(
            "font-size: 7.5pt; color: #7A8B9C; font-weight: 700; "
            "letter-spacing: 0.5px; background: transparent; border: none; padding: 0;"
        )
        v.addWidget(lbl)

        val = QLabel(str(value))
        val.setStyleSheet(
            "font-size: 11pt; font-weight: 700; color: #0F1E2E; "
            "background: transparent; border: none; padding: 0;"
        )
        val.setWordWrap(True)
        v.addWidget(val)

        if subtitle:
            sub = QLabel(subtitle)
            sub.setStyleSheet(
                "font-size: 8pt; color: #7A8B9C; "
                "background: transparent; border: none; padding: 0;"
            )
            sub.setWordWrap(True)
            v.addWidget(sub)

        return box


# =====================================================
# PAGE PRINCIPALE
# =====================================================
class EmployeesPage(QWidget):
    """Page Employes complete."""

    navigate_to = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.stats_svc = StatsService()
        self.current_dept_filter = "Tous"
        self.all_employees = []
        self.current_selected = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(24, 20, 24, 20)
        outer.setSpacing(14)

        # ============================================
        # 1. HEADER
        # ============================================
        header = QHBoxLayout()
        header.setSpacing(16)

        left_head = QVBoxLayout()
        left_head.setSpacing(4)
        left_head.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Ligne titre + badge "PORTAL TALENTS"
        title_row = QHBoxLayout()
        title_row.setSpacing(10)

        t = QLabel("Répertoire des Collaborateurs")
        t.setStyleSheet(
            "font-size: 18pt; font-weight: 800; color: #0F1E2E; "
            "background: transparent; border: none; padding: 0;"
        )
        title_row.addWidget(t)

        badge_portal = QLabel("PORTAL TALENTS")
        badge_portal.setFixedHeight(22)
        badge_portal.setStyleSheet("""
            QLabel {
                background-color: #E8F5F1;
                color: #0D7A6A;
                padding: 2px 12px;
                border-radius: 11px;
                font-size: 8pt;
                font-weight: 800;
                letter-spacing: 0.8px;
                border: none;
            }
        """)
        title_row.addWidget(badge_portal, 0, Qt.AlignmentFlag.AlignVCenter)
        title_row.addStretch()
        left_head.addLayout(title_row)

        s = QLabel("Consultez, filtrez et pilotez les fiches talents, contrats actifs et trajectoires RH du groupe.")
        s.setStyleSheet(
            "font-size: 9pt; color: #7A8B9C; "
            "background: transparent; border: none; padding: 0;"
        )
        s.setWordWrap(True)
        left_head.addWidget(s)

        header.addLayout(left_head, 1)

        # KPIs inline (compacts)
        kpis = self._load_kpis()

        kpi_box1 = QFrame()
        kpi_box1.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                border: 1px solid #E4E9EF;
            }
        """)
        kpi_h1 = QHBoxLayout(kpi_box1)
        kpi_h1.setContentsMargins(16, 10, 16, 10)
        kpi_h1.setSpacing(24)
        kpi_h1.addLayout(self._header_kpi(
            "EFFECTIF TOTAL", str(kpis["total_employees"])
        ))

        kpi_box2 = QFrame()
        kpi_box2.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                border: 1px solid #E4E9EF;
            }
        """)
        kpi_h2 = QHBoxLayout(kpi_box2)
        kpi_h2.setContentsMargins(16, 10, 16, 10)
        kpi_h2.setSpacing(24)
        kpi_h2.addLayout(self._header_kpi(
            "TAUX DE PRÉSENCE", f"{kpis['presence_rate']}%"
        ))

        header.addWidget(kpi_box1, 0, Qt.AlignmentFlag.AlignTop)
        header.addWidget(kpi_box2, 0, Qt.AlignmentFlag.AlignTop)

        outer.addLayout(header)

        # ============================================
        # 2. BARRE D'ONGLETS SUR 2 LIGNES
        # ============================================
        tabs_frame = QFrame()
        tabs_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                border: 1px solid #E4E9EF;
            }
        """)
        tabs_v = QVBoxLayout(tabs_frame)
        tabs_v.setContentsMargins(12, 10, 12, 10)
        tabs_v.setSpacing(8)

        self.all_employees = self._load_employees()
        dept_counts = self._count_by_dept()

        # --- LIGNE 1 : filtres par département ---
        row1 = QHBoxLayout()
        row1.setSpacing(6)

        departments = [("Tous", dept_counts.get("Tous", 0))]
        for dept_name, count in sorted(dept_counts.items()):
            if dept_name == "Tous":
                continue
            departments.append((dept_name, count))

        self.tab_buttons = {}
        for dept, count in departments:
            btn = TabButton(dept, count, is_active=(dept == "Tous"))
            btn.clicked.connect(lambda _, d=dept: self._on_tab_click(d))
            row1.addWidget(btn)
            self.tab_buttons[dept] = btn

        row1.addStretch()
        tabs_v.addLayout(row1)

        # --- LIGNE 2 : actions ---
        row2 = QHBoxLayout()
        row2.setSpacing(8)

        # ✅ Emoji "🔄" retiré → texte simple
        btn_refresh = QPushButton("Rafraîchir")
        btn_refresh.setObjectName("secondaryButton")
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setMinimumHeight(36)
        btn_refresh.clicked.connect(self._reload)
        row2.addWidget(btn_refresh)

        # ✅ Emoji "📥" déjà retiré
        btn_import = QPushButton("Importer CV")
        btn_import.setObjectName("secondaryButton")
        btn_import.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_import.setMinimumHeight(36)
        btn_import.clicked.connect(self._on_import_cv)
        row2.addWidget(btn_import)

        btn_new = QPushButton("+  Nouvel employé")
        btn_new.setObjectName("primaryButton")
        btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new.setMinimumHeight(36)
        btn_new.clicked.connect(self._on_new_employee)
        row2.addWidget(btn_new)

        row2.addStretch()
        tabs_v.addLayout(row2)

        outer.addWidget(tabs_frame)

        # ============================================
        # 3. CONTENU : Liste | Separateur | Detail
        # ============================================
        content = QHBoxLayout()
        content.setSpacing(14)

        # --- Colonne gauche : liste ---
        left_col = QVBoxLayout()
        left_col.setSpacing(8)

        list_head = QHBoxLayout()
        self.count_lbl = QLabel(f"<b>{len(self.all_employees)}</b> COLLABORATEURS ACTIFS")
        self.count_lbl.setStyleSheet(
            "font-size: 9pt; color: #5A6B7D; font-weight: 700; "
            "letter-spacing: 0.5px; background: transparent; border: none; padding: 0;"
        )
        list_head.addWidget(self.count_lbl)
        list_head.addStretch()

        # ✅ Emoji "⇅" retiré → texte simple
        tri_lbl = QLabel("Trier : Récent")
        tri_lbl.setStyleSheet(
            "font-size: 9pt; color: #7A8B9C; "
            "background: transparent; border: none; padding: 0;"
        )
        list_head.addWidget(tri_lbl)
        left_col.addLayout(list_head)

        # ==========================================
        # LISTE SCROLLABLE (HORIZONTAL + VERTICAL)
        # ==========================================
        self.list_scroll = QScrollArea()
        self.list_scroll.setWidgetResizable(True)
        self.list_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.list_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.list_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.list_scroll.setStyleSheet(
            "QScrollArea { background-color: transparent; border: none; }"
        )

        self.list_inner = QWidget()
        self.list_inner.setMinimumWidth(420)
        self.list_inner.setStyleSheet("background-color: transparent;")
        self.list_scroll.setWidget(self.list_inner)

        self.list_layout = QVBoxLayout(self.list_inner)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(8)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        left_col.addWidget(self.list_scroll, 1)
        content.addLayout(left_col, 5)

        # --- Séparateur vertical ---
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet("background-color: #E4E9EF; max-width: 1px;")
        content.addWidget(separator)

        # --- Colonne droite : detail (scrollable aussi) ---
        self.detail_scroll = QScrollArea()
        self.detail_scroll.setWidgetResizable(True)
        self.detail_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.detail_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.detail_scroll.setStyleSheet(
            "QScrollArea { background-color: transparent; border: none; }"
        )

        self.detail_panel = DetailPanel()
        self.detail_scroll.setWidget(self.detail_panel)
        content.addWidget(self.detail_scroll, 6)

        outer.addLayout(content, 1)

        self._render_employee_list()

    # =====================================================
    # HELPERS
    # =====================================================
    def _header_kpi(self, label, value):
        """KPI compact : label à gauche, valeur à droite."""
        h = QHBoxLayout()
        h.setSpacing(16)

        lbl = QLabel(label.upper())
        lbl.setStyleSheet(
            "font-size: 7.5pt; color: #7A8B9C; font-weight: 700; "
            "letter-spacing: 0.5px; background: transparent; border: none; padding: 0;"
        )
        h.addWidget(lbl)

        val = QLabel(value)
        val.setStyleSheet(
            "font-size: 14pt; font-weight: 800; color: #0F1E2E; "
            "background: transparent; border: none; padding: 0;"
        )
        h.addWidget(val)

        return h

    def _count_by_dept(self) -> dict:
        counts = {"Tous": len(self.all_employees)}
        for e in self.all_employees:
            dept = e.get("department", "—")
            if dept and dept != "—":
                counts[dept] = counts.get(dept, 0) + 1
        return counts

    def _load_kpis(self) -> dict:
        try:
            return self.stats_svc.get_employee_kpis()
        except Exception as e:
            print(f"[EmployeesPage] Erreur KPIs: {e}")
            return {"total_employees": 0, "presence_rate": 0, "absence_rate": 0}

    def _load_employees(self) -> list:
        try:
            return self.stats_svc.get_all_employees()
        except Exception as e:
            print(f"[EmployeesPage] Erreur employees: {e}")
            return []

    def _reload(self):
        self.all_employees = self._load_employees()
        self._render_employee_list()

    def _on_import_cv(self):
        try:
            dialog = ImportCVDialog(mode="employee", parent=self)
            dialog.cv_imported.connect(self._on_employee_from_cv)
            dialog.exec()
        except Exception as e:
            print(f"[EmployeesPage] Erreur import CV: {e}")
            QMessageBox.critical(self, "Erreur", str(e))

    def _on_employee_from_cv(self, data: dict):
        try:
            departments = self.stats_svc.get_all_departments()
            dialog = EmployeeDialog(departments, self, prefill_data=data)
            dialog.employee_created.connect(self._on_employee_created)
            dialog.exec()
        except Exception as e:
            print(f"[EmployeesPage] Erreur: {e}")

    def _on_new_employee(self):
        try:
            departments = self.stats_svc.get_all_departments()
            dialog = EmployeeDialog(departments, self)
            dialog.employee_created.connect(self._on_employee_created)
            dialog.exec()
        except Exception as e:
            print(f"[EmployeesPage] Erreur dialogue: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible d'ouvrir le formulaire :\n{e}")

    def _on_employee_created(self, data: dict):
        try:
            if self.stats_svc.email_exists(data["email"]):
                QMessageBox.warning(
                    self, "Email deja utilise",
                    f"L'email {data['email']} existe deja dans le systeme."
                )
                return

            emp_id = self.stats_svc.create_employee(**data)

            AuditService().log_action(
                action="create_employee",
                entity_type="employee",
                entity_id=emp_id,
                details=f"{data['first_name']} {data['last_name']} — {data['job_title']}",
            )

            QMessageBox.information(
                self, "Succes",
                f"L'employe {data['first_name']} {data['last_name']} a ete cree."
            )

            self._reload()

        except Exception as e:
            print(f"[EmployeesPage] Erreur creation employe: {e}")
            QMessageBox.critical(self, "Erreur", f"Impossible de creer l'employe :\n{e}")

    def _render_employee_list(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if self.current_dept_filter == "Tous":
            filtered = self.all_employees
        else:
            filtered = [
                e for e in self.all_employees
                if e.get("department", "") == self.current_dept_filter
            ]

        self.count_lbl.setText(f"<b>{len(filtered)}</b> COLLABORATEURS ACTIFS")

        if not filtered:
            empty = QLabel("Aucun employé pour ce filtre")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setStyleSheet(
                "color: #7A8B9C; font-style: italic; padding: 40px;"
            )
            self.list_layout.addWidget(empty)
            return

        for emp in filtered:
            is_active = (self.current_selected and
                         self.current_selected.get("id") == emp.get("id"))
            card = EmployeeCard(emp, is_active=is_active)
            card.clicked.connect(self._on_employee_click)
            card.view_requested.connect(self._on_employee_click)
            self.list_layout.addWidget(card)

        if filtered and not self.current_selected:
            self.current_selected = filtered[0]
            self.detail_panel.show_employee(filtered[0])

    def _on_employee_click(self, employee: dict):
        self.current_selected = employee
        self.detail_panel.show_employee(employee)
        self._render_employee_list()

    def _on_tab_click(self, dept: str):
        self.current_dept_filter = dept
        for d, btn in self.tab_buttons.items():
            btn.set_active(d == dept)
        self._render_employee_list()