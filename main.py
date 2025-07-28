import fitz  # PyMuPDF
import os
import re
import json
import collections

def merge_and_clean_spans(spans):
    merged = []
    for span in spans:
        span['bold'] = (span.get('flags', 0) & 2) != 0
        if merged and span['font'] == merged[-1]['font'] and abs(span['size'] - merged[-1]['size']) < 0.1 and abs(merged[-1]['bbox'][2] - span['bbox'][0]) < 10:
            merged[-1]['text'] += span['text']
            merged[-1]['bbox'] = [
                min(merged[-1]['bbox'][0], span['bbox'][0]),
                min(merged[-1]['bbox'][1], span['bbox'][1]),
                max(merged[-1]['bbox'][2], span['bbox'][2]),
                max(merged[-1]['bbox'][3], span['bbox'][3]),
            ]
            merged[-1]['bold'] = merged[-1]['bold'] or span['bold']
        else:
            merged.append(span.copy())
    return merged

def extract_lines(pdf_path):
    doc = fitz.open(pdf_path)
    lines = []
    for page_num, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                spans = merge_and_clean_spans(line["spans"])
                if not spans:
                    continue
                text = ''.join(span['text'] for span in spans).strip()
                if not text:
                    continue
                size, font = spans[0]['size'], spans[0]['font']
                lines.append({
                    'text': text,
                    'font_size': size,
                    'font_name': font,
                    'page_num': page_num,
                    'bbox': line['bbox'],
                    'page_width': page.rect.width,
                    'spans': spans
                })
    doc.close()
    return lines

def detect_body_style(lines):
    counter = collections.Counter((line['font_size'], line['font_name']) for line in lines if line['font_size'])
    (size, font), _ = counter.most_common(1)[0]
    return {'font_size': size, 'font_name': font}

def is_heading_candidate(line, body):
    text = line['text']
    size = line['font_size']
    width = line['page_width']
    if not text or size is None:
        return False
    if len(text) < 10:
        return False
    if sum(c.isalpha() for c in text) / max(len(text), 1) < 0.6:
        return False
    if re.search(r'(\w)\1{2,}', text):
        return False
    if re.match(r'^[a-zA-Z]\)$', text) or re.match(r'^\(\d+\)$', text):
        return False
    if text[-1] in '.۔؟' and not re.match(r'^\d+(\.\d+)*', text):
        return False

    bold = any(span.get('bold') for span in line.get('spans', []))
    concise = (line['bbox'][2] - line['bbox'][0]) < width * 0.9
    large = size > body['font_size'] * 1.1
    no_dot = not text.endswith('.')

    if large and concise and no_dot and (bold or size > body['font_size'] * 1.2):
        return True
    return False

def assign_heading_levels(headings):
    sizes = sorted({h['font_size'] for h in headings}, reverse=True)
    size_map = {s: f"H{i+1}" for i, s in enumerate(sizes[:3])}

    for h in headings:
        if h['font_size'] in size_map:
            h['level'] = size_map[h['font_size']]
        if re.match(r'^(\d+\.)+\d*', h['text']):
            depth = h['text'].count('.')
            h['level'] = f"H{min(3, depth+1)}"
    return [h for h in headings if 'level' in h]

def extract_best_title(pdf_path, lines):
    doc = fitz.open(pdf_path)
    if doc.metadata and doc.metadata.get('title') and len(doc.metadata['title'].strip()) > 10:
        return doc.metadata['title'].strip()
    candidates = [l for l in lines if l['page_num'] == 1]
    for line in sorted(candidates, key=lambda x: -x['font_size']):
        if any(s.get('bold') for s in line['spans']) and abs((line['bbox'][0] + line['bbox'][2]) / 2 - line['page_width'] / 2) < line['page_width'] * 0.25:
            return line['text'].strip()
    for line in candidates:
        if len(line['text']) > 20 and sum(c.isalpha() for c in line['text']) / len(line['text']) > 0.5:
            return line['text'].strip()
    return "Untitled"

def process_pdf(pdf_path):
    lines = extract_lines(pdf_path)
    if not lines:
        return None

    body_style = detect_body_style(lines)
    heading_lines = [l for l in lines if is_heading_candidate(l, body_style)]
    labeled = assign_heading_levels(heading_lines)
    outline = [
        {"level": h["level"], "text": h["text"], "page": h["page_num"]}
        for h in labeled
        if h["level"] in ["H1", "H2", "H3"]
    ]
    title = extract_best_title(pdf_path, heading_lines or lines)
    return {
        "title": title,
        "outline": outline
    }

def main():
    input_dir = os.environ.get("INPUT_DIR", "input")
    output_dir = os.environ.get("OUTPUT_DIR", "output")
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    found = False
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            found = True
            path = os.path.join(input_dir, filename)
            print(f"Processing {filename}...")
            result = process_pdf(path)
            if result:
                out_name = os.path.splitext(filename)[0] + ".json"
                out_path = os.path.join(output_dir, out_name)
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"Done: {out_name}")
    if not found:
        print(f"No PDFs found in {input_dir}")

if __name__ == "__main__":
    main()
