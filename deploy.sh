#!/bin/bash

# Tennis Warehouse API Deployment Script
# Supports multiple platforms: Railway, Render, Heroku, Docker

set -e

echo "🎾 Tennis Warehouse API Deployment"
echo "=================================="

# Function to deploy to Railway
deploy_railway() {
    echo "🚄 Deploying to Railway..."
    
    if ! command -v railway &> /dev/null; then
        echo "❌ Railway CLI not installed. Installing..."
        npm install -g @railway/cli
    fi
    
    echo "📦 Deploying to Railway..."
    railway up
    
    echo "✅ Deployed to Railway!"
    echo "🌐 Your API will be available at: https://your-app.railway.app"
}

# Function to deploy to Render
deploy_render() {
    echo "🎨 Deploying to Render..."
    echo "📝 Please follow these steps:"
    echo "1. Go to https://render.com"
    echo "2. Connect your GitHub repository"
    echo "3. Create new Web Service"
    echo "4. Set build command: pip install -r requirements-api.txt"
    echo "5. Set start command: uvicorn api_server:app --host 0.0.0.0 --port \$PORT"
    echo "6. Deploy!"
}

# Function to deploy with Docker
deploy_docker() {
    echo "🐳 Building Docker container..."
    
    # Build the image
    docker build -t tennis-warehouse-api .
    
    echo "🚀 Running container locally..."
    echo "Available at: http://localhost:8000"
    docker run -p 8000:8000 tennis-warehouse-api
}

# Function to test local deployment
test_local() {
    echo "🧪 Testing local deployment..."
    
    # Install dependencies
    pip install -r requirements-api.txt
    
    # Start the server
    echo "🚀 Starting local server..."
    echo "Available at: http://localhost:8000"
    echo "API docs at: http://localhost:8000/docs"
    uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
}

# Main menu
echo ""
echo "Choose deployment option:"
echo "1) Railway (Recommended - Free tier available)"
echo "2) Render (Free tier available)"
echo "3) Docker (Local container)"
echo "4) Test locally"
echo "5) Exit"

read -p "Enter choice [1-5]: " choice

case $choice in
    1)
        deploy_railway
        ;;
    2)
        deploy_render
        ;;
    3)
        deploy_docker
        ;;
    4)
        test_local
        ;;
    5)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid option"
        exit 1
        ;;
esac