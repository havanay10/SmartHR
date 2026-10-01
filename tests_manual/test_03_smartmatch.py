"""Test 3 : SmartMatchService (CDC §5).

Verifie :
- Mode A : 1 vs 1 (duo)
- Mode B : 1 vs Tous (multi-scan departement)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.smartmatch_service import SmartMatchService


def titre(txt):
    print("\n" + "=" * 65)
    print(f"  {txt}")
    print("=" * 65)


def sous_titre(txt):
    print(f"\n[{txt}]")


# ============================================================
titre("TEST 3 : SmartMatchService (CDC §5)")
# ============================================================

svc = SmartMatchService()

# ------------------------------------------------------------
sous_titre("3.1 Liste des departements")
# ------------------------------------------------------------
depts = svc.get_departments()
if not depts:
    print("    [ERREUR] Aucun departement en base")
    sys.exit(1)

for d in depts:
    print(f"    {d['id'][:8]}... | {d['name']}")

# ------------------------------------------------------------
sous_titre("3.2 Employes par departement")
# ------------------------------------------------------------
for d in depts:
    emps = svc.get_employees_by_department(d["id"])
    print(f"\n    {d['name']} : {len(emps)} employe(s)")
    for e in emps:
        print(f"      - {e['name']:22} | {e['job_title']:30} | DISC: {e['disc']}")

# ------------------------------------------------------------
sous_titre("3.3 Choix du departement de test")
# ------------------------------------------------------------
rd = next((d for d in depts if "R&D" in d["name"]), depts[0])
rd_emps = svc.get_employees_by_department(rd["id"])
print(f"    Departement selectionne : {rd['name']}")
print(f"    Nombre d'employes       : {len(rd_emps)}")

if len(rd_emps) < 2:
    print("\n    [ERREUR] Il faut au moins 2 employes pour tester SmartMatch")
    sys.exit(1)

# ------------------------------------------------------------
sous_titre("3.4 MODE A : 1 vs 1 (duo)")
# ------------------------------------------------------------
pivot = rd_emps[0]
target = rd_emps[1]
print(f"    Pivot  : {pivot['name']} ({pivot['job_title']})")
print(f"    Cible  : {target['name']} ({target['job_title']})")

session = svc.run_duo(pivot["id"], target["id"])
print(f"\n    Session ID : {session['session_id'][:8]}...")
print(f"    Resultats :")
for r in session["results"]:
    print(f"      Cible              : {r['target_name']}")
    print(f"      Score global       : {r['global_score']}%")
    print(f"      Score skills       : {r['skills_score']}%")
    print(f"      Score communication: {r['communication_score']}%")
    print(f"      Diagnostic         : {r['diagnosis']}")

# ------------------------------------------------------------
sous_titre("3.5 MODE B : 1 vs Tous (multi-scan)")
# ------------------------------------------------------------
print(f"    Pivot : {rd_emps[0]['name']}")
print(f"    Comparaison avec les {len(rd_emps) - 1} autres employes du departement...")

session_multi = svc.run_multi_scan(rd_emps[0]["id"])
results = session_multi["results"]

print(f"\n    Session ID : {session_multi['session_id'][:8]}...")
print(f"    {len(results)} comparaisons effectuees :\n")
print(f"    {'#':<3} {'Nom':<25} {'Global':>8} {'Skills':>8} {'Comm.':>8}")
print(f"    {'-' * 3} {'-' * 25} {'-' * 8} {'-' * 8} {'-' * 8}")
for i, r in enumerate(results, 1):
    print(f"    {i:<3} {r['target_name']:<25} {r['global_score']:>7.1f}% {r['skills_score']:>7.1f}% {r['communication_score']:>7.1f}%")

# ------------------------------------------------------------
sous_titre("3.6 Top 3 des meilleurs binomes")
# ------------------------------------------------------------
if results:
    top3 = results[:3]
    print(f"    Classement des 3 meilleurs binomes avec {rd_emps[0]['name']} :\n")
    for i, r in enumerate(top3, 1):
        print(f"    #{i} : {r['target_name']}")
        print(f"         Score global : {r['global_score']}%")
        print(f"         Diagnostic   : {r['diagnosis']}")

# ------------------------------------------------------------
sous_titre("3.7 Verification en base")
# ------------------------------------------------------------
from sqlalchemy import select, func
from app.db.connection import get_session
from app.models.smartmatch import MatchSession, MatchResult

with get_session() as db:
    n_sessions = db.scalar(select(func.count()).select_from(MatchSession)) or 0
    n_results = db.scalar(select(func.count()).select_from(MatchResult)) or 0

print(f"    Sessions enregistrees : {n_sessions}")
print(f"    Resultats enregistres : {n_results}")

if n_sessions >= 2 and n_results >= 2:
    print("    [OK] Donnees bien persistees")
else:
    print("    [ATTENTION] Verifier la persistance")

# ============================================================
titre("TEST 3 TERMINE")
# ============================================================