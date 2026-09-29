"""Env loading and a thin wrapper around an OpenAI-compatible client."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_env():
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if key and key not in os.environ:
            os.environ[key] = value


load_env()

LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "text-embedding-3-small")

SYSTEM_PROMPT = (
    "Answer only using the passages provided below. Cite every claim inline "
    "like [file p.N] using the file and page given with each passage. "
    "If the passages do not answer the question, say plainly that it isn't "
    "covered in the documents. Keep answers short."
)


def has_key() -> bool:
    return bool(LLM_API_KEY)


def _client():
    from openai import OpenAI
    return OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY or "none")


def embed_texts(texts):
    """Return a list of embedding vectors for the given texts."""
    client = _client()
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]


def answer_question(question: str, passages: list[dict]) -> str:
    """Ask the chat model to answer from the given passages only."""
    context = "\n\n".join(
        f"[{p['source']} p.{p['page']}]\n{p['text']}" for p in passages
    )
    client = _client()
    resp = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Passages:\n{context}\n\nQuestion: {question}"},
        ],
        temperature=0,
    )
    return resp.choices[0].message.content.strip()
