from __future__ import annotations

from dataclasses import dataclass
from typing import List
import requests


@dataclass(frozen=True)
class OllamaEmbeddingClient:
    base_url: str = "http://127.0.0.1:11434"
    model: str = "nomic-embed-text"
    timeout_sec: int = 60

    def embed(self, text: str) -> List[float]:
        text = (text or "").strip()
        if not text:
            return []

        url = f"{self.base_url.rstrip('/')}/api/embeddings"
        payload = {"model": self.model, "prompt": text}

        resp = requests.post(url, json=payload, timeout=self.timeout_sec)
        if resp.status_code != 200:
            raise RuntimeError(f"Ollama embeddings HTTP {resp.status_code}: {resp.text}")

        data = resp.json()
        emb = data.get("embedding")
        if not isinstance(emb, list) or not emb:
            raise RuntimeError(f"Ollama embeddings returned invalid embedding: {data}")

        return emb
