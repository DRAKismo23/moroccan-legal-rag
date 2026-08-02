with open("data/processed/code_route_ar_2024.txt", encoding="utf-8") as f:
    content = f.read()

idx = content.find("املادة")
word = content[idx:idx + 6]

import re
pattern = re.compile(r'^\s*318\s+' + re.escape(word), re.MULTILINE)
m = pattern.search(content)
print(content[m.start():])