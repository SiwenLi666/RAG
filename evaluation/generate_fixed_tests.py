import json
import random
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = BASE_DIR / "data" / "20170107-061401-recipeitems.json"
OUTPUT_PATH = BASE_DIR / "evaluation" / "test_cases.json"


random.seed(42)  # deterministic

STOPWORDS = {
    "cup", "cups", "tablespoon", "tablespoons", "teaspoon", "teaspoons",
    "pound", "pounds", "ounce", "ounces", "clove", "whole", "large",
    "small", "fresh", "optional", "cut", "into", "pieces"
}

SWEDISH_MAP = {
    "chicken": "kyckling",
    "garlic": "vitlök",
    "coconut": "kokos",
    "beef": "nötkött",
    "egg": "ägg",
    "milk": "mjölk"
}

def clean_ingredient_line(line):
    line = line.lower()
    line = re.sub(r"[\d/]+", "", line)
    words = re.findall(r"[a-zA-Z]+", line)
    words = [w for w in words if w not in STOPWORDS]
    return " ".join(words).strip()

def extract_core_ingredients(recipe):
    lines = recipe.get("ingredients", "").split("\n")
    cleaned = [clean_ingredient_line(l) for l in lines]
    cleaned = [c for c in cleaned if len(c.split()) <= 3 and len(c) > 3]
    return list(set(cleaned))

def translate_query(query):
    words = query.split()
    return " ".join([SWEDISH_MAP.get(w, w) for w in words])

def main():
    recipes = []
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        for line in f:
            recipes.append(json.loads(line))

    recipes = [r for r in recipes if "ingredients" in r and "name" in r]

    selected = recipes[:20]

    tests = []

    # 8 single-step
    for i, r in enumerate(selected[:8]):
        ingredients = extract_core_ingredients(r)
        if len(ingredients) < 2:
            continue
        query = " ".join(ingredients[:2])
        tests.append({
            "id": f"T{i+1:02}",
            "category": "single_step",
            "difficulty": "easy",
            "query": query,
            "expected_id": r["_id"]["$oid"]
        })

    # 4 noise tests
    for i, r in enumerate(selected[8:12]):
        ingredients = extract_core_ingredients(r)
        if len(ingredients) < 2:
            continue
        noise = extract_core_ingredients(selected[0])[0]
        query = " ".join(ingredients[:2]) + " " + noise
        tests.append({
            "id": f"T{len(tests)+1:02}",
            "category": "single_step",
            "difficulty": "medium",
            "query": query,
            "expected_id": r["_id"]["$oid"]
        })

    # 4 multi-step
    for i, r in enumerate(selected[12:16]):
        ingredients = extract_core_ingredients(r)
        if len(ingredients) < 3:
            continue
        tests.append({
            "id": f"T{len(tests)+1:02}",
            "category": "multi_step",
            "difficulty": "hard",
            "steps": [
                " ".join(ingredients[:2]),
                ingredients[2]
            ],
            "expected_id": r["_id"]["$oid"]
        })

    # 2 multilingual
    for r in selected[16:18]:
        ingredients = extract_core_ingredients(r)
        if len(ingredients) < 2:
            continue
        query = " ".join(ingredients[:2])
        tests.append({
            "id": f"T{len(tests)+1:02}",
            "category": "multilingual",
            "difficulty": "hard",
            "query": translate_query(query),
            "expected_id": r["_id"]["$oid"]
        })

    # 1 stability
    r = selected[18]
    ingredients = extract_core_ingredients(r)
    tests.append({
        "id": f"T{len(tests)+1:02}",
        "category": "stability",
        "difficulty": "medium",
        "query": " ".join(ingredients[:2]),
        "expected_id": r["_id"]["$oid"]
    })

    # 1 negative
    r1, r2, r3 = selected[0], selected[1], selected[2]
    ing1 = extract_core_ingredients(r1)[0]
    ing2 = extract_core_ingredients(r2)[0]
    ing3 = extract_core_ingredients(r3)[0]
    tests.append({
        "id": f"T{len(tests)+1:02}",
        "category": "negative",
        "difficulty": "hard",
        "query": f"{ing1} {ing2} {ing3}",
        "expected_id": None
    })

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(tests, f, indent=2)

    print("Generated 20 fixed test cases.")

if __name__ == "__main__":
    main()
