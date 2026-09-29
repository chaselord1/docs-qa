from app.ingest import chunk_document


def test_chunking_keeps_page_numbers():
    raw = b"hello world " * 400  # one "page" since it's a .txt file
    records = chunk_document("sample.txt", raw)
    assert records
    assert all(r["page"] == 1 for r in records)
    assert all(r["source"] == "sample.txt" for r in records)
    assert len(records) > 1  # long enough to split into multiple chunks


def test_chunk_overlap_present():
    raw = (" ".join(f"word{i}" for i in range(300))).encode("utf-8")
    records = chunk_document("sample.txt", raw)
    assert len(records) >= 2
    first_words = records[0]["text"].split()
    second_words = records[1]["text"].split()
    assert set(first_words) & set(second_words)  # overlapping tail/head
