"""Recolore TOUTES les icones avec les bonnes couleurs SmartRH.

Transforme les icones (blanches, noires, grises) en couleurs vives
correspondant a chaque usage.
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


# =====================================================
# COULEURS PAR FICHIER (RGB)
# =====================================================
COLOR_MAP = {
    # ---------- SIDEBAR (vert SmartRH) ----------
    "sidebar-home.png":       (13, 122, 106),   # #0D7A6A
    "sidebar-users.png":      (13, 122, 106),
    "sidebar-recruit.png":    (13, 122, 106),
    "sidebar-chart.png":      (13, 122, 106),
    "sidebar-warning.png":    (13, 122, 106),
    "sidebar-link.png":       (13, 122, 106),
    "sidebar-settings.png":   (13, 122, 106),

    # ---------- KPI (couleur selon accent) ----------
    "kpi-employees.png":      (13, 122, 106),   # vert
    "kpi-calendar.png":       (192, 57, 43),    # rouge
    "kpi-target.png":         (124, 58, 237),   # violet
    "kpi-turnover.png":       (13, 122, 106),   # vert
    "kpi-interview.png":      (243, 156, 18),   # orange
    "kpi-money.png":          (13, 122, 106),   # vert
    "kpi-time.png":           (13, 122, 106),   # vert
    "kpi-alert.png":          (192, 57, 43),    # rouge

    # ---------- APP ----------
    "app-bell.png":           (13, 122, 106),   # vert
    "app-help.png":           (100, 116, 139),  # gris
    "app-avatar.png":         (13, 122, 106),   # vert
    "app-ia.png":             (13, 122, 106),   # vert
    "app-logo.png":           (13, 122, 106),   # vert

    # ---------- ACTIONS (gris par defaut) ----------
    "action-add.png":         (13, 122, 106),   # vert
    "action-edit.png":        (100, 116, 139),  # gris
    "action-delete.png":      (192, 57, 43),    # rouge
    "action-view.png":        (100, 116, 139),  # gris
    "action-download.png":    (13, 122, 106),   # vert
    "action-upload.png":      (13, 122, 106),   # vert
    "action-export.png":      (46, 134, 222),   # bleu
    "action-refresh.png":     (100, 116, 139),  # gris
    "action-filter.png":      (100, 116, 139),  # gris
    "action-search.png":      (100, 116, 139),  # gris
    "action-check.png":       (13, 122, 106),   # vert
    "action-close.png":       (192, 57, 43),    # rouge

    # ---------- STATUTS ----------
    "status-success.png":     (13, 122, 106),   # vert
    "status-warning.png":     (243, 156, 18),   # orange
    "status-danger.png":      (192, 57, 43),    # rouge
    "status-info.png":        (46, 134, 222),   # bleu
    "status-pending.png":     (100, 116, 139),  # gris
    "status-match.png":       (13, 122, 106),   # vert

    # ---------- CHARTS ----------
    "chart-bar.png":          (13, 122, 106),   # vert
    "chart-pie.png":          (46, 134, 222),   # bleu
    "chart-line.png":         (13, 122, 106),   # vert
    "chart-report.png":       (100, 116, 139),  # gris
    "chart-pdf.png":          (192, 57, 43),    # rouge
    "chart-excel.png":        (13, 122, 106),   # vert
}


def recolor_icon(png_path: Path, rgb_target: tuple) -> tuple[bool, str]:
    """Recolore une icone en gardant la transparence."""
    try:
        img = Image.open(png_path).convert("RGBA")
        data = np.array(img)
        alpha = data[:, :, 3]

        # Nouvelle couleur RGB partout
        new_rgb = np.zeros_like(data[:, :, :3])
        new_rgb[:, :, 0] = rgb_target[0]
        new_rgb[:, :, 1] = rgb_target[1]
        new_rgb[:, :, 2] = rgb_target[2]

        # Combine avec l'alpha d'origine
        new_data = np.dstack((new_rgb, alpha))

        # Sauvegarde
        new_img = Image.fromarray(new_data, "RGBA")
        new_img.save(png_path, "PNG", optimize=True)

        # Stats
        visible = int((alpha > 10).sum())
        total = alpha.size
        pct = round(100 * visible / total, 1)

        return True, f"{pct}% pixels visibles"

    except Exception as e:
        return False, str(e)


def main():
    print("=" * 75)
    print("  RECOLORISATION DE TOUTES LES ICONES")
    print("=" * 75)
    print(f"\n  Dossier : {ICONS_DIR}\n")

    if not ICONS_DIR.exists():
        print("  ERREUR : dossier introuvable")
        return

    ok = 0
    skip = 0
    err = 0

    for f in sorted(ICONS_DIR.glob("*.png")):
        if f.name in COLOR_MAP:
            rgb = COLOR_MAP[f.name]
            success, msg = recolor_icon(f, rgb)
            if success:
                print(f"  OK  {f.name:30} RGB{rgb}  {msg}")
                ok += 1
            else:
                print(f"  ERR {f.name:30} {msg}")
                err += 1
        else:
            print(f"  --  {f.name:30} (non configure, ignore)")
            skip += 1

    print("\n" + "=" * 75)
    print(f"  RESUME : {ok} recolorees, {skip} ignorees, {err} erreurs")
    print("=" * 75)
    print("\n  Relancez l'application : python main.py\n")


if __name__ == "__main__":
    main()