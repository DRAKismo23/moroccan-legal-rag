with open("data/processed/code_penal_fr_2023.txt", encoding="utf-8") as f:
    content = f.read()

idx = content.find("DISPOSITIONS PRELIMINAIRES")
trimmed = content[idx:]

# Let's see a wider window before the first "Article 316" to find where
# this Code de Commerce section starts
pos = 108838
print(trimmed[pos-3000:pos+50])