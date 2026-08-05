from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

COLLECTION_NAME = "moroccan_legal_articles"
VECTOR_SIZE = 1024  # BGE-M3's embedding dimension, confirmed in our test


def main():
    client = QdrantClient(url="http://localhost:6333")

    # Check if the collection already exists
    existing_collections = [c.name for c in client.get_collections().collections]

    if COLLECTION_NAME in existing_collections:
        print(f"Collection '{COLLECTION_NAME}' already exists.")
    else:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
        )
        print(f"Created collection '{COLLECTION_NAME}' (size={VECTOR_SIZE}, distance=COSINE)")

    # Confirm it worked by fetching info about the collection
    info = client.get_collection(COLLECTION_NAME)
    print(f"\nCollection info:")
    print(f"  Vectors count: {info.points_count}")
    print(f"  Vector size: {info.config.params.vectors.size}")
    print(f"  Distance metric: {info.config.params.vectors.distance}")


if __name__ == "__main__":
    main()