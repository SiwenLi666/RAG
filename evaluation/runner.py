import json
import time
from pathlib import Path
from collections import defaultdict

from api_client import call_api, generate_session_id
from scorer import score_rank
from report_writer import save_reports


BASE_DIR = Path(__file__).resolve().parent
TEST_CASES_PATH = BASE_DIR / "test_cases.json"


CATEGORY_WEIGHTS = {
    "single_step": 40,
    "multi_step": 25,
    "multilingual": 15,
    "stability": 10,
    "negative": 10
}


RUN_LABEL = "v2_detailed_inspection"


def run():

    with open(TEST_CASES_PATH, "r", encoding="utf-8") as f:
        tests = json.load(f)

    detailed_results = []
    category_scores = defaultdict(list)
    difficulty_scores = defaultdict(list)

    print("\n==================================================")
    print("STARTING DETAILED EVALUATION RUN")
    print("==================================================\n")

    global_start = time.time()

    for test in tests:

        session_id = generate_session_id()

        # ---------------------------
        # CALL API
        # ---------------------------
        if test["category"] == "multi_step":
            latency_total = 0
            response = None
            for step in test["steps"]:
                response, latency = call_api(step, session_id)
                latency_total += latency
        else:
            response, latency_total = call_api(test["query"], session_id)

        returned_ids = [r["id"] for r in response.get("results", [])]

        # ---------------------------
        # SCORE
        # ---------------------------
        score = score_rank(test.get("expected_id"), returned_ids)

        category_scores[test["category"]].append(score)
        difficulty_scores[test["difficulty"]].append(score)

        detailed_results.append({
            "test_id": test["id"],
            "category": test["category"],
            "difficulty": test["difficulty"],
            "score": score,
            "expected_id": test.get("expected_id"),
            "returned_ids": returned_ids,
            "latency": latency_total
        })

        # ---------------------------
        # 🔎 INSPECTION PRINT
        # ---------------------------
        print("--------------------------------------------------")
        print(f"Test ID: {test['id']}")
        print(f"Category: {test['category']} | Difficulty: {test['difficulty']}")

        if test["category"] == "multi_step":
            print(f"Steps: {test['steps']}")
        else:
            print(f"Query: {test.get('query')}")

        print(f"Expected ID: {test.get('expected_id')}")
        print(f"Returned IDs (top 5): {returned_ids[:5]}")
        print(f"Score: {score}")
        print(f"Latency: {round(latency_total, 3)} sec")
        print("--------------------------------------------------\n")

    # ---------------------------
    # CATEGORY SUMMARY
    # ---------------------------
    weighted_total = 0
    category_summary = {}

    for cat, scores in category_scores.items():
        avg = sum(scores) / len(scores)
        category_summary[cat] = round(avg, 2)

        weight = CATEGORY_WEIGHTS.get(cat, 0)
        weighted_total += (avg / 100) * weight

    overall_score = round(weighted_total, 2)

    if overall_score >= 90:
        grade = "A"
    elif overall_score >= 80:
        grade = "B"
    elif overall_score >= 70:
        grade = "C"
    elif overall_score >= 60:
        grade = "D"
    else:
        grade = "F"

    total_runtime = round(time.time() - global_start, 2)

    # ---------------------------
    # DIFFICULTY SUMMARY
    # ---------------------------
    difficulty_summary = {}
    for diff, scores in difficulty_scores.items():
        avg = sum(scores) / len(scores)
        difficulty_summary[diff] = round(avg, 2)

    summary = {
        "run_label": RUN_LABEL,
        "overall_score": overall_score,
        "grade": grade,
        "category_scores": category_summary,
        "difficulty_scores": difficulty_summary,
        "total_runtime_sec": total_runtime
    }

    save_reports(
        {"tests": detailed_results},
        summary
    )

    print("==================================================")
    print("EVALUATION COMPLETE")
    print("==================================================")
    print(f"Run Label: {RUN_LABEL}")
    print(f"Overall Score: {overall_score} / 100")
    print(f"Grade: {grade}")
    print(f"Total Runtime: {total_runtime} sec")
    print("\nCategory Breakdown:")
    for k, v in category_summary.items():
        print(f"  {k}: {v}")
    print("\nDifficulty Breakdown:")
    for k, v in difficulty_summary.items():
        print(f"  {k}: {v}")
    print("==================================================\n")


if __name__ == "__main__":
    run()
