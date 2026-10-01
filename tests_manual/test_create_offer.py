"""Test de creation d'offre."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from decimal import Decimal
from app.services.recruitment_service import RecruitmentService
from app.services.stats_service import StatsService

# Recupere un departement
depts = StatsService().get_all_departments()
if not depts:
    print("ERREUR : Aucun departement en base")
    sys.exit(1)

dept_id = depts[0]["id"]
dept_name = depts[0]["name"]

svc = RecruitmentService()

offer_id = svc.create_job_offer(
    title="Data Engineer",
    department_id=dept_id,
    contract_type="CDI",
    location="Paris 9e - Hybride",
    salary_min=Decimal("55000"),
    salary_max=Decimal("70000"),
    experience_level="Senior",
    hard_skills=["Python", "SQL", "Airflow"],
    soft_skills=["Autonomie", "Rigueur"],
    priority="normal",
    description="Nous sommes a la recherche de Data engineer",
    status="active",
)

print(f"OK - Offre creee : {offer_id}")
print(f"   Departement : {dept_name}")

# Verification
offers = svc.get_all_job_offers()
print(f"\nTotal offres en base : {len(offers)}")
for o in offers[-3:]:
    print(f"   {o['reference']:20} | {o['title'][:40]}")