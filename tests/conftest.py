import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ["LLM_API_KEY"] = ""  # force demo / BM25 mode for offline tests

import pytest


@pytest.fixture(autouse=True)
def isolated_data_dir(tmp_path, monkeypatch):
    import app.index as index_module
    monkeypatch.setattr(index_module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(index_module, "CHUNKS_PATH", tmp_path / "chunks.json")
    monkeypatch.setattr(index_module, "EMBEDDINGS_PATH", tmp_path / "embeddings.npy")
    yield
