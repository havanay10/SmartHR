"""Service d'analyse IA via LLM (Groq API).

Remplace les embeddings par des appels a un LLM distant.
Avantages :
- Pas de DLL PyTorch
- Plus puissant (analyse contextuelle)
- Reponses en JSON structure

Gratuit : 14400 requetes/jour sur Groq.
"""
import json
import re
from typing import Optional

import httpx

from config import settings


class LLMService:
    """Service d'appel au LLM (Groq API compatible OpenAI)."""

    GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.enabled = settings.LLM_ENABLED and bool(self.api_key)
        self.model = settings.LLM_MODEL
        self.timeout = 30.0

        if not self.enabled:
            print("[LLMService] IA desactivee (pas de cle API)")
        else:
            print(f"[LLMService] Pret avec modele {self.model}")

    def is_available(self) -> bool:
        """Verifie si le service est pret."""
        return self.enabled

    # =====================================================
    # APPEL BAS NIVEAU
    # =====================================================
    def _call(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1500,
    ) -> Optional[str]:
        """Appel brut a l'API Groq.

        Returns:
            Texte de reponse ou None en cas d'erreur.
        """
        if not self.enabled:
            return None

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},  # JSON garanti
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(self.GROQ_URL, headers=headers, json=payload)
                if resp.status_code != 200:
                    print(f"[LLMService] Erreur HTTP {resp.status_code} : {resp.text[:200]}")
                    return None

                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return content

        except httpx.TimeoutException:
            print("[LLMService] Timeout de la requete")
            return None
        except Exception as e:
            print(f"[LLMService] Erreur : {e}")
            return None

    def _parse_json(self, text: str) -> Optional[dict]:
        """Parse le JSON retourne par le LLM (robuste)."""
        if not text:
            return None

        # Essaie de parser directement
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Cherche un objet JSON dans le texte
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        return None

    # =====================================================
    # ANALYSE DE CV
    # =====================================================
    def analyze_cv(
        self,
        cv_text: str,
        offer_title: str,
        offer_skills: list[str],
        offer_description: str = "",
    ) -> Optional[dict]:
        """Analyse un CV par rapport a une offre.

        Returns:
            {
                "score": int (0-100),
                "matched_skills": [...],
                "missing_skills": [...],
                "years_experience": int,
                "candidate_summary": "...",
                "strengths": [...],
                "weaknesses": [...],
                "recommendation": "...",
                "justification": "..."
            }
        """
        if not self.enabled:
            return None

        system_prompt = """Tu es un expert RH specialise dans l'analyse de CV.
Tu analyses objectivement les candidats par rapport a une offre d'emploi.

Tu dois TOUJOURS retourner un JSON valide avec cette structure exacte :
{
    "score": 85,
    "matched_skills": ["Python", "React"],
    "missing_skills": ["Kubernetes"],
    "years_experience": 5,
    "candidate_summary": "Resume en 1-2 phrases",
    "strengths": ["Force 1", "Force 2"],
    "weaknesses": ["Faiblesse 1"],
    "recommendation": "Fortement recommande / A considerer / A ecarter",
    "justification": "Explication detaillee du score"
}

Le score est un entier de 0 a 100 base sur :
- Correspondance des competences (50%)
- Annees d'experience (25%)
- Qualite generale du profil (25%)
"""

        user_prompt = f"""Analyse ce CV pour l'offre suivante.

=== OFFRE ===
Titre : {offer_title}
Competences requises : {", ".join(offer_skills) if offer_skills else "Non specifiees"}
Description : {offer_description[:1000] if offer_description else "Non specifiee"}

=== CV DU CANDIDAT ===
{cv_text[:3000]}

Retourne le JSON structure demande."""

        response = self._call(system_prompt, user_prompt, temperature=0.2)
        result = self._parse_json(response)

        if not result:
            return None

        # Validation et nettoyage
        return {
            "score": int(result.get("score", 0)),
            "matched_skills": result.get("matched_skills", []),
            "missing_skills": result.get("missing_skills", []),
            "years_experience": result.get("years_experience", 0),
            "candidate_summary": result.get("candidate_summary", ""),
            "strengths": result.get("strengths", []),
            "weaknesses": result.get("weaknesses", []),
            "recommendation": result.get("recommendation", ""),
            "justification": result.get("justification", ""),
        }

        # =====================================================
    # EXTRACTION DE DONNEES DEPUIS UN CV PDF
    # =====================================================
    def extract_cv_data(self, cv_text: str, mode: str = "candidate") -> Optional[dict]:
        """Extrait les donnees structurees d'un CV.

        Args:
            cv_text: Texte brut du CV
            mode: "candidate" ou "employee"
                  - candidate : extrait les infos pour un candidat
                  - employee : extrait les infos pour un employe

        Returns:
            dict avec les donnees extraites (champs communs + specifiques)
        """
        if not self.enabled:
            return None

        if not cv_text or len(cv_text.strip()) < 50:
            return None

        # Champs supplementaires selon le mode
        extra_fields = ""
        if mode == "employee":
            extra_fields = '''
    "birth_date": "1990-05-15",
    "disc_profile": "C",'''
        else:
            extra_fields = '''
    "disc_profile": "C",'''

        system_prompt = f"""Tu es un expert RH specialise dans le parsing de CV.
Tu extrais les informations structurees d'un CV avec precision.

Retourne TOUJOURS un JSON valide avec EXACTEMENT cette structure :
{{
    "first_name": "Prenom",
    "last_name": "Nom",
    "email": "email@exemple.com",
    "phone": "0612345678",
    "city": "Paris",
    "current_title": "Titre du poste actuel",
    "years_experience": 5,
    "skills": ["Python", "React", "Docker"],
    "languages": ["Francais", "Anglais"],
    "summary": "Resume du profil en 2-3 phrases",
    "strengths": ["Force 1", "Force 2"],
    "weaknesses": ["Point de vigilance"],{extra_fields}
}}

Regles :
- Si une info n'est pas trouvee : "" ou 0 ou []
- skills = competences TECHNIQUES uniquement
- disc_profile : estime (D, I, S ou C) d'apres le style du CV
- birth_date : format YYYY-MM-DD si mentionnee, sinon ""
"""

        user_prompt = f"""Analyse ce CV et extrais les donnees.

=== CV ===
{cv_text[:4000]}

Retourne le JSON structure demande."""

        response = self._call(system_prompt, user_prompt, temperature=0.1)
        result = self._parse_json(response)

        if not result:
            return None

        # Nettoyage
        cleaned = {
            "first_name": (result.get("first_name") or "").strip()[:100],
            "last_name": (result.get("last_name") or "").strip()[:100],
            "email": (result.get("email") or "").strip()[:255],
            "phone": (result.get("phone") or "").strip()[:20],
            "city": (result.get("city") or "").strip()[:100],
            "current_title": (result.get("current_title") or "").strip()[:150],
            "years_experience": int(result.get("years_experience") or 0),
            "skills": result.get("skills", [])[:20],
            "languages": result.get("languages", [])[:5],
            "summary": (result.get("summary") or "").strip()[:500],
            "strengths": result.get("strengths", [])[:5],
            "weaknesses": result.get("weaknesses", [])[:5],
            "disc_profile": (result.get("disc_profile") or "").strip().upper()[:1],
        }

        # Ajout birth_date si mode employee
        if mode == "employee":
            cleaned["birth_date"] = (result.get("birth_date") or "").strip()

        return cleaned
    # =====================================================
    # COMPARAISON DE 2 PROFILS (SmartMatch)
    # =====================================================
    def compare_profiles(
        self,
        profile_a: dict,
        profile_b: dict,
    ) -> Optional[dict]:
        """Compare 2 profils pour SmartMatch.

        Returns:
            {
                "synergy_score": 85,
                "complementarity": "...",
                "potential_conflicts": [...],
                "recommendation": "...",
                "diagnostic": "..."
            }
        """
        if not self.enabled:
            return None

        system_prompt = """Tu es un expert en dynamique d'equipe et psychologie du travail.
Tu evalues la synergie entre 2 collaborateurs.

Retourne TOUJOURS un JSON valide :
{
    "synergy_score": 85,
    "complementarity": "Description de la complementarite",
    "potential_conflicts": ["Conflit 1", "Conflit 2"],
    "recommendation": "Conseil d'association",
    "diagnostic": "Binome hautement complementaire"
}

Score de 0 a 100 base sur :
- Complementarite des competences
- Compatibilite des personnalites
- Equilibre des forces
"""

        user_prompt = f"""Compare ces 2 collaborateurs.

=== COLLABORATEUR A ===
Nom : {profile_a.get('name', 'A')}
Poste : {profile_a.get('job_title', '—')}
Departement : {profile_a.get('department', '—')}
Profil DISC : {profile_a.get('disc', '—')}

=== COLLABORATEUR B ===
Nom : {profile_b.get('name', 'B')}
Poste : {profile_b.get('job_title', '—')}
Departement : {profile_b.get('department', '—')}
Profil DISC : {profile_b.get('disc', '—')}

Retourne le JSON structure demande."""

        response = self._call(system_prompt, user_prompt, temperature=0.3)
        result = self._parse_json(response)

        if not result:
            return None

        return {
            "synergy_score": int(result.get("synergy_score", 50)),
            "complementarity": result.get("complementarity", ""),
            "potential_conflicts": result.get("potential_conflicts", []),
            "recommendation": result.get("recommendation", ""),
            "diagnostic": result.get("diagnostic", ""),
        }