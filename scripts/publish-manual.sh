#!/bin/bash

# Manual PyPI Publishing Script for awdx
# This script builds and publishes the awdx package to PyPI manually

set -e

echo "🚀 Manual PyPI Publishing for awdx"
echo "=================================="

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Virtual environment created and activated"
fi

# Check if pip is available
if ! command -v pip &> /dev/null; then
    echo "❌ pip not found. Trying pip3..."
    if ! command -v pip3 &> /dev/null; then
        echo "❌ pip3 not found. Trying python -m pip..."
        PIP_CMD="python -m pip"
    else
        PIP_CMD="pip3"
    fi
else
    PIP_CMD="pip"
fi

# Install/upgrade build tools
echo "🔨 Installing/upgrade build tools..."
$PIP_CMD install --upgrade build twine

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# Build the package
echo "📦 Building package..."
python -m build

# Check the built package
echo "✅ Checking built package..."
twine check dist/*

echo ""
echo "📋 Package built successfully!"
echo ""
echo "To publish to PyPI:"
echo "1. Test on TestPyPI first (recommended):"
echo "   twine upload --repository testpypi dist/*"
echo ""
echo "2. Publish to PyPI production:"
echo "   twine upload dist/*"
echo ""
echo "Note: You'll need PyPI credentials for uploading."
echo "The package now includes GitHub-hosted images that will display properly on PyPI!" 