"""In-memory chunk index: numpy cosine search when embeddings exist,
pure-Python BM25 fallback otherwise. Persisted to a local data/ folder."""
import json
import math
import re
from collections import Counter
from pathlib import Path

import numpy as np

from app.llm import embed_texts, has_key

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CHUNKS_PATH = DATA_DIR / "chunks.json"
EMBEDDINGS_PATH = DATA_DIR / "embeddings.npy"

EMBED_SCORE_THRESHOLD = 0.50
BM25_SCORE_THRESHOLD = 0.5

_WORD_RE = re.compile(r"[a-z0-9]+")

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "can", "do",
    "does", "for", "from", "get", "how", "i", "if", "in", "into", "is",
    "it", "its", "long", "me", "my", "not", "of", "on", "or", "that",
    "the", "their", "there", "these", "this", "those", "to", "until",
    "up", "was", "we", "what", "when", "where", "which", "who", "will",
    "with", "you", "your",
}


def _tokenize(text: str) -> list[str]:
    return [
        w for w in _WORD_RE.findall(text.lower())
        if w not in _STOPWORDS and len(w) > 1
    ]


class BM25:
    def __init__(self, chunks: list[dict]):
        self.docs = [_tokenize(c["text"]) for c in chunks]
        self.doc_lens = [len(d) for d in self.docs]
        self.avg_len = sum(self.doc_lens) / len(self.doc_lens) if self.docs else 0.0
        self.n = len(self.docs)
        self.doc_freq = Counter()
        for doc in self.docs:
            for term in set(doc):
                self.doc_freq[term] += 1
        self.term_freqs = [Counter(doc) for doc in self.docs]
        self.k1 = 1.5
        self.b = 0.75

    def _idf(self, term: str) -> float:
        df = self.doc_freq.get(term, 0)
        return math.log(1 + (self.n - df + 0.5) / (df + 0.5))

    def scores(self, query: str) -> list[float]:
        q_terms = _tokenize(query)
        scores = [0.0] * self.n
        for i in range(self.n):
            tf = self.term_freqs[i]
            dl = self.doc_lens[i] or 1
            for term in q_terms:
                if term not in tf:
                    continue
                idf = self._idf(term)
                freq = tf[term]
                denom = freq + self.k1 * (1 - self.b + self.b * dl / (self.avg_len or 1))
                scores[i] += idf * (freq * (self.k1 + 1)) / (denom or 1)
        return scores


class Index:
    def __init__(self):
        self.chunks: list[dict] = []
        self.embeddings: np.ndarray | None = None
        self._load()

    def _load(self):
        DATA_DIR.mkdir(exist_ok=True)
        if CHUNKS_PATH.exists():
            self.chunks = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
        if EMBEDDINGS_PATH.exists() and self.chunks:
            self.embeddings = np.load(EMBEDDINGS_PATH)

    def _persist(self):
        DATA_DIR.mkdir(exist_ok=True)
        CHUNKS_PATH.write_text(json.dumps(self.chunks, indent=2), encoding="utf-8")
        if self.embeddings is not None:
            np.save(EMBEDDINGS_PATH, self.embeddings)
        elif EMBEDDINGS_PATH.exists():
            EMBEDDINGS_PATH.unlink()

    def documents(self) -> list[str]:
        seen = []
        for c in self.chunks:
            if c["source"] not in seen:
                seen.append(c["source"])
        return seen

    def add_document(self, filename: str, records: list[dict]):
        self.remove_document(filename)
        self.chunks.extend(records)
        if has_key() and records:
            vectors = np.array(embed_texts([r["text"] for r in records]), dtype=np.float32)
            if self.embeddings is None:
                self.embeddings = vectors
            else:
                self.embeddings = np.vstack([self.embeddings, vectors])
        self._persist()

    def remove_document(self, filename: str):
        keep_idx = [i for i, c in enumerate(self.chunks) if c["source"] != filename]
        if len(keep_idx) == len(self.chunks):
            return
        self.chunks = [self.chunks[i] for i in keep_idx]
        if self.embeddings is not None and len(self.embeddings):
            if keep_idx:
                self.embeddings = self.embeddings[keep_idx]
            else:
                self.embeddings = None
        self._persist()

    def search(self, query: str, k: int = 5) -> tuple[list[dict], float]:
        """Return (top chunks with scores, best score) using embeddings if
        available, else BM25. Score scale differs between the two modes,
        each compared against its own threshold by the caller."""
        if not self.chunks:
            return [], 0.0
        if has_key() and self.embeddings is not None and len(self.embeddings) == len(self.chunks):
            q_vec = np.array(embed_texts([query])[0], dtype=np.float32)
            sims = self._cosine(q_vec)
            order = np.argsort(-sims)[:k]
            results = [dict(self.chunks[i], score=float(sims[i])) for i in order]
            best = float(sims[order[0]]) if len(order) else 0.0
            return results, best
        bm25 = BM25(self.chunks)
        scores = bm25.scores(query)
        order = sorted(range(len(scores)), key=lambda i: -scores[i])[:k]
        results = [dict(self.chunks[i], score=scores[i]) for i in order]
        best = scores[order[0]] if order else 0.0
        return results, best

    def _cosine(self, q_vec: np.ndarray) -> np.ndarray:
        a = self.embeddings
        a_norm = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-8)
        q_norm = q_vec / (np.linalg.norm(q_vec) + 1e-8)
        return a_norm @ q_norm

    def is_covered(self, best_score: float) -> bool:
        threshold = EMBED_SCORE_THRESHOLD if (has_key() and self.embeddings is not None) else BM25_SCORE_THRESHOLD
        return best_score >= threshold
