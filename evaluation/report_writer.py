import json
from pathlib import Path

OUTPUT_DIR = Path(
    r"D:\Siwen\projects\RAG\recept_RAG\genre_rag_api\tests"
)

def save_reports(detailed, summary):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_DIR / "detailed_results.json", "w", encoding="utf-8") as f:
        json.dump(detailed, f, indent=2)

    with open(OUTPUT_DIR / "evaluation_grade.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
