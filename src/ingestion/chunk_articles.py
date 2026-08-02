import re


# Known foreign-code excerpts embedded within this specific document.
# Each entry marks exact start/end anchor text; everything between them
# gets removed before we chunk into articles, since it belongs to a
# DIFFERENT legal code and would otherwise be mislabeled as Code Pénal.
FOREIGN_EXCERPTS = [
    {
        "after": "Bulletin Officiel n° 4418 du 19 joumada I 1417 (3 octobre 1996), p. 568.",
        "before": "52- Les dispositions du chapitre premier bis",
        "reason": "Inline quotation of Code de Commerce Articles 316 & 331"
    },
]


def strip_foreign_excerpts(text):
    """Removes known embedded excerpts from OTHER legal codes, so they
    never get mistaken for real Code Pénal articles."""
    for excerpt in FOREIGN_EXCERPTS:
        start_idx = text.find(excerpt["after"])
        end_idx = text.find(excerpt["before"])

        if start_idx == -1 or end_idx == -1:
            print(f"⚠️  Could not locate excerpt markers for: {excerpt['reason']}")
            continue

        start_idx += len(excerpt["after"])
        removed_length = end_idx - start_idx

        print(f"🗑️  Removing {removed_length} characters: {excerpt['reason']}")
        text = text[:start_idx] + text[end_idx:]

    return text


def find_content_start(text, marker="DISPOSITIONS PRELIMINAIRES"):
    """
    Legal PDFs often include a Dahir (enacting decree) before the actual
    code text. We find the first occurrence of a marker phrase that reliably
    signals where the real substantive content begins, and discard everything
    before it.
    """
    idx = text.find(marker)
    if idx == -1:
        print(f"⚠️  Warning: marker '{marker}' not found — using full text")
        return 0
    return idx


def split_into_articles(text):
    """
    Splits legal text into a list of (article_number, article_text) dicts.
    Only matches real article headings: capital 'Article', at the start of
    a line, followed by 'premier' or a number.
    """
    pattern = re.compile(r'^Article\s+(premier|\d+)\s*$', re.MULTILINE)

    matches = list(pattern.finditer(text))
    articles = []

    for i, match in enumerate(matches):
        article_number = match.group(1)
        start_pos = match.end()  # content starts right after the heading

        # The article's content ends where the NEXT article begins
        # (or at the end of the whole text, for the very last article)
        if i + 1 < len(matches):
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(text)

        article_text = text[start_pos:end_pos].strip()
        articles.append({
            "number": article_number,
            "text": article_text
        })

    return articles


def correct_article_numbers(articles, tolerance=50):
    """
    Fixes article numbers that got a footnote reference digit-glued onto
    them during PDF extraction (e.g. 'Article 231' + footnote '68' = '23168').

    Uses each article's POSITION in the list (not the previous corrected
    value) as a stable reference point, so one wrong correction can never
    cascade into corrupting later ones.
    """
    corrected = []

    for i, article in enumerate(articles):
        raw_num = article["number"]
        expected = i + 1  # rough guess: article at position i is roughly "i+1"

        if raw_num == "premier":
            corrected.append({**article, "number": "premier", "raw_number": raw_num})
            continue

        num_value = int(raw_num)

        if abs(num_value - expected) <= tolerance:
            # Close enough to what we'd expect at this position — trust it
            corrected.append({**article, "number": raw_num, "raw_number": raw_num})
        else:
            # Try trimming trailing digits to find something close to "expected"
            raw_str = str(num_value)
            fixed = None
            for cut in range(len(raw_str) - 1, 0, -1):
                candidate = int(raw_str[:cut])
                if abs(candidate - expected) <= tolerance:
                    fixed = candidate
                    break

            if fixed is not None:
                print(f"🔧 Corrected '{raw_num}' → '{fixed}' (position {i}, expected ~{expected})")
                corrected.append({**article, "number": str(fixed), "raw_number": raw_num})
            else:
                print(f"⚠️  Could not auto-correct: '{raw_num}' (position {i}, expected ~{expected}) — leaving as-is")
                corrected.append({**article, "number": raw_num, "raw_number": raw_num})

    return corrected


def validate_articles(articles, max_reasonable_number=1000):
    """
    Sanity-checks our extracted articles to catch chunking bugs early,
    rather than silently shipping corrupted data into embeddings.
    """
    issues = []
    seen_numbers = set()

    for article in articles:
        num = article["number"]

        # Convert "premier" to 1 for numeric comparison
        num_value = 1 if num == "premier" else int(num)

        if num_value > max_reasonable_number:
            issues.append(f"⚠️  Suspiciously large article number: {num}")

        if num in seen_numbers:
            issues.append(f"⚠️  Duplicate article number: {num}")
        seen_numbers.add(num)

        if len(article["text"]) < 5:
            issues.append(f"⚠️  Article {num} has suspiciously little text ({len(article['text'])} chars)")

    if issues:
        print(f"\n🚨 Found {len(issues)} validation issues:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✅ All articles passed validation checks")

    return issues


if __name__ == "__main__":
    with open("data/processed/code_penal_fr_2023.txt", encoding="utf-8") as f:
        content = f.read()

    content = strip_foreign_excerpts(content)

    start_idx = find_content_start(content)
    trimmed = content[start_idx:]

    articles = split_into_articles(trimmed)
    print(f"Total articles found: {len(articles)}\n")

    articles = correct_article_numbers(articles)

    print("\n--- First article ---")
    print(f"Number: {articles[0]['number']}")
    print(f"Text: {articles[0]['text'][:300]}")

    print("\n--- Last article ---")
    print(f"Number: {articles[-1]['number']}")
    print(f"Text: {articles[-1]['text'][:300]}")

    validate_articles(articles)