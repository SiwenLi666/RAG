from __future__ import annotations
from typing import List
from sentence_transformers import SentenceTransformer
import torch
import numpy as np


class LocalEmbeddingClient:

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str = "cpu",   # 👈 NEW PARAM
    ):
        self.device = device
        print(f"[Embedding] Using device: {self.device}")

        self.model = SentenceTransformer(model_name, device=self.device)
        self.model.eval()

    # --------------------------------------------------------
    # Batch embedding (FAST PATH)
    # --------------------------------------------------------

    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 256,
    ) -> np.ndarray:

        if not texts:
            return np.array([])

        with torch.inference_mode():
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )

        return embeddings  # numpy array

    # --------------------------------------------------------
    # Single embedding (rare use)
    # --------------------------------------------------------

    def embed(self, text: str) -> List[float]:

        with torch.inference_mode():
            emb = self.model.encode(
                text,
                convert_to_numpy=True,
                normalize_embeddings=True,
            )

        return emb.tolist()
