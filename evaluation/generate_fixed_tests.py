import json
import random
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = BASE_DIR / "data" / "20170107-061401-recipeitems.json"
OUTPUT_PATH = BASE_DIR / "evaluation" / "test_cases.json"

random.seed(42)

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
    words = re.findall(r"[a-zA-ZäöåÄÖÅ]+", line)
    words = [w for w in words if w not in STOPWORDS]
    return " ".join(words).strip()


def extract_core_ingredients(recipe):
    lines = recipe.get("ingredients", "").split("\n")
    cleaned = [clean_ingredient_line(l) for l in lines]
    cleaned = [c for c in cleaned if 1 < len(c.split()) <= 3]
    return list(set(cleaned))


def translate_query(query):
    words = query.split()
    return " ".join([SWEDISH_MAP.get(w, w) for w in words])


def generate_progressive_test(recipe, test_id):
    ingredients = extract_core_ingredients(recipe)
    if len(ingredients) < 4:
        return None

    random.shuffle(ingredients)

    steps = []
    base = []

    for i in range(4):
        base.append(ingredients[i])
        steps.append(" ".join(base))

    return {
        "id": test_id,
        "category": "progressive_refinement",
        "difficulty": "medium",
        "steps": steps,
        "expected_id": recipe["_id"]["$oid"]
    }


def generate_description_test(recipe, test_id):
    ingredients = extract_core_ingredients(recipe)
    if len(ingredients) < 3:
        return None

    random.shuffle(ingredients)

    name_words = recipe.get("name", "").lower().split()[:2]
    steps = [" ".join(name_words)]

    base = name_words.copy()
    for i in range(3):
        base.append(ingredients[i])
        steps.append(" ".join(base))

    return {
        "id": test_id,
        "category": "description_refinement",
        "difficulty": "hard",
        "steps": steps,
        "expected_id": recipe["_id"]["$oid"]
    }


def generate_multilingual_test(recipe, test_id):
    base_test = generate_progressive_test(recipe, test_id)
    if not base_test:
        return None

    base_test["steps"] = [translate_query(s) for s in base_test["steps"]]
    base_test["category"] = "multilingual_progressive"
    base_test["difficulty"] = "medium"
    return base_test


def main():
    recipes = []

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        for line in f:
            recipes.append(json.loads(line))

    recipes = [r for r in recipes if "ingredients" in r and "name" in r]

    selected = recipes[:30]

    tests = []
    counter = 1

    # 5 progressive ingredient refinement
    for r in selected:
        if len(tests) >= 5:
            break
        test = generate_progressive_test(r, f"T{counter:02}")
        if test:
            tests.append(test)
            counter += 1

    # 3 description refinement
    for r in selected:
        if len(tests) >= 8:
            break
        test = generate_description_test(r, f"T{counter:02}")
        if test:
            tests.append(test)
            counter += 1

    # 2 multilingual
    for r in selected:
        if len(tests) >= 10:
            break
        test = generate_multilingual_test(r, f"T{counter:02}")
        if test:
            tests.append(test)
            counter += 1

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(tests, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(tests)} clean progressive test cases.")


if __name__ == "__main__":
    main()
