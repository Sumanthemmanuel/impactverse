import logging
import threading
from typing import List
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self._model = None
        self._lock = threading.Lock()
        self._model_name = getattr(settings, "EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

    def _load_model(self):
        if self._model is None:
            with self._lock:
                if self._model is None:
                    try:
                        from sentence_transformers import SentenceTransformer
                        self._model = SentenceTransformer(self._model_name)
                        logger.info(f"Loaded embedding model: {self._model_name}")
                    except ImportError:
                        logger.warning("sentence-transformers not installed. Returning zero vectors.")
                        self._model = "mock"
                    except Exception as e:
                        logger.error(f"Error loading embedding model: {e}")
                        self._model = "mock"

    def get_embedding(self, text: str) -> List[float]:
        self._load_model()
        if self._model == "mock":
            return [0.0] * 384
        return self._model.encode(text).tolist()

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        self._load_model()
        if self._model == "mock":
            return [[0.0] * 384 for _ in texts]
        return self._model.encode(texts).tolist()

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
