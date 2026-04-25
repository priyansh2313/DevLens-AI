from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    return model.encode(
        texts,
        batch_size=64,
        convert_to_numpy=True,
        show_progress_bar=False
    ).tolist()

def get_query_embedding(text: str) -> list[float]:
    return model.encode([text])[0].tolist()