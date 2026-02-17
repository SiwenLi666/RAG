from app.retrieval.bm25_retriever import BM25Retriever


def create_retriever(index_memory):
    retriever = BM25Retriever(index_memory)
    retriever.build()  # 🔥 THIS LINE IS CRITICAL
    return retriever
