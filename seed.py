from datetime import date, timedelta
from decimal import Decimal
import random
from uuid import uuid4

from app.db.connection import get_session
from app.models.alert import Alert
from app.models.employee import Employee, Department
from app.models.leave import LeaveRequest
from app.models.recruitment import JobOffer, Candidate, Application


def seed():
    with get_session() as db:
        # ========== DEPARTEMENTS ==========
        depts = {
            "SUP": Department(
                id=str(uuid4()),
                name="Support & Succes Client",
                code="SUP",
                management_style="Autonome & OKR",
            ),
            "COM": Department(
                id=str(uuid4()),
                name="Commercial & Partenariats",
                code="COM",
                management_style="Directif & Objectifs",
            ),
            "RD": Department(
                id=str(uuid4()),
                name="R&D / Ingenierie Produit",
                code="RD",
                management_style="Autonome & Objectifs OKR",
            ),
            "RH": Department(
                id=str(uuid4()),
                name="Ressources Humaines",
                code="RH",
                management_style="Collaboratif",
            ),
        }
        for d in depts.values():
            db.add(d)
        db.flush()
        print(f"[OK] {len(depts)} departements crees")

        # ========== EMPLOYES ==========
        employees_data = [
            ("EMP-001",  "Marc",      "LEFEBVRE", "M", "Directeur Technique",         "RD",  85000, "D", "06 12 34 56 78", date(1985, 3, 12)),
            ("EMP-8492", "Marie",     "DUPONT",   "F", "Chef de projet Marketing",    "SUP", 48000, "I", "06 23 45 67 89", date(1991, 3, 15)),
            ("EMP-7719", "Thomas",    "MARTIN",   "M", "Développeur Fullstack Lead",  "RD",  62000, "C", "06 34 56 78 90", date(1988, 7, 22)),
            ("EMP-6540", "Robert",    "STEFAN",   "M", "Senior Account Executive",    "COM", 55000, "D", "06 45 67 89 01", date(1982, 11, 8)),
            ("EMP-9128", "Sophie",    "MOREAU",   "F", "Ingénieur DevOps",            "RD",  52000, "S", "06 56 78 90 12", date(1993, 5, 30)),
            ("EMP-4432", "Lucas",     "PETIT",    "M", "Ingénieur Data",              "RD",  50000, "C", "06 67 89 01 23", date(1996, 1, 18)),
            ("EMP-5521", "Alexandre", "MARTIN",   "M", "Lead Backend",                "RD",  68000, "C", "06 78 90 12 34", date(1987, 9, 5)),
            ("EMP-5598", "Sophie",    "BERNARD",  "F", "Ingénieur Cloud",             "RD",  60000, "S", "06 89 01 23 45", date(1990, 4, 25)),
            # ========== ANCIENS EMPLOYES (PARTIS) ==========
            ("EMP-8001", "Pierre",    "DURAND",   "M", "Développeur Junior",          "RD",  38000, "C", "06 90 11 22 33", date(1998, 5, 12)),
            ("EMP-8002", "Julie",     "MOREAU",   "F", "Chargée de recrutement",      "RH",  42000, "I", "06 91 22 33 44", date(1995, 8, 20)),
            ("EMP-8003", "David",     "LEROY",    "M", "Chef de projet",              "RD",  62000, "D", "06 92 33 44 55", date(1980, 2, 15)),
            ("EMP-8004", "Anne",      "ROUSSEAU", "F", "Assistante de direction",     "RH", 35000, "S", "06 93 44 55 66", date(1960, 11, 3)),
            ("EMP-8005", "Karim",     "BENALI",   "M", "Ingénieur DevOps",            "RD",  58000, "C", "06 94 55 66 77", date(1992, 7, 18)),
            ("EMP-8006", "Sophie",    "GIRARD",   "F", "Account Manager",             "COM", 46000, "I", "06 95 66 77 88", date(1994, 3, 25)),
        ]

        emps = {}
        for code, fn, ln, g, title, dept_key, sal, disc, phone, bdate in employees_data:
            # Determine si c'est un ancien employe
            is_former = code.startswith("EMP-80")

            if is_former:
                # Ancien employe - parti
                hire = date(2019, 6, 1)
                departure = date(2024, 12, 31)
                e = Employee(
                    id=str(uuid4()),
                    employee_code=code,
                    first_name=fn,
                    last_name=ln,
                    gender=g,
                    email=f"{fn.lower()}.{ln.lower()}@smartrh.fr",
                    phone=phone,
                    birth_date=bdate,
                    job_title=title,
                    department_id=depts[dept_key].id,
                    hire_date=hire,
                    departure_date=departure,
                    departure_reason="Démission" if code in ["EMP-8001", "EMP-8003", "EMP-8005"] else
                                     ("Rupture conventionnelle" if code == "EMP-8002" else
                                      ("Retraite" if code == "EMP-8004" else "Fin de CDD")),
                    status="sorti",
                    contract_type="CDI",
                    salary_base=Decimal(str(sal)),
                    disc_profile=disc,
                    city="Paris",
                    work_mode="hybride",
                    remote_days_per_week=2,
                )
            else:
                # Employe actif
                e = Employee(
                    id=str(uuid4()),
                    employee_code=code,
                    first_name=fn,
                    last_name=ln,
                    gender=g,
                    email=f"{fn.lower()}.{ln.lower()}@smartrh.fr",
                    phone=phone,
                    birth_date=bdate,
                    job_title=title,
                    department_id=depts[dept_key].id,
                    hire_date=date(2022, 3, 15),
                    status="actif",
                    contract_type="CDI",
                    salary_base=Decimal(str(sal)),
                    disc_profile=disc,
                    city="Paris",
                    work_mode="hybride",
                    remote_days_per_week=2,
                )
            db.add(e)
            emps[code] = e
        db.flush()
        active_count = sum(1 for c in emps if not c.startswith("EMP-80"))
        former_count = len(emps) - active_count
        print(f"[OK] {active_count} employes actifs + {former_count} anciens crees")

        # Affecter Marc LEFEBVRE comme manager du dept RD
        depts["RD"].manager_id = emps["EMP-001"].id

        # ========== PROJETS ET COLLABORATIONS ==========
        # Objectif : creer des projets communs pour que SmartMatch
        # puisse calculer un vrai "historique co-travail"
        from app.models.project import Project, ProjectMember

        # --- Projet 1 : Refonte API (Marc + Thomas + Sophie M.) ---
        p1 = Project(
            id=str(uuid4()),
            name="Refonte API publique",
            description="Migration vers FastAPI et optimisation des endpoints",
            start_date=date(2024, 1, 15),
            end_date=date(2024, 9, 30),
            status="termine",
        )
        db.add(p1)
        db.flush()

        for code in ["EMP-001", "EMP-7719", "EMP-9128"]:  # Marc, Thomas, Sophie
            db.add(ProjectMember(
                project_id=p1.id,
                employee_id=emps[code].id,
                role="lead" if code == "EMP-001" else "membre",
            ))

        # --- Projet 2 : Dashboard Analytics (Thomas + Sophie B. + Lucas) ---
        p2 = Project(
            id=str(uuid4()),
            name="Dashboard Analytics RH",
            description="Creation du tableau de bord temps reel avec KPIs",
            start_date=date(2024, 3, 1),
            end_date=date(2024, 12, 15),
            status="termine",
        )
        db.add(p2)
        db.flush()

        for code in ["EMP-7719", "EMP-5598", "EMP-4432"]:  # Thomas, Sophie B., Lucas
            db.add(ProjectMember(
                project_id=p2.id,
                employee_id=emps[code].id,
                role="membre",
            ))

        # --- Projet 3 : Migration Cloud (Sophie M. + Alexandre + Marc) ---
        p3 = Project(
            id=str(uuid4()),
            name="Migration AWS",
            description="Migration complete vers AWS (ECS, RDS, S3)",
            start_date=date(2025, 1, 10),
            end_date=date(2025, 8, 30),
            status="termine",
        )
        db.add(p3)
        db.flush()

        for code in ["EMP-9128", "EMP-5521", "EMP-001"]:  # Sophie, Alexandre, Marc
            db.add(ProjectMember(
                project_id=p3.id,
                employee_id=emps[code].id,
                role="membre",
            ))

        # --- Projet 4 : Pipeline CI/CD (Thomas + Sophie M.) ---
        p4 = Project(
            id=str(uuid4()),
            name="Pipeline CI/CD",
            description="Mise en place de GitHub Actions et tests automatises",
            start_date=date(2025, 9, 1),
            end_date=None,  # en cours
            status="en_cours",
        )
        db.add(p4)
        db.flush()

        for code in ["EMP-7719", "EMP-9128"]:  # Thomas, Sophie M.
            db.add(ProjectMember(
                project_id=p4.id,
                employee_id=emps[code].id,
                role="membre",
            ))

        print("[OK] 4 projets et 11 membres crees")
        
        # ========== CONGES (pour declencher les alertes CDC) ==========
        # Regle 1 : > 5 jours d'absence dans le mois => alerte CRITIQUE
        # Regle 2 : conges > moyenne * 1.5 => alerte PREVENTIVE

        # --- Cas 1 : Sophie MOREAU (8j Maladie) => CRITIQUE ---
        db.add(LeaveRequest(
            id=str(uuid4()),
            employee_id=emps["EMP-9128"].id,
            leave_type="Maladie",
            start_date=date.today().replace(day=1),
            end_date=date.today().replace(day=1) + timedelta(days=7),
            duration_days=Decimal("8"),
            status="valide",
        ))
        # --- Cas 1b : Sophie MOREAU (15j Conge paye long) => 3eme alerte ---
        # Permet d'avoir 3 alertes pour Sophie (3+ alertes => "multi-alertes")
        db.add(LeaveRequest(
            id=str(uuid4()),
            employee_id=emps["EMP-9128"].id,
            leave_type="Congé payé",
            start_date=date.today() + timedelta(days=60),
            end_date=date.today() + timedelta(days=74),
            duration_days=Decimal("15"),
            status="valide",
        ))

        # --- Cas 2 : Thomas MARTIN (6j Conges) => CRITIQUE ---
        db.add(LeaveRequest(
            id=str(uuid4()),
            employee_id=emps["EMP-7719"].id,
            leave_type="Congé payé",
            start_date=date.today().replace(day=10),
            end_date=date.today().replace(day=15),
            duration_days=Decimal("6"),
            status="valide",
        ))

        # --- Cas 3 : Marie DUPONT (7j Conges) => PREVENTIF ---
        db.add(LeaveRequest(
            id=str(uuid4()),
            employee_id=emps["EMP-8492"].id,
            leave_type="Congé payé",
            start_date=date.today().replace(day=20),
            end_date=date.today().replace(day=26),
            duration_days=Decimal("7"),
            status="valide",
        ))

        # --- Cas 4 : Robert STEFAN (2j RTT) => sous le seuil ---
        db.add(LeaveRequest(
            id=str(uuid4()),
            employee_id=emps["EMP-6540"].id,
            leave_type="RTT",
            start_date=date.today().replace(day=5),
            end_date=date.today().replace(day=6),
            duration_days=Decimal("2"),
            status="valide",
        ))

        # --- Cas 5 : Lucas PETIT (1j en attente, pour test validation) ---
        db.add(LeaveRequest(
            id=str(uuid4()),
            employee_id=emps["EMP-4432"].id,
            leave_type="Congé payé",
            start_date=date.today() + timedelta(days=30),
            end_date=date.today() + timedelta(days=30),
            duration_days=Decimal("1"),
            status="en_attente",
        ))

        # --- Cas 6 : Alexandre MARTIN (3j Maladie) ---
        db.add(LeaveRequest(
            id=str(uuid4()),
            employee_id=emps["EMP-5521"].id,
            leave_type="Maladie",
            start_date=date.today().replace(day=3),
            end_date=date.today().replace(day=5),
            duration_days=Decimal("3"),
            status="valide",
        ))
        
        # ========== HISTORIQUE DES ANCIENS EMPLOYES ==========
        # Permet au modele ML d'apprendre une VRAIE correlation
        # entre historique RH et DEPART A RISQUE.

        # Pierre DURAND : BURNOUT - 10j Maladie + 1 alerte => RISQUE
        db.add(LeaveRequest(
            id=str(uuid4()),
            employee_id=emps["EMP-8001"].id,
            leave_type="Maladie",
            start_date=date(2024, 9, 1),
            end_date=date(2024, 9, 10),
            duration_days=Decimal("10"),
            status="valide",
        ))
        db.add(Alert(
            employee_id=emps["EMP-8001"].id,
            type="absences_repetees",
            severity="critique",
            title="Absences repetees - Pierre DURAND",
            description="10 jours d'absence (seuil : 5)",
            risk_score=Decimal("85"),
            status="active",
            period_month=date(2024, 9, 1),
        ))

        # David LEROY : DEPRIME - 12j CP => RISQUE
        db.add(LeaveRequest(
            id=str(uuid4()),
            employee_id=emps["EMP-8003"].id,
            leave_type="Congé payé",
            start_date=date(2024, 7, 1),
            end_date=date(2024, 7, 12),
            duration_days=Decimal("12"),
            status="valide",
        ))

        # Karim BENALI : BURNOUT - 8j Maladie + 1 alerte => RISQUE
        db.add(LeaveRequest(
            id=str(uuid4()),
            employee_id=emps["EMP-8005"].id,
            leave_type="Maladie",
            start_date=date(2024, 5, 1),
            end_date=date(2024, 5, 8),
            duration_days=Decimal("8"),
            status="valide",
        ))
        db.add(Alert(
            employee_id=emps["EMP-8005"].id,
            type="absences_repetees",
            severity="critique",
            title="Absences repetees - Karim BENALI",
            description="8 jours d'absence (seuil : 5)",
            risk_score=Decimal("75"),
            status="active",
            period_month=date(2024, 5, 1),
        ))

        # Julie MOREAU : DEMOTIVATION - 5j RTT => RISQUE
        db.add(LeaveRequest(
            id=str(uuid4()),
            employee_id=emps["EMP-8002"].id,
            leave_type="RTT",
            start_date=date(2024, 3, 15),
            end_date=date(2024, 3, 20),
            duration_days=Decimal("5"),
            status="valide",
        ))

        # Anne ROUSSEAU : RETRAITE - aucune absence => DEPART NORMAL (label 0)
        # (pas de conge ajoute - depart naturel)

        # Sophie GIRARD : FIN CDD - 3j RTT => DEPART NORMAL (label 0)
        db.add(LeaveRequest(
            id=str(uuid4()),
            employee_id=emps["EMP-8006"].id,
            leave_type="RTT",
            start_date=date(2024, 10, 1),
            end_date=date(2024, 10, 3),
            duration_days=Decimal("3"),
            status="valide",
        ))

        print("[OK] Historique RH des anciens employes cree (4 risques, 2 normaux)")

        print("[OK] 6 conges crees (3 devraient generer des alertes)")

        # ========== OFFRE D'EMPLOI 1 ==========
        offer1 = JobOffer(
            id=str(uuid4()),
            reference="OFF-2025-001",
            title="Developpeur Senior (Python / React)",
            department_id=depts["RD"].id,
            contract_type="CDI",
            location="Paris 9e - Hybride",
            salary_min=Decimal("55000"),
            salary_max=Decimal("68000"),
            experience_level="Senior",
            hard_skills=["Python", "React", "FastAPI", "Docker"],
            soft_skills=["Leadership", "Communication", "Autonomie"],
            status="active",
            priority="prioritaire",
        )
        db.add(offer1)
        db.flush()

        # ========== OFFRE D'EMPLOI 2 ==========
        offer2 = JobOffer(
            id=str(uuid4()),
            reference="OFF-2025-002",
            title="Chef de Produit (Product Manager)",
            department_id=depts["RD"].id,
            contract_type="CDI",
            location="Paris (Siège) - Hybride",
            salary_min=Decimal("65000"),
            salary_max=Decimal("80000"),
            experience_level="Confirmé-Senior",
            hard_skills=["Agile", "Scrum", "Jira", "Product Management"],
            soft_skills=["Leadership", "Communication", "Vision produit"],
            status="en_entretien",
            priority="normal",
        )
        db.add(offer2)
        db.flush()

        # ========== OFFRE D'EMPLOI 3 ==========
        offer3 = JobOffer(
            id=str(uuid4()),
            reference="OFF-2025-003",
            title="Commercial B2B / Grands Comptes",
            department_id=depts["COM"].id,
            contract_type="CDI",
            location="Paris - Déplacements",
            salary_min=Decimal("45000"),
            salary_max=Decimal("70000"),
            experience_level="Confirmé",
            hard_skills=["Vente B2B", "Négociation", "CRM", "Prospection"],
            soft_skills=["Relation client", "Persuasion", "Autonomie"],
            status="active",
            priority="prioritaire",
        )
        db.add(offer3)
        db.flush()
        print("[OK] 3 offres creees")

        # ========== CANDIDATS OFFRE 1 (Developpeur Senior) ==========
        candidates_offer1 = [
            ("Alexandre", "MARTIN", 96, ["Python", "React", "FastAPI", "Docker"], "Developpeur Senior"),
            ("Sophie", "BERNARD", 94, ["Python", "Django", "PostgreSQL"], "Developpeur Fullstack"),
            ("Julien", "VASSEUR", 78, ["Python", "Vue.js", "Docker"], "Developpeur Frontend"),
            ("Thomas", "DUBOIS", 82, ["Python", "FastAPI", "PostgreSQL"], "Backend Developer"),
            ("Camille", "RENOIR", 75, ["React", "TypeScript", "Node.js"], "Frontend Developer"),
            ("Nicolas", "PETIT", 88, ["Python", "Docker", "AWS"], "DevOps Engineer"),
            ("Laura", "DUPUIS", 65, ["Python", "Django", "Redis"], "Python Developer"),
            ("Hugo", "MARTIN", 71, ["React", "Redux", "GraphQL"], "React Developer"),
            ("Emma", "LEFEVRE", 84, ["Python", "FastAPI", "Docker"], "Fullstack Developer"),
            ("Lucas", "BERNARD", 69, ["Python", "PostgreSQL", "CI/CD"], "Backend Developer"),
            ("Chloe", "DURAND", 91, ["Python", "React", "AWS"], "Senior Developer"),
            ("Antoine", "MOREAU", 77, ["Python", "Django", "Docker"], "Python Developer"),
        ]

        for fn, ln, score, skills, title in candidates_offer1:
            c = Candidate(
                id=str(uuid4()),
                first_name=fn,
                last_name=ln,
                email=f"{fn.lower()}.{ln.lower()}@candidat.fr",
                current_title=title,
                skills=skills,
                years_experience=5,
                match_score=Decimal(str(score)),
                ai_summary=f"Profil avec 5 ans d'experience sur {', '.join(skills[:3])}",
            )
            db.add(c)
            db.flush()

            db.add(Application(
                id=str(uuid4()),
                candidate_id=c.id,
                job_offer_id=offer1.id,
                match_score=Decimal(str(score)),
                status="preselectionne" if score >= 80 else "recu",
            ))

        # ========== CANDIDATS OFFRE 2 (Chef de Produit) ==========
        candidates_offer2 = [
            ("Marie", "LEROY", 85, ["Agile", "Scrum", "Jira"], "Product Manager"),
            ("Pierre", "MOREL", 72, ["Product Management", "Roadmap", "KPI"], "Senior PM"),
            ("Isabelle", "BERNARD", 78, ["Agile", "UX Design", "User Research"], "Product Owner"),
            ("Jean", "DUPONT", 68, ["Scrum", "Jira", "Confluence"], "Agile Coach"),
            ("Sophie", "MARTIN", 74, ["Product Management", "Strategy", "Analytics"], "Product Lead"),
            ("Luc", "RENOIR", 81, ["Agile", "Scrum", "Product Strategy"], "Senior Product Manager"),
            ("Claire", "PETIT", 65, ["Jira", "Roadmap", "Stakeholder Management"], "Product Manager"),
            ("Marc", "DURAND", 70, ["Product Management", "UX", "Agile"], "Product Owner"),
        ]

        for fn, ln, score, skills, title in candidates_offer2:
            c = Candidate(
                id=str(uuid4()),
                first_name=fn,
                last_name=ln,
                email=f"{fn.lower()}.{ln.lower()}@candidat.fr",
                current_title=title,
                skills=skills,
                years_experience=6,
                match_score=Decimal(str(score)),
                ai_summary=f"Profil avec 6 ans d'experience en product management",
            )
            db.add(c)
            db.flush()

            db.add(Application(
                id=str(uuid4()),
                candidate_id=c.id,
                job_offer_id=offer2.id,
                match_score=Decimal(str(score)),
                status="preselectionne" if score >= 80 else "recu",
            ))

        # ========== CANDIDATS OFFRE 3 (Commercial B2B) ==========
        candidates_offer3 = [
            ("Francois", "LEFEVRE", 92, ["Vente B2B", "Négociation", "CRM"], "Senior Account Executive"),
            ("Caroline", "MARTIN", 95, ["Vente B2B", "Grands Comptes", "Prospection"], "Key Account Manager"),
            ("David", "BERNARD", 88, ["Vente B2B", "CRM", "Closing"], "Sales Executive"),
            ("Nathalie", "DUPONT", 90, ["Vente B2B", "Négociation", "Relation client"], "Business Developer"),
            ("Stephane", "RENOIR", 85, ["Vente B2B", "Prospection", "Pipeline"], "Sales Representative"),
            ("Celine", "PETIT", 93, ["Vente B2B", "Grands Comptes", "Contract"], "Senior Sales"),
            ("Philippe", "MOREAU", 87, ["Vente B2B", "CRM", "Account Management"], "Account Manager"),
            ("Valerie", "DURAND", 91, ["Vente B2B", "Négociation", "Closing"], "Sales Director"),
            ("Laurent", "LEFEVRE", 89, ["Vente B2B", "Prospection", "Lead Generation"], "Business Development"),
            ("Anne", "MARTIN", 94, ["Vente B2B", "Grands Comptes", "Strategic Sales"], "VP Sales"),
            ("Christophe", "BERNARD", 86, ["Vente B2B", "CRM", "Sales Operations"], "Sales Manager"),
            ("Martine", "DUPONT", 82, ["Vente B2B", "Négociation", "Customer Success"], "Account Executive"),
            ("Jean-Pierre", "RENOIR", 96, ["Vente B2B", "Grands Comptes", "Enterprise Sales"], "Enterprise Account Manager"),
            ("Dominique", "PETIT", 84, ["Vente B2B", "Prospection", "Business Development"], "Sales Consultant"),
            ("Patricia", "MOREAU", 90, ["Vente B2B", "Négociation", "Contract Negotiation"], "Senior Sales Executive"),
        ]

        for fn, ln, score, skills, title in candidates_offer3:
            c = Candidate(
                id=str(uuid4()),
                first_name=fn,
                last_name=ln,
                email=f"{fn.lower()}.{ln.lower()}@candidat.fr",
                current_title=title,
                skills=skills,
                years_experience=7,
                match_score=Decimal(str(score)),
                ai_summary=f"Profil avec 7 ans d'experience en vente B2B",
            )
            db.add(c)
            db.flush()

            db.add(Application(
                id=str(uuid4()),
                candidate_id=c.id,
                job_offer_id=offer3.id,
                match_score=Decimal(str(score)),
                status="preselectionne" if score >= 80 else "recu",
            ))

        total_candidates = len(candidates_offer1) + len(candidates_offer2) + len(candidates_offer3)
                # ========== RELATIONS ENTRE EMPLOYES ==========
        from app.models.relation import EmployeeRelation

        relations_data = [
            # (employe A, employe B, type, notes)
            ("EMP-7719", "EMP-9128", "ami", "Souvent en pause café ensemble"),
            ("EMP-7719", "EMP-5598", "ancien_collegue", "Ont travaillé chez OVH"),
            ("EMP-8492", "EMP-6540", "couple", "Déclaration PACS 2024"),
            ("EMP-5521", "EMP-4432", "mentor", "Alexandre forme Lucas"),
            ("EMP-001",  "EMP-5521", "famille", "Cousins"),
        ]

        for code_a, code_b, rtype, notes in relations_data:
            a, b = sorted([str(emps[code_a].id), str(emps[code_b].id)])
            db.add(EmployeeRelation(
                id=str(uuid4()),
                employee_a_id=a,
                employee_b_id=b,
                relation_type=rtype,
                notes=notes,
            ))

        print(f"[OK] {len(relations_data)} relations creees")

        print("Seed termine avec succes !")
        
        print(f"[OK] {total_candidates} candidats crees pour les 3 offres")

        print("\nSeed termine avec succes !")


if __name__ == "__main__":
    seed()