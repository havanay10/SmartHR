"""En-tete de page : breadcrumb + titre + sous-titre.

Utilisation :
    header = PageHeader(
        breadcrumb="SMARTRH  >  EMPLOYES",
        title="Repertoire des Collaborateurs",
        subtitle="Consultez et pilotez les fiches talents",
    )
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class PageHeader(QWidget):
    def __init__(
        self,
        title: str,
        subtitle: str = "",
        breadcrumb: str = "",
        parent=None,
    ):
        super().__init__(parent)
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(4)

        if breadcrumb:
            bc = QLabel(breadcrumb)
            bc.setObjectName("breadcrumb")
            v.addWidget(bc)

        t = QLabel(title)
        t.setObjectName("pageTitle")
        v.addWidget(t)

        if subtitle:
            s = QLabel(subtitle)
            s.setObjectName("pageSubtitle")
            s.setWordWrap(True)
            v.addWidget(s)