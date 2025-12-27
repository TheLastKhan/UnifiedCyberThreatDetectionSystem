#!/bin/bash
# ============================================
# Quick Start Production Deployment
# Unified Cyber Threat Detection System
# ============================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================"
echo "Unified Threat Detection System"
echo "Production Deployment Script"
echo "============================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose first"
    exit 1
fi

echo -e "${GREEN}✓ Docker installed${NC}"
echo -e "${GREEN}✓ Docker Compose installed${NC}"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found${NC}"
    echo "Creating .env from template..."
    
    if [ -f .env.production ]; then
        cp .env.production .env
        echo -e "${GREEN}✓ Created .env from .env.production${NC}"
        echo -e "${YELLOW}Please edit .env and configure your settings${NC}"
        echo ""
        read -p "Press Enter to continue or Ctrl+C to exit..."
    else
        echo -e "${RED}Error: .env.production template not found${NC}"
        exit 1
    fi
fi

# Check if models exist
if [ ! -d "models" ] || [ -z "$(ls -A models/*.pkl 2>/dev/null)" ]; then
    echo -e "${YELLOW}Warning: Trained models not found in models/ directory${NC}"
    echo "The application will work but predictions may not be accurate."
    echo ""
    read -p "Continue anyway? (y/N): " continue_without_models
    if [ "$continue_without_models" != "y" ] && [ "$continue_without_models" != "Y" ]; then
        echo "Please train models first: python train_models.py"
        exit 1
    fi
fi

# Build Docker images
echo ""
echo "Building Docker images..."
docker compose build

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Docker build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker images built successfully${NC}"
echo ""

# Start services
echo "Starting services..."
docker compose up -d

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to start services${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Services started${NC}"
echo ""

# Wait for services to be healthy
echo "Waiting for services to be ready..."
sleep 10

# Check health
echo "Checking application health..."
for i in {1..30}; do
    if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Application is healthy${NC}"
        break
    fi
    
    if [ $i -eq 30 ]; then
        echo -e "${RED}Error: Application health check failed${NC}"
        echo "Check logs: docker compose logs api"
        exit 1
    fi
    
    echo "Waiting... ($i/30)"
    sleep 2
done

echo ""
echo "============================================"
echo -e "${GREEN}Deployment Successful!${NC}"
echo "============================================"
echo ""
echo "Application URLs:"
echo "  - Dashboard: http://localhost:5000"
echo "  - API Health: http://localhost:5000/api/health"
echo "  - API Docs: http://localhost:5000/api/models/status"
echo ""
echo "Useful commands:"
echo "  - View logs: docker compose logs -f"
echo "  - Stop services: docker compose down"
echo "  - Restart: docker compose restart"
echo "  - Status: docker compose ps"
echo ""
echo "Container status:"
docker compose ps
echo ""
echo -e "${GREEN}Ready for production use!${NC}"
