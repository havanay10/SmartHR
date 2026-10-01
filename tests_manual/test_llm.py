"""Test du service LLM (Groq)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.llm_service import LLMService

svc = LLMService()

print("=" * 65)
print("  TEST LLM (Groq API)")
print("=" * 65)

if not svc.is_available():
    print("\n  ❌ Service non disponible")
    print("  Verifiez GROQ_API_KEY dans .env")
    sys.exit(1)

print(f"\n  ✅ Service pret avec {svc.model}")

# ============================================
# Test : Analyse d'un CV
# ============================================
print("\n" + "=" * 65)
print("  TEST : Analyse CV")
print("=" * 65)

cv_text = """
Alexandre MARTIN
Developpeur Senior Fullstack - 7 ans d'experience

EXPERIENCE :
- 2020-2024 : Lead Developpeur chez TechCorp (Paris)
  * Developpement d'APIs REST avec FastAPI
  * Migration d'une application monolithique vers microservices
  * Encadrement d'une equipe de 4 developpeurs

- 2017-2020 : Developpeur Fullstack chez WebAgency
  * Applications React + Node.js
  * Base de donnees PostgreSQL

COMPETENCES :
Python, React, FastAPI, Docker, Kubernetes, PostgreSQL, AWS, Git, CI/CD

FORMATION :
Master Informatique - Universite Paris-Saclay (2017)
"""

result = svc.analyze_cv(
    cv_text=cv_text,
    offer_title="Developpeur Senior (Python / React)",
    offer_skills=["Python", "React", "FastAPI", "Docker"],
    offer_description="Poste de developpeur senior pour renforcer l'equipe R&D",
)

if result:
    print("\n  ✅ Analyse reussie :")
    print(f"\n  Score global        : {result['score']}%")
    print(f"  Annees d'experience : {result['years_experience']}")
    print(f"  Recommandation      : {result['recommendation']}")

    print("\n  Competences trouvees :")
    for s in result['matched_skills']:
        print(f"    ✅ {s}")

    if result['missing_skills']:
        print("\n  Competences manquantes :")
        for s in result['missing_skills']:
            print(f"    ❌ {s}")

    print("\n  Resume IA :")
    print(f"    {result['candidate_summary']}")

    print("\n  Points forts :")
    for s in result['strengths']:
        print(f"    + {s}")

    if result['weaknesses']:
        print("\n  Points faibles :")
        for w in result['weaknesses']:
            print(f"    - {w}")

    print("\n  Justification :")
    print(f"    {result['justification']}")

else:
    print("\n  ❌ Echec de l'analyse")