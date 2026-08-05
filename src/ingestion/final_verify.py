from qdrant_client import QdrantClient
from collections import Counter

client = QdrantClient(url="http://localhost:6333")

info = client.get_collection("moroccan_legal_articles")
print(f"Total vectors in collection: {info.points_count}")

# Fetch all points to check the breakdown by law/language
points, _ = client.scroll(collection_name="moroccan_legal_articles", limit=3000)

breakdown = Counter((p.payload["law_name"], p.payload["language"]) for p in points)

print("\nBreakdown by law and language:")
for (law, lang), count in sorted(breakdown.items()):
    print(f"  {law} ({lang}): {count} articles")

print(f"\nTotal points fetched: {len(points)}")