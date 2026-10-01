"""Test du service d'embeddings IA."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.embedding_service import EmbeddingService

svc = EmbeddingService()

print("=" * 65)
print("  TEST EMBEDDINGS IA")
print("=" * 65)

if not svc.is_available():
    print("\n  ❌ Modele non disponible")
    print("  Verifiez : pip install sentence-transformers")
    sys.exit(1)

print("\n  ✅ Modele charge")

# ============================================
# Test 1 : Similarite de phrases
# ============================================
print("\n" + "=" * 65)
print("  TEST 1 : Similarite de phrases")
print("=" * 65)

pairs = [
    ("Developpeur Python Django",
     "Ingenieur logiciel Python Django"),

    ("Developpeur Python",
     "React Developer"),

    ("Marketing Manager",
     "Chef de projet Marketing"),

    ("Python developer",
     "Developpeur Python"),

    ("Cuisinier",
     "Ingenieur logiciel"),
]

for text_a, text_b in pairs:
    score = svc.similarity(text_a, text_b)
    print(f"\n  A: {text_a}")
    print(f"  B: {text_b}")
    print(f"  → Similarite : {score}%")

# ============================================
# Test 2 : Similarite de profils
# ============================================
print("\n" + "=" * 65)
print("  TEST 2 : Similarite de profils employes")
print("=" * 65)

profil_a = {
    "job_title": "Developpeur Fullstack",
    "department": "R&D",
    "disc": "C",
}
profil_b = {
    "job_title": "Ingenieur DevOps",
    "department": "R&D",
    "disc": "S",
}
profil_c = {
    "job_title": "Chef de projet Marketing",
    "department": "Marketing",
    "disc": "I",
}

print(f"\n  A: {profil_a['job_title']}")
print(f"  B: {profil_b['job_title']}")
print(f"  → Similarite : {svc.profile_similarity(profil_a, profil_b)}%")

print(f"\n  A: {profil_a['job_title']}")
print(f"  C: {profil_c['job_title']}")
print(f"  → Similarite : {svc.profile_similarity(profil_a, profil_c)}%")

print("\n" + "=" * 65)
print("  TEST TERMINE")
print("=" * 65)