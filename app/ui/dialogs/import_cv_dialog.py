"""Dialogue d'import de CV PDF avec extraction IA.

Deux modes :
- "candidate" : cree un candidat pour une offre
- "employee" : cree un employe (pre-remplit le formulaire)
"""
from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QWidget, QScrollArea, QFileDialog, QMessageBox,
    QComboBox, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal

from app.services.llm_service import LLMService
from app.services.recruitment_service import RecruitmentService


# =====================================================
# EXTRACTION DE TEXTE PDF
# =====================================================
def extract_pdf_text(pdf_path: str) -> str:
    """Extrait le texte d'un PDF avec pypdf."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        text_parts = []
        for page in reader.pages:
            try:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
            except Exception:
                continue
        return "\n".join(text_parts)
    except Exception as e:
        print(f"[ImportCV] Erreur extraction PDF: {e}")
        return ""


# =====================================================
# DIALOGUE
# =====================================================
class ImportCVDialog(QDialog):
    """Dialogue d'import de CV avec 2 modes."""

    cv_imported = pyqtSignal(dict)

    def __init__(self, mode: str = "candidate", parent=None):
        super().__init__(parent)
        self.mode = mode

        title_map = {
            "candidate": "Importer un CV — Candidat",
            "employee": "Importer un CV — Employé",
        }
        self.setWindowTitle(title_map.get(mode, "Importer un CV"))
        self.setFixedSize(780, 720)
        self.setStyleSheet("QDialog { background-color: #FFFFFF; }")

        self.pdf_path = None
        self.extracted_data = None

        self._setup_ui()

    # =====================================================
    # UI
    # =====================================================
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ============ HEADER ============
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2E86DE, stop:1 #0D7A6A
                );
            }
        """)
        h_layout = QVBoxLayout(header)
        h_layout.setContentsMargins(24, 20, 24, 20)
        h_layout.setSpacing(4)

        main_txt = ("Importer un CV candidat" if self.mode == "candidate"
                    else "Importer un CV employé")
        t = QLabel(main_txt)
        t.setStyleSheet("""
            font-size: 16pt; font-weight: 800; color: #FFFFFF;
            background: transparent; border: none;
        """)
        h_layout.addWidget(t)

        sub_txt = ("L'IA extrait les données pour créer un candidat"
                   if self.mode == "candidate"
                   else "L'IA pré-remplit le formulaire employé")
        sub = QLabel(sub_txt)
        sub.setStyleSheet("""
            font-size: 10pt; color: #E0E6ED;
            background: transparent; border: none;
        """)
        h_layout.addWidget(sub)

        layout.addWidget(header)

        # ============ BODY ============
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: #F4F6F9; border: none; }")

        inner = QWidget()
        inner.setStyleSheet("background-color: #F4F6F9;")
        scroll.setWidget(inner)

        body = QVBoxLayout(inner)
        body.setContentsMargins(24, 20, 24, 20)
        body.setSpacing(16)

        # ---- 1. Upload ----
        upload_box = QFrame()
        upload_box.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 2px dashed #2E86DE;
                border-radius: 12px;
            }
        """)
        ub = QVBoxLayout(upload_box)
        ub.setContentsMargins(20, 26, 20, 26)
        ub.setSpacing(10)

        upload_lbl = QLabel("Cliquez ci-dessous pour choisir un fichier PDF")
        upload_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        upload_lbl.setStyleSheet("""
            font-size: 11pt; color: #0F1E2E; font-weight: 600;
            background: transparent; border: none;
        """)
        ub.addWidget(upload_lbl)

        self.file_label = QLabel("Aucun fichier sélectionné")
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.file_label.setStyleSheet("""
            font-size: 9pt; color: #7A8B9C; font-style: italic;
            background: transparent; border: none;
        """)
        self.file_label.setWordWrap(True)
        ub.addWidget(self.file_label)

        btn_choose = QPushButton("Choisir un PDF")
        btn_choose.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_choose.setStyleSheet("""
            QPushButton {
                background-color: #2E86DE;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 10pt;
                font-weight: 700;
                min-width: 180px;
            }
            QPushButton:hover { background-color: #1E6FC0; }
        """)
        btn_choose.clicked.connect(self._choose_pdf)
        ub.addWidget(btn_choose, 0, Qt.AlignmentFlag.AlignCenter)

        body.addWidget(upload_box)

        # ---- 2. Offre (mode candidate) ----
        if self.mode == "candidate":
            offer_title = QLabel("Associer à une offre")
            offer_title.setStyleSheet("""
                font-size: 11pt; font-weight: 700; color: #0F1E2E; padding-top: 8px;
                background: transparent; border: none;
            """)
            body.addWidget(offer_title)

            offer_box = QFrame()
            offer_box.setStyleSheet("""
                QFrame {
                    background-color: #FFFFFF;
                    border-radius: 8px;
                    border: 1px solid #E4E9EF;
                }
            """)
            ob = QHBoxLayout(offer_box)
            ob.setContentsMargins(16, 12, 16, 12)
            ob.setSpacing(12)

            ob.addWidget(QLabel("Offre :"))
            self.offer_combo = QComboBox()
            self.offer_combo.setStyleSheet("""
                QComboBox {
                    border: 1px solid #E4E9EF;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 10pt;
                    background-color: #FFFFFF;
                    min-width: 300px;
                }
                QComboBox:focus { border: 1px solid #0D7A6A; }
            """)
            ob.addWidget(self.offer_combo, 1)

            body.addWidget(offer_box)
            self._load_offers()

        # ---- 3. Bouton analyse IA ----
        btn_analyze = QPushButton("Analyser avec l'IA")
        btn_analyze.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_analyze.setStyleSheet("""
            QPushButton {
                background-color: #0D7A6A;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                padding: 14px 24px;
                font-size: 11pt;
                font-weight: 700;
            }
            QPushButton:hover { background-color: #0A6456; }
            QPushButton:disabled { background-color: #94A3B8; }
        """)
        self.btn_analyze = btn_analyze
        btn_analyze.clicked.connect(self._analyze_pdf)
        body.addWidget(btn_analyze)

        # ---- 4. Resultat ----
        self.result_container = QVBoxLayout()
        self.result_container.setSpacing(12)
        body.addLayout(self.result_container)

        body.addStretch()
        layout.addWidget(scroll, 1)

        # ============ FOOTER ============
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background-color: #F4F6F9;
                border-top: 1px solid #E4E9EF;
            }
        """)
        f_layout = QHBoxLayout(footer)
        f_layout.setContentsMargins(20, 14, 20, 14)
        f_layout.addStretch()

        btn_cancel = QPushButton("Annuler")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #5A6B7D;
                border: 1px solid #E4E9EF;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 10pt;
            }
            QPushButton:hover { background-color: #F4F6F9; }
        """)
        btn_cancel.clicked.connect(self.reject)
        f_layout.addWidget(btn_cancel)

        action_txt = ("Créer le candidat" if self.mode == "candidate"
                      else "Continuer avec ces données")
        self.btn_save = QPushButton(action_txt)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setEnabled(False)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #0D7A6A;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 10pt;
                font-weight: 700;
            }
            QPushButton:hover { background-color: #0A6456; }
            QPushButton:disabled {
                background-color: #B8C4D0;
                color: #FFFFFF;
            }
        """)
        self.btn_save.clicked.connect(self._on_action)
        f_layout.addWidget(self.btn_save)

        layout.addWidget(footer)

    # =====================================================
    # CHARGEMENT
    # =====================================================
    def _load_offers(self):
        try:
            svc = RecruitmentService()
            offers = svc.get_all_job_offers()
            self.offer_combo.clear()
            self.offer_combo.addItem("— Sélectionner une offre —", None)
            for o in offers:
                if o.get("status") == "active":
                    self.offer_combo.addItem(o["title"], o["id"])
        except Exception as e:
            print(f"[ImportCV] Erreur chargement offres: {e}")

    # =====================================================
    # ACTIONS
    # =====================================================
    def _choose_pdf(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Choisir un CV",
            str(Path.home()),
            "Fichiers PDF (*.pdf)",
        )
        if path:
            self.pdf_path = path
            self.file_label.setText(f"{Path(path).name}")
            self.file_label.setStyleSheet("""
                font-size: 9pt; color: #0D7A6A; font-weight: 600;
                background: transparent; border: none;
            """)

    def _analyze_pdf(self):
        """Extrait le texte + analyse IA."""
        if not self.pdf_path:
            QMessageBox.warning(self, "Attention",
                                "Sélectionnez d'abord un fichier PDF.")
            return

        llm = LLMService()
        if not llm.is_available():
            QMessageBox.warning(
                self, "IA indisponible",
                "La clé GROQ_API_KEY n'est pas configurée dans .env"
            )
            return

        self.btn_analyze.setEnabled(False)
        self.btn_analyze.setText("Analyse en cours...")
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        QApplication.processEvents()

        try:
            pdf_text = extract_pdf_text(self.pdf_path)
            if not pdf_text or len(pdf_text.strip()) < 30:
                raise ValueError(
                    "Impossible d'extraire du texte du PDF. "
                    "Le PDF est peut-être scanné (image)."
                )

            print(f"[ImportCV] Texte extrait : {len(pdf_text)} caractères")

            data = llm.extract_cv_data(pdf_text, mode=self.mode)

            if not data:
                raise ValueError("L'IA n'a pas pu extraire les données du CV.")

            self.extracted_data = data
            self.extracted_data["cv_text"] = pdf_text
            self.extracted_data["cv_file_url"] = self.pdf_path

            self._show_extraction_result(data)
            self.btn_save.setEnabled(True)

        except Exception as e:
            print(f"[ImportCV] Erreur: {e}")
            QMessageBox.critical(
                self, "Erreur d'analyse",
                f"Impossible d'analyser le CV :\n{e}"
            )
        finally:
            QApplication.restoreOverrideCursor()
            self.btn_analyze.setEnabled(True)
            self.btn_analyze.setText("Analyser avec l'IA")

    # =====================================================
    # AFFICHAGE DU RESULTAT
    # =====================================================
    def _show_extraction_result(self, data: dict):
        """Affiche le resultat de l'extraction."""
        while self.result_container.count():
            item = self.result_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Titre section
        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        dot = QFrame()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet("""
            background-color: #0D7A6A;
            border-radius: 4px;
            border: none;
        """)
        title_row.addWidget(dot)

        title = QLabel("DONNÉES EXTRAITES PAR L'IA")
        title.setStyleSheet("""
            font-size: 10pt; font-weight: 800; color: #0D7A6A;
            letter-spacing: 0.8px;
            background: transparent; border: none;
        """)
        title_row.addWidget(title)
        title_row.addStretch()

        title_wrapper = QWidget()
        title_wrapper.setLayout(title_row)
        self.result_container.addWidget(title_wrapper)

        # Carte principale
        card = QFrame()
        card.setObjectName("resultCard")
        card.setStyleSheet("""
            QFrame#resultCard {
                background-color: #FFFFFF;
                border-radius: 12px;
                border: 1px solid #E4E9EF;
                border-left: 4px solid #0D7A6A;
            }
        """)

        cv = QVBoxLayout(card)
        cv.setContentsMargins(22, 20, 22, 20)
        cv.setSpacing(14)

        # === En-tête : Avatar + Nom + Poste ===
        header_row = QHBoxLayout()
        header_row.setSpacing(16)

        first_name = (data.get("first_name") or "").strip()
        last_name = (data.get("last_name") or "").strip()
        initials = f"{first_name[:1]}{last_name[:1]}".upper() or "?"

        avatar = QLabel(initials)
        avatar.setFixedSize(60, 60)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet("""
            background-color: #0D7A6A;
            color: #FFFFFF;
            border-radius: 30px;
            font-size: 20pt;
            font-weight: 800;
            border: none;
        """)
        header_row.addWidget(avatar, 0, Qt.AlignmentFlag.AlignTop)

        info_col = QVBoxLayout()
        info_col.setSpacing(4)

        full_name = f"{first_name} {last_name}".strip() or "—"
        name_lbl = QLabel(full_name)
        name_lbl.setStyleSheet("""
            font-size: 16pt; font-weight: 800; color: #0F1E2E;
            background: transparent; border: none;
        """)
        info_col.addWidget(name_lbl)

        if data.get("current_title"):
            poste_lbl = QLabel(data["current_title"])
            poste_lbl.setStyleSheet("""
                font-size: 10.5pt; color: #5A6B7D;
                background: transparent; border: none;
            """)
            info_col.addWidget(poste_lbl)

        years = data.get("years_experience", 0)
        if years:
            exp_row = QHBoxLayout()
            exp_row.setSpacing(6)

            exp_badge = QLabel(f"{years} ans d'expérience")
            exp_badge.setStyleSheet("""
                background-color: #E8F5F1;
                color: #0D7A6A;
                padding: 4px 12px;
                border-radius: 10px;
                font-size: 9pt;
                font-weight: 700;
                border: none;
            """)
            exp_row.addWidget(exp_badge)
            exp_row.addStretch()
            info_col.addLayout(exp_row)

        header_row.addLayout(info_col, 1)
        cv.addLayout(header_row)

        # === Contacts ===
        contacts = []
        if data.get("email"):
            contacts.append(("EMAIL", data["email"]))
        if data.get("phone"):
            contacts.append(("TÉL", data["phone"]))
        if data.get("city"):
            contacts.append(("VILLE", data["city"]))

        if contacts:
            contacts_row = QHBoxLayout()
            contacts_row.setSpacing(8)

            for label, value in contacts:
                chip = self._contact_chip(label, value)
                contacts_row.addWidget(chip)

            contacts_row.addStretch()
            cv.addLayout(contacts_row)

        # === Séparateur ===
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #EEF2F6; border: none;")
        cv.addWidget(sep)

        # === Compétences ===
        skills = data.get("skills", [])
        if skills:
            s_title = QLabel("COMPÉTENCES DÉTECTÉES")
            s_title.setStyleSheet("""
                font-size: 8pt; color: #7A8B9C; font-weight: 800;
                letter-spacing: 0.8px;
                background: transparent; border: none;
            """)
            cv.addWidget(s_title)

            skills_container = QWidget()
            skills_container.setStyleSheet("background: transparent;")
            skills_grid = QGridLayout(skills_container)
            skills_grid.setContentsMargins(0, 0, 0, 0)
            skills_grid.setSpacing(6)

            MAX_COLS = 4
            for idx, skill in enumerate(skills[:12]):
                chip = QLabel(skill)
                chip.setStyleSheet("""
                    background-color: #E8F5F1;
                    color: #0D7A6A;
                    padding: 6px 12px;
                    border-radius: 12px;
                    font-size: 9pt;
                    font-weight: 600;
                    border: none;
                """)
                chip.setAlignment(Qt.AlignmentFlag.AlignCenter)

                row_idx = idx // MAX_COLS
                col_idx = idx % MAX_COLS
                skills_grid.addWidget(chip, row_idx, col_idx)

            skills_grid.setColumnStretch(MAX_COLS, 1)
            cv.addWidget(skills_container)

        # === Résumé ===
        if data.get("summary"):
            sum_title = QLabel("RÉSUMÉ")
            sum_title.setStyleSheet("""
                font-size: 8pt; color: #7A8B9C; font-weight: 800;
                letter-spacing: 0.8px; padding-top: 6px;
                background: transparent; border: none;
            """)
            cv.addWidget(sum_title)

            sum_box = QFrame()
            sum_box.setStyleSheet("""
                QFrame {
                    background-color: #F8FAFC;
                    border-radius: 8px;
                    border: none;
                }
            """)
            sum_layout = QVBoxLayout(sum_box)
            sum_layout.setContentsMargins(14, 12, 14, 12)

            sum_txt = QLabel(data["summary"])
            sum_txt.setStyleSheet("""
                font-size: 9.5pt; color: #5A6B7D;
                background: transparent; border: none;
            """)
            sum_txt.setWordWrap(True)
            sum_layout.addWidget(sum_txt)

            cv.addWidget(sum_box)

        # === Points forts ===
        strengths = data.get("strengths", [])
        if strengths:
            str_title = QLabel("POINTS FORTS")
            str_title.setStyleSheet("""
                font-size: 8pt; color: #0D7A6A; font-weight: 800;
                letter-spacing: 0.8px; padding-top: 6px;
                background: transparent; border: none;
            """)
            cv.addWidget(str_title)

            for s in strengths[:5]:
                row = QHBoxLayout()
                row.setSpacing(10)

                bullet = QFrame()
                bullet.setFixedSize(6, 6)
                bullet.setStyleSheet("""
                    background-color: #0D7A6A;
                    border-radius: 3px;
                    border: none;
                """)
                row.addWidget(bullet, 0, Qt.AlignmentFlag.AlignTop)

                s_lbl = QLabel(s)
                s_lbl.setStyleSheet("""
                    font-size: 9.5pt; color: #0F1E2E;
                    background: transparent; border: none;
                """)
                s_lbl.setWordWrap(True)
                row.addWidget(s_lbl, 1)

                row_wrapper = QWidget()
                row_wrapper.setStyleSheet("background: transparent;")
                row_wrapper.setLayout(row)
                cv.addWidget(row_wrapper)

        self.result_container.addWidget(card)

    # =====================================================
    # HELPER : chip contact
    # =====================================================
    def _contact_chip(self, label: str, value: str) -> QFrame:
        """Petit chip de contact avec label + valeur."""
        chip = QFrame()
        chip.setStyleSheet("""
            QFrame {
                background-color: #F8FAFC;
                border-radius: 8px;
                border: 1px solid #EEF2F6;
            }
        """)
        h = QHBoxLayout(chip)
        h.setContentsMargins(10, 6, 12, 6)
        h.setSpacing(6)

        lbl = QLabel(label)
        lbl.setStyleSheet("""
            font-size: 7.5pt; color: #7A8B9C; font-weight: 700;
            letter-spacing: 0.3px; background: transparent; border: none;
        """)
        h.addWidget(lbl)

        val = QLabel(value)
        val.setStyleSheet("""
            font-size: 9pt; color: #0F1E2E; font-weight: 600;
            background: transparent; border: none;
        """)
        h.addWidget(val)

        return chip

    # =====================================================
    # ACTION FINALE
    # =====================================================
    def _on_action(self):
        if self.mode == "candidate":
            self._save_candidate()
        else:
            self._emit_employee_data()

    def _save_candidate(self):
        if not self.extracted_data:
            return

        offer_id = self.offer_combo.currentData()
        if not offer_id:
            QMessageBox.warning(self, "Attention",
                                "Sélectionnez une offre pour ce candidat.")
            return

        data = self.extracted_data
        first_name = data.get("first_name", "").strip()
        last_name = data.get("last_name", "").strip()

        if not first_name or not last_name:
            QMessageBox.warning(
                self, "Données incomplètes",
                "L'IA n'a pas pu extraire le nom et prénom."
            )
            return

        email = data.get("email", "").strip()
        if not email:
            base_email = f"{first_name.lower()}.{last_name.lower()}@gmail.com"
            email = base_email
        else:
            base_email = email

        try:
            from app.db.connection import get_session
            from app.models.recruitment import Candidate
            from sqlalchemy import select

            with get_session() as db:
                exists = db.scalar(
                    select(Candidate.id).where(Candidate.email == email)
                )
                if exists:
                    counter = 2
                    local_part, domain = email.rsplit("@", 1) if "@" in email else (email, "gmail.com")
                    base_local = local_part.rstrip("0123456789")
                    while True:
                        new_email = f"{base_local}{counter}@{domain}"
                        exists = db.scalar(
                            select(Candidate.id).where(Candidate.email == new_email)
                        )
                        if not exists:
                            email = new_email
                            break
                        counter += 1
                    print(f"[ImportCV] Email deja existant, utilise : {email}")
        except Exception as e:
            print(f"[ImportCV] Erreur verification email: {e}")

        try:
            from app.db.connection import get_session
            from app.models.recruitment import Candidate, Application
            from decimal import Decimal
            from uuid import uuid4

            cand_id = None

            with get_session() as db:
                cand = Candidate(
                    id=str(uuid4()),
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=data.get("phone") or None,
                    city=data.get("city") or None,
                    current_title=data.get("current_title") or None,
                    years_experience=data.get("years_experience") or 0,
                    skills=data.get("skills", []),
                    cv_text=data.get("cv_text", "")[:5000],
                    cv_file_url=data.get("cv_file_url"),
                    ai_summary=data.get("summary", ""),
                    disc_profile=data.get("disc_profile") or None,
                    match_score=Decimal("0"),
                )
                db.add(cand)
                db.flush()

                cand_id = str(cand.id)

                app = Application(
                    id=str(uuid4()),
                    candidate_id=cand_id,
                    job_offer_id=offer_id,
                    status="recu",
                    match_score=Decimal("0"),
                )
                db.add(app)

            QMessageBox.information(
                self, "Succès",
                f"Candidat {first_name} {last_name} créé avec succès."
            )

            self.cv_imported.emit({
                "candidate_id": cand_id,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "skills": data.get("skills", []),
            })

            self.accept()

        except Exception as e:
            print(f"[ImportCV] Erreur sauvegarde candidat: {e}")
            QMessageBox.critical(
                self, "Erreur",
                f"Impossible de créer le candidat :\n{e}"
            )

    def _emit_employee_data(self):
        if not self.extracted_data:
            return

        data = self.extracted_data

        if not data.get("first_name") or not data.get("last_name"):
            QMessageBox.warning(
                self, "Données incomplètes",
                "L'IA n'a pas pu extraire le nom et prénom."
            )
            return

        self.cv_imported.emit({
            "first_name": data.get("first_name", ""),
            "last_name": data.get("last_name", ""),
            "email": data.get("email", ""),
            "phone": data.get("phone", ""),
            "city": data.get("city", ""),
            "job_title": data.get("current_title", ""),
            "birth_date": data.get("birth_date", ""),
        })

        self.accept()