from __future__ import annotations

from pathlib import Path

from app.retrieval.local_embedding_client import LocalEmbeddingClient
from app.retrieval.vector_index import VectorIndex, VectorIndexArtifacts
from app.retrieval.vector_retriever import VectorRetriever
from app.retrieval.bm25_retriever import BM25Retriever
from app.retrieval.hybrid_retriever import HybridRetriever
from app.retrieval.router_retriever import RouterRetriever


def create_retriever(
    index_memory,
    data_dir: Path,
    default_mode: str = "hybrid",
    embed_model: str = "all-MiniLM-L6-v2",
) -> RouterRetriever:

    # -------------------------------------------------
    # Embedding client (FORCE CPU — RTX 5090 unsupported)
    # -------------------------------------------------
    client = LocalEmbeddingClient(
        model_name=embed_model,
        device="cpu",  # 🔴 FORCE CPU
    )

    artifacts = VectorIndexArtifacts(
        embeddings_path=data_dir / "embeddings.npy",
        faiss_index_path=data_dir / "faiss.index",
        id_map_path=data_dir / "id_map.json",
    )

    vindex = VectorIndex(client=client, artifacts=artifacts)

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

    # -------------------------------------------------
    # Build / Load Vector Index
    # -------------------------------------------------
    vindex.build_and_save(
        documents=docs,
        text_getter=lambda d: getattr(d, "text", "") or "",
        id_getter=lambda d: getattr(d, "id", ""),
        force_rebuild=False,
        batch_size=256,     # larger batches for CPU
        max_chars=2000,     # prevent huge text overflow
    )

    # -------------------------------------------------
    # BM25
    # -------------------------------------------------
    bm25 = BM25Retriever(index_memory=index_memory)
    bm25.build()

    # -------------------------------------------------
    # Hybrid Router
    # -------------------------------------------------
    vector = VectorRetriever(index_memory=index_memory, vector_index=vindex)
    hybrid = HybridRetriever(bm25=bm25, vector=vector)

    return RouterRetriever(
        bm25=bm25,
        vector=vector,
        hybrid=hybrid,
        default_mode=default_mode,
    )
