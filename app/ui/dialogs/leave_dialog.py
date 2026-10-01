"""Dialogue pour creer une nouvelle demande de conge."""
from datetime import date
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QComboBox, QDateEdit, QLineEdit, QPushButton,
    QMessageBox
)
from PyQt6.QtCore import Qt, QDate


class LeaveDialog(QDialog):
    """Boite de dialogue pour poser une demande de conge."""

    def __init__(self, employee_name: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Poser une demande de conge")
        self.setMinimumWidth(420)
        self.setStyleSheet("""
            QDialog { background-color: #F4F6F9; }
            QLabel { background: transparent; border: none; }
        """)

        # Valeurs retournees
        self.result_data = None

        # Layout principal
        v = QVBoxLayout(self)
        v.setContentsMargins(24, 20, 24, 20)
        v.setSpacing(16)

        # --- Titre ---
        title = QLabel(f"Demande de conge pour <b>{employee_name}</b>")
        title.setStyleSheet(
            "font-size: 13pt; font-weight: 700; color: #0F1E2E; "
            "background: transparent; border: none;"
        )
        v.addWidget(title)

        # --- Formulaire ---
        form = QFormLayout()
        form.setSpacing(12)

        # Type de conge
        self.combo_type = QComboBox()
        self.combo_type.addItems([
            "Conge paye",
            "RTT",
            "Maladie",
            "Sans solde",
        ])
        form.addRow("Type :", self.combo_type)

        # Date de debut
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDate(QDate.currentDate())
        self.date_start.setMinimumDate(QDate.currentDate())
        form.addRow("Date de debut :", self.date_start)

        # Date de fin
        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDate(QDate.currentDate())
        self.date_end.setMinimumDate(QDate.currentDate())
        form.addRow("Date de fin :", self.date_end)

        # Motif
        self.line_reason = QLineEdit()
        self.line_reason.setPlaceholderText("Motif (optionnel)")
        form.addRow("Motif :", self.line_reason)

        v.addLayout(form)

        # --- Durée calculée ---
        self.lbl_duree = QLabel("Duree : 1 jour")
        self.lbl_duree.setStyleSheet(
            "font-size: 10pt; color: #0D7A6A; font-weight: 700; "
            "background: #E8F5F1; border-radius: 6px; padding: 8px;"
        )
        self.lbl_duree.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(self.lbl_duree)

        # Connexion pour mise a jour de la duree
        self.date_start.dateChanged.connect(self._update_duration)
        self.date_end.dateChanged.connect(self._update_duration)

        # --- Boutons ---
        actions = QHBoxLayout()
        actions.addStretch()

        btn_cancel = QPushButton("Annuler")
        btn_cancel.setObjectName("secondaryButton")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        actions.addWidget(btn_cancel)

        btn_ok = QPushButton("Confirmer la demande")
        btn_ok.setObjectName("primaryButton")
        btn_ok.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ok.clicked.connect(self._on_submit)
        actions.addWidget(btn_ok)

        v.addLayout(actions)

    def _update_duration(self):
        """Met a jour l'affichage de la duree."""
        start = self.date_start.date().toPyDate()
        end = self.date_end.date().toPyDate()
        if end < start:
            self.lbl_duree.setText("Date de fin avant le debut")
            self.lbl_duree.setStyleSheet(
                "font-size: 10pt; color: #C0392B; font-weight: 700; "
                "background: #FADBD8; border-radius: 6px; padding: 8px;"
            )
            return
        duration = (end - start).days + 1
        self.lbl_duree.setText(f"Duree : {duration} jour(s)")
        self.lbl_duree.setStyleSheet(
            "font-size: 10pt; color: #0D7A6A; font-weight: 700; "
            "background: #E8F5F1; border-radius: 6px; padding: 8px;"
        )

    def _on_submit(self):
        """Valide et prepare les donnees de retour."""
        start = self.date_start.date().toPyDate()
        end = self.date_end.date().toPyDate()

        if end < start:
            QMessageBox.warning(
                self, "Attention",
                "La date de fin doit etre apres la date de debut."
            )
            return

        self.result_data = {
            "leave_type": self.combo_type.currentText(),
            "start_date": start,
            "end_date": end,
            "reason": self.line_reason.text().strip(),
        }
        self.accept()