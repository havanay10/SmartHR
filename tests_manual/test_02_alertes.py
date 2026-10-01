"""Test 2 : AlertService (regles CDC §3).

Verifie :
- Regle 1 : > 5 jours d'absence => alerte CRITIQUE
- Regle 2 : conges > moyenne x 1.5 => alerte PREVENTIVE
- Regle 3 : resolution d'alerte => statut "resolue"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.alert_service import AlertService
from config import settings


def titre(txt):
    print("\n" + "=" * 65)
    print(f"  {txt}")
    print("=" * 65)


def sous_titre(txt):
    print(f"\n[{txt}]")


# ============================================================
titre("TEST 2 : AlertService (CDC §3)")
# ============================================================

svc = AlertService()

# ------------------------------------------------------------
sous_titre("2.1 Configuration des seuils CDC")
# ------------------------------------------------------------
print(f"    ABSENCE_ALERT_THRESHOLD  : {settings.ABSENCE_ALERT_THRESHOLD} jours")
print(f"    LEAVE_RISK_MULTIPLIER    : {settings.LEAVE_RISK_MULTIPLIER}")

# ------------------------------------------------------------
sous_titre("2.2 Etat AVANT declenchement des regles")
# ------------------------------------------------------------
kpis_avant = svc.get_kpis()
print(f"    Alertes actives  : {kpis_avant['active_alerts']}")
print(f"    Risques detectes : {kpis_avant['detected_risks']}")
print(f"    Alertes resolues : {kpis_avant['resolved_alerts']}")

# ------------------------------------------------------------
sous_titre("2.3 Execution des regles metier")
# ------------------------------------------------------------
print("    Regle 1 : Absences > 5 jours / mois")
print("    Regle 2 : Conges > moyenne x 1.5")
svc.run_all_rules()
print("    [OK] Regles executees")

# ------------------------------------------------------------
sous_titre("2.4 Etat APRES declenchement")
# ------------------------------------------------------------
kpis_apres = svc.get_kpis()
print(f"    Alertes actives  : {kpis_apres['active_alerts']}")
print(f"    Risques detectes : {kpis_apres['detected_risks']}")
print(f"    Alertes resolues : {kpis_apres['resolved_alerts']}")

# ------------------------------------------------------------
sous_titre("2.5 Details des alertes actives")
# ------------------------------------------------------------
alerts = svc.get_active_alerts()
if not alerts:
    print("    Aucune alerte active")
else:
    print(f"    {len(alerts)} alerte(s) :")
    for i, a in enumerate(alerts, 1):
        print(f"\n    --- Alerte {i} ---")
        print(f"    Severite : {a['severity'].upper()}")
        print(f"    Employe  : {a['employee_name']}")
        print(f"    Titre    : {a['title']}")
        print(f"    Detail   : {a['description']}")
        print(f"    Risque   : {a['risk_score']}%")

# ------------------------------------------------------------
sous_titre("2.6 Test resolution d'une alerte")
# ------------------------------------------------------------
if alerts:
    first_id = alerts[0]["id"]
    print(f"    Resolution de l'alerte : {first_id[:8]}...")
    svc.resolve_alert(first_id)

    kpis_final = svc.get_kpis()
    print(f"\n    APRES resolution :")
    print(f"      Alertes actives  : {kpis_final['active_alerts']}")
    print(f"      Alertes resolues : {kpis_final['resolved_alerts']}")
else:
    print("    [SKIP] Aucune alerte a resoudre")

# ------------------------------------------------------------
sous_titre("2.7 Idempotence (re-execution des regles)")
# ------------------------------------------------------------
print("    Re-execution des regles...")
kpis_before = svc.get_kpis()
svc.run_all_rules()
kpis_after = svc.get_kpis()
print(f"    Avant  : {kpis_before['active_alerts']} alertes")
print(f"    Apres  : {kpis_after['active_alerts']} alertes")
if kpis_before['active_alerts'] == kpis_after['active_alerts']:
    print("    [OK] Pas de doublons (idempotent)")
else:
    print("    [ATTENTION] Des doublons ont ete crees")

# ============================================================
titre("TEST 2 TERMINE")
# ============================================================