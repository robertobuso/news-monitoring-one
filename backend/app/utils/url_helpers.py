"""
URL helper utilities for working with URLs.
"""
import re
from urllib.parse import urlparse


def extract_source_from_url(url: str) -> str:
    """
    Extract source name from URL.
    
    Args:
        url: URL to extract source from
        
    Returns:
        str: Source name
    """
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        # Remove www. if present
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Extract the main domain name (e.g., example.com from sub.example.com)
        domain_parts = domain.split('.')
        if len(domain_parts) > 2:
            # Handle cases like co.uk, com.au
            if domain_parts[-2] in ['co', 'com', 'org', 'net', 'gov', 'edu'] and len(domain_parts[-1]) == 2:
                main_domain = '.'.join(domain_parts[-3:])
            else:
                main_domain = '.'.join(domain_parts[-2:])
        else:
            main_domain = domain
        
        # Convert to title case and remove TLD
        source_name = main_domain.split('.')[0].title()
        
        return source_name
    except Exception:
        # Return the URL if parsing fails
        return url


def normalize_url(url: str) -> str:
    """
    Normalize URL by ensuring it has a scheme and removing trailing slashes.
    
    Args:
        url: URL to normalize
        
    Returns:
        str: Normalized URL
    """
    # Add scheme if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Remove trailing slash
    if url.endswith('/'):
        url = url[:-1]
    
    return url


def is_valid_url(url: str) -> bool:
    """
    Check if a URL is valid.
    
    Args:
        url: URL to check
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    # Simple URL validation regex
    url_pattern = re.compile(
        r'^(https?://)?'  # http:// or https:// (optional)
        r'([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?'  # domain
        r'(/[a-zA-Z0-9_-]+)*/?'  # path (optional)
        r'(\?[a-zA-Z0-9_=&]+)?'  # query parameters (optional)
    )
    
    return bool(url_pattern.match(url))