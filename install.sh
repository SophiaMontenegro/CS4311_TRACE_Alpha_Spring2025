#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "#############################################"
echo "############Installing Project###############"
echo "#############################################"

# BACKEND  
echo "Installing backend dependencies..."
cd Backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
if [ -f requirements.txt ]; then
    echo "Installing from requirements.txt..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "No requirements.txt found in Backend/"
    deactivate
    exit 1
fi

cd Team3/Database

# Prompt user for Neo4j credentials
echo "Please enter your Neo4j connection details:"
read -p "NEO4J_URI: " NEO4J_URI
read -p "NEO4J_USER: " NEO4J_USER
read -s -p "NEO4J_PASSWORD: " NEO4J_PASSWORD
echo ""

# Create .env file
echo "Creating .env file..."
cat > .env <<EOL
NEO4J_URI=$NEO4J_URI
NEO4J_USER=$NEO4J_USER
NEO4J_PASSWORD=$NEO4J_PASSWORD
EOL

echo ".env file created with provided Neo4j credentials."

# Return to project root
cd ..

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd Frontend
if [ -f package.json ]; then
    npm install
else
    echo "No package.json found in Frontend/"
    exit 1
fi

echo 'Generating enviroment variables for Database'


echo "#############################################"
echo "Installation complete!"
echo "#############################################"
