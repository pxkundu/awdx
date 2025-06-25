#!/bin/bash

# Setup Development Branch for Image Hosting
# This script helps set up the development branch for GitHub Actions image hosting

echo "🚀 Setting up development branch for image hosting..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Check if development branch exists
if git show-ref --verify --quiet refs/heads/development; then
    echo "✅ Development branch already exists"
    git checkout development
else
    echo "📝 Creating development branch..."
    git checkout -b development
fi

# Ensure assets folder exists
if [ ! -d "assests" ]; then
    echo "❌ Error: Assets folder not found"
    exit 1
fi

# Check if images exist
if [ ! -f "assests/AWDX.png" ] || [ ! -f "assests/AWDX_PROFILE_HELP.png" ]; then
    echo "❌ Error: Required images not found in assests folder"
    echo "Expected: assests/AWDX.png and assests/AWDX_PROFILE_HELP.png"
    exit 1
fi

echo "✅ Images found:"
ls -la assests/*.png

# Create .github/workflows directory if it doesn't exist
mkdir -p .github/workflows

echo "✅ Development branch setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Commit your changes: git add . && git commit -m 'Setup development branch for image hosting'"
echo "2. Push to GitHub: git push origin development"
echo "3. GitHub Actions will automatically host your images"
echo "4. Images will be available at:"
echo "   - https://raw.githubusercontent.com/pxkundu/awdx/development/assests/AWDX.png"
echo "   - https://raw.githubusercontent.com/pxkundu/awdx/development/assests/AWDX_PROFILE_HELP.png"
echo ""
echo "🎯 Your README.md is already updated to use these hosted images!" 