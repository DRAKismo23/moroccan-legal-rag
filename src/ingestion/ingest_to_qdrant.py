import json
import os
import time
import uuid

import requests
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

CHUNKS_DIR = "data/chunks"
COLLECTION_NAME = "moroccan_legal_articles"
OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"
BATCH_SIZE = 20


def get_embeddings_batch(texts):
    """Get embeddings for multiple texts in a single Ollama request."""
    response = requests.post(
        OLLAMA_EMBED_URL,
        json={"model": "bge-m3", "input": texts}
    )
    response.raise_for_status()
    return response.json()["embeddings"]


def load_all_articles():
    """Load every article from every JSON file in data/chunks/."""
    all_articles = []
    for filename in os.listdir(CHUNKS_DIR):
        if filename.endswith(".json"):
            path = os.path.join(CHUNKS_DIR, filename)
            with open(path, encoding="utf-8") as f:
                articles = json.load(f)
                all_articles.extend(articles)
    return all_articles


def chunked(items, size):
    """Split a list into smaller lists of at most `size` items each."""
    for i in range(0, len(items), size):
        yield items[i:i + size]


def main():
    client = QdrantClient(url="http://localhost:6333")

    articles = load_all_articles()
    total = len(articles)
    print(f"Loaded {total} articles from {CHUNKS_DIR}")
    print(f"Processing in batches of {BATCH_SIZE}\n")

    start_time = time.time()
    processed = 0

    for batch in chunked(articles, BATCH_SIZE):
        texts = [a["text"] for a in batch]
        embeddings = get_embeddings_batch(texts)

        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload=article,
            )
            for article, embedding in zip(batch, embeddings)
        ]

        client.upsert(collection_name=COLLECTION_NAME, points=points)

        processed += len(batch)
        elapsed = time.time() - start_time
        rate = processed / elapsed
        remaining = (total - processed) / rate if rate > 0 else 0
        print(f"  [{processed}/{total}] — {rate:.1f} articles/sec — ~{remaining/60:.1f} min remaining")

    print(f"\nDone! Ingested {total} articles in {(time.time() - start_time)/60:.1f} minutes.")


if __name__ == "__main__":
    main()