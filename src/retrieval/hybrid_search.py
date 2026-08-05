import sys
sys.path.insert(0, "src/ingestion")
sys.path.insert(0, "src/retrieval")

from test_search import search as semantic_search, get_embedding
from bm25_search import load_all_articles, build_bm25_index, simple_tokenize

# Load once at module level - reused across searches
print("Loading articles and building BM25 index (one-time setup)...")
ARTICLES = load_all_articles()
BM25_INDEX = build_bm25_index(ARTICLES)
print(f"Ready. {len(ARTICLES)} articles indexed.\n")


def bm25_search(query, top_k=10):
    """Returns list of (article, score) tuples, sorted best first."""
    tokenized_query = simple_tokenize(query)
    scores = BM25_INDEX.get_scores(tokenized_query)
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    return [(ARTICLES[i], scores[i]) for i in top_indices]


def dense_search(query, top_k=10):
    """Returns list of (article, score) tuples, sorted best first."""
    results = semantic_search(query, top_k=top_k)
    return [(r.payload, r.score) for r in results]


def reciprocal_rank_fusion(dense_results, bm25_results, k=60):
    """
    Combines two ranked lists using Reciprocal Rank Fusion.
    Each article gets a fused score based on its RANK (position) in each
    list, not raw scores - this avoids issues comparing incompatible scales
    (BM25 scores vs cosine similarity scores).

    k=60 is a standard, well-tested constant from the original RRF paper.
    """
    fused_scores = {}
    article_lookup = {}

    for rank, (article, _score) in enumerate(dense_results):
        key = (article["source_document"], article["article_number"])
        fused_scores[key] = fused_scores.get(key, 0) + 1 / (k + rank + 1)
        article_lookup[key] = article

    for rank, (article, _score) in enumerate(bm25_results):
        key = (article["source_document"], article["article_number"])
        fused_scores[key] = fused_scores.get(key, 0) + 1 / (k + rank + 1)
        article_lookup[key] = article

    ranked = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    return [(article_lookup[key], score) for key, score in ranked]


def hybrid_search(query, top_k=5, candidates_per_method=15):
    dense_results = dense_search(query, top_k=candidates_per_method)
    bm25_results = bm25_search(query, top_k=candidates_per_method)
    fused = reciprocal_rank_fusion(dense_results, bm25_results)
    return fused[:top_k]


if __name__ == "__main__":
    query = "peine de mort"
    print(f"Query: '{query}'\n")

    results = hybrid_search(query)
    for article, score in results:
        print(f"Fused score: {score:.4f}")
        print(f"Article {article['article_number']} ({article['law_name']}, {article['language']})")
        print(f"Text: {article['text'][:150]}")
        print()