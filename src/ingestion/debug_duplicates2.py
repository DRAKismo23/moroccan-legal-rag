with open("data/processed/code_penal_fr_2023.txt", encoding="utf-8") as f:
    content = f.read()

idx = content.find("DISPOSITIONS PRELIMINAIRES")
trimmed = content[idx:]

import re

for target_num in ["316", "331"]:
    pattern = re.compile(r'^Article\s+' + target_num + r'\s*$', re.MULTILINE)
    matches = list(pattern.finditer(trimmed))
    print(f"=== 'Article {target_num}' found {len(matches)} times ===")
    for m in matches:
        pos = m.start()
        print(f"--- Occurrence at position {pos} ---")
        print(trimmed[pos:pos+200])
        print()