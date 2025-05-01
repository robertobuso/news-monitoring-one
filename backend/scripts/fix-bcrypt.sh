#!/bin/bash
# Script to fix dependency issues with bcrypt

# Set terminal colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Fixing bcrypt dependency issues...${NC}"

# Check if virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo -e "${RED}Virtual environment not activated. Please activate your virtual environment first.${NC}"
    echo -e "Run: ${YELLOW}source venv/bin/activate${NC}"
    exit 1
fi

# Uninstall problematic packages
echo -e "${YELLOW}Uninstalling bcrypt and passlib...${NC}"
pip uninstall -y bcrypt passlib

# Install specific versions that work together
echo -e "${YELLOW}Installing compatible versions...${NC}"
pip install bcrypt==4.0.1
pip install passlib==1.7.4

# Install python-jose which may use bcrypt
echo -e "${YELLOW}Installing python-jose with cryptography...${NC}"
pip install "python-jose[cryptography]==3.3.0"

echo -e "${GREEN}Dependency fix completed!${NC}"
echo -e "You should now be able to run the application without bcrypt errors."
