"""Run the local, labelled FinMatrix source-retrieval benchmark."""
from pathlib import Path
import json
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.retrieval import PolicyRAGEngine
from src.rag_benchmark import score_ranked_sources, summarize_benchmark


def main():
    dataset_path = ROOT / "data" / "rag_benchmark_queries.json"
    output_path = ROOT / "docs" / "rag_benchmark_results.json"
    cases = json.loads(dataset_path.read_text(encoding="utf-8"))

    if not cases:
        raise SystemExit("Benchmark dataset is empty.")

    ids = [case.get("id") for case in cases]
    if any(not item for item in ids) or len(set(ids)) != len(ids):
        raise SystemExit("Benchmark case IDs must be non-empty and unique.")

    for case in cases:
        if not isinstance(case.get("query"), str) or not case["query"].strip():
            raise SystemExit(f"Invalid query in case {case.get('id')}")
        if case.get("should_abstain") != (case.get("expected_source") is None):
            raise SystemExit(f"Abstention label mismatch in case {case.get('id')}")

    engine = PolicyRAGEngine(docs_dir=str(ROOT / "data" / "rag_docs"))
    build_start = time.perf_counter()
    engine.build_index()
    build_ms = (time.perf_counter() - build_start) * 1000

    rows = []
    latency_samples = []

    for case in cases:
        query = case["query"]

        # Warm-up is excluded from timed samples.
        for _ in range(3):
            engine.query_policy(query, top_k=3)

        timings = []
        results = None
        for _ in range(20):
            started = time.perf_counter()
            results = engine.query_policy(query, top_k=3)
            timings.append((time.perf_counter() - started) * 1000)

        latency_samples.extend(timings)
        expected = case["expected_source"]
        scored = score_ranked_sources(results or [], expected)

        rows.append({
            "id": case["id"],
            "query": query,
            "expected_source": expected,
            "should_abstain": case["should_abstain"],
            "retrieved_sources": [item.get("source") for item in (results or [])],
            "retrieved_unique_sources": scored["unique_sources"],
            "expected_source_rank": scored["expected_source_rank"],
            "retrieved_scores": [
                item.get("relevance_score") for item in (results or [])
            ],
            "result_count": len(results or []),
            "rank_1_hit": scored["rank_1_hit"],
            "hit_at_3": scored["hit_at_3"],
            "returned_any": scored["returned_any"],
            "median_query_latency_ms": sorted(timings)[len(timings) // 2],
        })

    summary = summarize_benchmark(rows, latency_samples)
    payload = {
        "benchmark_name": "FinMatrix policy source retrieval development benchmark",
        "dataset_path": "data/rag_benchmark_queries.json",
        "corpus_path": "data/rag_docs",
        "indexed_chunk_count": len(engine.documents),
        "indexed_sources": sorted({
            item.get("source") for item in engine.documents
        }),
        "index_build_ms": round(build_ms, 3),
        "summary": summary,
        "cases": rows,
        "limitations": [
            "Small manually labelled development set; not an external test set.",
            "Source retrieval metrics do not establish answer correctness.",
            "PDF extraction quality and document authority are not independently verified.",
            "Latency is local-process timing and depends on hardware and runtime state.",
            "The first index build is reported separately from warmed query latency."
        ],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print("=" * 72)
    print("FINMATRIX RAG BENCHMARK")
    print("=" * 72)
    print("Cases:", summary["case_count"])
    print("Relevant cases:", summary["relevant_case_count"])
    print("Negative cases:", summary["negative_case_count"])
    print("Indexed chunks:", len(engine.documents))
    print("Index build ms:", round(build_ms, 3))
    print("Source accuracy @1:",
          summary["source_accuracy_at_1"])
    print("Source hit rate @3:",
          summary["source_hit_rate_at_3"])
    print("Negative abstention accuracy:",
          summary["negative_abstention_accuracy"])
    print("Warm query latency median ms:",
          round(summary["latency_ms_median"], 4))
    print("Warm query latency p95 ms:",
          round(summary["latency_ms_p95"], 4))
    print("Latency samples:", summary["latency_sample_count"])

    print("\nPER-CASE RESULTS")
    for row in rows:
        print(
            f"{row['id']}: expected={row['expected_source']}; "
            f"rank1={row['rank_1_hit']}; hit@3={row['hit_at_3']}; "
            f"returned={row['result_count']}; "
            f"median_ms={row['median_query_latency_ms']:.4f}; "
            f"got={row['retrieved_sources']}"
        )

    print("\nJSON report:", output_path.relative_to(ROOT))
    print("Interpretation: development benchmark only; not external validation.")

    # Exit non-zero only for invalid benchmark execution, not low retrieval scores.
    if len(rows) != len(cases):
        raise SystemExit("Benchmark case count mismatch.")


if __name__ == "__main__":
    main()
