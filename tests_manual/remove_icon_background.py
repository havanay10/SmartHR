"""Rend transparent le fond blanc des icones PNG.

Utile quand les icones telechargees ont un fond blanc
au lieu d'un fond transparent.

Cible : assets/icons/*.png
Resultat : les pixels blancs (ou proches du blanc) deviennent transparents.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from PIL import Image
    import numpy as np
except ImportError:
    print("ERREUR : pip install Pillow numpy")
    sys.exit(1)


ICONS_DIR = Path(__file__).resolve().parent.parent / "assets" / "icons"

# Seuil de detection du "blanc" (0-255)
# Plus le seuil est eleve, plus on est tolerant
WHITE_THRESHOLD = 230   # pixels avec R,G,B > 230 = consideres comme blancs


def remove_white_background(png_path: Path, threshold: int = WHITE_THRESHOLD) -> tuple[bool, str]:
    """Rend transparent tous les pixels blancs d'une image PNG.

    Args:
        png_path: chemin vers le PNG
        threshold: seuil de blanc (0-255). Au-dessus = transparent.

    Returns:
        (success, message)
    """
    try:
        # Ouvre en RGBA (avec canal alpha)
        img = Image.open(png_path).convert("RGBA")
        data = np.array(img).astype(np.int16)

        # Separe les canaux
        r = data[:, :, 0]
        g = data[:, :, 1]
        b = data[:, :, 2]
        a = data[:, :, 3]

        # Detecte les pixels "blancs" (R, G, B tous > threshold)
        white_mask = (r > threshold) & (g > threshold) & (b > threshold)

        # Nombre de pixels a rendre transparents
        n_white = int(white_mask.sum())
        n_total = r.size
        pct = round(100 * n_white / n_total, 1)

        # Applique : les pixels blancs deviennent transparents (alpha = 0)
        # On garde les pixels non-blancs avec leur alpha d'origine
        new_alpha = np.where(white_mask, 0, a)
        new_data = np.dstack((r, g, b, new_alpha)).astype(np.uint8)

        # Sauvegarde
        new_img = Image.fromarray(new_data, "RGBA")
        new_img.save(png_path, "PNG", optimize=True)

        return True, f"{pct}% du fond rendu transparent"

    except Exception as e:
        return False, str(e)


def main():
    print("=" * 75)
    print("  SUPPRESSION DU FOND BLANC DES ICONES")
    print("=" * 75)
    print(f"\n  Dossier : {ICONS_DIR}")
    print(f"  Seuil de blanc : {WHITE_THRESHOLD} (R,G,B > {WHITE_THRESHOLD})\n")

    if not ICONS_DIR.exists():
        print("  ❌ Dossier introuvable")
        return

    # Liste tous les PNG
    files = sorted(ICONS_DIR.glob("*.png"))
    if not files:
        print("  ⚠️  Aucune icone PNG trouvee")
        return

    print(f"  {len(files)} fichier(s) a traiter :\n")

    ok_count = 0
    err_count = 0

    for f in files:
        success, msg = remove_white_background(f)
        if success:
            print(f"  ✅ {f.name:40} {msg}")
            ok_count += 1
        else:
            print(f"  ❌ {f.name:40} ERREUR: {msg}")
            err_count += 1

    print("\n" + "=" * 75)
    print(f"  RESUME : {ok_count} succes, {err_count} erreurs")
    print("=" * 75)
    print("\n  Relancez l'application pour voir le resultat.")
    print("    python main.py\n")


if __name__ == "__main__":
    main()