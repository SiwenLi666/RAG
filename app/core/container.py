from app.retrieval.factory import create_retriever
from app.index.index_memory import IndexMemory   # ✅ FIXED PATH
from app.memory.session_memory import SessionMemory
from app.ai.translator import Translator


index_memory = IndexMemory()
retriever = None
memory = SessionMemory()
translator = Translator()
