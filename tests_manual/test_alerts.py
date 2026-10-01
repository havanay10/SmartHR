"""Test rapide des alertes actives."""
import sys
from pathlib import Path

# Ajoute la racine du projet au PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.alert_service import AlertService


# Executer les regles
svc = AlertService()
svc.run_all_rules()

# Recuperer les KPIs
kpis = svc.get_kpis()
print("=" * 70)
print(f"  ALERTES : {kpis}")
print("=" * 70)

# Detail des alertes
alerts = svc.get_active_alerts()
print(f"\n  {len(alerts)} alerte(s) active(s) :\n")

for a in alerts:
    sev = a['severity'].upper()
    name = a['employee_name']
    desc = a['description']
    print(f"  [{sev:9}] {name:20} - {desc}")