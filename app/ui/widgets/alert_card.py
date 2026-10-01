"""Carte d'alerte (support icones images)."""
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
)
from app.ui.widgets.badge import Badge
from app.ui.icons import IconLabel, is_emoji


class AlertCard(QFrame):
    def __init__(
        self,
        employee: str,
        severity: str,
        tag: str,
        fact: str,
        observation: str,
        risk_score: str,
        kind: str = "danger",
        tag_icon: str = "🔔",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("kpiCard")
        self.setProperty("accentColor", "red" if kind == "danger" else "orange")

        v = QVBoxLayout(self)
        v.setContentsMargins(24, 18, 24, 18)
        v.setSpacing(12)

        # --- Header ---
        head = QHBoxLayout()

        name = QLabel(f"<b>{employee}</b>")
        name.setStyleSheet("font-size: 12pt; color: #0F1E2E;")
        head.addWidget(name)

        head.addWidget(Badge(
            severity,
            variant="priority" if kind == "danger" else "warning",
        ))

        head.addStretch()

        # Tag avec icone
        tag_widget = QWidget()
        tag_layout = QHBoxLayout(tag_widget)
        tag_layout.setContentsMargins(8, 4, 10, 4)
        tag_layout.setSpacing(4)
        tag_layout.addWidget(IconLabel(
            "status-info", fallback="🔔", size=14,
        ))

        tag_lbl = QLabel(tag)
        tag_lbl.setStyleSheet(
            "font-size: 8pt; font-weight: 700; color: #2E86DE; background: transparent;"
        )
        tag_layout.addWidget(tag_lbl)
        tag_widget.setStyleSheet(
            "background-color: #D6EAF8; border-radius: 10px;"
        )
        head.addWidget(tag_widget)

        # --- Corps ---
        body = QHBoxLayout()
        body.setSpacing(24)

        # Constat
        c1 = QVBoxLayout()
        c1.setSpacing(4)
        lbl1 = QLabel("CONSTAT FACTUEL")
        lbl1.setObjectName("kpiTitle")
        c1.addWidget(lbl1)
        v1 = QLabel(f"<b>{fact}</b>")
        v1.setStyleSheet("font-size: 11pt; color: #0F1E2E;")
        c1.addWidget(v1)
        d1 = QLabel(observation)
        d1.setStyleSheet("font-size: 9pt; color: #7A8B9C;")
        d1.setWordWrap(True)
        c1.addWidget(d1)
        body.addLayout(c1, 2)

        # Diagnostic
        c2 = QVBoxLayout()
        c2.setSpacing(4)
        lbl2 = QLabel("DIAGNOSTIC IA")
        lbl2.setObjectName("kpiTitle")
        c2.addWidget(lbl2)
        score_lbl = QLabel(f"Risque : <b>{risk_score}</b>")
        score_lbl.setStyleSheet(
            f"font-size: 11pt; color: {'#C0392B' if kind == 'danger' else '#B9770E'};"
        )
        c2.addWidget(score_lbl)
        body.addLayout(c2, 1)

        v.addLayout(body)

        # --- Actions ---
        actions = QHBoxLayout()
        actions.addStretch()

        b1 = QPushButton("Alerter manager")
        b1.setObjectName("secondaryButton")
        actions.addWidget(b1)

        b2 = QPushButton("Traiter l'anomalie")
        b2.setObjectName("primaryButton")
        actions.addWidget(b2)

        v.addLayout(actions)