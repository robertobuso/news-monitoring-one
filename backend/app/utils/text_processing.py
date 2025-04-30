"""
Text processing utilities for article content.
"""
import logging
import re
from typing import Dict, List, Set

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

# Download NLTK resources if not already downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

logger = logging.getLogger(__name__)


def extract_entities_from_text(text: str) -> Dict[str, List[str]]:
    """
    Extract potential named entities from text.
    This is a simple implementation that could be enhanced with NLP libraries.
    
    Args:
        text: Text to extract entities from
        
    Returns:
        Dict: Dictionary of entity types and values
    """
    entities = {
        "organizations": [],
        "locations": [],
        "people": [],
        "topics": []
    }
    
    # Simple regex patterns for demonstration
    # In a production environment, use a proper NER library
    org_pattern = r'\b([A-Z][a-z]+ (Inc|Corp|Company|Technologies|Systems|Group|LLC|Ltd|Association|Organization))\b'
    loc_pattern = r'\b([A-Z][a-z]+ (City|County|State|Country|Island|Mountain|River|Lake|Region))\b'
    person_pattern = r'\b(Mr\.|Ms\.|Mrs\.|Dr\.) ([A-Z][a-z]+ [A-Z][a-z]+)\b'
    
    # Extract organizations
    orgs = re.findall(org_pattern, text)
    if orgs:
        entities["organizations"] = list(set([org[0] for org in orgs]))
    
    # Extract locations
    locs = re.findall(loc_pattern, text)
    if locs:
        entities["locations"] = list(set([loc[0] for loc in locs]))
    
    # Extract people
    people = re.findall(person_pattern, text)
    if people:
        entities["people"] = list(set([f"{p[0]} {p[1]}" for p in people]))
    
    # Extract topics (keywords)
    entities["topics"] = extract_keywords(text, 10)
    
    return entities


def extract_keywords(text: str, num_keywords: int = 10) -> List[str]:
    """
    Extract keywords from text based on frequency.
    
    Args:
        text: Text to extract keywords from
        num_keywords: Number of keywords to extract
        
    Returns:
        List[str]: List of keywords
    """
    try:
        # Tokenize and lowercase
        words = word_tokenize(text.lower())
        
        # Remove stopwords and non-alphabetic tokens
        stop_words = set(stopwords.words('english'))
        words = [word for word in words if word.isalpha() and word not in stop_words and len(word) > 3]
        
        # Count word frequencies
        word_freq = {}
        for word in words:
            if word in word_freq:
                word_freq[word] += 1
            else:
                word_freq[word] = 1
        
        # Sort by frequency and get top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, freq in sorted_words[:num_keywords]]
        
        return keywords
    
    except Exception as e:
        logger.error(f"Error extracting keywords: {e}")
        return []


def calculate_text_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts using Jaccard similarity.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        float: Similarity score (0.0 to 1.0)
    """
    try:
        # Tokenize and create sets of words
        words1 = set(word_tokenize(text1.lower()))
        words2 = set(word_tokenize(text2.lower()))
        
        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        words1 = {w for w in words1 if w.isalpha() and w not in stop_words}
        words2 = {w for w in words2 if w.isalpha() and w not in stop_words}
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    except Exception as e:
        logger.error(f"Error calculating text similarity: {e}")
        return 0.0


def truncate_text(text: str, max_length: int, preserve_words: bool = True) -> str:
    """
    Truncate text to a maximum length, optionally preserving whole words.
    
    Args:
        text: Text to truncate
        max_length: Maximum length in characters
        preserve_words: Whether to preserve whole words
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    
    if preserve_words:
        # Truncate at the last space before max_length
        truncated = text[:max_length]
        last_space = truncated.rfind(' ')
        if last_space > 0:
            truncated = truncated[:last_space]
        return truncated + "..."
    
    return text[:max_length] + "..."


def split_text_into_chunks(text: str, max_chunk_size: int = 1000) -> List[str]:
    """
    Split text into chunks of maximum size, preserving sentence boundaries.
    
    Args:
        text: Text to split
        max_chunk_size: Maximum chunk size in characters
        
    Returns:
        List[str]: List of text chunks
    """
    # Split text into sentences
    sentences = sent_tokenize(text)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # If adding this sentence would exceed the chunk size, start a new chunk
        if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk += " " + sentence if current_chunk else sentence
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks