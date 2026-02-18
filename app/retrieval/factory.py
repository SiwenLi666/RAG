from __future__ import annotations

from pathlib import Path

from app.core.config import RETRIEVER_TYPE

from app.retrieval.local_embedding_client import LocalEmbeddingClient
from app.retrieval.vector_index import VectorIndex, VectorIndexArtifacts
from app.retrieval.vector_retriever import VectorRetriever
from app.retrieval.bm25_retriever import BM25Retriever
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.router_retriever import RouterRetriever


def create_retriever(
    index_memory,
    data_dir: Path,
    default_mode: str | None = None,
    embed_model: str = "all-MiniLM-L6-v2",
) -> RouterRetriever:

    mode = (default_mode or RETRIEVER_TYPE or "hybrid").strip().lower()

    # -------------------------------------------------
    # Load documents
    # -------------------------------------------------
    if hasattr(index_memory, "documents"):
        docs = getattr(index_memory, "documents") or []
    elif hasattr(index_memory, "_documents"):
        docs = getattr(index_memory, "_documents") or []
    elif hasattr(index_memory, "get_documents"):
        docs = index_memory.get_documents()
    elif hasattr(index_memory, "all"):
        docs = index_memory.all()
    else:
        raise RuntimeError(
            "IndexMemory does not expose documents "
            "(documents/_documents/get_documents/all)."
        )

    bm25 = None
    vector = None
    hybrid = None

    # -------------------------------------------------
    # BM25 Mode
    # -------------------------------------------------
    if mode == "bm25":
        bm25 = BM25Retriever(index_memory=index_memory)
        bm25.build()

    # -------------------------------------------------
    # Vector Mode
    # -------------------------------------------------
    elif mode == "vector":
        client = LocalEmbeddingClient(
            model_name=embed_model,
            device="cpu",
        )

        artifacts = VectorIndexArtifacts(
            embeddings_path=data_dir / "embeddings.npy",
            faiss_index_path=data_dir / "faiss.index",
            id_map_path=data_dir / "id_map.json",
        )

        vindex = VectorIndex(client=client, artifacts=artifacts)

        vindex.build_and_save(
            documents=docs,
            text_getter=lambda d: getattr(d, "text", "") or "",
            id_getter=lambda d: getattr(d, "id", ""),
            force_rebuild=False,
            batch_size=256,
            max_chars=2000,
        )

        vector = VectorRetriever(index_memory=index_memory, vector_index=vindex)

    # -------------------------------------------------
    # Hybrid Mode
    # -------------------------------------------------
    elif mode == "hybrid":
        # Build BM25
        bm25 = BM25Retriever(index_memory=index_memory)
        bm25.build()

        # Build Vector
        client = LocalEmbeddingClient(
            model_name=embed_model,
            device="cpu",
        )

        artifacts = VectorIndexArtifacts(
            embeddings_path=data_dir / "embeddings.npy",
            faiss_index_path=data_dir / "faiss.index",
            id_map_path=data_dir / "id_map.json",
        )

        vindex = VectorIndex(client=client, artifacts=artifacts)

        vindex.build_and_save(
            documents=docs,
            text_getter=lambda d: getattr(d, "text", "") or "",
            id_getter=lambda d: getattr(d, "id", ""),
            force_rebuild=False,
            batch_size=256,
            max_chars=2000,
        )

        vector = VectorRetriever(index_memory=index_memory, vector_index=vindex)
        hybrid = HybridRetriever(bm25=bm25, vector=vector)

    else:
        raise ValueError(
            f"Invalid RETRIEVER_TYPE '{mode}'. Use bm25 | vector | hybrid."
        )

    return RouterRetriever(
        bm25=bm25,
        vector=vector,
        hybrid=hybrid,
        default_mode=mode,
    )
