from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional, Any
import json
import numpy as np
import time

try:
    import faiss
except Exception:
    faiss = None


@dataclass
class VectorIndexArtifacts:
    embeddings_path: Path
    faiss_index_path: Path
    id_map_path: Path


class VectorIndex:

    def __init__(self, client, artifacts: VectorIndexArtifacts):
        if faiss is None:
            raise RuntimeError("faiss not installed")

        self.client = client
        self.artifacts = artifacts

        self._index = None
        self._id_map: List[str] = []
        self._dim: Optional[int] = None

    @property
    def is_ready(self) -> bool:
        return self._index is not None and self._dim is not None

    # --------------------------------------------------------
    # Resume Support
    # --------------------------------------------------------

    def load_if_exists(self) -> bool:
        a = self.artifacts

        if not (a.faiss_index_path.exists() and a.id_map_path.exists()):
            return False

        print("Loading existing FAISS index...")
        self._index = faiss.read_index(str(a.faiss_index_path))

        with a.id_map_path.open("r", encoding="utf-8") as f:
            self._id_map = json.load(f)

        self._dim = self._index.d
        print(f"Loaded {len(self._id_map)} vectors.")
        return True

    # --------------------------------------------------------
    # GPU Optimized Builder
    # --------------------------------------------------------

    def build_and_save(
        self,
        documents: List[Any],
        text_getter,
        id_getter,
        force_rebuild: bool = False,
        batch_size: int = 256,
        max_chars: int = 2000,
    ) -> None:

        a = self.artifacts
        a.faiss_index_path.parent.mkdir(parents=True, exist_ok=True)

        if not force_rebuild and self.load_if_exists():
            start_index = len(self._id_map)
        else:
            print("Starting fresh GPU index build...")
            self._id_map = []
            self._index = None
            self._dim = None
            start_index = 0

        total_docs = len(documents)
        start_time = time.time()

        print(f"Total documents: {total_docs}")
        print(f"Resuming from document index: {start_index}")

        for i in range(start_index, total_docs, batch_size):

            batch_docs = documents[i : i + batch_size]

            texts = []
            ids_batch = []

            for doc in batch_docs:

                doc_id = str(id_getter(doc))
                text = str(text_getter(doc) or "").strip()

                if not text:
                    continue

                if len(text) > max_chars:
                    text = text[:max_chars]

                texts.append(text)
                ids_batch.append(doc_id)

            if not texts:
                continue

            try:
                X = self.client.embed_batch(texts, batch_size=batch_size)
            except Exception as e:
                print(f"[Batch Skip] {str(e)[:120]}")
                continue

            if self._dim is None:
                self._dim = X.shape[1]
                self._index = faiss.IndexFlatIP(self._dim)

            self._index.add(X)
            self._id_map.extend(ids_batch)

            # Save checkpoint
            faiss.write_index(self._index, str(a.faiss_index_path))

            with a.id_map_path.open("w", encoding="utf-8") as f:
                json.dump(self._id_map, f, ensure_ascii=False)

            elapsed = time.time() - start_time
            processed = len(self._id_map)
            speed = processed / elapsed if elapsed > 0 else 0
            eta = (total_docs - processed) / speed if speed > 0 else 0

            print(
                f"[Checkpoint] {processed}/{total_docs} "
                f"({processed/total_docs:.2%}) | "
                f"Speed: {speed:.2f}/s | "
                f"ETA: {eta/60:.2f} min"
            )

        print("Vector index build complete.")
        print(f"Final vector count: {len(self._id_map)}")

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    def search(self, query: str, top_k: int) -> List[Tuple[str, float]]:

        if not self.is_ready:
            raise RuntimeError("VectorIndex not ready")

        query = (query or "").strip()
        if not query:
            return []

        q = self.client.embed_batch([query], batch_size=1)

        faiss.normalize_L2(q)
        D, I = self._index.search(q, top_k)

        results = []
        for idx, score in zip(I[0], D[0]):
            if idx < 0 or idx >= len(self._id_map):
                continue
            results.append((self._id_map[idx], float(score)))

        return results
