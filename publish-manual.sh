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
else
    echo "❌ Virtual environment not found. Please run ./setup-dev.sh first."
    exit 1
fi

# Install/upgrade build tools
echo "🔨 Installing/upgrading build tools..."
pip install --upgrade build twine

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
echo "The package now includes ASCII art that will display properly on PyPI!" 