"""Test 5 : CVService (CDC §4).

Verifie :
- Extraction de competences depuis un texte de CV
- Calcul du score de matching (formule CDC)
- Analyse complete d'une candidature
- Liste des candidats d'une offre (recus / preselectionnes)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.cv_service import CVService
from app.db.connection import get_session
from app.models.recruitment import JobOffer, Application, Candidate
from config import settings


def titre(txt):
    print("\n" + "=" * 65)
    print(f"  {txt}")
    print("=" * 65)


def sous_titre(txt):
    print(f"\n[{txt}]")


# ============================================================
titre("TEST 5 : CVService (CDC §4)")
# ============================================================

svc = CVService()

# ------------------------------------------------------------
sous_titre("5.1 Configuration")
# ------------------------------------------------------------
print(f"    MATCH_SCORE_THRESHOLD : {settings.MATCH_SCORE_THRESHOLD}%")
print(f"    Competences reconnues : {len(svc.SKILLS_POOL)} mots-cles")

# ------------------------------------------------------------
sous_titre("5.2 Test parsing d'un texte de CV")
# ------------------------------------------------------------
sample_cv = """
Alexandre MARTIN
Developpeur Senior - 7 ans d'experience
Competences : Python, React, FastAPI, Docker, PostgreSQL, AWS, Kubernetes
Formation : Master Informatique
"""
print("    --- Texte du CV ---")
for line in sample_cv.strip().split("\n"):
    print(f"    | {line}")
print()

parsed = svc.parse_cv_text(sample_cv)
print(f"    --- Resultat du parsing ---")
print(f"    Competences extraites : {parsed['skills']}")
print(f"    Annees d'experience   : {parsed['years_experience']}")
print(f"    Resume                : {parsed['summary']}")

# ------------------------------------------------------------
sous_titre("5.3 Test calcul du score de matching")
# ------------------------------------------------------------
offer_skills = ["Python", "React", "FastAPI", "Docker"]

# Cas 1 : match parfait
cand_full = ["Python", "React", "FastAPI", "Docker"]
score_full = svc.compute_match_score(cand_full, offer_skills)
print(f"    Cas 1 - Match parfait :")
print(f"      Candidat : {cand_full}")
print(f"      Offre    : {offer_skills}")
print(f"      Score    : {score_full}%  (attendu : 100.0%)")

# Cas 2 : match partiel
cand_partial = ["Python", "Docker"]
score_partial = svc.compute_match_score(cand_partial, offer_skills)
print(f"\n    Cas 2 - Match partiel :")
print(f"      Candidat : {cand_partial}")
print(f"      Score    : {score_partial}%  (attendu : 50.0%)")

# Cas 3 : match nul
cand_none = ["Java", "C++"]
score_none = svc.compute_match_score(cand_none, offer_skills)
print(f"\n    Cas 3 - Aucun match :")
print(f"      Candidat : {cand_none}")
print(f"      Score    : {score_none}%  (attendu : 0.0%)")

# Cas 4 : casse ignoree
cand_case = ["python", "REACT"]
score_case = svc.compute_match_score(cand_case, offer_skills)
print(f"\n    Cas 4 - Casse ignoree :")
print(f"      Candidat : {cand_case}")
print(f"      Score    : {score_case}%  (attendu : 50.0%)")

# ------------------------------------------------------------
sous_titre("5.4 Liste des offres et candidatures en base")
# ------------------------------------------------------------
with get_session() as db:
    offers = db.query(JobOffer).all()
    print(f"    {len(offers)} offre(s) en base :")
    for o in offers:
        apps_count = db.query(Application).filter(
            Application.job_offer_id == o.id
        ).count()
        print(f"      - {o.title}")
        print(f"        Skills requis : {o.hard_skills}")
        print(f"        Candidatures  : {apps_count}")

    if not offers:
        print("    [ERREUR] Aucune offre en base")
        sys.exit(1)

# ------------------------------------------------------------
sous_titre("5.5 Analyse complete d'une candidature")
# ------------------------------------------------------------
with get_session() as db:
    offer = db.query(JobOffer).first()
    print(f"    Offre cible : {offer.title}")
    print(f"    Skills requis : {offer.hard_skills}\n")

    app = db.query(Application).filter(
        Application.job_offer_id == offer.id
    ).first()

    if not app:
        print("    [ERREUR] Aucune candidature pour cette offre")
        sys.exit(1)

    # Injecter un CV texte pour tester
    cand = db.query(Candidate).filter(Candidate.id == app.candidate_id).first()
    if not cand.cv_text:
        cand.cv_text = (
            "Developpeur Senior Python React Docker AWS "
            "5 ans d'experience en developpement web"
        )
        db.commit()

    print(f"    Candidat : {cand.first_name} {cand.last_name}")
    print(f"    CV texte : {cand.cv_text[:60]}...\n")

    result = svc.analyze_candidate_for_offer(str(app.id))
    print(f"    --- Resultat de l'analyse ---")
    print(f"    Score match      : {result['match_score']}%")
    print(f"    Skills trouves   : {result['skills_found']}")
    print(f"    Resume IA        : {result['ai_summary']}")
    print(f"    Preselectionne   : {result['auto_preselected']}")

# ------------------------------------------------------------
sous_titre("5.6 Liste des candidats d'une offre")
# ------------------------------------------------------------
with get_session() as db:
    offer = db.query(JobOffer).first()
    result = svc.get_candidates_of_offer(str(offer.id))

    print(f"    Offre : {offer.title}\n")
    print(f"    Reçus / A trier : {len(result['received'])}")
    for c in result["received"]:
        print(f"      - {c['name']:25} | Score: {c['match_score']:>6}% | {c['status']}")

    print(f"\n    Preselectionnes par IA : {len(result['preselected'])}")
    for c in result["preselected"]:
        print(f"      - {c['name']:25} | Score: {c['match_score']:>6}%")

# ------------------------------------------------------------
sous_titre("5.7 Verification du seuil de preselection")
# ------------------------------------------------------------
with get_session() as db:
    preselected_count = db.query(Application).filter(
        Application.status == "preselectionne"
    ).count()
    received_count = db.query(Application).filter(
        Application.status == "recu"
    ).count()

print(f"    Seuil de preselection : {settings.MATCH_SCORE_THRESHOLD}%")
print(f"    Candidats preselectionnes : {preselected_count}")
print(f"    Candidats en attente      : {received_count}")

# ============================================================
titre("TEST 5 TERMINE")
# ============================================================