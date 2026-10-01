"""Dialogue EmployeeDialog - Creer un nouvel employe.

Formulaire simplifie avec les champs essentiels :
- Identite (prenom, nom, email, telephone)
- Poste (titre, departement, contrat)
- Embauche (date, ville, salaire)
"""
from datetime import date
from decimal import Decimal

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QDateEdit, QPushButton,
    QFrame, QWidget, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate


class EmployeeDialog(QDialog):
    """Dialogue pour creer un nouvel employe."""

    employee_created = pyqtSignal(dict)   # Signal emis avec les donnees

    def __init__(self, departments: list[dict], parent=None, prefill_data: dict = None):
        super().__init__(parent)
        self.departments = departments
        self.prefill_data = prefill_data or {}

        self.setWindowTitle("Ajouter un employe")
        self.setFixedSize(700, 620)
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
        """)

        self._setup_ui()

        # Applique les donnees pre-remplies (issues de l'IA)
        if self.prefill_data:
            self._apply_prefill()

    # =====================================================
    # INTERFACE
    # =====================================================
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ========== HEADER ==========
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #F4F6F9;
                border-bottom: 1px solid #E4E9EF;
            }
        """)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(20, 16, 20, 16)

        title = QLabel("Ajouter un nouvel employe")
        title.setStyleSheet("font-size: 14pt; font-weight: 700; color: #0F1E2E;")
        h_layout.addWidget(title)
        h_layout.addStretch()

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(32, 32)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 14pt;
                color: #7A8B9C;
            }
            QPushButton:hover { color: #C0392B; }
        """)
        btn_close.clicked.connect(self.reject)
        h_layout.addWidget(btn_close)

        layout.addWidget(header)

        # ========== CONTENU ==========
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 20, 24, 20)
        content_layout.setSpacing(16)

        # ----- Section 1 : Identite -----
        s1 = QLabel("Identité")
        s1.setStyleSheet("font-size: 11pt; font-weight: 700; color: #0F1E2E;")
        content_layout.addWidget(s1)

        g1 = QGridLayout()
        g1.setSpacing(10)

        # Prenom
        g1.addWidget(QLabel("Prénom *"), 0, 0)
        self.first_name_input = self._make_line("Ex: Marie")
        g1.addWidget(self.first_name_input, 0, 1)

        # Nom
        g1.addWidget(QLabel("Nom *"), 0, 2)
        self.last_name_input = self._make_line("Ex: DUPONT")
        g1.addWidget(self.last_name_input, 0, 3)

        # Email
        g1.addWidget(QLabel("Email *"), 1, 0)
        self.email_input = self._make_line("Ex: marie.dupont@smartrh.fr")
        g1.addWidget(self.email_input, 1, 1)

        # Telephone
        g1.addWidget(QLabel("Téléphone"), 1, 2)
        self.phone_input = self._make_line("Ex: 06 12 34 56 78")
        g1.addWidget(self.phone_input, 1, 3)

        # Date de naissance
        g1.addWidget(QLabel("Date de naissance"), 2, 0)
        self.birth_date_input = QDateEdit()
        self.birth_date_input.setCalendarPopup(True)
        self.birth_date_input.setDate(QDate(1990, 1, 1))
        self.birth_date_input.setDisplayFormat("dd/MM/yyyy")
        self.birth_date_input.setStyleSheet(self._input_style())
        g1.addWidget(self.birth_date_input, 2, 1)

        # Ville
        g1.addWidget(QLabel("Ville"), 2, 2)
        self.city_input = self._make_line("Ex: Paris")
        g1.addWidget(self.city_input, 2, 3)

        content_layout.addLayout(g1)

        # ----- Section 2 : Poste -----
        s2 = QLabel("Poste & Contrat")
        s2.setStyleSheet("font-size: 11pt; font-weight: 700; color: #0F1E2E; padding-top: 8px;")
        content_layout.addWidget(s2)

        g2 = QGridLayout()
        g2.setSpacing(10)

        # Intitule du poste
        g2.addWidget(QLabel("Intitulé du poste *"), 0, 0)
        self.job_title_input = self._make_line("Ex: Développeur Fullstack")
        g2.addWidget(self.job_title_input, 0, 1, 1, 3)

        # Departement
        g2.addWidget(QLabel("Département *"), 1, 0)
        self.dept_combo = QComboBox()
        for dept in self.departments:
            self.dept_combo.addItem(dept["name"], dept["id"])
        self.dept_combo.setStyleSheet(self._input_style())
        g2.addWidget(self.dept_combo, 1, 1)

        # Type de contrat
        g2.addWidget(QLabel("Type de contrat"), 1, 2)
        self.contract_combo = QComboBox()
        self.contract_combo.addItems(["CDI", "CDD", "Stage", "Alternance", "Freelance"])
        self.contract_combo.setStyleSheet(self._input_style())
        g2.addWidget(self.contract_combo, 1, 3)

        # Date d'embauche
        g2.addWidget(QLabel("Date d'embauche *"), 2, 0)
        self.hire_date_input = QDateEdit()
        self.hire_date_input.setCalendarPopup(True)
        self.hire_date_input.setDate(QDate.currentDate())
        self.hire_date_input.setDisplayFormat("dd/MM/yyyy")
        self.hire_date_input.setStyleSheet(self._input_style())
        g2.addWidget(self.hire_date_input, 2, 1)

        # Mode de travail
        g2.addWidget(QLabel("Mode de travail"), 2, 2)
        self.work_mode_combo = QComboBox()
        self.work_mode_combo.addItems(["présentiel", "hybride", "télétravail"])
        self.work_mode_combo.setStyleSheet(self._input_style())
        g2.addWidget(self.work_mode_combo, 2, 3)

        content_layout.addLayout(g2)

        # ----- Section 3 : Remuneration -----
        s3 = QLabel("Rémunération")
        s3.setStyleSheet("font-size: 11pt; font-weight: 700; color: #0F1E2E; padding-top: 8px;")
        content_layout.addWidget(s3)

        g3 = QGridLayout()
        g3.setSpacing(10)

        g3.addWidget(QLabel("Salaire de base (€) *"), 0, 0)
        self.salary_base_input = self._make_line("Ex: 48000")
        g3.addWidget(self.salary_base_input, 0, 1)

        g3.addWidget(QLabel("Salaire variable (€)"), 0, 2)
        self.salary_var_input = self._make_line("Ex: 5000")
        g3.addWidget(self.salary_var_input, 0, 3)

        content_layout.addLayout(g3)
        content_layout.addStretch()

        layout.addWidget(content)

        # ========== FOOTER ==========
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background-color: #F4F6F9;
                border-top: 1px solid #E4E9EF;
            }
        """)
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(20, 16, 20, 16)
        f_layout.addStretch()

        btn_cancel = QPushButton("Annuler")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #5A6B7D;
                border: 1px solid #E4E9EF;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #F4F6F9;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        f_layout.addWidget(btn_cancel)

        btn_save = QPushButton("+  Ajouter l'employé")
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #0D7A6A;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 10pt;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #0A6456; }
        """)
        btn_save.clicked.connect(self._on_submit)
        f_layout.addWidget(btn_save)

        layout.addWidget(footer)

    # =====================================================
    # HELPERS
    # =====================================================
    def _make_line(self, placeholder: str) -> QLineEdit:
        line = QLineEdit()
        line.setPlaceholderText(placeholder)
        line.setStyleSheet(self._input_style())
        return line

    def _input_style(self) -> str:
        return """
            QLineEdit, QComboBox, QDateEdit {
                border: 1px solid #E4E9EF;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 9pt;
                background-color: #FFFFFF;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 1px solid #0D7A6A;
            }
        """

    # =====================================================
    # VALIDATION & SOUMISSION
    # =====================================================
    def _on_submit(self):
        """Valide le formulaire et emet le signal."""
        # Champs obligatoires
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        email = self.email_input.text().strip()
        job_title = self.job_title_input.text().strip()
        salary_base_txt = self.salary_base_input.text().strip()

        if not first_name or not last_name:
            QMessageBox.warning(self, "Attention", "Prénom et Nom sont obligatoires.")
            return

        if not email or "@" not in email:
            QMessageBox.warning(self, "Attention", "Un email valide est obligatoire.")
            return

        if not job_title:
            QMessageBox.warning(self, "Attention", "L'intitulé du poste est obligatoire.")
            return

        try:
            salary_base = float(salary_base_txt or "0")
        except ValueError:
            QMessageBox.warning(self, "Attention", "Le salaire de base doit etre un nombre.")
            return

        try:
            salary_var = float(self.salary_var_input.text().strip() or "0")
        except ValueError:
            salary_var = 0.0

        # Departement
        dept_id = self.dept_combo.currentData()
        if not dept_id:
            QMessageBox.warning(self, "Attention", "Selectionnez un departement.")
            return

        # Convertir QDate en date Python
        birth_date = self.birth_date_input.date().toPyDate()
        hire_date = self.hire_date_input.date().toPyDate()

        # Construire le payload
        data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "phone": self.phone_input.text().strip(),
            "birth_date": birth_date,
            "job_title": job_title,
            "department_id": dept_id,
            "contract_type": self.contract_combo.currentText(),
            "hire_date": hire_date,
            "city": self.city_input.text().strip(),
            "salary_base": salary_base,
            "salary_variable": salary_var,
            "work_mode": self.work_mode_combo.currentText(),
        }

        self.employee_created.emit(data)
        self.accept()
        
    def _apply_prefill(self):
        """Applique les donnees pre-remplies (issues de l'IA)."""
        data = self.prefill_data

        if data.get("first_name"):
            self.first_name_input.setText(data["first_name"])
        if data.get("last_name"):
            self.last_name_input.setText(data["last_name"])
        if data.get("email"):
            self.email_input.setText(data["email"])
        if data.get("phone"):
            self.phone_input.setText(data["phone"])
        if data.get("city"):
            self.city_input.setText(data["city"])
        if data.get("job_title"):
            self.job_title_input.setText(data["job_title"])

        # Date de naissance
        birth = data.get("birth_date")
        if birth:
            try:
                from PyQt6.QtCore import QDate
                parts = birth.split("-")
                if len(parts) == 3:
                    y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
                    self.birth_date_input.setDate(QDate(y, m, d))
            except Exception:
                pass