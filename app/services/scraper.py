import httpx
from bs4 import BeautifulSoup
from readability import Document
import ipaddress
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

# Define private IP ranges to block for SSRF protection
BLOCKED_IP_RANGES = [
    ipaddress.ip_network('127.0.0.0/8'),      # Loopback
    ipaddress.ip_network('10.0.0.0/8'),       # Private Class A
    ipaddress.ip_network('172.16.0.0/12'),    # Private Class B
    ipaddress.ip_network('192.168.0.0/16'),   # Private Class C
    ipaddress.ip_network('169.254.0.0/16'),   # Link-local
    ipaddress.ip_network('::1/128'),          # IPv6 loopback
    ipaddress.ip_network('fc00::/7'),         # IPv6 private
    ipaddress.ip_network('fe80::/10'),        # IPv6 link-local
]


def is_safe_url(url: str) -> bool:
    """
    Check if URL is safe from SSRF attacks
    
    Args:
        url: URL to check
        
    Returns:
        True if safe, False otherwise
    """
    try:
        parsed = urlparse(url)
        
        # Check scheme
        if parsed.scheme not in ['http', 'https']:
            logger.warning(f"Blocked URL with invalid scheme: {url}")
            return False
        
        # Get hostname
        hostname = parsed.hostname
        if not hostname:
            logger.warning(f"Blocked URL with no hostname: {url}")
            return False
        
        # Try to resolve IP
        try:
            import socket
            ip_address = socket.gethostbyname(hostname)
            ip_obj = ipaddress.ip_address(ip_address)
            
            # Check if IP is in blocked ranges
            for blocked_range in BLOCKED_IP_RANGES:
                if ip_obj in blocked_range:
                    logger.warning(f"Blocked URL with private IP: {url} -> {ip_address}")
                    return False
                    
        except (socket.gaierror, ValueError) as e:
            logger.warning(f"Could not resolve hostname for {url}: {e}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking URL safety: {e}")
        return False


def fetch_article_text(url: str, timeout: int = 10) -> str:
    """
    Fetch and extract main text from a URL with SSRF protection
    
    Args:
        url: URL to fetch
        timeout: Request timeout in seconds
        
    Returns:
        Extracted text content
        
    Raises:
        ValueError: If URL is unsafe or invalid
        httpx.HTTPError: If request fails
    """
    # SSRF protection
    if not is_safe_url(url):
        raise ValueError(f"URL blocked for security reasons: {url}")
    
    # Fetch the URL
    try:
        with httpx.Client(timeout=timeout, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            html = response.text
    except httpx.TimeoutException:
        raise ValueError(f"Request timed out after {timeout} seconds")
    except httpx.HTTPError as e:
        raise ValueError(f"Failed to fetch URL: {str(e)}")
    
    # Try readability first for better extraction
    try:
        doc = Document(html)
        title = doc.title()
        content = doc.summary()
        
        # Parse with BeautifulSoup to extract text
        soup = BeautifulSoup(content, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)
        
        # Add title if available
        if title:
            text = f"{title}\n\n{text}"
            
        return text
        
    except Exception as e:
        logger.warning(f"Readability extraction failed: {e}. Falling back to basic extraction.")
        
        # Fallback to basic extraction
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Try to find article or main content
        article = soup.find('article') or soup.find('main') or soup
        
        # Get text from paragraphs
        paragraphs = article.find_all('p')
        text = '\n'.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        
        if not text:
            # If no paragraphs, get all text
            text = soup.get_text(separator='\n', strip=True)
        
        return text
