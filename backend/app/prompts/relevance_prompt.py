"""
Prompts for article relevance evaluation.
"""
from app.models.article import Article
from app.models.client_profile import ClientProfile


def get_relevance_evaluation_prompt(article: Article, client_profile: ClientProfile) -> str:
    """
    Generate a prompt for evaluating article relevance to a client profile.
    
    Args:
        article: Article to evaluate
        client_profile: Client profile to evaluate against
        
    Returns:
        str: Formatted prompt
    """
    # Truncate article content to avoid token limits
    max_content_length = 1500
    truncated_content = article.content[:max_content_length]
    if len(article.content) > max_content_length:
        truncated_content += "..."
    
    prompt = f"""You are an expert news analyst. Evaluate the relevance of this article to the client profile.

CLIENT PROFILE:
Name: {client_profile.name}
Industry: {client_profile.industry}
Description: {client_profile.description}
Keywords: {', '.join(client_profile.keywords)}

ARTICLE:
Title: {article.title}
Source: {article.source}
Published: {article.published_at.isoformat()}
Content: {truncated_content}

Analyze how relevant this article is to the client profile. Consider:
1. Direct mentions of the client's industry or related sectors
2. Topics that would impact the client's business
3. Alignment with the client's keywords
4. Potential strategic value of the information

Provide a relevance score from 0.0 to 1.0, where:
- 0.0-0.2: Not relevant
- 0.3-0.5: Somewhat relevant
- 0.6-0.8: Relevant
- 0.9-1.0: Highly relevant

Also provide a brief explanation of why this article is or isn't relevant.

Format your response as JSON: {{"score": float, "explanation": "string"}}
"""
    
    return prompt


def get_batch_relevance_prompt(articles: list, client_profile: ClientProfile) -> str:
    """
    Generate a prompt for batch evaluation of article relevance.
    
    Args:
        articles: List of articles to evaluate
        client_profile: Client profile to evaluate against
        
    Returns:
        str: Formatted prompt
    """
    # Format article snippets
    article_texts = []
    for i, article in enumerate(articles, 1):
        # Truncate content
        max_content_length = 500  # Shorter for batch processing
        truncated_content = article.content[:max_content_length]
        if len(article.content) > max_content_length:
            truncated_content += "..."
        
        article_text = f"""ARTICLE {i}:
ID: {article.id}
Title: {article.title}
Source: {article.source}
Published: {article.published_at.isoformat()}
Content Snippet: {truncated_content}
"""
        article_texts.append(article_text)
    
    articles_section = "\n\n".join(article_texts)
    
    prompt = f"""You are an expert news analyst. Evaluate the relevance of multiple articles to the client profile.

CLIENT PROFILE:
Name: {client_profile.name}
Industry: {client_profile.industry}
Description: {client_profile.description}
Keywords: {', '.join(client_profile.keywords)}

{articles_section}

For each article, provide a relevance score from 0.0 to 1.0 and a brief explanation.

Format your response as JSON:
{{
  "evaluations": [
    {{"article_id": "id1", "score": float, "explanation": "string"}},
    {{"article_id": "id2", "score": float, "explanation": "string"}},
    ...
  ]
}}
"""
    
    return prompt