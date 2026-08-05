import sys
sys.path.insert(0, "src/ingestion")
sys.path.insert(0, "src/retrieval")

from sentence_transformers import CrossEncoder
from hybrid_search import hybrid_search

print("Loading reranker model...")
RERANKER = CrossEncoder("BAAI/bge-reranker-v2-m3")
print("Ready.\n")


def rerank(query, candidates, top_k=3):
    """
    Takes a list of (article, score) tuples from hybrid search and
    re-scores each one using the cross-encoder reranker for final,
    precise relevance ranking.
    """
    pairs = [[query, article["text"]] for article, _ in candidates]
    rerank_scores = RERANKER.predict(pairs)

    reranked = sorted(
        zip([a for a, _ in candidates], rerank_scores),
        key=lambda x: x[1],
        reverse=True
    )
    return reranked[:top_k]


def full_search(query, hybrid_candidates=15, final_top_k=3):
    """The complete pipeline: hybrid retrieval -> cross-encoder reranking."""
    candidates = hybrid_search(query, top_k=hybrid_candidates)
    return rerank(query, candidates, top_k=final_top_k)


if __name__ == "__main__":
    query = "Quelle est la sanction pour un excès de vitesse important ?"
    print(f"Query: '{query}'\n")

    results = full_search(query)
    for article, score in results:
        print(f"Rerank score: {score:.4f}")
        print(f"Article {article['article_number']} ({article['law_name']}, {article['language']})")
        print(f"Text: {article['text'][:400]}")
        print()