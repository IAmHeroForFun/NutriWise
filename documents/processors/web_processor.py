import requests
from bs4 import BeautifulSoup

def scrape_website(url):
    """
    Scrapes content from a website/article URL.
    Returns: list of dicts [{'page_number': None, 'chapter': str, 'text': str, 'url': str}]
    """
    results = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        raise RuntimeError(f"Failed to fetch website ({url}): {e}")

    soup = BeautifulSoup(resp.text, 'html.parser')

    # Remove non-content elements
    for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form', 'noscript', 'svg']):
        tag.decompose()

    title_elem = soup.find(['h1', 'title'])
    page_title = title_elem.get_text().strip() if title_elem else "Web Reference"

    # Gather main paragraphs and list items
    content_blocks = []
    for p in soup.find_all(['p', 'li', 'h2', 'h3']):
        txt = p.get_text(strip=True)
        if len(txt) > 25:
            content_blocks.append(txt)

    full_text = "\n\n".join(content_blocks)
    if full_text:
        results.append({
            'page_number': None,
            'chapter': page_title,
            'text': full_text,
            'url': url,
        })
    return results
