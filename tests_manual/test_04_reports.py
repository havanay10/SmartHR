"""Test 4 : ReportService (CDC §6).

Verifie la generation des 4 rapports PDF :
- Analyse des remunerations par departement
- Analyse du turnover et de l'absenteisme
- Pyramide des ages et de l'anciennete
- Projection de la masse salariale
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.report_service import ReportService, REPORT_TYPES
from config import settings


def titre(txt):
    print("\n" + "=" * 65)
    print(f"  {txt}")
    print("=" * 65)


def sous_titre(txt):
    print(f"\n[{txt}]")


# ============================================================
titre("TEST 4 : ReportService (CDC §6)")
# ============================================================

svc = ReportService()

# ------------------------------------------------------------
sous_titre("4.1 Configuration")
# ------------------------------------------------------------
print(f"    Dossier d'export : {settings.EXPORT_DIR}")
print(f"    Existe ?         : {settings.EXPORT_DIR.exists()}")

# ------------------------------------------------------------
sous_titre("4.2 Types de rapports disponibles")
# ------------------------------------------------------------
for key, label in REPORT_TYPES.items():
    print(f"    {key:25} : {label}")

# ------------------------------------------------------------
sous_titre("4.3 Generation de chaque type")
# ------------------------------------------------------------
generated_files = []
for rtype in REPORT_TYPES.keys():
    print(f"\n    Generation : {rtype}")
    try:
        path = svc.generate(rtype)
        p = Path(path)
        size_kb = p.stat().st_size // 1024
        generated_files.append((rtype, p.name, size_kb))
        print(f"      [OK] Fichier : {p.name}")
        print(f"           Taille  : {size_kb} Ko")
    except Exception as e:
        print(f"      [ERREUR] {e}")

print(f"\n    Total : {len(generated_files)} / {len(REPORT_TYPES)} rapports generes")

# ------------------------------------------------------------
sous_titre("4.4 Verification des fichiers sur disque")
# ------------------------------------------------------------
export_dir = settings.EXPORT_DIR
if export_dir.exists():
    pdf_files = sorted(export_dir.glob("*.pdf"), key=lambda f: f.stat().st_mtime, reverse=True)
    print(f"    {len(pdf_files)} fichier(s) PDF dans {export_dir}")
    print(f"\n    Les 5 plus recents :")
    for f in pdf_files[:5]:
        size_kb = f.stat().st_size // 1024
        mtime = f.stat().st_mtime
        from datetime import datetime
        dt = datetime.fromtimestamp(mtime).strftime("%d/%m/%Y %H:%M:%S")
        print(f"      {dt} | {f.name:45} | {size_kb} Ko")
else:
    print(f"    [ERREUR] Dossier {export_dir} introuvable")

# ------------------------------------------------------------
sous_titre("4.5 Verification en base")
# ------------------------------------------------------------
from sqlalchemy import select, func
from app.db.connection import get_session
from app.models.report import Report

with get_session() as db:
    total_reports = db.scalar(select(func.count()).select_from(Report)) or 0
    print(f"    Rapports en base : {total_reports}")

    # Repartition par type
    print(f"\n    Repartition par type :")
    stmt = (
        select(Report.report_type, func.count())
        .group_by(Report.report_type)
    )
    for rtype, count in db.execute(stmt):
        print(f"      {rtype:25} : {count}")

# ------------------------------------------------------------
sous_titre("4.6 Derniers rapports generes")
# ------------------------------------------------------------
latest = svc.get_latest(10)
print(f"    {len(latest)} rapport(s) :")
for i, r in enumerate(latest, 1):
    dt = r["created_at"].strftime("%d/%m/%Y %H:%M")
    print(f"      {i}. {dt} | {r['title'][:40]:40} | {r['format']} | {r['size_kb']} Ko")

# ------------------------------------------------------------
sous_titre("4.7 Ouverture d'un PDF (verification)")
# ------------------------------------------------------------
if generated_files:
    first_type, first_file, size = generated_files[0]
    full_path = export_dir / first_file
    print(f"    Fichier a verifier : {full_path}")
    print(f"    Chemin absolu : {full_path.resolve()}")
    print(f"\n    Pour ouvrir ce PDF manuellement :")
    print(f"      Windows : start \"\" \"{full_path.resolve()}\"")
    print(f"      macOS   : open \"{full_path.resolve()}\"")
    print(f"      Linux   : xdg-open \"{full_path.resolve()}\"")

# ============================================================
titre("TEST 4 TERMINE")
# ============================================================