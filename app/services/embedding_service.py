"""Service d'embeddings IA (sentence-transformers).

Utilise un modele multilingue pour transformer du texte en vecteurs
semantiques, permettant des comparaisons de sens (pas juste de mots).

Cas d'usage :
- Similarite entre CVs et offres
- Similarite entre profils employes (SmartMatch)
- Recherche semantique
"""
import os
from pathlib import Path
from typing import List

import numpy as np

# Cache le modele en memoire
_MODEL = None
_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


def _get_model():
    """Modele IA DESACTIVE.

    L'IA semantique est desactivee car le chargement de PyTorch
    echoue sur certaines configurations Windows (erreur DLL c10.dll).

    Pour reactiver : decommenter le code ci-dessous et installer :
        pip install sentence-transformers
    """
    global _MODEL
    if _MODEL is None:
        # ⭐ DESACTIVE : on retourne False immediatement
        print("[EmbeddingService] IA semantique DESACTIVEE (mode fallback)")
        _MODEL = False

        # ============ POUR REACTIVER PLUS TARD ============
        # Decommenter le bloc ci-dessous :
        #
        # try:
        #     import torch
        #     from sentence_transformers import SentenceTransformer
        #     print(f"[EmbeddingService] Torch {torch.__version__} charge")
        #     _MODEL = SentenceTransformer(_MODEL_NAME)
        #     print("[EmbeddingService] Modele charge.")
        # except Exception as e:
        #     print(f"[EmbeddingService] IA non disponible : {e}")
        #     _MODEL = False

    return _MODEL if _MODEL else None


class EmbeddingService:
    """Service d'embeddings semantiques."""

    def __init__(self):
        self._model = None  # charge a la demande

    def _ensure_model(self):
        if self._model is None:
            self._model = _get_model()
        return self._model is not None

    # =====================================================
    # ENCODAGE
    # =====================================================
    def encode(self, text: str) -> np.ndarray | None:
        """Encode un texte en vecteur (384 dimensions).

        Retourne None si le modele n'est pas dispo.
        """
        if not text or not text.strip():
            return None

        if not self._ensure_model():
            return None

        try:
            emb = self._model.encode(
                text,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )
            return emb
        except Exception as e:
            print(f"[EmbeddingService] Erreur encodage : {e}")
            return None

    def encode_batch(self, texts: List[str]) -> np.ndarray | None:
        """Encode plusieurs textes en une fois (plus rapide)."""
        if not texts:
            return None

        if not self._ensure_model():
            return None

        try:
            embs = self._model.encode(
                texts,
                convert_to_numpy=True,
                normalize_embeddings=True,
                batch_size=8,
                show_progress_bar=False,
            )
            return embs
        except Exception as e:
            print(f"[EmbeddingService] Erreur batch : {e}")
            return None

    # =====================================================
    # SIMILARITE
    # =====================================================
    def similarity(self, text_a: str, text_b: str) -> float:
        """Retourne la similarite cosinus entre 2 textes (0-100)."""
        emb_a = self.encode(text_a)
        emb_b = self.encode(text_b)

        if emb_a is None or emb_b is None:
            return 0.0

        # Similarite cosinus (vecteurs normalises => dot product)
        score = float(np.dot(emb_a, emb_b))
        return round(max(0.0, min(1.0, score)) * 100, 2)

    def similarity_batch(self, target: str, candidates: List[str]) -> List[float]:
        """Similarite entre un texte cible et plusieurs candidats."""
        if not candidates:
            return []

        target_emb = self.encode(target)
        if target_emb is None:
            return [0.0] * len(candidates)

        cand_embs = self.encode_batch(candidates)
        if cand_embs is None:
            return [0.0] * len(candidates)

        # Dot product (cosine car vecteurs normalises)
        scores = np.dot(cand_embs, target_emb)
        return [round(max(0.0, min(1.0, float(s))) * 100, 2) for s in scores]

    # =====================================================
    # HELPERS SPECIFIQUES
    # =====================================================
    def cv_offer_match(self, cv_text: str, offer_description: str) -> float:
        """Similarite entre un CV et une offre (0-100)."""
        if not cv_text or not offer_description:
            return 0.0

        # On enrichit avec du contexte pour ameliorer l'encodage
        cv_enriched = f"CV professionnel : {cv_text}"
        offer_enriched = f"Offre d'emploi : {offer_description}"

        return self.similarity(cv_enriched, offer_enriched)

    def profile_similarity(self, profile_a: dict, profile_b: dict) -> float:
        """Similarite semantique entre 2 profils employes.

        Args:
            profile_a / profile_b : dict avec 'name', 'job_title',
                                    'department', 'disc'

        Returns:
            Score 0-100.
        """
        def build_text(p):
            parts = [
                p.get("job_title", ""),
                p.get("department", ""),
                f"DISC {p.get('disc', '')}" if p.get("disc") else "",
            ]
            return " | ".join([x for x in parts if x])

        text_a = build_text(profile_a)
        text_b = build_text(profile_b)

        if not text_a or not text_b:
            return 50.0

        return self.similarity(text_a, text_b)

    def is_available(self) -> bool:
        """Indique si le modele est disponible."""
        return self._ensure_model()