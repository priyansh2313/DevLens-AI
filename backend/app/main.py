import numpy as np
import ast
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.ingest import ingest_repo
from app.embeddings import get_query_embedding
from app.database import supabase
from app.llm import generate_answer


app = FastAPI(title="DevLens AI")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ REQUEST MODELS ------------------

class IngestRequest(BaseModel):
    repo_url: str

class SearchRequest(BaseModel):
    repo_url: str
    query: str
    top_k: int = 10

class ChatRequest(BaseModel):
    repo_url: str
    query: str


# ------------------ INGEST ------------------

@app.post("/ingest")
async def ingest(request: IngestRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(ingest_repo, request.repo_url)
    return {
        "message": "Ingestion started",
        "repo_url": request.repo_url
    }


# ------------------ SEARCH ------------------

@app.post("/search")
async def search(request: SearchRequest):
    query_embedding = get_query_embedding(request.query)

    result = supabase.rpc("match_chunks", {
        "query_embedding": query_embedding,
        "repo_filter": request.repo_url,
        "match_count": request.top_k
    }).execute()

    data = result.data or []

    return {
        "results": [
            {
                "file": r["file_path"],
                "chunk_index": r["chunk_index"],
                "content": r["content"],
                "similarity": r["similarity"]
            }
            for r in data
        ]
    }


# ------------------ CHAT ------------------

def to_float_array(x):
    if isinstance(x, str):
        x = ast.literal_eval(x)
    return np.array(x, dtype=float)


def cosine_sim(a, b):
    a = to_float_array(a)
    b = to_float_array(b)

    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0 or np.isnan(denom):
        return 0.0

    return float(np.dot(a, b) / denom)


@app.post("/chat")
async def chat(request: ChatRequest):
    query_embedding = get_query_embedding(request.query)

    # Fetch chunks (no vector comparison in DB)
    result = supabase.rpc("match_chunks_direct", {
        "repo_filter": request.repo_url,
        "match_count": 200
    }).execute()

    data = result.data or []

    if not data:
        return {"answer": "No data found", "sources": []}

    # -------- Similarity scoring --------
    scored = []
    for row in data:
        sim = cosine_sim(query_embedding, row["embedding"])
        scored.append((sim, row))

    # Sort by similarity
    scored.sort(key=lambda x: x[0], reverse=True)

    # -------- Filter + Diversity --------
    MIN_SIM = 0.2

    filtered = [(s, r) for s, r in scored if s >= MIN_SIM]
    base = filtered if filtered else scored

    top = []
    per_file = {}

    for sim, row in base:
        fp = row["file_path"]

        # max 2 chunks per file
        if per_file.get(fp, 0) >= 2:
            continue

        top.append((sim, row))
        per_file[fp] = per_file.get(fp, 0) + 1

        if len(top) == 8:
            break

    # Extract content
    chunks = [r[1]["content"] for r in top]

    # Debug logs
    print("Total rows fetched:", len(data))
    print("Retrieved chunks:", len(top))
    print("Top files:", [r[1]["file_path"] for r in top[:5]])

    # -------- LLM --------
    answer = generate_answer(request.query, chunks)

    return {
        "answer": answer,
        "sources": [
            {
                "file": r[1]["file_path"],
                "similarity": float(r[0])
            }
            for r in top
        ]
    }


# ------------------ HEALTH ------------------

@app.get("/health")
async def health():
    return {"status": "ok"}