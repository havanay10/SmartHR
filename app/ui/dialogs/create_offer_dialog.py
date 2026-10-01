"""Dialogue CreateOfferDialog - Créer une nouvelle offre d'emploi.

Formulaire complet pour créer une offre d'emploi avec :
- Informations clés (titre, département, contrat, salaire, etc.)
- Compétences techniques avec système de tags
- Soft skills avec sélection
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QScrollArea,
    QFrame, QWidget, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal
from decimal import Decimal


class TagButton(QPushButton):
    """Bouton tag pour les compétences."""

    def __init__(self, text: str, removable: bool = False, parent=None):
        super().__init__(text, parent)
        self.removable = removable
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        if removable:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #E8F5F1;
                    color: #0D7A6A;
                    border: 1px solid #0D7A6A;
                    border-radius: 16px;
                    padding: 6px 12px;
                    font-size: 9pt;
                }
                QPushButton:hover {
                    background-color: #0D7A6A;
                    color: #FFFFFF;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #F4F6F9;
                    color: #5A6B7D;
                    border: 1px solid #E4E9EF;
                    border-radius: 16px;
                    padding: 6px 12px;
                    font-size: 9pt;
                }
                QPushButton:hover {
                    background-color: #E8F5F1;
                    color: #0D7A6A;
                    border-color: #0D7A6A;
                }
                QPushButton:checked {
                    background-color: #0D7A6A;
                    color: #FFFFFF;
                    border-color: #0D7A6A;
                }
            """)
            self.setCheckable(True)


class CreateOfferDialog(QDialog):
    """Dialogue pour créer une nouvelle offre d'emploi."""

    offer_created = pyqtSignal(dict)  # Signal émis avec les données de l'offre

    def __init__(self, departments: list[dict], parent=None):
        super().__init__(parent)
        self.departments = departments
        self.setWindowTitle("Créer une nouvelle offre d'emploi")
        self.setFixedSize(900, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
            }
        """)

        # Données du formulaire
        self.hard_skills = []
        self.soft_skills = []

        self._setup_ui()

    def _setup_ui(self):
        """Configure l'interface du dialogue."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ===== Header =====
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #F4F6F9;
                border-bottom: 1px solid #E4E9EF;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 16, 20, 16)

        title = QLabel("Créer une nouvelle offre d'emploi")
        title.setStyleSheet(
            "font-size: 14pt; font-weight: 700; color: #0F1E2E;"
        )
        header_layout.addWidget(title)

        header_layout.addStretch()

        btn_close = QPushButton("✕")
        btn_close.setFixedSize(32, 32)
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 14pt;
                color: #7A8B9C;
            }
            QPushButton:hover {
                color: #C0392B;
            }
        """)
        btn_close.clicked.connect(self.reject)
        header_layout.addWidget(btn_close)

        layout.addWidget(header)

        # ===== Contenu principal =====
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(24, 20, 24, 20)
        content_layout.setSpacing(24)

        # ===== Section gauche : Informations clés =====
        left_section = QFrame()
        left_layout = QVBoxLayout(left_section)
        left_layout.setSpacing(16)

        left_title = QLabel("Informations Clés & Profil")
        left_title.setStyleSheet(
            "font-size: 11pt; font-weight: 700; color: #0F1E2E;"
        )
        left_layout.addWidget(left_title)

        # Formulaire
        form_layout = QGridLayout()
        form_layout.setSpacing(12)

        # Intitulé du poste
        form_layout.addWidget(QLabel("INTITULÉ DU POSTE"), 0, 0)
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Ex: Développeur Fullstack Lead")
        self.title_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E4E9EF;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 9pt;
            }
        """)
        form_layout.addWidget(self.title_input, 0, 1)

        # Département
        form_layout.addWidget(QLabel("DÉPARTEMENT / PÔLE"), 1, 0)
        self.dept_combo = QComboBox()
        for dept in self.departments:
            self.dept_combo.addItem(dept['name'], dept['id'])
        self.dept_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #E4E9EF;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 9pt;
            }
        """)
        form_layout.addWidget(self.dept_combo, 1, 1)

        # Type de contrat
        form_layout.addWidget(QLabel("TYPE DE CONTRAT"), 2, 0)
        self.contract_combo = QComboBox()
        self.contract_combo.addItems([
            "CDI - Temps plein",
            "CDI - Temps partiel",
            "CDD",
            "Freelance",
        ])
        self.contract_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #E4E9EF;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 9pt;
            }
        """)
        form_layout.addWidget(self.contract_combo, 2, 1)

        # Expérience requise
        form_layout.addWidget(QLabel("EXPÉRIENCE REQUISE"), 3, 0)
        self.experience_combo = QComboBox()
        self.experience_combo.addItems([
            "Junior (0-2 ans)",
            "Confirmé (2-5 ans)",
            "Confirmé-Senior (3-5 ans)",
            "Senior (5+ ans)",
            "Expert (10+ ans)",
        ])
        self.experience_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #E4E9EF;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 9pt;
            }
        """)
        form_layout.addWidget(self.experience_combo, 3, 1)

        # Fourchette salariale
        form_layout.addWidget(QLabel("FOURCHETTE SALARIALE"), 4, 0)
        salary_layout = QHBoxLayout()
        self.salary_min_input = QLineEdit()
        self.salary_min_input.setPlaceholderText("Min (ex: 55000)")
        self.salary_min_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E4E9EF;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 9pt;
            }
        """)
        salary_layout.addWidget(self.salary_min_input)

        salary_layout.addWidget(QLabel("—"))

        self.salary_max_input = QLineEdit()
        self.salary_max_input.setPlaceholderText("Max (ex: 68000)")
        self.salary_max_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E4E9EF;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 9pt;
            }
        """)
        salary_layout.addWidget(self.salary_max_input)

        salary_layout.addWidget(QLabel("€ / an"))
        form_layout.addLayout(salary_layout, 4, 1)

        # Localisation
        form_layout.addWidget(QLabel("LOCALISATION"), 5, 0)
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Ex: Paris (Siège) & Hybride")
        self.location_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E4E9EF;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 9pt;
            }
        """)
        form_layout.addWidget(self.location_input, 5, 1)

        # Description
        form_layout.addWidget(QLabel("DESCRIPTION"), 6, 0, Qt.AlignmentFlag.AlignTop)
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText(
            "Description du poste, missions principales, contexte..."
        )
        self.description_input.setFixedHeight(100)
        self.description_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #E4E9EF;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 9pt;
                background-color: #FFFFFF;
            }
        """)
        form_layout.addWidget(self.description_input, 6, 1)

        left_layout.addLayout(form_layout)
        left_layout.addStretch()

        content_layout.addWidget(left_section, 1)

        # ===== Section droite : Compétences =====
        right_section = QFrame()
        right_layout = QVBoxLayout(right_section)
        right_layout.setSpacing(16)

        right_title = QLabel("Compétences cibles & SmartMatch IA")
        right_title.setStyleSheet(
            "font-size: 11pt; font-weight: 700; color: #0F1E2E;"
        )
        right_layout.addWidget(right_title)

        # Compétences techniques
        tech_label = QLabel("COMPÉTENCES TECHNIQUES INCONTOURNABLES")
        tech_label.setStyleSheet(
            "font-size: 9pt; font-weight: 600; color: #5A6B7D;"
        )
        right_layout.addWidget(tech_label)

        # Input pour ajouter des compétences
        tech_input_layout = QHBoxLayout()
        self.tech_input = QLineEdit()
        self.tech_input.setPlaceholderText("Ajouter une compétence (ex: Python)")
        self.tech_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #E4E9EF;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 9pt;
            }
        """)
        tech_input_layout.addWidget(self.tech_input)

        btn_add_tech = QPushButton("+ Ajouter")
        btn_add_tech.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_add_tech.setStyleSheet("""
            QPushButton {
                background-color: #0D7A6A;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 9pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0A6456;
            }
        """)
        btn_add_tech.clicked.connect(self._add_hard_skill)
        tech_input_layout.addWidget(btn_add_tech)

        right_layout.addLayout(tech_input_layout)

        # Container pour les tags de compétences techniques
        self.tech_tags_container = QWidget()
        self.tech_tags_layout = QHBoxLayout(self.tech_tags_container)
        self.tech_tags_layout.setSpacing(8)
        right_layout.addWidget(self.tech_tags_container)

        # Soft skills
        soft_label = QLabel("SOFT SKILLS & CULTURE FIT PRÉCONISÉS")
        soft_label.setStyleSheet(
            "font-size: 9pt; font-weight: 600; color: #5A6B7D;"
        )
        right_layout.addWidget(soft_label)

        # Tags de soft skills prédéfinis
        soft_skills_options = [
            "Leadership d'équipe",
            "Rigueur d'architecture",
            "Communication bienveillante",
            "Esprit d'initiative",
            "Autonomie",
            "Esprit d'équipe",
            "Résolution de problèmes",
            "Adaptabilité",
        ]

        soft_tags_layout = QGridLayout()
        soft_tags_layout.setSpacing(8)

        # Repartition sur 2 colonnes max pour eviter le debordement
        cols = 2
        for i, skill in enumerate(soft_skills_options):
            btn = TagButton(skill, removable=False)
            btn.clicked.connect(lambda checked, s=skill: self._toggle_soft_skill(s, btn))
            row = i // cols
            col = i % cols
            soft_tags_layout.addWidget(btn, row, col)

        right_layout.addLayout(soft_tags_layout)
        right_layout.addStretch()

        content_layout.addWidget(right_section, 1)

        layout.addWidget(content)

        # ===== Footer =====
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background-color: #F4F6F9;
                border-top: 1px solid #E4E9EF;
            }
        """)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 16, 20, 16)

        footer_layout.addStretch()

        btn_draft = QPushButton("Enregistrer en brouillon")
        btn_draft.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_draft.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #5A6B7D;
                border: 1px solid #E4E9EF;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 10pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #E8F5F1;
                color: #0D7A6A;
                border-color: #0D7A6A;
            }
        """)
        btn_draft.clicked.connect(self._save_draft)
        footer_layout.addWidget(btn_draft)

        btn_publish = QPushButton("Publier l'offre")
        btn_publish.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_publish.setStyleSheet("""
            QPushButton {
                background-color: #0D7A6A;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 10pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #0A6456;
            }
        """)
        btn_publish.clicked.connect(self._publish_offer)
        footer_layout.addWidget(btn_publish)

        layout.addWidget(footer)

    def _add_hard_skill(self):
        """Ajoute une compétence technique aux tags."""
        skill = self.tech_input.text().strip()
        if skill and skill not in self.hard_skills:
            self.hard_skills.append(skill)
            self._refresh_tech_tags()
            self.tech_input.clear()

    def _remove_hard_skill(self, skill: str):
        """Supprime une compétence technique des tags."""
        if skill in self.hard_skills:
            self.hard_skills.remove(skill)
            self._refresh_tech_tags()

    def _refresh_tech_tags(self):
        """Rafraîchit l'affichage des tags de compétences techniques."""
        # Nettoyer le layout
        while self.tech_tags_layout.count():
            item = self.tech_tags_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Recréer les tags
        for skill in self.hard_skills:
            tag = TagButton(skill, removable=True)
            tag.clicked.connect(lambda _, s=skill: self._remove_hard_skill(s))
            self.tech_tags_layout.addWidget(tag)

    def _toggle_soft_skill(self, skill: str, button: TagButton):
        """Ajoute ou supprime un soft skill."""
        if button.isChecked():
            if skill not in self.soft_skills:
                self.soft_skills.append(skill)
        else:
            if skill in self.soft_skills:
                self.soft_skills.remove(skill)

    def _save_draft(self):
        """Sauvegarde l'offre en brouillon."""
        self._create_offer(status="brouillon")

    def _publish_offer(self):
        """Publie l'offre."""
        self._create_offer(status="active")

    def _create_offer(self, status: str):
        """Crée l'offre avec les données du formulaire."""
        # Validation basique
        if not self.title_input.text().strip():
            return

        # Récupérer les données
        offer_data = {
            "title": self.title_input.text().strip(),
            "department_id": self.dept_combo.currentData(),
            "contract_type": self.contract_combo.currentText(),
            "experience_level": self.experience_combo.currentText(),
            "salary_min": Decimal(self.salary_min_input.text() or "0"),
            "salary_max": Decimal(self.salary_max_input.text() or "0"),
            "location": self.location_input.text().strip(),
            "hard_skills": self.hard_skills.copy(),
            "soft_skills": self.soft_skills.copy(),
            "description": self.description_input.toPlainText().strip() or None,   # ⭐ AJOUT
            "status": status,
            "priority": "normal",
        }

        # Émettre le signal
        self.offer_created.emit(offer_data)
        self.accept()
