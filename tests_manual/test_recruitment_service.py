"""Test rapide du RecruitmentService."""
from app.services.recruitment_service import RecruitmentService

def test_recruitment_service():
    service = RecruitmentService()

    print("=== TEST RECRUITMENT SERVICE ===\n")

    # Test 1 : KPIs
    print("1. KPIs de recrutement :")
    kpis = service.get_recruitment_kpis()
    print(f"   - Total candidats : {kpis['total_candidates']}")
    print(f"   - Pré-sélectionnés : {kpis['preselected_count']}")
    print(f"   - Entretiens : {kpis['interviews_count']}\n")

    # Test 2 : Offres d'emploi
    print("2. Offres d'emploi :")
    offers = service.get_all_job_offers()
    for offer in offers:
        print(f"   - {offer['title']}")
        print(f"     Département : {offer['department']}")
        print(f"     Candidats : {offer['total_candidates']} (pré-sélectionnés : {offer['preselected_count']})")
        print(f"     Score moyen : {offer['avg_match_score']}%\n")

    # Test 3 : Top matches
    print("3. Top 5 matchs IA :")
    top_matches = service.get_top_matches(limit=5)
    for i, match in enumerate(top_matches, 1):
        print(f"   {i}. {match['name']} - {match['match_score']}%")
        print(f"      Poste : {match['current_title']}")
        print(f"      Offre : {match['offer_title']}")
        print(f"      Compétences : {', '.join(match['skills'][:3])}\n")

    print("=== TEST TERMINÉ ===")

if __name__ == "__main__":
    test_recruitment_service()
