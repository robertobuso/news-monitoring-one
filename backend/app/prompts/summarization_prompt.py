"""
Prompts for article summarization.
"""
from typing import List, Optional

from app.models.article import Article
from app.models.client_profile import ClientProfile


def get_article_summary_prompt(
    article: Article, 
    client_profile: Optional[ClientProfile] = None,
    max_length: int = 200
) -> str:
    """
    Generate a prompt for article summarization.
    
    Args:
        article: Article to summarize
        client_profile: Optional client profile to tailor summary for
        max_length: Maximum summary length in words
        
    Returns:
        str: Formatted prompt
    """
    # Add client context if provided
    client_context = ""
    if client_profile:
        client_context = f"""This summary is for a client in the {client_profile.industry} industry.
Client description: {client_profile.description}
Important keywords: {', '.join(client_profile.keywords)}
Focus on aspects relevant to this client."""

    prompt = f"""Summarize the following news article in a concise, informative manner.
Keep the summary under {max_length} words and focus on the key facts and implications.
{client_context}

ARTICLE:
Title: {article.title}
Source: {article.source}
Date: {article.published_at.isoformat()}
Content: {article.content}

Your summary should:
1. Capture the main points and key information
2. Maintain objectivity and factual accuracy
3. Be clear and well-structured
4. Avoid unnecessary details while preserving important context
5. Be written in a professional tone suitable for business readers

Provide only the summary text with no additional commentary or metadata.
"""
    
    return prompt


def get_executive_summary_prompt(
    article_texts: List[str],
    client_profile: ClientProfile,
    max_length: int = 400
) -> str:
    """
    Generate a prompt for executive summary of multiple articles.
    
    Args:
        article_texts: List of article texts (title and summary)
        client_profile: Client profile to tailor summary for
        max_length: Maximum summary length in words
        
    Returns:
        str: Formatted prompt
    """
    article_list = "\n\n".join(article_texts)
    
    prompt = f"""You are an executive briefing specialist. Create a comprehensive executive summary of these news articles.

CLIENT PROFILE:
Name: {client_profile.name}
Industry: {client_profile.industry}
Description: {client_profile.description}
Keywords: {', '.join(client_profile.keywords)}

ARTICLES:
{article_list}

Create an executive summary that synthesizes the key information from these articles.
Focus on insights relevant to the client's industry and interests.
The summary should be well-structured, concise (under {max_length} words), and highlight actionable insights.

Your executive summary should:
1. Begin with a brief overview of the main themes and trends
2. Group related information from different articles
3. Highlight potential business implications and opportunities
4. Identify any risks or challenges relevant to the client
5. Conclude with key takeaways or strategic considerations

Format the summary with clear sections and professional business language.
"""
    
    return prompt