from src.retrieval import PolicyRAGEngine


def test_empty_knowledge_base_returns_no_policy(tmp_path):
    engine = PolicyRAGEngine(docs_dir=str(tmp_path))

    results = engine.query_policy("What is the current SME loan interest rate?")

    assert results == []


def test_unrelated_query_returns_no_policy(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "policy.txt").write_text(
        "This policy describes working capital refinancing for small businesses.",
        encoding="utf-8",
    )

    engine = PolicyRAGEngine(docs_dir=str(docs_dir))

    results = engine.query_policy(
        "How can I bake a chocolate cake?"
    )

    assert results == []


def test_retrieved_policy_includes_source(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "policy.txt").write_text(
        "Working capital refinancing is available to eligible small businesses.",
        encoding="utf-8",
    )

    engine = PolicyRAGEngine(docs_dir=str(docs_dir))

    results = engine.query_policy("working capital refinancing")

    assert results
    assert results[0]["source"] == "policy.txt"
    assert results[0]["relevance_score"] > 0


def test_unverified_summary_is_not_returned_as_verified_policy(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "sme_circular_summary.txt").write_text(
        "CMSME refinancing interest rate is 7% for all eligible businesses.",
        encoding="utf-8",
    )

    engine = PolicyRAGEngine(docs_dir=str(docs_dir))
    results = engine.query_policy("CMSME refinancing interest rate")

    assert results == []


def test_rebuilding_index_does_not_duplicate_documents(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "policy.txt").write_text(
        "Working capital refinancing is available to eligible small businesses.",
        encoding="utf-8",
    )

    engine = PolicyRAGEngine(docs_dir=str(docs_dir))

    engine.build_index()
    first_documents = list(engine.documents)
    first_count = len(first_documents)

    engine.build_index()

    assert len(engine.documents) == first_count
    assert engine.documents == first_documents
    assert engine.tfidf_matrix is not None
    assert engine.tfidf_matrix.shape[0] == len(engine.documents)


def test_bangla_unicode_policy_text_is_not_rejected_only_for_non_ascii(tmp_path):
    engine = PolicyRAGEngine(docs_dir=str(tmp_path))

    bangla_text = (
        "\u09AC\u09BE\u0982\u09B2\u09BE\u09A6\u09C7\u09B6 "
        "\u09AC\u09CD\u09AF\u09BE\u0982\u0995 CMSME "
        "\u0989\u09A6\u09CD\u09AF\u09CB\u0995\u09CD\u09A4\u09BE\u09A6\u09C7\u09B0 "
        "\u098B\u09A3 \u0993 \u09AA\u09C1\u09A8\u0983\u0985\u09B0\u09CD\u09A5\u09BE\u09AF\u09BC\u09A8 "
        "\u09B8\u09C1\u09AC\u09BF\u09A7\u09BE \u09B8\u0982\u0995\u09CD\u09B0\u09BE\u09A8\u09CD\u09A4 "
        "\u09A8\u09C0\u09A4\u09BF\u09AE\u09BE\u09B2\u09BE"
    )

    assert engine._is_clean_text(bangla_text)

def test_query_returns_distinct_sources_when_one_source_has_multiple_chunks(
    monkeypatch, tmp_path
):
    import numpy as np
    import src.retrieval as retrieval_module
    from src.retrieval import PolicyRAGEngine

    engine = PolicyRAGEngine(docs_dir=str(tmp_path))
    engine.documents = [
        {"source": "policy_a.pdf", "section": "page-1", "text": "alpha policy"},
        {"source": "policy_a.pdf", "section": "page-2", "text": "alpha policy"},
        {"source": "policy_b.pdf", "section": "page-1", "text": "alpha policy"},
    ]
    engine.vectorizer.fit(["alpha policy", "alpha policy", "alpha policy"])
    engine.tfidf_matrix = engine.vectorizer.transform(
        ["alpha policy", "alpha policy", "alpha policy"]
    )
    engine._is_indexed = True

    monkeypatch.setattr(
        retrieval_module,
        "cosine_similarity",
        lambda query_vec, matrix: np.array([0.95, 0.90, 0.80]),
    )

    results = engine.query_policy("alpha", top_k=2)

    assert len(results) == 2
    assert [item["source"] for item in results] == [
        "policy_a.pdf",
        "policy_b.pdf",
    ]
    assert results[0]["section"] == "page-1"


def test_retrieval_metadata_augments_search_text_without_mutating_evidence():
    engine = PolicyRAGEngine()
    original_text = "Legacy encoded text from the original circular."
    doc = {
        "source": "sep202026smespdl04.pdf",
        "text": original_text,
        "section": "PDF-Page-1",
    }

    retrieval_text = engine._retrieval_text(doc)

    assert "CMSME Working Capital Refinance Fund" in retrieval_text
    assert original_text in retrieval_text
    assert doc["text"] == original_text
    assert doc["section"] == "PDF-Page-1"


def test_unknown_sources_receive_no_invented_metadata():
    engine = PolicyRAGEngine()
    doc = {"source": "unknown.pdf", "text": "Original policy text."}

    assert engine._retrieval_text(doc) == "Original policy text."
    assert doc["text"] == "Original policy text."

def test_known_mojibake_pdfs_are_quarantined():
    engine = PolicyRAGEngine()
    assert engine._extract_pdf_text("sep132026smespd05.pdf") == []
    assert engine._extract_pdf_text("sep202026smespdl04.pdf") == []


def test_verified_pdf_source_date_is_attached(tmp_path, monkeypatch):
    (tmp_path / "jul022026smespdl03e.pdf").write_bytes(b"test placeholder")
    engine = PolicyRAGEngine(docs_dir=str(tmp_path))
    monkeypatch.setattr(
        engine, "_extract_pdf_text",
        lambda path: ["[Page 1] Date: July 02, 2026"],
    )
    engine.load_and_chunk_documents()
    assert len(engine.documents) == 1
    assert engine.documents[0]["effective_date"] == "2026-07-02"

def test_low_similarity_policy_match_is_rejected(tmp_path, monkeypatch):
    import numpy as np
    import src.retrieval as retrieval_module

    (tmp_path / "policy.txt").write_text(
        "Working capital refinancing is available to eligible small businesses.",
        encoding="utf-8",
    )
    engine = PolicyRAGEngine(docs_dir=str(tmp_path))
    engine.load_and_chunk_documents()
    engine.build_index()

    monkeypatch.setattr(
        retrieval_module,
        "cosine_similarity",
        lambda query_vec, matrix: np.array([0.0573]),
    )

    assert engine.query_policy("current SME loan interest rate") == []

