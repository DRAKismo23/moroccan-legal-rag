import json
import os
import re

from rank_bm25 import BM25Okapi

CHUNKS_DIR = "data/chunks"


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


def simple_tokenize(text):
    """Basic tokenizer: lowercase, split on whitespace and punctuation.
    Works reasonably for both French and Arabic as a starting point."""
    text = text.lower()
    tokens = re.findall(r'\w+', text, re.UNICODE)
    return tokens


def build_bm25_index(articles):
    tokenized_corpus = [simple_tokenize(a["text"]) for a in articles]
    bm25 = BM25Okapi(tokenized_corpus)
    return bm25


if __name__ == "__main__":
    print("Loading articles...")
    articles = load_all_articles()
    print(f"Loaded {len(articles)} articles")

    print("Building BM25 index...")
    bm25 = build_bm25_index(articles)
    print("Index built successfully")

    # Quick test query
    query = "peine de mort"
    tokenized_query = simple_tokenize(query)

    scores = bm25.get_scores(tokenized_query)

    # Get top 3 results
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:3]

    print(f"\nQuery: '{query}'")
    for idx in top_indices:
        article = articles[idx]
        print(f"\nScore: {scores[idx]:.3f}")
        print(f"Article {article['article_number']} ({article['law_name']}, {article['language']})")
        print(f"Text: {article['text'][:150]}")