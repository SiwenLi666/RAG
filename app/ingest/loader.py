import json
import zipfile
from pathlib import Path
from typing import List, Dict, Any


def load_json_dataset(file_path: Path) -> List[Dict[str, Any]]:
    """
    Loads:
    - JSON array
    - JSON lines (one JSON object per line)
    - Zipped JSON
    """

    if file_path.suffix == ".zip":
        with zipfile.ZipFile(file_path, "r") as z:
            file_name = z.namelist()[0]
            with z.open(file_name) as f:
                content = f.read().decode("utf-8")
                return _parse_content(content)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        return _parse_content(content)


def _parse_content(content: str) -> List[Dict[str, Any]]:
    content = content.strip()

    # Case 1: Proper JSON array
    if content.startswith("["):
        return json.loads(content)

    # Case 2: JSON Lines (multiple objects separated by newline)
    documents = []
    for line in content.splitlines():
        line = line.strip()
        if line:
            documents.append(json.loads(line))

    return documents
