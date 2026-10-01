"""Diagnostic des icones disponibles."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ui.icons import IMAGES_DIR, EMOJI_TO_ICON

print("=" * 70)
print(f"  DOSSIER : {IMAGES_DIR}")
print(f"  EXISTE  : {IMAGES_DIR.exists()}")
print("=" * 70)

# Liste des fichiers
print("\n=== FICHIERS DANS assets/icons/ ===\n")
if IMAGES_DIR.exists():
    files = sorted(IMAGES_DIR.glob("*"))
    if not files:
        print("  ⚠️  Dossier VIDE")
    else:
        print(f"  {len(files)} fichier(s) :")
        for f in files:
                size_bytes = f.stat().st_size
                if size_bytes < 1024:
                    size_str = f"{size_bytes} octets"
                else:
                    size_str = f"{size_bytes / 1024:.1f} Ko"
                print(f"    - {f.name} ({size_str})")
else:
    print("  ❌ Dossier inexistant")

# Verifier chaque emoji mappe
print("\n=== VERIFICATION DU MAPPING EMOJI -> ICONE ===\n")

found = 0
missing = 0

for emoji, icon_name in sorted(EMOJI_TO_ICON.items()):
    # Verifie si le fichier existe
    exists = False
    for ext in [".png", ".svg", ".jpg", ".jpeg"]:
        if (IMAGES_DIR / f"{icon_name}{ext}").exists():
            exists = True
            break

    if exists:
        print(f"  ✅ {emoji}  ->  {icon_name}")
        found += 1
    else:
        print(f"  ❌ {emoji}  ->  {icon_name}  (fichier absent)")
        missing += 1

print(f"\n  Total : {found} trouvées, {missing} manquantes")

print("\n" + "=" * 70)