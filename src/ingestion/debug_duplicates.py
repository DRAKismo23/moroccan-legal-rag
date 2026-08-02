with open("data/processed/code_penal_fr_2023.txt", encoding="utf-8") as f:
    content = f.read()

idx = content.find("DISPOSITIONS PRELIMINAIRES")
trimmed = content[idx:]

for target in ["Article 316", "Article 331"]:
    pos = trimmed.find(target)
    print(f"--- Context around '{target}' ---")
    print(repr(trimmed[pos-100:pos+150]))
    print()