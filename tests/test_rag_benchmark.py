from src.rag_benchmark import (
    percentile,
    score_ranked_sources,
    summarize_benchmark,
)


def test_rank_metrics_identify_expected_source():
    results = [
        {"source": "wrong.pdf"},
        {"source": "expected.pdf"},
    ]
    scored = score_ranked_sources(results, "expected.pdf")
    assert scored["rank_1_hit"] is False
    assert scored["hit_at_3"] is True
    assert scored["expected_source_rank"] == 2


def test_duplicate_chunks_do_not_count_as_distinct_sources():
    results = [
        {"source": "wrong.pdf"},
        {"source": "wrong.pdf"},
        {"source": "wrong.pdf"},
        {"source": "expected.pdf"},
    ]
    scored = score_ranked_sources(results, "expected.pdf")
    assert scored["unique_sources"] == ["wrong.pdf", "expected.pdf"]
    assert scored["hit_at_3"] is True
    assert scored["expected_source_rank"] == 2
    assert scored["rank_1_hit"] is False


def test_expected_source_outside_top_three_unique_sources_is_miss():
    results = [
        {"source": "a.pdf"},
        {"source": "a.pdf"},
        {"source": "b.pdf"},
        {"source": "c.pdf"},
        {"source": "d.pdf"},
    ]
    scored = score_ranked_sources(results, "d.pdf")
    assert scored["hit_at_3"] is False
    assert scored["expected_source_rank"] == 4


def test_rank_metrics_handle_missing_expected_source():
    scored = score_ranked_sources([], "expected.pdf")
    assert scored["rank_1_hit"] is False
    assert scored["hit_at_3"] is False


def test_negative_case_does_not_get_source_accuracy_credit():
    scored = score_ranked_sources([], None)
    assert scored["rank_1_hit"] is None
    assert scored["hit_at_3"] is None
    assert scored["returned_any"] is False


def test_nearest_rank_percentile():
    assert percentile([1, 2, 3, 4, 5], 95) == 5
    assert percentile([], 95) is None


def test_summary_separates_relevant_and_negative_cases():
    rows = [
        {
            "expected_source": "a.pdf",
            "rank_1_hit": True,
            "hit_at_3": True,
            "returned_any": True,
        },
        {
            "expected_source": "b.pdf",
            "rank_1_hit": False,
            "hit_at_3": True,
            "returned_any": True,
        },
        {
            "expected_source": None,
            "rank_1_hit": None,
            "hit_at_3": None,
            "returned_any": False,
        },
    ]
    summary = summarize_benchmark(rows, [1.0, 2.0, 3.0, 4.0])
    assert summary["case_count"] == 3
    assert summary["relevant_case_count"] == 2
    assert summary["negative_case_count"] == 1
    assert summary["source_accuracy_at_1"] == 0.5
    assert summary["source_hit_rate_at_3"] == 1.0
    assert summary["negative_abstention_accuracy"] == 1.0
    assert summary["latency_sample_count"] == 4
