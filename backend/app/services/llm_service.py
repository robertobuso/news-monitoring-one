"""
LLM service for interacting with language models.

This service provides a unified interface for making requests to language models
through LangChain, handling initialization, error handling, and response parsing.
"""
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Union

from langchain_community.chat_models import ChatOpenAI, ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service for interacting with language models via LangChain.
    """

    def __init__(self, model_name: Optional[str] = None, provider: Optional[str] = None, temperature: float = 0.0):
        """
        Initialize LLM service.

        Args:
            model_name: Name of the language model to use (defaults to settings or "gpt-4")
            provider: Provider to use (defaults to settings or "openai")
            temperature: Temperature parameter for generation
        """
        self.provider = provider or getattr(settings, "LLM_PROVIDER", "openai")
        self.model_name = model_name or getattr(settings, "LLM_MODEL", "gpt-4")
        self.temperature = temperature
        self._llm = None

    def initialize_llm(self) -> Any:
        """
        Initialize the language model based on the configured provider.

        Returns:
            Any: Initialized language model
        """
        if self._llm is None:
            if self.provider == "openai":
                self._llm = ChatOpenAI(
                    model_name=self.model_name,
                    temperature=self.temperature,
                    max_tokens=1000
                )
            elif self.provider == "claude":
                self._llm = ChatAnthropic(
                    model=self.model_name,
                    temperature=self.temperature,
                    max_tokens_to_sample=1000
                )
            elif self.provider == "gemini":
                self._llm = ChatGoogleGenerativeAI(
                    model=self.model_name,
                    temperature=self.temperature,
                    max_output_tokens=1000
                )
            else:
                # Default to OpenAI for backward compatibility
                logger.warning(f"Unsupported LLM provider: {self.provider}. Falling back to OpenAI.")
                self._llm = ChatOpenAI(
                    model_name="gpt-4",
                    temperature=self.temperature,
                    max_tokens=1000
                )
                
        return self._llm

    async def call_llm(
        self, 
        prompt: str, 
        messages: Optional[List[Union[SystemMessage, HumanMessage, AIMessage]]] = None
    ) -> Dict[str, Any]:
        """
        Call the language model with a prompt or messages.

        Args:
            prompt: Text prompt
            messages: Optional list of LangChain message objects

        Returns:
            Dict: Result with success status and response or error
        """
        try:
            llm = self.initialize_llm()

            if messages:
                response = await llm.agenerate([messages])
                content = response.generations[0][0].text
            else:
                response = await llm.agenerate([[SystemMessage(content=prompt)]])
                content = response.generations[0][0].text

            return {"success": True, "response": content}
        except Exception as e:
            logger.error(f"Error calling LLM: {str(e)}")
            return {"success": False, "error": str(e)}

    async def call_llm_with_json_response(
        self, 
        prompt: str, 
        json_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call the language model and parse the response as JSON.

        Args:
            prompt: Text prompt
            json_schema: Expected JSON schema

        Returns:
            Dict: Result with success status and parsed JSON or error
        """
        schema_str = json.dumps(json_schema, indent=2)
        formatted_prompt = f"""
        {prompt}

        Your response must be valid JSON that follows this schema:
        {schema_str}

        Return ONLY the JSON with no additional text.
        """

        result = await self.call_llm(formatted_prompt)

        if not result["success"]:
            return result

        # Try to parse JSON response
        try:
            # Extract JSON if it's wrapped in markdown code blocks
            response_text = result["response"]
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
            json_str = json_match.group(1) if json_match else response_text

            # Clean up JSON string
            json_str = json_str.strip()
            
            # Parse JSON
            parsed_json = json.loads(json_str)
            
            return {"success": True, "response": parsed_json}
        except Exception as e:
            logger.error(f"Error parsing LLM JSON response: {str(e)}")
            return {"success": False, "error": f"Failed to parse JSON response: {str(e)}"}
            
    async def generate_summary(
        self, 
        text: str, 
        max_length: int = 200,
        context: Optional[str] = None
    ) -> str:
        """
        Generate a summary of the provided text.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary in words
            context: Optional context to guide the summarization
            
        Returns:
            str: Summary text
        """
        prompt_context = f"Context: {context}\n\n" if context else ""
        
        prompt = f"""
        {prompt_context}Please summarize the following text in approximately {max_length} words:
        
        {text}
        
        Provide only the summary text with no additional commentary.
        """
        
        result = await self.call_llm(prompt)
        
        if result["success"]:
            return result["response"].strip()
        else:
            logger.error(f"Error generating summary: {result.get('error', 'Unknown error')}")
            return f"Error generating summary"