#!/bin/bash
# Script to set up the NewsMonitor application

# Set terminal colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up NewsMonitor application...${NC}"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${GREEN}Created .env file. Please update it with your credentials.${NC}"
else
    echo -e "${YELLOW}.env file already exists. Skipping...${NC}"
fi

# Navigate to backend directory
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python -m venv venv
    echo -e "${GREEN}Virtual environment created.${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists. Skipping...${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -r requirements.txt

# Run migrations
echo -e "${YELLOW}Running database migrations...${NC}"
alembic upgrade head

# Seed database
echo -e "${YELLOW}Seeding database with initial data...${NC}"
python -m scripts.seed_database

# Deactivate virtual environment
deactivate

# Navigate back to root directory
cd ..

# Navigate to frontend directory
cd frontend

# Install dependencies
echo -e "${YELLOW}Installing frontend dependencies...${NC}"
npm install

# Navigate back to root directory
cd ..

echo -e "${GREEN}Setup complete!${NC}"
echo -e "To start the backend server, run: ${YELLOW}cd backend && source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload${NC}"
echo -e "To start the frontend server, run: ${YELLOW}cd frontend && npm run dev${NC}"
echo -e "To start Celery worker, run: ${YELLOW}cd backend && source venv/bin/activate && celery -A app.worker.celery worker --loglevel=info${NC}"
echo -e "To start Celery beat, run: ${YELLOW}cd backend && source venv/bin/activate && celery -A app.worker.celery beat --loglevel=info${NC}"