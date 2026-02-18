import json
import time
from pathlib import Path
from collections import defaultdict

from api_client import call_api, generate_session_id
from report_writer import save_reports

BASE_DIR = Path(__file__).resolve().parent
TEST_CASES_PATH = BASE_DIR / "test_cases.json"

# Only current categories
CATEGORY_WEIGHTS = {
    "progressive_refinement": 40,
    "description_refinement": 35,
    "multilingual_progressive": 25,
}

RUN_LABEL = "v6_clean_progressive_eval"


# ---------------------------------------------------------
# Overlap scoring helper
# ---------------------------------------------------------
def compute_overlap_score(query_text: str, matched_terms: list):
    if not query_text:
        return 0

    query_tokens = set(query_text.lower().split())
    matched_tokens = set(matched_terms or [])

    if not query_tokens:
        return 0

    overlap = query_tokens.intersection(matched_tokens)
    ratio = len(overlap) / len(query_tokens)

    return int(ratio * 100)


# ---------------------------------------------------------
# Runner
# ---------------------------------------------------------
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
        expected_id = test.get("expected_id")

        latency_total = 0.0
        last_response = None

        print("--------------------------------------------------")
        print(f"Test ID: {test.get('id')}")
        print(f"Category: {test.get('category')} | Difficulty: {test.get('difficulty')}")
        print(f"Expected ID: {expected_id}")

        steps = test.get("steps") or [test.get("query", "")]

        step_debug = []
        final_returned_ids = []

        # -------------------------------------------------
        # Execute steps
        # -------------------------------------------------
        for idx, step in enumerate(steps, start=1):

            resp, latency = call_api(step, session_id)
            latency_total += float(latency)
            last_response = resp or {}

            results = last_response.get("results", []) or []
            returned_ids = [r.get("id") for r in results if r.get("id")]
            final_returned_ids = returned_ids

            top1 = results[0] if results else {}
            top1_id = top1.get("id")
            top1_score = top1.get("score")
            top1_meta = top1.get("metadata", {}) or {}

            matched_terms = top1_meta.get("matched_terms", [])
            enhanced_query = top1_meta.get("enhanced_query")

            hit_top5 = expected_id in returned_ids[:5]

            step_debug.append({
                "step_index": idx,
                "step_query": step,
                "top1_id": top1_id,
                "top1_score": top1_score,
                "hit_top5": hit_top5,
                "returned_top5": returned_ids[:5],
                "matched_terms": matched_terms,
                "enhanced_query": enhanced_query,
            })

            # ---- Debug print ----
            print(f"\n  Step {idx}/{len(steps)} query: {step}")
            print(f"    hit_top5: {hit_top5}")
            print(f"    top1: {top1_id} | score={top1_score}")
            if enhanced_query:
                print(f"    enhanced_query: {enhanced_query}")
            if matched_terms:
                print(f"    matched_terms: {matched_terms}")
            print(f"    returned_top5: {returned_ids[:5]}")

        # -------------------------------------------------
        # SCORING LOGIC
        # -------------------------------------------------

        # Rule 1: If expected id appears in top5 at ANY step → 100
        hit_any_step = any(s["hit_top5"] for s in step_debug)

        if hit_any_step:
            score = 100
        else:
            # Rule 2: fallback overlap scoring on FINAL step
            final_step = step_debug[-1] if step_debug else {}
            final_query = final_step.get("step_query", "")
            matched_terms = final_step.get("matched_terms", [])

            overlap_score = compute_overlap_score(final_query, matched_terms)

            # Soft floor to avoid catastrophic failure
            score = max(60, overlap_score)

        category_scores[test["category"]].append(score)
        difficulty_scores[test["difficulty"]].append(score)

        detailed_results.append({
            "test_id": test.get("id"),
            "category": test.get("category"),
            "difficulty": test.get("difficulty"),
            "expected_id": expected_id,
            "score": score,
            "latency": latency_total,
            "steps_debug": step_debug,
        })

        print("\n  FINAL:")
        print(f"    Final returned_top5: {final_returned_ids[:5]}")
        print(f"    Score: {score}")
        print(f"    Latency total: {round(latency_total, 3)} sec")
        print("--------------------------------------------------\n")

    # -------------------------------------------------
    # CATEGORY SUMMARY
    # -------------------------------------------------

    category_summary = {}
    weighted_sum = 0.0
    weight_sum_present = 0.0

    for cat, scores in category_scores.items():
        avg = sum(scores) / len(scores)
        category_summary[cat] = round(avg, 2)

        w = CATEGORY_WEIGHTS.get(cat, 0)
        if w > 0:
            weighted_sum += (avg / 100.0) * w
            weight_sum_present += w

    overall_score = (
        round((weighted_sum / weight_sum_present) * 100.0, 2)
        if weight_sum_present > 0
        else 0.0
    )

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
        "total_runtime_sec": total_runtime,
        "weight_sum_present": weight_sum_present,
    }

    save_reports({"tests": detailed_results}, summary)

    print("==================================================")
    print("EVALUATION COMPLETE")
    print("==================================================")
    print(f"Run Label: {RUN_LABEL}")
    print(f"Overall Score: {overall_score} / 100")
    print(f"Grade: {grade}")
    print(f"Total Runtime: {total_runtime} sec")
    print(f"Weight sum used: {weight_sum_present}")
    print("\nCategory Breakdown:")
    for k, v in category_summary.items():
        print(f"  {k}: {v}")
    print("\nDifficulty Breakdown:")
    for k, v in difficulty_summary.items():
        print(f"  {k}: {v}")
    print("==================================================\n")


if __name__ == "__main__":
    run()
