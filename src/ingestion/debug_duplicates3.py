import re

with open("data/processed/code_penal_fr_2023.txt", encoding="utf-8") as f:
    content = f.read()

idx = content.find("DISPOSITIONS PRELIMINAIRES")
trimmed = content[idx:]

# Look for section headings (LIVRE, TITRE, CHAPITRE) anywhere before each occurrence
heading_pattern = re.compile(r'^(LIVRE|TITRE|CHAPITRE)\s+.+$', re.MULTILINE)

positions_to_check = [108838, 204203]

for pos in positions_to_check:
    print(f"=== Looking backward from position {pos} ===")
    # Find all headings before this position
    headings_before = [m for m in heading_pattern.finditer(trimmed) if m.start() < pos]
    if headings_before:
        last_heading = headings_before[-1]
        print(f"Nearest section heading: {last_heading.group().strip()}")
    else:
        print("No section heading found before this position")
    print()