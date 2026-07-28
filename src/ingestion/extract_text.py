import fitz
import os

RAW_FOLDER = "data/raw"
PROCESSED_FOLDER = "data/processed"

def extract_pdf_to_text(pdf_path, output_path):
    """Extract all text from a PDF, page by page, with page markers."""
    doc = fitz.open(pdf_path)
    
    all_text = []
    for page_num in range(len(doc)):
        page_text = doc[page_num].get_text()
        marker = f"\n--- PAGE {page_num + 1} ---\n"
        all_text.append(marker + page_text)
    
    full_text = "".join(all_text)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    
    return len(doc), len(full_text)


def main():
    for filename in os.listdir(RAW_FOLDER):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(RAW_FOLDER, filename)
            
            # Turn "code_route_ar_2024.pdf" into "code_route_ar_2024.txt"
            txt_filename = filename.replace(".pdf", ".txt")
            output_path = os.path.join(PROCESSED_FOLDER, txt_filename)
            
            print(f"Processing {filename}...")
            num_pages, char_count = extract_pdf_to_text(pdf_path, output_path)
            print(f"  → Saved {output_path} ({num_pages} pages, {char_count} characters)")


if __name__ == "__main__":
    main()