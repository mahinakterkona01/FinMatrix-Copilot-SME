"""Source-level benchmark helpers for FinMatrix policy retrieval."""
from statistics import median


def score_ranked_sources(results, expected_source):
    """Score ranked, distinct source documents, not repeated chunks."""
    unique_sources = []
    for item in results:
        source = item.get("source")
        if source and source not in unique_sources:
            unique_sources.append(source)

    if expected_source is None:
        return {
            "expected_source": None,
            "rank_1_hit": None,
            "hit_at_3": None,
            "expected_source_rank": None,
            "unique_sources": unique_sources,
            "returned_any": bool(results),
        }

    rank = (
        unique_sources.index(expected_source) + 1
        if expected_source in unique_sources else None
    )
    return {
        "expected_source": expected_source,
        "rank_1_hit": rank == 1,
        "hit_at_3": rank is not None and rank <= 3,
        "expected_source_rank": rank,
        "unique_sources": unique_sources,
        "returned_any": bool(results),
    }


def percentile(values, percentile_value):
    """Nearest-rank percentile, returning milliseconds when input is ms."""
    if not values:
        return None
    ordered = sorted(float(value) for value in values)
    rank = max(1, int((percentile_value / 100.0) * len(ordered) + 0.999999))
    return ordered[min(rank - 1, len(ordered) - 1)]


def summarize_benchmark(case_results, latency_samples_ms):
    relevant = [
        row for row in case_results
        if row["expected_source"] is not None
    ]
    negatives = [
        row for row in case_results
        if row["expected_source"] is None
    ]

    return {
        "case_count": len(case_results),
        "relevant_case_count": len(relevant),
        "negative_case_count": len(negatives),
        "source_accuracy_at_1": (
            sum(row["rank_1_hit"] for row in relevant) / len(relevant)
            if relevant else None
        ),
        "source_hit_rate_at_3": (
            sum(row["hit_at_3"] for row in relevant) / len(relevant)
            if relevant else None
        ),
        "negative_abstention_accuracy": (
            sum(not row["returned_any"] for row in negatives) / len(negatives)
            if negatives else None
        ),
        "latency_ms_median": median(latency_samples_ms) if latency_samples_ms else None,
        "latency_ms_p95": percentile(latency_samples_ms, 95),
        "latency_sample_count": len(latency_samples_ms),
        "metric_scope": (
            "Small manually labelled development set; distinct-source retrieval only. "
            "Not answer correctness, official policy verification, or external validation."
        ),
    }
