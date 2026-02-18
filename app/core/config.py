from pathlib import Path


# --------------------------------------------------
# Engine Configuration (Genre Agnostic)
# --------------------------------------------------

# Domain name registered in DomainRegistry
ACTIVE_DOMAIN = "structured_text"

# Dataset file name inside /data
DATASET_FILE = "20170107-061401-recipeitems.json"

# Retrieval
RETRIEVER_TYPE = "hybrid"  # "hybrid" or "bm25" or "vector"

TOP_K = 20


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
