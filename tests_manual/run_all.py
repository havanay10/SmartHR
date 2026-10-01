"""Lance tous les tests manuels dans l'ordre."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TESTS = [
    "test_01_stats.py",
    "test_02_alertes.py",
    "test_03_smartmatch.py",
    "test_04_reports.py",
    "test_05_cv.py",
    "test_06_integration.py",
]

for t in TESTS:
    print(f"\n{'=' * 70}")
    print(f"  EXECUTION : {t}")
    print(f"{'=' * 70}")
    result = subprocess.run(
        [sys.executable, str(HERE / t)],
        cwd=HERE.parent,
    )
    if result.returncode != 0:
        print(f"\n[ERREUR] {t} a echoue (code {result.returncode})")
        sys.exit(1)

print("\n" + "=" * 70)
print("  TOUS LES TESTS SONT PASSES")
print("=" * 70)