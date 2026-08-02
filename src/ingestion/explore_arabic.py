import re

with open("data/processed/code_route_ar_2024.txt", encoding="utf-8") as f:
    content = f.read()

# Extract the exact word for "Article" directly from the file (avoids
# character-mismatch issues we hit before)
idx = content.find("املادة")
word = content[idx:idx + 6]
print(f"Extracted word: {repr(word)}")

# Test pattern: number, then the word, at start of line
pattern = re.compile(r'^\s*\d+\s+' + re.escape(word) + r'\s*$', re.MULTILINE)
matches = list(pattern.finditer(content))
print(f"Found {len(matches)} article headings matching 'number + word' at start of line")

print("\nFirst 5 matches:")
for m in matches[:5]:
    print(repr(m.group()))

print("\nLast 5 matches:")
for m in matches[-5:]:
    print(repr(m.group()))