"""Test 1 : StatsService (KPIs dashboard)."""
import sys
from pathlib import Path

# Ajouter la racine du projet au PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.stats_service import StatsService


def titre(txt):
    print("\n" + "=" * 65)
    print(f"  {txt}")
    print("=" * 65)


def sous_titre(txt):
    print(f"\n[{txt}]")


# ============================================================
titre("TEST 1 : StatsService")
# ============================================================

svc = StatsService()

# ------------------------------------------------------------
sous_titre("1.1 KPIs Dashboard")
# ------------------------------------------------------------
kpis = svc.get_dashboard_kpis()
attendus = [
    "total_employees", "active_employees", "absences_this_month",
    "annual_turnover_rate", "turnover_label", "turnover_alert",
    "open_positions", "selected_candidates",
    "annual_payroll", "average_seniority_years",
]
for key in attendus:
    val = kpis.get(key, "MANQUANT")
    print(f"    {key:30} : {val}")

manquants = [k for k in attendus if k not in kpis]
if manquants:
    print(f"\n    [ERREUR] Cles manquantes : {manquants}")
else:
    print("\n    [OK] Toutes les cles sont presentes")

# ------------------------------------------------------------
sous_titre("1.2 Repartition par departement")
# ------------------------------------------------------------
depts = svc.get_headcount_by_department()
if not depts:
    print("    [ERREUR] Aucun departement trouve")
else:
    for d in depts:
        print(f"    {d['name']:35} : {d['count']} employes")
    print(f"\n    Total : {sum(d['count'] for d in depts)} employes")

# ------------------------------------------------------------
sous_titre("1.3 KPIs Employes (taux presence/absence)")
# ------------------------------------------------------------
emp_kpis = svc.get_employee_kpis()
for k, v in emp_kpis.items():
    print(f"    {k:30} : {v}")

# ------------------------------------------------------------
sous_titre("1.4 Liste des employes")
# ------------------------------------------------------------
emps = svc.get_all_employees()
print(f"    Total : {len(emps)} employes")
for e in emps:
    print(f"      {e['employee_code']:10} | {e['full_name']:22} | {e['job_title']:30} | {e['seniority_years']} ans")

# ------------------------------------------------------------
sous_titre("1.5 Departements")
# ------------------------------------------------------------
for d in svc.get_all_departments():
    print(f"    {d['code']:5} | {d['name']:35} | Style: {d['management_style'] or 'N/A'}")
# ------------------------------------------------------------
sous_titre("1.6 Donnees graphiques")
# ------------------------------------------------------------
alerts_monthly = svc.get_alerts_monthly()
print(f"    Alertes par mois : {len(alerts_monthly)} entree(s)")
for a in alerts_monthly:
    print(f"      {a['month']} : {a['critiques']} critiques, {a['preventives']} preventives")

absences_repart = svc.get_absence_repartition()
print(f"\n    Repartition des absences :")
if not absences_repart:
    print("      (aucune absence en base)")
else:
    for a in absences_repart:
        print(f"      {a['type']:20} : {a['count']}")

# ============================================================
titre("TEST 1 TERMINE")
# ============================================================