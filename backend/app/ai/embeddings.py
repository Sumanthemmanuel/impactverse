import hashlib
import logging
import math
import re
import threading
from typing import List
from app.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Generate 384-dimensional embeddings with a reliable offline fallback.

    ``sentence-transformers`` is used whenever the configured model can be
    loaded.  Development, tests, and offline demos must not silently receive
    zero vectors, however: zero vectors make every similarity score zero and
    make institution assignment impossible.  The fallback is a deterministic
    hashed lexical embedding.  It is not a replacement for a trained model,
    but preserves meaningful token-overlap ranking until the model is ready.
    """

    DIMENSIONS = 384

    def __init__(self):
        self._model = None
        self._lock = threading.Lock()
        self._model_name = getattr(settings, "EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
        self._configured_device = getattr(settings, "EMBEDDING_DEVICE", "auto").lower()
        self._device = "cpu"
        self._batch_size = max(1, getattr(settings, "EMBEDDING_BATCH_SIZE", 16))
        self._using_fallback = False

    @property
    def method(self) -> str:
        """The embedding implementation currently serving requests."""
        self._load_model()
        return "sentence-transformers" if not self._using_fallback else "hashed-lexical-fallback"

    @property
    def device(self) -> str:
        """The selected model device after model initialization."""
        self._load_model()
        return self._device

    def _select_device(self) -> str:
        if self._configured_device in {"cpu", "cuda"}:
            return self._configured_device
        try:
            import torch

            return "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            return "cpu"

    def _load_model(self):
        if self._model is None:
            with self._lock:
                if self._model is None:
                    try:
                        from sentence_transformers import SentenceTransformer
                        self._device = self._select_device()
                        self._model = SentenceTransformer(self._model_name, device=self._device)
                        logger.info("Loaded embedding model %s on %s", self._model_name, self._device)
                    except ImportError:
                        logger.warning("sentence-transformers not installed; using hashed lexical embeddings.")
                        self._model = "fallback"
                        self._device = "cpu"
                        self._using_fallback = True
                    except Exception as e:
                        logger.warning("Unable to load embedding model; using hashed lexical embeddings: %s", e)
                        self._model = "fallback"
                        self._device = "cpu"
                        self._using_fallback = True

    @classmethod
    def _fallback_embedding(cls, text: str) -> List[float]:
        """Return a stable, normalized bag-of-words-and-bigrams embedding."""
        tokens = re.findall(r"[a-z0-9]+", (text or "").lower())
        if not tokens:
            return [0.0] * cls.DIMENSIONS

        features = tokens + [f"{left}_{right}" for left, right in zip(tokens, tokens[1:])]
        vector = [0.0] * cls.DIMENSIONS
        for feature in features:
            digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
            index = int.from_bytes(digest, "big") % cls.DIMENSIONS
            vector[index] += 1.0

        norm = math.sqrt(sum(value * value for value in vector))
        return [value / norm for value in vector] if norm else vector

    def get_embedding(self, text: str) -> List[float]:
        self._load_model()
        if self._model == "fallback":
            return self._fallback_embedding(text)
        return self._model.encode(text, normalize_embeddings=True, show_progress_bar=False).tolist()

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        self._load_model()
        if self._model == "fallback":
            return [self._fallback_embedding(text) for text in texts]
        return self._model.encode(
            texts,
            batch_size=self._batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).tolist()

    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        if not embedding1 or not embedding2:
            return 0.0
        import math
        dot_product = sum(a * b for a, b in zip(embedding1, embedding2))
        norm_a = math.sqrt(sum(a * a for a in embedding1))
        norm_b = math.sqrt(sum(b * b for b in embedding2))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

embedding_service = EmbeddingService()
