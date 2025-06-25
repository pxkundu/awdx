#!/bin/bash

# awdx Development Setup Script
# This script sets up the development environment for the awdx project

set -e

echo "🚀 Setting up awdx development environment..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install build dependencies
echo "🔨 Installing build dependencies..."
pip install build

# Install awdx in development mode
echo "📦 Installing awdx in development mode..."
pip install -e .

echo "✅ Setup complete! Your awdx CLI tool is ready to use."
echo ""
echo "To use awdx:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run awdx commands: awdx --help"
echo ""
echo "To deactivate the virtual environment: deactivate" 