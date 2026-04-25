import os
import git
import tempfile
import shutil
import time

from app.embeddings import get_embeddings_batch
from app.database import supabase

ALLOWED_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx",
    ".java", ".go", ".rs", ".cpp", ".c", ".txt"
}

SKIP_DIRS = {
    "node_modules", ".git", "__pycache__",
    "venv", ".venv", "dist", "build", ".next","docs", "docs_src"
}

MAX_FILE_SIZE_BYTES = 300_000
EMBED_BATCH_SIZE = 64
DB_INSERT_BATCH_SIZE = 200

def chunk_file(content: str, chunk_size: int = 60, overlap: int = 10):
    lines = content.splitlines()
    chunks = []
    start = 0

    while start < len(lines):
        end = min(start + chunk_size, len(lines))
        chunk = "\n".join(lines[start:end])

        if chunk.strip() and len(chunk.strip()) > 30:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def _flush_rows(rows: list[dict]) -> int:
    if not rows:
        return 0
    supabase.table("code_chunks").insert(rows).execute()
    return len(rows)


def ingest_repo(repo_url: str):
    tmp_dir = tempfile.mkdtemp()
    total_chunks = 0
    rows_buffer: list[dict] = []
    started_at = time.time()

    try:
        print(f"Cloning {repo_url}...")
        git.Repo.clone_from(repo_url, tmp_dir, depth=1)

        # Delete old data (re-ingest safe)
        supabase.table("code_chunks").delete().eq("repo_url", repo_url).execute()

        for root, dirs, files in os.walk(tmp_dir):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

            for filename in files:
                ext = os.path.splitext(filename)[1].lower()
                if ext not in ALLOWED_EXTENSIONS:
                    continue

                filepath = os.path.join(root, filename)
                relative_path = os.path.relpath(filepath, tmp_dir)

                try:
                    if os.path.getsize(filepath) > MAX_FILE_SIZE_BYTES:
                        continue
                except OSError:
                    continue

                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                except:
                    continue

                if not content.strip():
                    continue

                chunks = chunk_file(content)

                for i in range(0, len(chunks), EMBED_BATCH_SIZE):
                    batch = chunks[i:i + EMBED_BATCH_SIZE]

                    embeddings = get_embeddings_batch(batch)

                    for j, emb in enumerate(embeddings):
                        index = i + j

                        rows_buffer.append({
                            "repo_url": repo_url,
                            "file_path": relative_path,
                            "chunk_index": index,
                            "content": batch[j],
                            "embedding": emb
                        })

                        if len(rows_buffer) >= DB_INSERT_BATCH_SIZE:
                            total_chunks += _flush_rows(rows_buffer)
                            rows_buffer.clear()
                            if total_chunks % 500 == 0:
                                elapsed = time.time() - started_at
                                print(f"Stored {total_chunks} chunks in {elapsed:.1f}s")

        total_chunks += _flush_rows(rows_buffer)
        rows_buffer.clear()
        elapsed = time.time() - started_at
        print(f"Ingestion completed: {total_chunks} chunks in {elapsed:.1f}s")

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    return {
        "repo_url": repo_url,
        "chunks_stored": total_chunks
    }