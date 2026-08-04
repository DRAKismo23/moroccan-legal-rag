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


def trim_trailing_annex(text, marker="--- PAGE 126 ---"):
    """
    Some documents include transitional/amendment provisions after the
    final article, with no article numbering of their own. We trim this
    off so it doesn't pollute the last real article's content.

    NOTE: this marker is specific to the Code de la Route — other
    documents need their own trailing-annex check, not this exact marker.
    """
    idx = text.find(marker)
    if idx == -1:
        return text
    removed_length = len(text) - idx
    print(f"🗑️  Trimmed {removed_length} characters of trailing annex content (after '{marker}')")
    return text[:idx]


def split_into_articles(text):
    """
    Splits FRENCH legal text into a list of (article_number, article_text)
    dicts. Only matches real article headings: capital 'Article', at the
    start of a line, followed by 'premier' or a number.
    """
    pattern = re.compile(r'^Article\s+(premier|\d+)\s*$', re.MULTILINE)

    matches = list(pattern.finditer(text))
    articles = []

    for i, match in enumerate(matches):
        article_number = match.group(1)
        start_pos = match.end()

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


def split_into_articles_arabic(text, article_word="املادة"):
    """
    Splits the ARABIC Code de la Route into articles. This document
    extracts with the NUMBER BEFORE the word (e.g. '5 المادة' instead
    of 'المادة 5'), and may have leading whitespace before the number.
    """
    pattern = re.compile(r'^\s*(\d+)\s+' + re.escape(article_word) + r'\s*$', re.MULTILINE)

    matches = list(pattern.finditer(text))
    articles = []

    for i, match in enumerate(matches):
        article_number = match.group(1)
        start_pos = match.end()

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


def split_into_articles_arabic_penal(text, base_word="الفصل"):
    """
    Splits the ARABIC Code Pénal into articles. This document has its own
    distinct quirks:
      - Uses 'الفصل' instead of 'المادة' for "Article"
      - Uses WORD-before-number ordering, with RTL-reversed compound
        numbers for inserted articles (e.g. raw '1-1-218' means '218-1-1')
      - Has 'bis'/'ter' articles marked with 'مكرر' / 'مكرر مرتين', which
        often have a footnote number glued directly onto them with no space
      - One specific article (content: abortion exemption provisions) has
        its real number obscured by a footnote/page-number collision in
        the source PDF and could not be reliably recovered; it is flagged
        explicitly rather than guessed, so it never silently collides with
        a real article number
      - Some articles (e.g. 169) repeat their own heading mid-article as
        a formatting quirk; consecutive same-numbered matches are merged
    """
    pattern = re.compile(
        r'^\s*' + re.escape(base_word) +
        r'(\d+(?:\s*-\s*\d+)*)'
        r'(\s*ال?\s*مكرر(?:\s*مرتين)?)?'
        r'\d*'  # consume (and discard) a footnote number glued onto the bis marker
        r'\s*$',
        re.MULTILINE
    )
    matches = list(pattern.finditer(text))

    def build_number(m):
        nums = re.findall(r'\d+', m.group(1))
        nums.reverse()
        base = "-".join(nums)
        if m.group(2):
            base += "-ter" if "مرتين" in m.group(2) else "-bis"
        return base

    # Filter out obvious mid-sentence references
    candidates = []
    for m in matches:
        num = build_number(m)
        after = text[m.end():m.end() + 20].lstrip()
        after_no_newline = after.replace("\n", "")

        is_reference = (
            after[:1] in ".،"
            or after_no_newline.startswith("أعاله")
            or after.startswith("من هذا")
            or after.startswith("وذلك")
            or bool(re.match(r'^فقرة\s*\d', after))
        )
        if is_reference:
            continue

        # This specific document has one article (content: abortion
        # exemption provisions) whose real number could not be reliably
        # recovered due to a footnote/page-number collision in the source
        # PDF. Rather than guess, we flag it explicitly for manual review
        # so it never silently collides with or displaces a real article.
        if num == "53" and "اإلجهاض" in text[m.end():m.end() + 200]:
            print("⚠️  Flagging unresolved article number (content: abortion provisions)")
            num = "53-UNRESOLVED-see-source"

        candidates.append((num, m))

    # Build final article list, merging consecutive same-numbered matches
    # (handles cases like Article 169 repeating its own heading mid-article)
    articles = []
    i = 0
    while i < len(candidates):
        num, m = candidates[i]
        start_pos = m.end()

        j = i + 1
        while j < len(candidates) and candidates[j][0] == num:
            j += 1

        end_pos = candidates[j][1].start() if j < len(candidates) else len(text)
        article_text = text[start_pos:end_pos].strip()

        articles.append({"number": num, "text": article_text})
        i = j

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
        expected = i + 1

        if raw_num == "premier":
            corrected.append({**article, "number": "premier", "raw_number": raw_num})
            continue

        num_value = int(raw_num)

        if abs(num_value - expected) <= tolerance:
            corrected.append({**article, "number": raw_num, "raw_number": raw_num})
        else:
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

        leading_digits = re.match(r'\d+', num)
        num_value = 1 if num == "premier" else (int(leading_digits.group()) if leading_digits else 0)

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
    print("=" * 60)
    print("PROCESSING: Code Pénal (French)")
    print("=" * 60)

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

    print("\n\n" + "=" * 60)
    print("PROCESSING: Code de la Route (Arabic)")
    print("=" * 60)

    with open("data/processed/code_route_ar_2024.txt", encoding="utf-8") as f:
        ar_content = f.read()

    ar_content = trim_trailing_annex(ar_content)

    ar_articles = split_into_articles_arabic(ar_content)
    print(f"Total articles found: {len(ar_articles)}")

    print("\n--- First article ---")
    print(f"Number: {ar_articles[0]['number']}")
    print(f"Text: {ar_articles[0]['text'][:200]}")

    print("\n--- Last article ---")
    print(f"Number: {ar_articles[-1]['number']}")
    print(f"Text: {ar_articles[-1]['text'][:200]}")

    validate_articles(ar_articles)

    print("\n\n" + "=" * 60)
    print("PROCESSING: Code Pénal (Arabic)")
    print("=" * 60)

    with open("data/processed/code_penal_ar_2024.txt", encoding="utf-8") as f:
        penal_ar_content = f.read()

    book_one_idx = penal_ar_content.find("الكتاب األول")
    penal_ar_trimmed = penal_ar_content[book_one_idx:]

    penal_ar_articles = split_into_articles_arabic_penal(penal_ar_trimmed)
    print(f"Total articles found: {len(penal_ar_articles)}")

    print("\n--- First article ---")
    print(f"Number: {penal_ar_articles[0]['number']}")
    print(f"Text: {penal_ar_articles[0]['text'][:150]}")

    print("\n--- Last article ---")
    print(f"Number: {penal_ar_articles[-1]['number']}")
    print(f"Text: {penal_ar_articles[-1]['text'][:150]}")

    validate_articles(penal_ar_articles)