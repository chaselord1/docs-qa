from pathlib import Path

from app import ingest
from app.index import Index

SAMPLE_DOCS = Path(__file__).resolve().parent.parent / "sample_docs"


def _load_all(index: Index):
    for path in SAMPLE_DOCS.glob("*.md"):
        records = ingest.chunk_document(path.name, path.read_bytes())
        index.add_document(path.name, records)


def test_bm25_finds_returns_policy_for_refund_question():
    index = Index()
    _load_all(index)
    results, best = index.search("how long until I get my refund back", k=3)
    assert results
    assert results[0]["source"] == "returns-and-warranty.md"
    assert index.is_covered(best)


def test_not_covered_for_unrelated_question():
    index = Index()
    _load_all(index)
    results, best = index.search("what is the capital of France", k=3)
    assert not index.is_covered(best)
