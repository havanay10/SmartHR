"""Test du modele ML de turnover."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.prediction_service import PredictionService
from app.services.alert_service import AlertService

# ⭐ Genere les alertes AVANT de predire (sinon elles n'existent pas)
print("Generation des alertes CDC...")
AlertService().run_all_rules()
print("OK\n")

svc = PredictionService()

print("=" * 65)
print("  ENTRAINEMENT DU MODELE ML")
print("=" * 65)

info = svc.train(force=True)
print(f"  Entraine      : {info.get('trained')}")
print(f"  Echantillons  : {info.get('n_samples')}  (8 actifs + 6 sortis)")
print(f"  Features      : {info.get('n_features')}")

print("\n  IMPORTANCE DES FEATURES :")
for feat, imp in info.get("feature_importances", []):
    bar = "#" * int(imp * 50)
    print(f"    {feat:25} {imp*100:5.1f}%  {bar}")

print("\n" + "=" * 65)
print("  PREDICTIONS POUR EMPLOYES ACTIFS")
print("=" * 65)

predictions = svc.predict_all()
for p in predictions:
    print(f"\n  {p['employee_name']:25} - {p['risk_score']:5.1f}% [{p['risk_level']}]")
    if p['reasons']:
        print(f"      Raisons: {' | '.join(p['reasons'])}")

# Resume
print("\n" + "=" * 65)
print("  RESUME")
print("=" * 65)
summary = svc.get_summary()
print(f"  Total actifs         : {summary['total']}")
print(f"  Risque eleve         : {summary['high']}")
print(f"  Risque modere        : {summary['medium']}")
print(f"  Risque faible        : {summary['low']}")