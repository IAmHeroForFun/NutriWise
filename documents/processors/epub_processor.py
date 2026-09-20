import os
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

def extract_epub(file_path):
    """
    Extracts chapters and text sections from an EPUB ebook.
    Returns: list of dicts [{'page_number': int, 'chapter': str, 'text': str, 'url': ''}]
    """
    results = []
    if not os.path.exists(file_path):
        return results

    try:
        book = epub.read_epub(file_path)
    except Exception:
        return results

    idx = 1
    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            content = item.get_content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Strip scripts, styles, navs
            for elem in soup(['script', 'style', 'nav']):
                elem.decompose()

            # Check if this item is a monolithic document with chapter breaks (e.g. '≈' or headers)
            paras = soup.find_all('p')
            has_chapter_breaks = any(p.get_text().strip() == '≈' for p in paras)

            if has_chapter_breaks:
                current_title = ''
                current_paras = []
                for p in paras:
                    txt = p.get_text().strip()
                    if txt == '≈':
                        if current_paras:
                            sec_text = '\n\n'.join(current_paras).strip()
                            t_start = sec_text.lower()[:300]
                            if len(sec_text) > 150 and not any(term in t_start for term in ['table of contents', 'contents\n', 'index\n', 'copyright ©']):
                                results.append({
                                    'page_number': idx,
                                    'chapter': current_title or f"Chapter {idx}",
                                    'text': sec_text,
                                    'url': '',
                                })
                                idx += 1
                        current_title = ''
                        current_paras = []
                    elif not current_title and txt and txt not in ['PENGUIN BOOKS', 'The INDIAN Pantry', 'The Very Best of Rude Food']:
                        current_title = txt
                        current_paras.append(txt)
                    elif txt:
                        current_paras.append(txt)

                if current_paras:
                    sec_text = '\n\n'.join(current_paras).strip()
                    t_start = sec_text.lower()[:300]
                    if len(sec_text) > 150 and not any(term in t_start for term in ['table of contents', 'contents\n', 'index\n', 'copyright ©']):
                        results.append({
                            'page_number': idx,
                            'chapter': current_title or f"Chapter {idx}",
                            'text': sec_text,
                            'url': '',
                        })
                        idx += 1
            else:
                # Extract chapter title
                title_tag = soup.find(['h1', 'h2', 'title'])
                chapter_name = title_tag.get_text().strip() if title_tag else f"Section {idx}"
                text = soup.get_text(separator="\n\n").strip()
                
                # Skip Table of Contents, Index, Title/Copyright pages
                t_start = text.lower()[:400]
                if any(term in t_start for term in ['table of contents', 'contents\n', 'index\n', 'bibliography', 'copyright ©', 'all rights reserved']):
                    continue

                if len(text) > 40:
                    results.append({
                        'page_number': idx,
                        'chapter': chapter_name,
                        'text': text,
                        'url': '',
                    })
                    idx += 1
    return results
