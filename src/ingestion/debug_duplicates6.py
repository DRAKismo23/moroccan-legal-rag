with open("data/processed/code_penal_fr_2023.txt", encoding="utf-8") as f:
    content = f.read()

idx = content.find("DISPOSITIONS PRELIMINAIRES")
trimmed = content[idx:]

# Print from the start of the embedded "Article 331" section onward,
# to find where it ends and real Code Pénal content resumes
print(trimmed[110975:113000])