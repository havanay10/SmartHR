"""Execute les regles CDC et affiche les alertes."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.alert_service import AlertService

svc = AlertService()
svc.run_all_rules()

print("=" * 60)
print("  KPIs DES ALERTES")
print("=" * 60)

kpis = svc.get_kpis()
for k, v in kpis.items():
    print(f"  {k:25} : {v}")

print("\n" + "=" * 60)
print("  DETAILS DES ALERTES ACTIVES")
print("=" * 60)

for a in svc.get_active_alerts():
    print(f"  [{a['severity'].upper():9}] {a['employee_name']:20} - {a['description'][:60]}")