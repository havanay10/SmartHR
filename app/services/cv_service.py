import re
from decimal import Decimal
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService
from app.db.connection import get_session
from app.models.recruitment import Candidate, JobOffer, Application
from config import settings



class CVService:
    """Analyse CV simple (CDC §4).

    Extraction de competences par mots-cles.
    A remplacer plus tard par un vrai modele IA (embeddings + LLM).
    """

    SKILLS_POOL = [
        "python", "react", "node", "django", "fastapi", "postgresql",
        "docker", "kubernetes", "aws", "typescript", "java", "go",
        "javascript", "vue", "angular", "redis", "mongodb", "git",
        "ci/cd", "terraform", "graphql", "flask", "pandas", "numpy",
    ]

    def parse_cv_text(self, text: str) -> dict:
        """Extrait les competences et annees d'experience d'un texte de CV."""
        if not text:
            return {"skills": [], "years_experience": None, "summary": "CV vide"}

        text_lower = text.lower()
        found = [s.capitalize() for s in self.SKILLS_POOL if s in text_lower]

        years_match = re.search(r"(\d+)\s*(ans|years|annees)", text_lower)
        years = int(years_match.group(1)) if years_match else None

        return {
            "skills": found,
            "years_experience": years,
            "summary": (
                f"Profil avec {years or '?'} ans d'experience, "
                f"competences : {', '.join(found[:5]) or 'N/A'}"
            ),
        }

    def compute_match_score(
        self, candidate_skills: list[str], offer_skills: list[str]
    ) -> Decimal:
        """Formule CDC §4 : (correspondances / total requis) x 100."""
        if not offer_skills:
            return Decimal("0")
        c = set(s.lower() for s in (candidate_skills or []))
        o = set(s.lower() for s in offer_skills)
        matched = len(c & o)
        return Decimal(str(round(100 * matched / len(o), 2)))

    def analyze_candidate_for_offer(self, application_id: str) -> dict:
        """Analyse complete d'un CV par rapport a une offre."""
        with get_session() as db:
            app = db.get(Application, application_id)
            if not app:
                raise ValueError("Candidature introuvable")

            cand = db.get(Candidate, app.candidate_id)
            offer = db.get(JobOffer, app.job_offer_id)

            parsed = self.parse_cv_text(cand.cv_text or "")
            score = self.compute_match_score(parsed["skills"], offer.hard_skills or [])

            cand.skills = parsed["skills"]
            cand.years_experience = parsed["years_experience"]
            cand.ai_summary = parsed["summary"]
            cand.match_score = score
            app.match_score = score

            # Auto-preselection (CDC)
            if score >= settings.MATCH_SCORE_THRESHOLD:
                app.status = "preselectionne"

            return {
                "application_id": application_id,
                "match_score": float(score),
                "skills_found": parsed["skills"],
                "ai_summary": parsed["summary"],
                "auto_preselected": score >= settings.MATCH_SCORE_THRESHOLD,
            }

    def analyze_candidate_with_llm(self, application_id: str) -> dict:
        """Analyse un CV via le LLM (Groq).

        Combine :
        - Parsing classique (fallback)
        - Analyse IA via LLM (si disponible)

        Returns:
            {
                "application_id": str,
                "match_score": float,
                "ai_summary": str,
                "strengths": [...],
                "weaknesses": [...],
                "recommendation": str,
                "auto_preselected": bool,
                "llm_used": bool,
            }
        """
        from app.db.connection import get_session
        from app.models.recruitment import Application, Candidate, JobOffer

        with get_session() as db:
            app = db.get(Application, application_id)
            if not app:
                raise ValueError("Candidature introuvable")

            cand = db.get(Candidate, app.candidate_id)
            offer = db.get(JobOffer, app.job_offer_id)

            if not cand or not offer:
                raise ValueError("Candidat ou offre introuvable")

            # ============ 1. Parsing classique (fallback) ============
            parsed = self.parse_cv_text(cand.cv_text or "")
            score_kw = self.compute_match_score(
                parsed["skills"], offer.hard_skills or []
            )

            # ============ 2. Analyse LLM (si disponible) ============
            llm_result = None
            llm_svc = LLMService()

            if llm_svc.is_available() and cand.cv_text:
                print(f"[CVService] Analyse LLM du CV de {cand.full_name}...")
                llm_result = llm_svc.analyze_cv(
                    cv_text=cand.cv_text,
                    offer_title=offer.title,
                    offer_skills=offer.hard_skills or [],
                    offer_description=offer.description or "",
                )

            # ============ 3. Choix du resultat ============
            if llm_result:
                score = float(llm_result["score"])
                summary = llm_result.get("candidate_summary", "")
                strengths = llm_result.get("strengths", [])
                weaknesses = llm_result.get("weaknesses", [])
                recommendation = llm_result.get("recommendation", "")
                years_exp = llm_result.get("years_experience") or parsed.get("years_experience")
                used_llm = True
            else:
                # Fallback : utilisation du parsing classique
                score = float(score_kw)
                summary = parsed["summary"]
                strengths = [f"Competences trouvees : {', '.join(parsed['skills'][:5])}"]
                weaknesses = []
                recommendation = "Analyse classique (IA indisponible)"
                years_exp = parsed.get("years_experience")
                used_llm = False

            # ============ 4. Mise a jour en base ============
            cand.skills = parsed["skills"] or (cand.skills or [])
            cand.years_experience = years_exp
            cand.ai_summary = summary
            cand.match_score = Decimal(str(score))
            app.match_score = Decimal(str(score))

            # Auto-preselection
            if score >= 80:
                app.status = "preselectionne"

            return {
                "application_id": application_id,
                "candidate_name": cand.full_name,
                "match_score": score,
                "ai_summary": summary,
                "strengths": strengths,
                "weaknesses": weaknesses,
                "recommendation": recommendation,
                "auto_preselected": score >= 80,
                "llm_used": used_llm,
                "score_keywords": float(score_kw),
            }
    def get_candidates_of_offer(self, offer_id: str) -> dict:
        """Retourne les candidats d'une offre, separes en 2 listes (CDC §4)."""
        with get_session() as db:
            from sqlalchemy import select
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
                    "title": cand.current_title,
                    "match_score": float(app.match_score or 0),
                    "status": app.status,
                    "ai_summary": cand.ai_summary,
                }
                received.append(item)
                if app.status == "preselectionne":
                    preselected.append(item)
            return {"received": received, "preselected": preselected}
        
    def compute_semantic_match(
        self,
        candidate_skills: list[str],
        candidate_years: int | None,
        offer_skills: list[str],
        offer_title: str = "",
        offer_description: str = "",
    ) -> dict:
        """Score de matching SEMANTIQUE avec embeddings IA.

        Combine :
        - 60% : matching classique (mots-cles)
        - 40% : similarite semantique (embeddings)

        Returns:
            {
                "score_final": float,
                "score_keywords": float,
                "score_semantic": float,
                "sentence_candidate": str,
                "sentence_offer": str,
            }
        """
        # ============ 1. Score par mots-cles ============
        score_kw = float(self.compute_match_score(candidate_skills, offer_skills))

        # ============ 2. Score semantique ============
        # Construit les phrases a comparer
        cand_text = ", ".join(candidate_skills or [])
        if candidate_years:
            cand_text += f" ({candidate_years} ans d'experience)"

        offer_text = offer_title + " " + " ".join(offer_skills or [])
        if offer_description:
            offer_text += " " + offer_description[:500]

        # Utilise EmbeddingService
        try:
            svc = EmbeddingService()
            if svc.is_available():
                score_sem = svc.similarity(cand_text, offer_text)
            else:
                score_sem = score_kw  # fallback
        except Exception as e:
            print(f"[CVService] Erreur semantique: {e}")
            score_sem = score_kw

        # ============ 3. Score final ============
        final = round(0.6 * score_kw + 0.4 * score_sem, 2)

        return {
            "score_final": final,
            "score_keywords": score_kw,
            "score_semantic": score_sem,
            "sentence_candidate": cand_text,
            "sentence_offer": offer_text[:200],
        }    