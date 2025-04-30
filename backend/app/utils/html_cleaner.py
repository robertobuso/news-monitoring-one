"""
HTML cleaning utilities for processing article content.
"""
import re
from typing import List, Optional

from bs4 import BeautifulSoup, Comment


def clean_html(html_content: str) -> str:
    """
    Clean HTML content by removing scripts, styles, comments, and unnecessary tags.
    
    Args:
        html_content: HTML content to clean
        
    Returns:
        str: Cleaned text
    """
    if not html_content:
        return ""
    
    # Remove scripts, styles, and comments
    cleaned = re.sub(r"<script[^>]*>.*?</script>", "", html_content, flags=re.DOTALL)
    cleaned = re.sub(r"<style[^>]*>.*?</style>", "", cleaned, flags=re.DOTALL)
    cleaned = re.sub(r"<!--.*?-->", "", cleaned, flags=re.DOTALL)
    
    # Parse with BeautifulSoup
    soup = BeautifulSoup(cleaned, "html.parser")
    
    # Remove comments
    for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
        comment.extract()
    
    # Remove unwanted tags
    unwanted_tags = ['script', 'style', 'iframe', 'form', 'button', 'input', 'nav', 'footer', 'header']
    for tag in unwanted_tags:
        for element in soup.find_all(tag):
            element.decompose()
    
    # Remove unwanted attributes
    for tag in soup.find_all(True):
        for attr in list(tag.attrs):
            if attr not in ['href', 'src']:
                del tag[attr]
    
    # Get text with some structure preservation
    text = ""
    for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']):
        text += element.get_text() + "\n\n"
    
    # If no structured content was found, get all text
    if not text.strip():
        text = soup.get_text(separator="\n\n")
    
    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'\s{2,}', ' ', text)
    
    return text.strip()


def extract_main_content(html_content: str) -> str:
    """
    Extract the main content from an HTML document.
    Uses heuristics to find the main article content.
    
    Args:
        html_content: HTML content
        
    Returns:
        str: Main content HTML
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Try to find main content containers
    main_selectors = [
        "article", "main", ".article", ".post", ".content", 
        "#article", "#post", "#content", "#main-content"
    ]
    
    for selector in main_selectors:
        main_content = soup.select_one(selector)
        if main_content:
            return str(main_content)
    
    # If no main content container found, use heuristics
    # Find the div with the most paragraphs
    divs = soup.find_all("div")
    max_p_count = 0
    max_div = None
    
    for div in divs:
        p_count = len(div.find_all("p"))
        if p_count > max_p_count:
            max_p_count = p_count
            max_div = div
    
    if max_div and max_p_count > 3:
        return str(max_div)
    
    # Fallback to body
    body = soup.find("body")
    if body:
        return str(body)
    
    return html_content


def html_to_plain_text(html_content: str, preserve_links: bool = False) -> str:
    """
    Convert HTML to plain text while optionally preserving links.
    
    Args:
        html_content: HTML content
        preserve_links: Whether to preserve links as [text](url)
        
    Returns:
        str: Plain text
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Replace <br> and <p> with newlines
    for br in soup.find_all(['br', 'p']):
        br.replace_with('\n' + br.get_text())
    
    # Handle links
    if preserve_links:
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text().strip()
            if text and href.startswith(('http://', 'https://')):
                a.replace_with(f"[{text}]({href})")
    
    # Get text
    text = soup.get_text()
    
    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'\s{2,}', ' ', text)
    
    return text.strip()