with open("data/processed/code_route_ar_2024.txt", encoding="utf-8") as f:
    content = f.read()

# Check what surrounds where Article 136 and Article 138 are 
# (137 should be conspicuously absent between them if genuinely repealed)
idx = content.find("املادة")
word = content[idx:idx + 6]

import re
for num in [136, 138, 220, 222]:
    pattern = re.compile(r'^\s*' + str(num) + r'\s+' + re.escape(word), re.MULTILINE)
    m = pattern.search(content)
    if m:
        pos = m.start()
        print(f"--- Article {num} ---")
        print(content[pos:pos+200])
        print()