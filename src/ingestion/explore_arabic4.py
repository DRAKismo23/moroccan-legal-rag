import re

with open("data/processed/code_route_ar_2024.txt", encoding="utf-8") as f:
    content = f.read()

idx = content.find("املادة")
word = content[idx:idx + 6]

pattern = re.compile(r'^\s*(\d+)\s+' + re.escape(word) + r'\s*$', re.MULTILINE)
matches = list(pattern.finditer(content))
numbers = [int(m.group(1)) for m in matches]

# Check for duplicates
from collections import Counter
counts = Counter(numbers)
duplicates = {num: count for num, count in counts.items() if count > 1}

print(f"Total matches: {len(numbers)}")
print(f"Unique article numbers: {len(set(numbers))}")
print(f"Duplicate numbers found: {duplicates}")

# Check for gaps in the sequence
expected = set(range(1, max(numbers) + 1))
actual = set(numbers)
missing = sorted(expected - actual)
print(f"\nMissing numbers in sequence 1-{max(numbers)}: {missing}")