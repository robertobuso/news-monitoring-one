"""
LLM service for interacting with language models.

This service provides a unified interface for making requests to language models
through LangChain, handling initialization, error handling, and response parsing.
"""
import json
import logging
import re
from typing import Any, Dict, List, Optional, Union

from langchain_community.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service for interacting with language models via LangChain.
    """

    def __init__(self, model_name: str = "gpt-4", temperature: float = 0.0):
        """
        Initialize LLM service.

        Args:
            model_name: Name of the language model to use
            temperature: Temperature parameter for generation
        """
        self.model_name = model_name
        self.temperature = temperature
        self._llm = None

    def initialize_llm(self) -> ChatOpenAI:
        """
        Initialize the language model.

        Returns:
            ChatOpenAI: Initialized language model
        """
        if self._llm is None:
            self._llm = ChatOpenAI(
                model_name=self.model_name,
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
            json_match = re.search(r'