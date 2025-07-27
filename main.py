

import os
import json
import fitz  # PyMuPDF

INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"

def extract_outline(pdf_path):
    doc = fitz.open(pdf_path)
    font_data = []  # (size, bold, text, page_num, x_position, y_position)

    for page_num, page in enumerate(doc, start=1):
        page_dict = page.get_text("dict")
        for block in page_dict.get("blocks", []):
            if block.get("type", 0) != 0:  # Skip non-text blocks
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "").strip()
                    if not text:
                        continue
                    size = span.get("size", 0)
                    font_flags = span.get("flags", 0)
                    bold = bool(font_flags & 2)  # flag 2 = bold
                    x0, y0, x1, y1 = span.get("bbox", [0, 0, 0, 0])
                    font_data.append((size, bold, text, page_num, x0, y0))

    # Title heuristic: largest bold/centered text on page 1
    page1_data = [f for f in font_data if f[3] == 1]
    title = ""
    if page1_data:
        title = max(page1_data, key=lambda x: (x[0], x[1]))[2]

    # Unique font sizes sorted
    unique_sizes = sorted({f[0] for f in font_data}, reverse=True)
    size_to_level = {}
    levels = ["H1", "H2", "H3"]
    for lvl, size in zip(levels, unique_sizes):
        size_to_level[size] = lvl

    # Outline building
    outline = []
    seen = set()
    for size, bold, text, page_num, _, _ in font_data:
        if len(text.split()) > 10:  # Skip long paragraphs
            continue
        level = size_to_level.get(size)
        if not level:
            continue
        key = (level, text, page_num)
        if key not in seen:
            seen.add(key)
            outline.append({"level": level, "text": text, "page": page_num})

    return {"title": title, "outline": outline}

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for file in os.listdir(INPUT_DIR):
        if file.lower().endswith(".pdf"):
            pdf_path = os.path.join(INPUT_DIR, file)
            data = extract_outline(pdf_path)
            out_path = os.path.join(OUTPUT_DIR, file[:-4] + ".json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()



