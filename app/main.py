from fastapi import FastAPI
from pathlib import Path

from app.api.routes_search import router as search_router
from app.ingest.loader import load_json_dataset
from app.ingest.normalize import normalize_documents
from app.retrieval.factory import create_retriever
from app.domain.registry import DomainRegistry
import app.core.container as container
from app.core.config import (
    ACTIVE_DOMAIN,
    DATASET_FILE,
    DATA_DIR,
)


# --------------------------------------------------
# App
# --------------------------------------------------

app = FastAPI()

app.include_router(search_router)


# --------------------------------------------------
# Config
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


# --------------------------------------------------
# Startup
# --------------------------------------------------

@app.on_event("startup")
def startup_event():

    dataset_path = DATA_DIR / DATASET_FILE

    print(f"Loading dataset from: {dataset_path}")

    raw_data = load_json_dataset(dataset_path)

    adapter = DomainRegistry.get_adapter(ACTIVE_DOMAIN)

    documents = normalize_documents(raw_data, adapter)

    container.index_memory.load_documents(documents)

    container.retriever = create_retriever(
    index_memory=container.index_memory,
    data_dir=DATA_DIR,
    )


    print(f"Loaded {len(documents)} documents.")
    print("Index built.")

