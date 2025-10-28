#!/bin/bash

# Docker deployment script for AI Quote Generator
# This script helps you quickly deploy using Docker

set -e

echo "AI Quote Generator - Docker Deployment Script"
echo "================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Docker Compose not found. Checking for docker compose plugin...${NC}"
    if ! docker compose version &> /dev/null; then
        echo -e "${RED}Docker Compose is not installed. Please install Docker Compose.${NC}"
        exit 1
    else
        DOCKER_COMPOSE="docker compose"
    fi
else
    DOCKER_COMPOSE="docker-compose"
fi

echo -e "${GREEN}Docker is installed${NC}"
echo -e "${GREEN}Docker Compose is installed${NC}"
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW} .env file not found!${NC}"
    if [ -f ".env.example" ]; then
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo -e "${YELLOW} Please edit .env file and add your GEMINI_API_KEY before continuing.${NC}"
        echo ""
        read -p "Press Enter after you've updated the .env file..."
    else
        echo -e "${RED} .env.example not found. Cannot create .env file.${NC}"
        exit 1
    fi
fi

# Verify GEMINI_API_KEY is set
if ! grep -q "GEMINI_API_KEY=.*[^[:space:]]" .env; then
    echo -e "${RED} GEMINI_API_KEY is not set in .env file!${NC}"
    echo "Please add your Gemini API key to the .env file."
    exit 1
fi

echo -e "${GREEN}Environment configuration found${NC}"
echo ""

# Menu for deployment options
echo "Select deployment option:"
echo "1) Development (with hot reload)"
echo "2) Production (optimized)"
echo "3) Build only (no run)"
echo "4) Stop and remove containers"
echo "5) View logs"
echo "6) Exit"
echo ""
read -p "Enter your choice [1-6]: " choice

case $choice in
    1)
        echo ""
        echo "Starting in Development mode..."
        echo "Building and starting containers..."
        $DOCKER_COMPOSE up -d --build
        echo ""
        echo -e "${GREEN}Application is running!${NC}"
        echo ""
        echo "Access your application at:"
        echo "   - Application: http://localhost:8000"
        echo "   - API Docs: http://localhost:8000/docs"
        echo "   - ReDoc: http://localhost:8000/redoc"
        echo ""
        echo "View logs with: $DOCKER_COMPOSE logs -f"
        echo "Stop with: $DOCKER_COMPOSE down"
        ;;
    2)
        echo ""
        echo "Starting in Production mode..."
        echo "Building and starting containers..."
        $DOCKER_COMPOSE -f docker-compose.prod.yml up -d --build
        echo ""
        echo -e "${GREEN}Application is running in production mode!${NC}"
        echo ""
        echo "Access your application at:"
        echo "   - Application: http://localhost:8000"
        echo "   - API Docs: http://localhost:8000/docs"
        echo "   - ReDoc: http://localhost:8000/redoc"
        echo ""
        echo "View logs with: $DOCKER_COMPOSE -f docker-compose.prod.yml logs -f"
        echo "Stop with: $DOCKER_COMPOSE -f docker-compose.prod.yml down"
        ;;
    3)
        echo ""
        echo "Building Docker image..."
        docker build -t ai-quote-generator .
        echo ""
        echo -e "${GREEN}Image built successfully!${NC}"
        echo ""
        echo "Run with: docker run -p 8000:8000 --env-file .env ai-quote-generator"
        ;;
    4)
        echo ""
        echo "Stopping and removing containers..."
        $DOCKER_COMPOSE down
        $DOCKER_COMPOSE -f docker-compose.prod.yml down 2>/dev/null || true
        echo -e "${GREEN}Containers stopped and removed${NC}"
        ;;
    5)
        echo ""
        echo "Select which logs to view:"
        echo "1) Development"
        echo "2) Production"
        read -p "Enter choice [1-2]: " log_choice
        echo ""
        case $log_choice in
            1)
                $DOCKER_COMPOSE logs -f
                ;;
            2)
                $DOCKER_COMPOSE -f docker-compose.prod.yml logs -f
                ;;
            *)
                echo -e "${RED}Invalid choice${NC}"
                ;;
        esac
        ;;
    6)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice. Please run the script again.${NC}"
        exit 1
        ;;
esac
