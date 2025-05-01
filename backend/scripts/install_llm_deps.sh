#!/bin/bash
# Script to install dependencies for various LLM providers

# Set terminal colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Installing LLM dependencies...${NC}"

# Check if virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo -e "${RED}Virtual environment not activated. Please activate your virtual environment first.${NC}"
    echo -e "Run: ${YELLOW}source venv/bin/activate${NC}"
    exit 1
fi

# Install base LangChain
pip install langchain>=0.0.335 langchain-community>=0.0.10

# Install OpenAI integration
echo -e "${YELLOW}Installing OpenAI integration...${NC}"
pip install langchain-openai>=0.0.2 openai>=1.3.0

# Install Anthropic (Claude) integration
echo -e "${YELLOW}Installing Anthropic integration...${NC}"
pip install langchain-anthropic>=0.0.3 anthropic>=0.5.0

# Install Google Gemini integration
echo -e "${YELLOW}Installing Google Generative AI integration...${NC}"
pip install langchain-google-genai>=0.0.3 google-generativeai>=0.3.0

# Install HTML processing dependencies for article content
echo -e "${YELLOW}Installing HTML processing dependencies...${NC}"
pip install beautifulsoup4>=4.12.2

echo -e "${GREEN}LLM dependencies installed successfully!${NC}"
echo -e "Now you can set up your .env file with your API keys for the LLM provider of your choice."
echo -e "Available providers: openai, claude, gemini"
echo -e "Example .env settings:"
echo -e "${YELLOW}LLM_PROVIDER=claude${NC}"
echo -e "${YELLOW}LLM_MODEL=claude-3-sonnet${NC}"
echo -e "${YELLOW}ANTHROPIC_API_KEY=sk-ant-...${NC}"