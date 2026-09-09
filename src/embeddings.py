import os
import numpy as np

class EmbeddingModel:
    def __init__(self, model_name=None):
        self.model_name = model_name or os.getenv('EMBEDDING_MODEL','all-MiniLM-L6-v2')
        self._model = None
    def _load(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model
    def encode(self, texts):
        if isinstance(texts, str): texts = [texts]
        return np.asarray(self._load().encode(texts, normalize_embeddings=True, show_progress_bar=False), dtype='float32')

def cosine_similarity(a,b):
    a,b=np.asarray(a),np.asarray(b)
    denom=np.linalg.norm(a)*np.linalg.norm(b)
    return float(np.dot(a,b)/denom) if denom else 0.0
