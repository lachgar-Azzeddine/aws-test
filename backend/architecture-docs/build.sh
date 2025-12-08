#!/bin/bash

# Build script for SRM-CS Architecture Documentation
# This script installs dependencies and builds the static website

set -e  # Exit on error

echo "=================================================="
echo "SRM-CS Architecture Documentation - Build Script"
echo "=================================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "Python version:"
python3 --version
echo ""

# Check if we're in the architecture-docs directory
if [ ! -f "mkdocs.yml" ]; then
    echo "ERROR: mkdocs.yml not found. Please run this script from the architecture-docs directory."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install/upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Clean previous build
if [ -d "site" ]; then
    echo "Cleaning previous build..."
    rm -rf site
    echo "✓ Previous build cleaned"
    echo ""
fi

# Build the site
echo "Building MkDocs site..."
mkdocs build --clean
echo "✓ Site built successfully"
echo ""

# Get site size
SITE_SIZE=$(du -sh site | cut -f1)
echo "=================================================="
echo "Build completed successfully!"
echo "=================================================="
echo ""
echo "Output directory: ./site"
echo "Site size: $SITE_SIZE"
echo ""
echo "To view the site locally, run: ./serve.sh"
echo "To view offline, open: site/en/index.html or site/fr/index.html in your browser"
echo ""
echo "To share with your team:"
echo "  1. Compress the site: tar -czf architecture-docs.tar.gz site/"
echo "  2. Share the archive file"
echo "  3. Recipients extract and open site/en/index.html in a browser"
echo ""
