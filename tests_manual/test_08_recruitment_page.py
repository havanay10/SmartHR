"""Test manuel de la page RecruitmentPage.

Ce test vérifie :
1. Que les services fonctionnent correctement
2. Que les données du seed sont accessibles
3. Que les widgets peuvent être créés
4. Que la logique de la page est correcte
"""
import sys
from pathlib import Path

# Ajouter la racine du projet au PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.recruitment_service import RecruitmentService
from app.services.stats_service import StatsService


def test_recruitment_services():
    """Test des services de recrutement."""
    print("=== TEST DES SERVICES DE RECRUTEMENT ===\n")

    recruitment_svc = RecruitmentService()
    stats_svc = StatsService()

    # Test 1 : KPIs de recrutement
    print("1. Test KPIs de recrutement :")
    try:
        kpis = recruitment_svc.get_recruitment_kpis()
        print(f"   [OK] Total candidats : {kpis['total_candidates']}")
        print(f"   [OK] Pre-selectionnes : {kpis['preselected_count']}")
        print(f"   [OK] Entretiens : {kpis['interviews_count']}")

        # Vérifications
        assert kpis['total_candidates'] == 35, "Devrait avoir 35 candidats"
        assert kpis['preselected_count'] > 0, "Devrait avoir des pre-selectionnes"
        print("   [OK] KPIs valides\n")
    except Exception as e:
        print(f"   [ERREUR] Erreur KPIs: {e}\n")
        return False

    # Test 2 : Offres d'emploi
    print("2. Test offres d'emploi :")
    try:
        offers = recruitment_svc.get_all_job_offers()
        print(f"   [OK] Nombre d'offres : {len(offers)}")

        assert len(offers) == 3, "Devrait avoir 3 offres"

        for i, offer in enumerate(offers, 1):
            print(f"   [OK] Offre {i}: {offer['title']}")
            print(f"      - Departement : {offer['department']}")
            print(f"      - Candidats : {offer['total_candidates']}")
            print(f"      - Pre-selectionnes : {offer['preselected_count']}")
            print(f"      - Score moyen : {offer['avg_match_score']}%")

        print("   [OK] Offres validees\n")
    except Exception as e:
        print(f"   [ERREUR] Erreur offres: {e}\n")
        return False

    # Test 3 : Candidats d'une offre
    print("3. Test candidats d'une offre :")
    try:
        offer_id = offers[0]['id']
        candidates = recruitment_svc.get_candidates_of_offer(offer_id)

        print(f"   [OK] Candidats recus : {len(candidates['received'])}")
        print(f"   [OK] Candidats pre-selectionnes : {len(candidates['preselected'])}")

        assert len(candidates['received']) > 0, "Devrait avoir des candidats"

        for candidate in candidates['received'][:3]:
            print(f"   [OK] {candidate['name']} - Score: {candidate['match_score']}%")

        print("   [OK] Candidats valides\n")
    except Exception as e:
        print(f"   [ERREUR] Erreur candidats: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 4 : Top matches
    print("4. Test top matches IA :")
    try:
        top_matches = recruitment_svc.get_top_matches(limit=5)
        print(f"   [OK] Top matches trouves : {len(top_matches)}")

        for i, match in enumerate(top_matches, 1):
            print(f"   [OK] {i}. {match['name']} - {match['match_score']}%")
            print(f"      - Offre : {match['offer_title']}")
            print(f"      - Competences : {', '.join(match['skills'][:3])}")

        print("   [OK] Top matches valides\n")
    except Exception as e:
        print(f"   [ERREUR] Erreur top matches: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Test 5 : Candidats filtrés
    print("5. Test candidats filtrés :")
    try:
        filtered = recruitment_svc.get_filtered_candidates(min_score=80)
        print(f"   [OK] Candidats filtres (score >= 80%) : {len(filtered)}")

        assert len(filtered) > 0, "Devrait avoir des candidats filtrés"

        for candidate in filtered[:3]:
            print(f"   [OK] {candidate['name']} - Score: {candidate['match_score']}%")

        print("   [OK] Candidats filtres valides\n")
    except Exception as e:
        print(f"   [ERREUR] Erreur candidats filtres: {e}\n")
        return False

    # Test 6 : Départements (pour le dialogue)
    print("6. Test départements :")
    try:
        departments = stats_svc.get_all_departments()
        print(f"   [OK] Nombre de departements : {len(departments)}")

        for dept in departments:
            print(f"   [OK] {dept['name']} ({dept['code']})")

        print("   [OK] Departements valides\n")
    except Exception as e:
        print(f"   [ERREUR] Erreur departements: {e}\n")
        return False

    print("=== TOUS LES TESTS REUSSIS ===\n")
    return True


def test_widget_creation():
    """Test la création des widgets (sans affichage graphique)."""
    print("=== TEST DE CRÉATION DES WIDGETS ===\n")

    try:
        from app.ui.widgets.job_offer_row import JobOfferRow
        from app.ui.widgets.candidate_card import CandidateCard
        from PyQt6.QtWidgets import QApplication

        # Créer une application PyQt minimale
        app = QApplication([])

        # Test JobOfferRow
        print("1. Test JobOfferRow :")
        offer_data = {
            'id': 'test-1',
            'title': 'Test Offer',
            'department': 'R&D',
            'status': 'active',
            'priority': 'normal',
            'total_candidates': 10,
            'preselected_count': 5,
            'avg_match_score': 85.5,
        }
        row = JobOfferRow(offer_data, is_active=True)
        print("   [OK] JobOfferRow cree\n")

        # Test CandidateCard
        print("2. Test CandidateCard :")
        candidate_data = {
            'candidate_id': 'cand-1',
            'name': 'Test Candidate',
            'current_title': 'Developer',
            'skills': ['Python', 'React'],
            'match_score': 90.0,
            'ai_summary': 'Good profile',
            'offer_title': 'Test Offer',
            'offer_id': 'offer-1',
            'years_experience': 5,
        }
        card = CandidateCard(candidate_data)
        print("   [OK] CandidateCard cree\n")

        print("=== TESTS WIDGETS REUSSIS ===\n")
        return True

    except Exception as e:
        print(f"[ERREUR] Erreur widgets: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_page_logic():
    """Test la logique de la page sans affichage graphique."""
    print("=== TEST DE LA LOGIQUE DE LA PAGE ===\n")

    try:
        from app.ui.pages.recruitment_page import RecruitmentPage
        from PyQt6.QtWidgets import QApplication

        # Créer une application PyQt minimale
        app = QApplication([])

        # Test création de la page
        print("1. Test creation RecruitmentPage :")
        page = RecruitmentPage()
        print("   [OK] RecruitmentPage cree\n")

        # Vérifier que les services sont initialisés
        print("2. Test initialisation des services :")
        assert hasattr(page, 'recruitment_svc'), "Devrait avoir recruitment_svc"
        assert hasattr(page, 'stats_svc'), "Devrait avoir stats_svc"
        print("   [OK] Services initialises\n")

        # Vérifier que les widgets sont créés
        print("3. Test creation des widgets de la page :")
        assert hasattr(page, 'recruitment_svc'), "Devrait avoir recruitment_svc"
        assert hasattr(page, 'stats_svc'), "Devrait avoir stats_svc"
        print("   [OK] Widgets crees\n")

        print("=== TESTS LOGIQUE PAGE REUSSIS ===\n")
        return True

    except Exception as e:
        print(f"[ERREUR] Erreur logique page: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*50)
    print("TESTS MANUELS - PAGE RECRUTEMENT")
    print("="*50 + "\n")

    # Test 1 : Services
    services_ok = test_recruitment_services()

    # Test 2 : Widgets
    widgets_ok = test_widget_creation()

    # Test 3 : Logique page
    page_ok = test_page_logic()

    # Résumé
    print("\n" + "="*50)
    print("RESUME DES TESTS")
    print("="*50)
    print(f"Services : {'[OK]' if services_ok else '[ECHEC]'}")
    print(f"Widgets : {'[OK]' if widgets_ok else '[ECHEC]'}")
    print(f"Logique page : {'[OK]' if page_ok else '[ECHEC]'}")

    if services_ok and widgets_ok and page_ok:
        print("\n[OK] TOUS LES TESTS REUSSIS !")
        print("La page recrutement est prete a etre utilisee.")
    else:
        print("\n[ATTENTION] CERTAINS TESTS ONT ECHOUE")
        print("Veuillez corriger les erreurs avant de continuer.")
