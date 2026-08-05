import sys
sys.path.insert(0, "src/ingestion")
sys.path.insert(0, "src/retrieval")

from test_search import search as semantic_search
from bm25_search import load_all_articles, build_bm25_index, simple_tokenize

query = "peine de mort"

print("=" * 60)
print("SEMANTIC SEARCH (dense vectors)")
print("=" * 60)
semantic_results = semantic_search(query, top_k=3)
for r in semantic_results:
    print(f"\nScore: {r.score:.3f}")
    print(f"Article {r.payload['article_number']} ({r.payload['law_name']}, {r.payload['language']})")
    print(f"Text: {r.payload['text'][:150]}")

print("\n\n" + "=" * 60)
print("BM25 SEARCH (keyword matching)")
print("=" * 60)
articles = load_all_articles()
bm25 = build_bm25_index(articles)
tokenized_query = simple_tokenize(query)
scores = bm25.get_scores(tokenized_query)
top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:3]
for idx in top_indices:
    article = articles[idx]
    print(f"\nScore: {scores[idx]:.3f}")
    print(f"Article {article['article_number']} ({article['law_name']}, {article['language']})")
    print(f"Text: {article['text'][:150]}")