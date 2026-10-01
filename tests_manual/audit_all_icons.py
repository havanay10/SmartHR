"""Audit complet : verifie TOUS les noms d'icones utilises dans le code.

Compare :
- Les noms utilises dans IconLabel(...) partout dans app/ui/
- Les fichiers presents dans assets/icons/

Detecte :
- Les icones manquantes (nom utilise mais fichier absent)
- Les fichiers orphelins (fichier present mais jamais utilise)
"""
import sys
import re
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.ui.icons import IMAGES_DIR, EMOJI_TO_ICON, resolve_icon_path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
UI_DIR = PROJECT_ROOT / "app" / "ui"


# =====================================================
# 1. SCAN DU CODE
# =====================================================
def scan_code_icons():
    """Cherche toutes les utilisations d'IconLabel(nom) dans app/ui/."""
    pattern = re.compile(
        r'IconLabel\(\s*["\']([^"\']+)["\']',
        re.MULTILINE
    )

    results = defaultdict(list)  # {nom_icone: [(fichier, ligne)]}

    for py_file in UI_DIR.rglob("*.py"):
        try:
            content = py_file.read_text(encoding="utf-8")
        except Exception:
            continue

        for i, line in enumerate(content.splitlines(), start=1):
            for match in pattern.finditer(line):
                icon_name = match.group(1)
                rel_path = py_file.relative_to(PROJECT_ROOT)
                results[icon_name].append((str(rel_path), i))

    return results


# =====================================================
# 2. SCAN DES FICHIERS
# =====================================================
def scan_available_icons():
    """Liste tous les fichiers dans assets/icons/."""
    if not IMAGES_DIR.exists():
        return set()

    extensions = [".png", ".svg", ".jpg", ".jpeg", ".webp"]
    files = set()

    for f in IMAGES_DIR.iterdir():
        if f.suffix.lower() in extensions:
            files.add(f.stem)  # sans extension

    return files


# =====================================================
# 3. ANALYSE
# =====================================================
def main():
    print("=" * 75)
    print("  AUDIT COMPLET DES ICONES — SmartRH")
    print("=" * 75)
    print(f"\n  Dossier icones : {IMAGES_DIR}")

    code_icons = scan_code_icons()
    available = scan_available_icons()

    print(f"  Noms utilises dans le code  : {len(code_icons)}")
    print(f"  Fichiers presents           : {len(available)}")

    # ============================================
    # SECTION 1 : Icones utilisees dans le code
    # ============================================
    print("\n" + "=" * 75)
    print("  1. ICONES UTILISEES DANS LE CODE")
    print("=" * 75)

    used_but_missing = []
    used_but_emoji = []
    used_ok = []

    for name, locations in sorted(code_icons.items()):
        # Ignore les emojis directs
        if len(name) <= 4 and not name.replace("-", "").replace("_", "").isalnum():
            continue

        # Verifie si un fichier correspond
        path = resolve_icon_path(name)
        if path and path.exists():
            used_ok.append((name, locations))
        else:
            used_but_missing.append((name, locations))

    print(f"\n  ✅ Icones trouvees ({len(used_ok)}) :")
    for name, locations in used_ok:
        files = ", ".join(f"{f}:{l}" for f, l in locations[:2])
        more = f" (+{len(locations)-2})" if len(locations) > 2 else ""
        print(f"     ✅ {name:30} <- {files}{more}")

    print(f"\n  ❌ Icones MANQUANTES ({len(used_but_missing)}) :")
    for name, locations in used_but_missing:
        files = ", ".join(f"{f}:{l}" for f, l in locations[:2])
        more = f" (+{len(locations)-2})" if len(locations) > 2 else ""
        print(f"     ❌ {name:30} <- {files}{more}")

    # ============================================
    # SECTION 2 : Fichiers orphelins
    # ============================================
    print("\n" + "=" * 75)
    print("  2. FICHIERS ORPHELINS (jamais utilises dans le code)")
    print("=" * 75)

    used_names = set(code_icons.keys())

    orphans = []
    for fname in sorted(available):
        # Verifie si ce nom est utilise dans le code
        if fname in used_names:
            continue

        # Verifie si c'est un nom mappe dans EMOJI_TO_ICON
        is_mapped = fname in EMOJI_TO_ICON.values()

        if not is_mapped:
            orphans.append(fname)

    if orphans:
        print(f"\n  ⚠️  {len(orphans)} fichier(s) jamais utilise(s) :")
        for fname in orphans:
            print(f"     - {fname}")
    else:
        print("\n  ✅ Aucun orphelin — tous les fichiers sont utilises")

    # ============================================
    # SECTION 3 : Mapping EMOJI_TO_ICON
    # ============================================
    print("\n" + "=" * 75)
    print("  3. MAPPING EMOJI_TO_ICON")
    print("=" * 75)

    mapped_ok = []
    mapped_missing = []

    for emoji, icon_name in sorted(EMOJI_TO_ICON.items()):
        path = resolve_icon_path(icon_name)
        if path and path.exists():
            mapped_ok.append((emoji, icon_name))
        else:
            mapped_missing.append((emoji, icon_name))

    print(f"\n  ✅ Emojis remplaces par image ({len(mapped_ok)}) :")
    for emoji, icon_name in mapped_ok:
        print(f"     {emoji}  ->  {icon_name}")

    print(f"\n  ⚠️  Emojis avec image manquante ({len(mapped_missing)}) :")
    for emoji, icon_name in mapped_missing[:15]:
        print(f"     {emoji}  ->  {icon_name}  (absent)")
    if len(mapped_missing) > 15:
        print(f"     ... et {len(mapped_missing) - 15} autres")

    # ============================================
    # RESUME FINAL
    # ============================================
    print("\n" + "=" * 75)
    print("  RESUME")
    print("=" * 75)
    print(f"\n  Total noms utilises dans le code     : {len(code_icons)}")
    print(f"  Icones OK                            : {len(used_ok)}")
    print(f"  Icones MANQUANTES (utilisees)        : {len(used_but_missing)}")
    print(f"  Fichiers orphelins                   : {len(orphans)}")
    print(f"  Emojis mappes avec image             : {len(mapped_ok)}")
    print(f"  Emojis avec image manquante          : {len(mapped_missing)}")

    if used_but_missing:
        print("\n  ⚠️  A CORRIGER : les icones suivantes sont utilisees")
        print("     dans le code mais n'ont pas de fichier :")
        for name, locations in used_but_missing:
            print(f"     -> {name}")
            for f, l in locations:
                print(f"          {f}:{l}")


if __name__ == "__main__":
    main()