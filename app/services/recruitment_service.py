from datetime import datetime
from decimal import Decimal
from sqlalchemy import func, select, and_
from app.db.connection import get_session
from app.models.recruitment import JobOffer, Candidate, Application, Interview
from app.models.employee import Department


class RecruitmentService:
    """Service de gestion du recrutement (Page Recrutement IA).

    Fournit toutes les donnees necessaires pour la page recrutement
    en utilisant les modeles existants et les donnees du seed.
    """

    def get_recruitment_kpis(self) -> dict:
        """KPIs principaux pour la page recrutement.

        Retourne :
        - total_candidates : Total des candidats en base
        - preselected_count : Candidats pré-sélectionnés par l'IA
        - interviews_count : Entretiens planifiés
        """
        with get_session() as db:
            # Total des candidats
            total_candidates = db.scalar(
                select(func.count()).select_from(Candidate)
            ) or 0

            # Candidats pré-sélectionnés (status = "preselectionne")
            preselected_count = db.scalar(
                select(func.count()).select_from(Application)
                .where(Application.status == "preselectionne")
            ) or 0

            # Entretiens planifiés
            interviews_count = db.scalar(
                select(func.count()).select_from(Interview)
                .where(Interview.status == "planifié")
            ) or 0

            return {
                "total_candidates": total_candidates,
                "preselected_count": preselected_count,
                "interviews_count": interviews_count,
            }

    def get_all_job_offers(self) -> list[dict]:
        """Retourne toutes les offres d'emploi avec leurs statistiques.

        Pour chaque offre :
        - Informations de base (titre, département, statut, etc.)
        - Statistiques (nb candidats, nb pré-sélectionnés, score moyen)
        """
        with get_session() as db:
            offers = db.scalars(
                select(JobOffer).order_by(JobOffer.published_at.desc())
            ).all()

            result = []
            for offer in offers:
                # Récupérer le département
                dept = db.get(Department, offer.department_id) if offer.department_id else None

                # Statistiques pour cette offre
                stmt = select(Application).where(Application.job_offer_id == offer.id)
                applications = db.scalars(stmt).all()

                total_candidates = len(applications)
                preselected_count = sum(1 for app in applications if app.status == "preselectionne")

                # Score moyen des candidats
                scores = [float(app.match_score or 0) for app in applications if app.match_score]
                avg_score = round(sum(scores) / len(scores), 1) if scores else 0

                result.append({
                    "id": str(offer.id),
                    "reference": offer.reference,
                    "title": offer.title,
                    "department": dept.name if dept else "—",
                    "department_id": str(offer.department_id) if offer.department_id else None,
                    "contract_type": offer.contract_type,
                    "location": offer.location,
                    "salary_min": float(offer.salary_min) if offer.salary_min else 0,
                    "salary_max": float(offer.salary_max) if offer.salary_max else 0,
                    "experience_level": offer.experience_level,
                    "status": offer.status,
                    "priority": offer.priority,
                    "published_at": offer.published_at,
                    # Statistiques
                    "total_candidates": total_candidates,
                    "preselected_count": preselected_count,
                    "avg_match_score": avg_score,
                })

            return result

    def get_candidates_of_offer(self, offer_id: str) -> dict:
        """Retourne les candidats d'une offre spécifique.

        Separe en 2 listes :
        - received : Tous les candidats
        - preselected : Candidats pré-sélectionnés
        """
        with get_session() as db:
            stmt = (
                select(Application, Candidate)
                .join(Candidate, Candidate.id == Application.candidate_id)
                .where(Application.job_offer_id == offer_id)
                .order_by(Application.match_score.desc().nullslast())
            )

            received, preselected = [], []
            for app, cand in db.execute(stmt):
                item = {
                    "application_id": str(app.id),
                    "candidate_id": str(cand.id),
                    "name": f"{cand.first_name} {cand.last_name}",
                    "first_name": cand.first_name,
                    "last_name": cand.last_name,
                    "email": cand.email,
                    "current_title": cand.current_title,
                    "skills": cand.skills or [],
                    "years_experience": cand.years_experience,
                    "match_score": float(app.match_score or 0),
                    "status": app.status,
                    "ai_summary": cand.ai_summary,
                    "applied_at": app.applied_at,
                }
                received.append(item)
                if app.status == "preselectionne":
                    preselected.append(item)

            return {
                "received": received,
                "preselected": preselected,
            }

    def get_top_matches(self, limit: int = 10) -> list[dict]:
        """Retourne les meilleurs candidats toutes offres confondues.

        Trie par score de matching décroissant.
        """
        with get_session() as db:
            stmt = (
                select(Application, Candidate, JobOffer)
                .join(Candidate, Candidate.id == Application.candidate_id)
                .join(JobOffer, JobOffer.id == Application.job_offer_id)
                .where(Application.match_score.isnot(None))
                .order_by(Application.match_score.desc())
                .limit(limit)
            )

            result = []
            for app, cand, offer in db.execute(stmt):
                result.append({
                    "candidate_id": str(cand.id),
                    "name": f"{cand.first_name} {cand.last_name}",
                    "current_title": cand.current_title,
                    "skills": cand.skills or [],
                    "match_score": float(app.match_score or 0),
                    "ai_summary": cand.ai_summary,
                    "offer_title": offer.title,
                    "offer_id": str(offer.id),
                    "years_experience": cand.years_experience,
                    "email": cand.email,
                })

            return result

    def get_filtered_candidates(
        self,
        min_score: float = 0,
        max_score: float = 100,
        skills_filter: list[str] = None,
    ) -> list[dict]:
        """Retourne les candidats filtrés par critères.

        Args:
            min_score: Score minimum (0-100)
            max_score: Score maximum (0-100)
            skills_filter: Liste de compétences requises (optionnel)
        """
        with get_session() as db:
            stmt = (
                select(Application, Candidate, JobOffer)
                .join(Candidate, Candidate.id == Application.candidate_id)
                .join(JobOffer, JobOffer.id == Application.job_offer_id)
                .where(
                    and_(
                        Application.match_score >= min_score,
                        Application.match_score <= max_score,
                    )
                )
                .order_by(Application.match_score.desc())
            )

            result = []
            for app, cand, offer in db.execute(stmt):
                # Filtrer par compétences si demandé
                if skills_filter:
                    candidate_skills = set(s.lower() for s in (cand.skills or []))
                    required_skills = set(s.lower() for s in skills_filter)
                    if not required_skills.issubset(candidate_skills):
                        continue

                result.append({
                    "candidate_id": str(cand.id),
                    "name": f"{cand.first_name} {cand.last_name}",
                    "current_title": cand.current_title,
                    "skills": cand.skills or [],
                    "match_score": float(app.match_score or 0),
                    "ai_summary": cand.ai_summary,
                    "offer_title": offer.title,
                    "offer_id": str(offer.id),
                    "years_experience": cand.years_experience,
                })

            return result

    def create_job_offer(
        self,
        title: str,
        department_id: str,
        contract_type: str,
        location: str,
        salary_min: Decimal,
        salary_max: Decimal,
        experience_level: str,
        hard_skills: list[str],
        soft_skills: list[str],
        priority: str = "normal",
        status: str = "active",           # ⭐ AJOUT
        description: str = None,          # ⭐ AJOUT
    ) -> str:
        """Cree une nouvelle offre d'emploi.

        Args:
            title: Intitule du poste
            department_id: UUID du departement
            contract_type: CDI, CDD, Stage...
            location: Lieu
            salary_min: Salaire minimum
            salary_max: Salaire maximum
            experience_level: Junior, Confirme, Senior
            hard_skills: Competences techniques
            soft_skills: Soft skills
            priority: "normal" ou "prioritaire"
            status: "active" ou "brouillon"
            description: Description detaillee (optionnel)

        Returns:
            ID de l'offre creee
        """
        from uuid import uuid4

        with get_session() as db:
            # Reference UNIQUE : OFF-YYYY-MM-XXX
            year = datetime.now().year
            month = datetime.now().month

            count_this_month = db.scalar(
                select(func.count()).select_from(JobOffer)
                .where(
                    func.extract("year", JobOffer.published_at) == year,
                    func.extract("month", JobOffer.published_at) == month,
                )
            ) or 0
            seq = count_this_month + 1

            reference = f"OFF-{year}-{month:02d}-{seq:03d}"

            offer = JobOffer(
                id=str(uuid4()),
                reference=reference,
                title=title,
                department_id=department_id,
                contract_type=contract_type,
                location=location,
                salary_min=salary_min,
                salary_max=salary_max,
                experience_level=experience_level,
                hard_skills=hard_skills or [],
                soft_skills=soft_skills or [],
                description=description,
                status=status,
                priority=priority,
            )
            db.add(offer)
            db.flush()
            offer_id = str(offer.id)

        return offer_id

        # =====================================================
    
    # DETAIL D'UN CANDIDAT
    def get_candidate_details(self, candidate_id: str) -> dict | None:
        """Retourne toutes les infos d'un candidat.

        Combine :
        - Les infos du candidat (nom, email, skills...)
        - La candidature (score, status, offre)
        - L'offre associee (titre, departement)

        Retourne None si le candidat n'existe pas.
        """
        with get_session() as db:
            cand = db.get(Candidate, candidate_id)
            if not cand:
                return None

            # Cherche la candidature (la plus recente)
            app = db.scalar(
                select(Application)
                .where(Application.candidate_id == candidate_id)
                .order_by(Application.applied_at.desc())
            )

            # Cherche l'offre associee
            offer = None
            if app:
                offer = db.get(JobOffer, app.job_offer_id)

            # Departement de l'offre
            dept_name = "—"
            if offer and offer.department_id:
                dept = db.get(Department, offer.department_id)
                if dept:
                    dept_name = dept.name

            return {
                # --- Candidat ---
                "id": str(cand.id),
                "first_name": cand.first_name,
                "last_name": cand.last_name,
                "full_name": f"{cand.first_name} {cand.last_name}",
                "email": cand.email,
                "phone": cand.phone,
                "city": cand.city,
                "current_title": cand.current_title,
                "years_experience": cand.years_experience,
                "skills": cand.skills or [],
                "disc_profile": cand.disc_profile,
                "ai_summary": cand.ai_summary,

                # --- Candidature ---
                "match_score": float(app.match_score) if app and app.match_score else 0.0,
                "application_status": app.status if app else "—",
                "applied_at": app.applied_at if app else None,
                "application_id": str(app.id) if app else None,

                # --- Offre associee ---
                "offer_id": str(offer.id) if offer else None,
                "offer_title": offer.title if offer else "—",
                "offer_department": dept_name,
                "offer_contract": offer.contract_type if offer else "—",
                "offer_location": offer.location if offer else "—",
            }
    
    def update_application_status(self, application_id: str, new_status: str) -> bool:
        """Met à jour le statut d'une candidature.

        Retourne True si succès, False sinon.
        """
        with get_session() as db:
            app = db.get(Application, application_id)
            if not app:
                return False
            app.status = new_status
            return True
