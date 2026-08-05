from qdrant_client import QdrantClient
import requests

client = QdrantClient(url="http://localhost:6333")


def get_embedding(text):
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={"model": "bge-m3", "prompt": text}
    )
    response.raise_for_status()
    return response.json()["embedding"]


def search(query, top_k=3):
    query_vector = get_embedding(query)
    results = client.query_points(
        collection_name="moroccan_legal_articles",
        query=query_vector,
        limit=top_k,
    )
    return results.points


if __name__ == "__main__":
    query = "Quelles sont les peines pour un crime?"
    print(f"Query: {query}\n")

    results = search(query)
    for r in results:
        print(f"Score: {r.score:.3f}")
        print(f"Article {r.payload['article_number']} ({r.payload['law_name']}, {r.payload['language']})")
        print(f"Text: {r.payload['text'][:150]}")
        print()