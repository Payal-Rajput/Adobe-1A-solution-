

# Multilingual Handling



import os
import json
import re
import unicodedata
import fitz  # PyMuPDF

INPUT_DIR = "/app/input"
OUTPUT_DIR = "/app/output"

JP_CHARS_RE = re.compile(r"[ぁ-ゔァ-ヴー々〆〤一-龯]")
JP_HEAD_RE_LIST = [
    re.compile(r"^第[０-９0-9一二三四五六七八九十百千]+章$"),
    re.compile(r"^第[０-９0-9一二三四五六七八九十百千]+節$"),
    re.compile(r"^第[０-９0-9一二三四五六七八九十百千]+条$"),
]

ASCII_HEAD_RE_LIST = [
    re.compile(r"^\d+(\.\d+)*\s+.+$"),  # 1, 1.1, 1.1.1 ...
    re.compile(r"^[A-Z]\.\s+.+$"),     # A. Something
    re.compile(r"^[IVXLC]+\.?\s+.+$", re.IGNORECASE),  # I, II, III ...
]

LEVELS = ["H1", "H2", "H3"]

def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFKC", text).strip()

def is_japanese(text: str) -> bool:
    return bool(JP_CHARS_RE.search(text))

def looks_like_japanese_heading(text: str) -> bool:
    return any(pat.match(text) for pat in JP_HEAD_RE_LIST)

def looks_like_ascii_heading(text: str) -> bool:
    return any(pat.match(text) for pat in ASCII_HEAD_RE_LIST)

def is_heading_candidate(text: str, lang_jp: bool) -> bool:
    # length-based heuristic (no spaces in JP)
    if lang_jp:
        if len(text) > 80:  # likely a paragraph
            return False
        if looks_like_japanese_heading(text):
            return True
        # fallback: short-ish bold-ish lines will still pass via font-size later
        return True
    else:
        if len(text.split()) > 12:  # your original 10, made a bit softer
            return False
        if looks_like_ascii_heading(text):
            return True
        return True

def map_sizes_to_levels(sizes, top_n=3):
    """
    Map the top_n largest *distinct* font sizes to H1..H(top_n)
    Everything else returns None (ignored) to reduce noise.
    """
    unique_sizes = sorted(set(sizes), reverse=True)
    size_to_level = {}
    for i, size in enumerate(unique_sizes[:top_n]):
        size_to_level[size] = LEVELS[i] if i < len(LEVELS) else f"H{i+1}"
    return size_to_level

def extract_outline(pdf_path):
    doc = fitz.open(pdf_path)

    # 0) Try the built-in TOC first
    toc = doc.get_toc(simple=True)  # [[level, title, page], ...]
    if toc:
        # Normalize and emit
        title_guess = ""
        if toc and len(toc) > 0:
            title_guess = normalize_text(toc[0][1])
        outline = []
        for lvl, txt, page in toc:
            txt_n = normalize_text(txt)
            outline.append({
                "level": f"H{min(lvl, 6)}",
                "text": txt_n,
                "page": page
            })
        return {"title": title_guess, "outline": outline}

    # 1) Collect spans
    font_data = []  # (size, bold, text, page_num, x0, y0)
    all_text_snippet = []

    for page_num, page in enumerate(doc, start=1):
        page_dict = page.get_text("dict")
        for block in page_dict.get("blocks", []):
            if block.get("type", 0) != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    raw_text = span.get("text", "")
                    text = normalize_text(raw_text)
                    if not text:
                        continue
                    size = span.get("size", 0)
                    font_flags = span.get("flags", 0)
                    bold = bool(font_flags & 2)
                    x0, y0, x1, y1 = span.get("bbox", [0, 0, 0, 0])
                    font_data.append((size, bold, text, page_num, x0, y0))
                    if len(all_text_snippet) < 5000:
                        all_text_snippet.append(text)

    merged_snippet = "".join(all_text_snippet[:5000])
    lang_jp = is_japanese(merged_snippet)

    # 2) Title heuristic: largest bold/centered-ish text on page 1
    page1_data = [f for f in font_data if f[3] == 1]
    title = ""
    if page1_data:
        # If JP, prioritize lines that match Japanese heading patterns for title fallback
        if lang_jp:
            jp_candidates = [f for f in page1_data if looks_like_japanese_heading(f[2])]
            if jp_candidates:
                title = max(jp_candidates, key=lambda x: (x[0], x[1]))[2]
        if not title:
            title = max(page1_data, key=lambda x: (x[0], x[1]))[2]

    # 3) Map sizes to heading levels
    all_sizes = [f[0] for f in font_data]
    size_to_level = map_sizes_to_levels(all_sizes, top_n=3)

    # 4) Build outline
    outline = []
    seen = set()

    for size, bold, text, page_num, _, _ in font_data:
        if not is_heading_candidate(text, lang_jp):
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
