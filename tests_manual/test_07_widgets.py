"""Test : import des widgets reutilisables."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication
from app.ui.styles import APP_STYLE


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_STYLE)

    print("=" * 65)
    print("  TEST 7.2 : Widgets reutilisables")
    print("=" * 65)

    # --- Test import ---
    from app.ui.widgets import (
        KpiCard, Badge, PageHeader, SectionTitle,
        Sidebar, TopBar, AlertCard,
    )
    print("\n[OK] Tous les widgets importes :")
    print("  - KpiCard")
    print("  - Badge")
    print("  - PageHeader")
    print("  - SectionTitle")
    print("  - Sidebar")
    print("  - TopBar")
    print("  - AlertCard")

    # --- Test instanciation ---
    print("\n[TEST] Instanciation de chaque widget...")

    kpi = KpiCard(
        title="Test KPI",
        value="42",
        subtitle="Sous-titre test",
        icon="🎯",
        accent="green",
        trend="+5",
    )
    print("  [OK] KpiCard")

    badge = Badge("Test", variant="success")
    print("  [OK] Badge")

    header = PageHeader(
        title="Titre test",
        subtitle="Sous-titre test",
        breadcrumb="TEST  >  PAGE",
    )
    print("  [OK] PageHeader")

    section = SectionTitle("Section test", badge_text="3 items")
    print("  [OK] SectionTitle")

    sidebar = Sidebar()
    print("  [OK] Sidebar")

    topbar = TopBar(user_name="Rakoto")
    print("  [OK] TopBar")

    alert = AlertCard(
        employee="TEST User",
        severity="TEST",
        tag="Test tag",
        fact="Fait test",
        observation="Observation test",
        risk_score="50%",
        kind="danger",
    )
    print("  [OK] AlertCard")

    print("\n" + "=" * 65)
    print("  TEST 7.2 TERMINE AVEC SUCCES")
    print("=" * 65)
    print("\n  Tous les widgets sont operationnels.")
    print("  Ils peuvent maintenant etre utilises dans les pages.")


if __name__ == "__main__":
    main()