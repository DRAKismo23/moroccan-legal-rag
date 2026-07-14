import fitz
import os

raw_folder = "data/raw"

for filename in os.listdir(raw_folder):
    if filename.endswith(".pdf"):
        filepath = os.path.join(raw_folder, filename)
        doc = fitz.open(filepath)
        
        print(f"\n📄 {filename}")
        print(f"   Total pages: {len(doc)}")
        
        # Check the first 5 pages instead of just page 1
        pages_to_check = min(5, len(doc))
        
        for page_num in range(pages_to_check):
            text = doc[page_num].get_text()
            char_count = len(text.strip())
            status = "✅ text" if char_count >= 20 else "⚠️  low/no text"
            print(f"   Page {page_num + 1}: {char_count} characters — {status}")