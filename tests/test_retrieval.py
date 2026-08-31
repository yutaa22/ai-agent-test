from app.retrieval.retriever import KnowledgeRetriever


def test_retriever_loads_documents():
    retriever = KnowledgeRetriever()

    assert len(retriever.documents) >= 14


def test_returns_policy_prefers_current_document():
    retriever = KnowledgeRetriever()

    # Search broadly so both current and legacy policy sections
    # are available for the precedence comparison.
    results = retriever.search(
        "What is the return window?",
        top_k=len(retriever.documents),
    )

    current = next(
        result
        for result in results
        if result["filename"]
        == "01-returns-policy-current.md"
    )

    legacy = next(
        result
        for result in results
        if result["filename"]
        == "02-returns-policy-legacy.md"
    )

    assert current["score"] > legacy["score"]


def test_internal_migration_is_not_authoritative():
    retriever = KnowledgeRetriever()

    results = retriever.search(
        "return policy 60 days",
        top_k=len(retriever.documents),
    )

    migration = next(
        result
        for result in results
        if result["filename"]
        == "14-internal-content-migration-notes.md"
    )

    assert migration["authority_score"] < 0


def test_sources_contain_heading():
    retriever = KnowledgeRetriever()

    results = retriever.search(
        "return shipping fee",
        top_k=3,
    )

    sources = retriever.format_sources(results)

    assert len(sources) > 0

    for source in sources:
        assert source["filename"]
        assert source["heading"]