with open("data/processed/code_penal_fr_2023.txt", encoding="utf-8") as f:
    content = f.read()

idx = content.find("DISPOSITIONS PRELIMINAIRES")
trimmed = content[idx:]

positions_to_check = [108838, 204203]

for pos in positions_to_check:
    print(f"=========== Full context before position {pos} ===========")
    print(trimmed[pos-1500:pos+50])
    print()