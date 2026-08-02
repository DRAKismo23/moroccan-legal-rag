import re

with open("data/processed/code_route_ar_2024.txt", encoding="utf-8") as f:
    content = f.read()

idx = content.find("املادة")
word = content[idx:idx + 6]

pattern = re.compile(r'^\s*(\d+)\s+' + re.escape(word) + r'\s*$', re.MULTILINE)
matches = list(pattern.finditer(content))

numbers = [int(m.group(1)) for m in matches]

# Find where numbers go backward or repeat — a sign of false positives
print("Checking for out-of-order or repeated numbers...\n")
for i in range(1, len(numbers)):
    if numbers[i] <= numbers[i-1] - 5:  # allow small dips, catch big jumps backward
        pos = matches[i].start()
        print(f"⚠️  Position {i}: number {numbers[i]} follows {numbers[i-1]} (went backward)")
        print(f"   Context: {repr(content[pos-50:pos+50])}")
        print()