import pymupdf as fitz
import os

def extract_pdf(file_path):
    """
    Extracts pages from a PDF ebook file.
    Filters out margin gutters, headers, footers, and vertical sidebar OCR noise.
    Returns: list of dicts [{'page_number': int, 'chapter': str, 'text': str, 'url': ''}]
    """
    results = []
    if not os.path.exists(file_path):
        return results

    doc = fitz.open(file_path)
    toc = doc.get_toc()  # [[lvl, title, page], ...]
    toc_dict = {}
    for item in toc:
        lvl, title, pno = item[0], item[1], item[2]
        if pno not in toc_dict:
            toc_dict[pno] = title

    # Known noise phrases from digital textbook UI and revision bars
    NOISE_PHRASES = {
        'link to textbook', 'linktotextbook', 'my revision notes',
        'revision notes', 'test yourself', 'exam tip', 'exam practice',
        'key facts', 'specification'
    }

    current_chapter = ""
    for idx, page in enumerate(doc, start=1):
        if idx in toc_dict:
            current_chapter = toc_dict[idx]

        rect = page.rect
        page_width = rect.width
        page_height = rect.height

        blocks = page.get_text("blocks")
        valid_blocks = []

        for b in blocks:
            x0, y0, x1, y1, text, block_no, block_type = b
            if block_type != 0:  # 0 is text
                continue

            # Strip left sidebar gutter (width < 45 on standard pages) where rotated vertical icons live
            if x1 < 45:
                continue
            # Strip top header bar
            if y1 < 22:
                continue
            # Strip bottom footer bar (page numbers, 'My Revision Notes')
            if y0 > (page_height - 35):
                continue

            # Clean lines within block
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            cleaned_lines = []
            for line in lines:
                l_lower = line.lower()
                # Skip single or 2-char tokens or OCR glyph noise
                if len(line) <= 3 and (len(line) <= 2 or not line.isalnum() or l_lower in {'exe', 'oo', '‘p', '©', '>', '=', 'se)', 'wy)', 'see', 'ba?', 'cc', 'y', 'on', 'is', 'iva)', '4"', 'e)', 'hele', '(an'}):
                    continue
                if l_lower in NOISE_PHRASES:
                    continue
                cleaned_lines.append(line)

            block_text = "\n".join(cleaned_lines).strip()
            if len(block_text) > 15:
                valid_blocks.append(block_text)

        text = "\n\n".join(valid_blocks).strip()

        # Fallback OCR for scanned pages if text is sparse
        if len(text) < 30:
            try:
                import pytesseract
                from PIL import Image
                import io
                pix = page.get_pixmap()
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                ocr_text = pytesseract.image_to_string(img).strip()
                if len(ocr_text) > len(text):
                    text = ocr_text
            except Exception:
                pass

        if len(text) > 30:
            results.append({
                'page_number': idx,
                'chapter': current_chapter,
                'text': text,
                'url': '',
            })
    doc.close()
    return results
