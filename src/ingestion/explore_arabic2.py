with open("data/processed/code_route_ar_2024.txt", encoding="utf-8") as f:
    content = f.read()

idx = content.find("املادة")
word = content[idx:idx + 6]

# Find where "3 المادة" appears, using simple search (not our strict regex)
import re
pattern = re.compile(r'3\s*' + re.escape(word))
matches = list(pattern.finditer(content))

print(f"Found {len(matches)} loose matches for '3 + word'")
for m in matches[:3]:
    pos = m.start()
    print(repr(content[pos-20:pos+30]))
    print()