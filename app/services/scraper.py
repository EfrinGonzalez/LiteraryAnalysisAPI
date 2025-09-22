import requests
from bs4 import BeautifulSoup

def fetch_article_text(url: str) -> str:
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    article = soup.find('article') or soup
    paragraphs = article.find_all('p')
    return '\n'.join(p.get_text() for p in paragraphs)