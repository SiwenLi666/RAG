from sentence_transformers import SentenceTransformer
from typing import List
import torch


class GPUEmbeddingClient:
    def __init__(self, model_name: str = "nomic-ai/nomic-embed-text-v1"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[Embedding] Using device: {self.device}")
        self.model = SentenceTransformer(model_name, device=self.device)

    def embed_batch(self, texts: List[str], batch_size: int = 128) -> List[List[float]]:
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embeddings.tolist()
