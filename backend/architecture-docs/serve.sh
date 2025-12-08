#!/bin/bash

# Serve script for SRM-CS Architecture Documentation
# This script starts a local development server for previewing the documentation

set -e  # Exit on error

echo "=================================================="
echo "SRM-CS Architecture Documentation - Serve Script"
echo "=================================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if we're in the architecture-docs directory
if [ ! -f "mkdocs.yml" ]; then
    echo "ERROR: mkdocs.yml not found. Please run this script from the architecture-docs directory."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running build.sh first..."
    ./build.sh
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Check if MkDocs is installed
if ! command -v mkdocs &> /dev/null; then
    echo "MkDocs not found. Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Start the development server
echo "=================================================="
echo "Starting MkDocs development server..."
echo "=================================================="
echo ""
echo "Documentation will be available at:"
echo "  - English: http://localhost:8000/en/"
echo "  - French:  http://localhost:8000/fr/"
echo ""
echo "The server will automatically reload when you make changes."
echo "Press Ctrl+C to stop the server."
echo ""
echo "--------------------------------------------------"
echo ""

# Serve the site (will run until Ctrl+C)
mkdocs serve -a localhost:8000
