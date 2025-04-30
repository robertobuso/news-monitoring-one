"""
Content extraction service for processing article content.
"""
import logging
import re
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

from app.utils.html_cleaner import clean_html

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


def extract_text_from_html(html_content: str) -> str:
    """
    Extract plain text from HTML content.
    
    Args:
        html_content: HTML content
        
    Returns:
        str: Plain text content
    """
    return clean_html(html_content)


def extract_summary(text: str, sentences: int = 3) -> str:
    """
    Extract a summary from text by selecting the most important sentences.
    
    Args:
        text: Text to summarize
        sentences: Number of sentences to include in summary
        
    Returns:
        str: Summary text
    """
    try:
        # Tokenize text into sentences
        sentence_list = sent_tokenize(text)
        
        # Return early if there are fewer sentences than requested
        if len(sentence_list) <= sentences:
            return text
        
        # Calculate word frequency
        stop_words = set(stopwords.words('english'))
        word_frequencies = {}
        
        for sentence in sentence_list:
            for word in word_tokenize(sentence.lower()):
                if word not in stop_words and word.isalnum():
                    if word not in word_frequencies:
                        word_frequencies[word] = 1
                    else:
                        word_frequencies[word] += 1
        
        # Calculate sentence scores based on word frequency
        sentence_scores = {}
        for i, sentence in enumerate(sentence_list):
            for word in word_tokenize(sentence.lower()):
                if word in word_frequencies:
                    if i not in sentence_scores:
                        sentence_scores[i] = word_frequencies[word]
                    else:
                        sentence_scores[i] += word_frequencies[word]
        
        # Get top sentences
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:sentences]
        top_sentences = sorted(top_sentences, key=lambda x: x[0])  # Sort by original position
        
        # Combine sentences
        summary = ' '.join([sentence_list[i] for i, _ in top_sentences])
        return summary
    
    except Exception as e:
        logger.error(f"Error extracting summary: {e}")
        # Return first few sentences if summarization fails
        return ' '.join(sentence_list[:sentences]) if len(sentence_list) > sentences else text


def extract_entities(text: str) -> Dict[str, List[str]]:
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
        "people": []
    }
    
    # Simple regex patterns for demonstration
    # In a production environment, use a proper NER library
    org_pattern = r'\b([A-Z][a-z]+ (Inc|Corp|Company|Technologies|Systems|Group|LLC))\b'
    loc_pattern = r'\b([A-Z][a-z]+ (City|County|State|Country|Island|Mountain|River|Lake))\b'
    
    # Extract organizations
    orgs = re.findall(org_pattern, text)
    if orgs:
        entities["organizations"] = [org[0] for org in orgs]
    
    # Extract locations
    locs = re.findall(loc_pattern, text)
    if locs:
        entities["locations"] = [loc[0] for loc in locs]
    
    return entities


def extract_metadata(article_content: str) -> Dict:
    """
    Extract metadata from article content.
    
    Args:
        article_content: Article content
        
    Returns:
        Dict: Extracted metadata
    """
    metadata = {}
    
    # Clean text if it's HTML
    if "<" in article_content and ">" in article_content:
        text = clean_html(article_content)
    else:
        text = article_content
    
    # Extract entities
    metadata["entities"] = extract_entities(text)
    
    # Extract URLs
    metadata["urls"] = re.findall(r'https?://\S+', text)
    
    # Calculate word count
    words = word_tokenize(text)
    metadata["word_count"] = len(words)
    
    # Calculate reading time (average reading speed: 200-250 words per minute)
    metadata["reading_time_minutes"] = round(len(words) / 200, 1)
    
    return metadata