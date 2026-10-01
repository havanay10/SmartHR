"""Test 6 : Integration globale de tous les services.

Simule un scenario complet d'utilisation de SmartRH :
1. Chargement du dashboard
2. Detection des alertes CDC
3. Analyse SmartMatch
4. Generation de rapport
5. Analyse d'un CV
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.stats_service import StatsService
from app.services.alert_service import AlertService
from app.services.smartmatch_service import SmartMatchService
from app.services.report_service import ReportService
from app.services.cv_service import CVService
from config import settings


def titre(txt):
    print("\n" + "=" * 65)
    print(f"  {txt}")
    print("=" * 65)


def sous_titre(txt):
    print(f"\n[{txt}]")


# ============================================================
titre("TEST 6 : INTEGRATION GLOBALE")
# ============================================================

# ------------------------------------------------------------
sous_titre("6.1 Initialisation des services")
# ------------------------------------------------------------
stats_svc = StatsService()
alert_svc = AlertService()
sm_svc = SmartMatchService()
report_svc = ReportService()
cv_svc = CVService()

print("    [OK] StatsService")
print("    [OK] AlertService")
print("    [OK] SmartMatchService")
print("    [OK] ReportService")
print("    [OK] CVService")

# ------------------------------------------------------------
sous_titre("6.2 Etape 1 : Chargement du dashboard (Module 1)")
# ------------------------------------------------------------
kpis = stats_svc.get_dashboard_kpis()
print(f"    Effectif total       : {kpis['total_employees']}")
print(f"    Employes actifs      : {kpis['active_employees']}")
print(f"    Absences ce mois     : {kpis['absences_this_month']}")
print(f"    Taux turnover        : {kpis['annual_turnover_rate']}%")
print(f"    Statut turnover      : {kpis['turnover_label']}")
print(f"    Postes ouverts       : {kpis['open_positions']}")
print(f"    Candidats choisis    : {kpis['selected_candidates']}")
print(f"    Masse salariale      : {kpis['annual_payroll']:,.0f} EUR")
print(f"    Anciennete moyenne   : {kpis['average_seniority_years']} ans")

# ------------------------------------------------------------
sous_titre("6.3 Etape 2 : Detection des alertes (Module 3)")
# ------------------------------------------------------------
print("    Execution des regles CDC...")
alert_svc.run_all_rules()
kpis_alert = alert_svc.get_kpis()
print(f"    Alertes actives      : {kpis_alert['active_alerts']}")
print(f"    Risques detectes     : {kpis_alert['detected_risks']}")
print(f"    Alertes resolues     : {kpis_alert['resolved_alerts']}")

alerts = alert_svc.get_active_alerts()
if alerts:
    print(f"\n    Detail des {len(alerts)} alerte(s) :")
    for a in alerts[:3]:  # top 3
        print(f"      [{a['severity'].upper():9}] {a['employee_name']:22} | Risque: {a['risk_score']}%")

# ------------------------------------------------------------
sous_titre("6.4 Etape 3 : SmartMatch IA (Module 5)")
# ------------------------------------------------------------
depts = sm_svc.get_departments()
rd = next((d for d in depts if "R&D" in d["name"]), depts[0])
emps = sm_svc.get_employees_by_department(rd["id"])
print(f"    Departement : {rd['name']} ({len(emps)} employes)")

if len(emps) >= 2:
    # Mode A : duo
    duo = sm_svc.run_duo(emps[0]["id"], emps[1]["id"])
    top = duo["results"][0]
    print(f"\n    [Mode A] Duo {emps[0]['name']} + {emps[1]['name']}")
    print(f"      Score global : {top['global_score']}%")
    print(f"      Diagnostic   : {top['diagnosis']}")

    # Mode B : multi-scan
    multi = sm_svc.run_multi_scan(emps[0]["id"])
    print(f"\n    [Mode B] Multi-scan depuis {emps[0]['name']}")
    print(f"      {len(multi['results'])} comparaisons :")
    for r in multi["results"][:3]:
        print(f"        {r['target_name']:22} : {r['global_score']}%")

# ------------------------------------------------------------
sous_titre("6.5 Etape 4 : Generation de rapport (Module 6)")
# ------------------------------------------------------------
report_path = report_svc.generate("turnover_absenteeism")
p = Path(report_path)
print(f"    [OK] Rapport genere : {p.name}")
print(f"         Chemin        : {p.resolve()}")
print(f"         Taille        : {p.stat().st_size // 1024} Ko")

latest = report_svc.get_latest(3)
print(f"\n    Derniers rapports :")
for r in latest:
    dt = r["created_at"].strftime("%d/%m/%Y %H:%M")
    print(f"      {dt} | {r['title'][:45]}")

# ------------------------------------------------------------
sous_titre("6.6 Etape 5 : Analyse CV (Module 4)")
# ------------------------------------------------------------
sample_cv = "Developpeur Python React Docker AWS 6 ans d'experience"
parsed = cv_svc.parse_cv_text(sample_cv)
print(f"    CV analyse : {sample_cv}")
print(f"    Skills     : {parsed['skills']}")
print(f"    Experience : {parsed['years_experience']} ans")

offer_skills = ["Python", "React", "FastAPI", "Docker"]
score = cv_svc.compute_match_score(parsed["skills"], offer_skills)
print(f"\n    Offre      : {offer_skills}")
print(f"    Score match: {score}%")

# ------------------------------------------------------------
sous_titre("6.7 Verification croisee")
# ------------------------------------------------------------
from sqlalchemy import select, func
from app.db.connection import get_session
from app.models.employee import Employee
from app.models.alert import Alert
from app.models.smartmatch import MatchSession, MatchResult
from app.models.report import Report

with get_session() as db:
    n_emp = db.scalar(select(func.count()).select_from(Employee)) or 0
    n_alert = db.scalar(select(func.count()).select_from(Alert)) or 0
    n_session = db.scalar(select(func.count()).select_from(MatchSession)) or 0
    n_result = db.scalar(select(func.count()).select_from(MatchResult)) or 0
    n_report = db.scalar(select(func.count()).select_from(Report)) or 0

print(f"    Employes         : {n_emp}")
print(f"    Alertes          : {n_alert}")
print(f"    Sessions Match   : {n_session}")
print(f"    Resultats Match  : {n_result}")
print(f"    Rapports         : {n_report}")

# ============================================================
titre("BILAN FINAL")
# ============================================================
print("  [OK] StatsService       - KPIs charges")
print("  [OK] AlertService       - Regles CDC executees")
print(f"  [OK] SmartMatchService  - {len(depts)} depts, {len(emps)} employes R&D")
print("  [OK] ReportService      - PDF genere")
print("  [OK] CVService          - Parsing + scoring OK")
print()
print(f"  Tous les services communiquent correctement.")
print(f"  La base contient : {n_emp} employes, {n_alert} alertes,")
print(f"                    {n_session} sessions match, {n_report} rapports.")
print()
print("=" * 65)
print("  TEST 6 TERMINE AVEC SUCCES")
print("=" * 65)