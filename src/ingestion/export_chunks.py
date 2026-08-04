import json
import os

from chunk_articles import (
    strip_foreign_excerpts,
    find_content_start,
    trim_trailing_annex,
    split_into_articles,
    split_into_articles_arabic,
    split_into_articles_arabic_penal,
    split_into_articles_arabic_cpp,
    correct_article_numbers,
    validate_articles,
)

OUTPUT_DIR = "data/chunks"


def build_penal_fr():
    with open("data/processed/code_penal_fr_2023.txt", encoding="utf-8") as f:
        content = f.read()
    content = strip_foreign_excerpts(content)
    start_idx = find_content_start(content)
    trimmed = content[start_idx:]
    articles = split_into_articles(trimmed)
    articles = correct_article_numbers(articles)
    return articles


def build_route_ar():
    with open("data/processed/code_route_ar_2024.txt", encoding="utf-8") as f:
        content = f.read()
    content = trim_trailing_annex(content)
    return split_into_articles_arabic(content)


def build_penal_ar():
    with open("data/processed/code_penal_ar_2024.txt", encoding="utf-8") as f:
        content = f.read()
    idx = content.find("الكتاب األول")
    trimmed = content[idx:]
    return split_into_articles_arabic_penal(trimmed)


def build_cpp_ar():
    with open("data/processed/code_procedure_penale_ar_2025.txt", encoding="utf-8") as f:
        content = f.read()
    idx = content.find("الكتاب التمهيدي", 30000)
    trimmed = content[idx:]
    return split_into_articles_arabic_cpp(trimmed)


# Config describing each document: how to build it, and what metadata
# to attach to every article extracted from it.
DOCUMENTS = [
    {
        "id": "code_penal_fr",
        "law_name": "Code Pénal",
        "language": "fr",
        "source_type": "official_primary",
        "builder": build_penal_fr,
        "output_file": "code_penal_fr.json",
    },
    {
        "id": "code_route_ar",
        "law_name": "Code de la Route",
        "language": "ar",
        "source_type": "official_primary",
        "builder": build_route_ar,
        "output_file": "code_route_ar.json",
    },
    {
        "id": "code_penal_ar",
        "law_name": "Code Pénal",
        "language": "ar",
        "source_type": "official_primary",
        "builder": build_penal_ar,
        "output_file": "code_penal_ar.json",
    },
    {
        "id": "code_procedure_penale_ar",
        "law_name": "Code de Procédure Pénale",
        "language": "ar",
        "source_type": "official_primary",
        "builder": build_cpp_ar,
        "output_file": "code_procedure_penale_ar.json",
    },
]


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    summary = []

    for doc in DOCUMENTS:
        print(f"\nBuilding: {doc['law_name']} ({doc['language']})")
        articles = doc["builder"]()

        validate_articles(articles)

        enriched = [
            {
                "article_number": a["number"],
                "text": a["text"],
                "law_name": doc["law_name"],
                "language": doc["language"],
                "source_document": doc["id"],
                "source_type": doc["source_type"],
            }
            for a in articles
        ]

        output_path = os.path.join(OUTPUT_DIR, doc["output_file"])
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(enriched, f, ensure_ascii=False, indent=2)

        print(f"Saved {len(enriched)} articles -> {output_path}")
        summary.append((doc["law_name"], doc["language"], len(enriched)))

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    total = 0
    for name, lang, count in summary:
        print(f"  {name} ({lang}): {count} articles")
        total += count
    print(f"\nTotal articles across all documents: {total}")


if __name__ == "__main__":
    main()