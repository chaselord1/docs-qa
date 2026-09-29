"""FastAPI app: upload docs, list/remove them, ask questions with citations."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles

from app import ingest
from app.index import Index
from app.llm import answer_question, has_key

ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT / "static"
SAMPLE_DOCS_DIR = ROOT / "sample_docs"
NOT_COVERED = "That isn't covered in the documents I have."

ALLOWED_SUFFIXES = {".pdf", ".txt", ".md"}

index = Index()


def load_sample_docs():
    if index.documents():
        return
    if not SAMPLE_DOCS_DIR.exists():
        return
    for path in sorted(SAMPLE_DOCS_DIR.iterdir()):
        if path.suffix.lower() in ALLOWED_SUFFIXES:
            raw = path.read_bytes()
            records = ingest.chunk_document(path.name, raw)
            index.add_document(path.name, records)


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_sample_docs()
    yield


app = FastAPI(title="docs-qa", lifespan=lifespan)


@app.get("/api/documents")
def list_documents():
    return {"documents": index.documents(), "demo_mode": not has_key()}


@app.post("/api/upload")
async def upload(file: UploadFile):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(400, f"unsupported file type: {suffix}")
    raw = await file.read()
    records = ingest.chunk_document(file.filename, raw)
    if not records:
        raise HTTPException(400, "no extractable text found in file")
    index.add_document(file.filename, records)
    return {"filename": file.filename, "chunks": len(records)}


@app.delete("/api/documents/{filename}")
def remove_document(filename: str):
    if filename not in index.documents():
        raise HTTPException(404, "document not found")
    index.remove_document(filename)
    return {"removed": filename}


@app.post("/api/ask")
def ask(payload: dict):
    question = (payload or {}).get("question", "").strip()
    if not question:
        raise HTTPException(400, "question is required")

    results, best_score = index.search(question, k=5)
    if not results or not index.is_covered(best_score):
        return {"answer": NOT_COVERED, "citations": [], "demo_mode": not has_key()}

    citations = _unique_citations(results)

    if not has_key():
        top = results[:3]
        snippet = "\n\n".join(f"[{r['source']} p.{r['page']}] {r['text']}" for r in top)
        return {
            "answer": f"demo mode: set LLM_API_KEY for written answers\n\n{snippet}",
            "citations": citations[:3],
            "demo_mode": True,
        }

    answer = answer_question(question, results)
    # Show only the sources the answer actually cites; fall back to the
    # retrieved ones if the model left its citations out.
    cited = [c for c in citations if f"[{c['source']} p.{c['page']}]" in answer]
    return {"answer": answer, "citations": cited or citations, "demo_mode": False}


def _unique_citations(results: list[dict]) -> list[dict]:
    """One citation per file and page, keeping the best-scoring chunk."""
    best: dict[tuple, dict] = {}
    for r in results:
        key = (r["source"], r["page"])
        if key not in best or r["score"] > best[key]["score"]:
            best[key] = {"source": r["source"], "page": r["page"], "text": r["text"], "score": r["score"]}
    return sorted(best.values(), key=lambda c: c["score"], reverse=True)


app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
