# Manual PyPI Publishing Guide for awdx

This guide explains how to manually publish your awdx package to PyPI.

## Quick Publish Commands

### Step 1: Prepare Environment
```bash
cd /path/to/awdx
source venv/bin/activate  # or your virtual environment
```

### Step 2: Update Version
Edit `pyproject.toml`:
```toml
version = "0.0.4"  # or your next version
```

### Step 3: Build and Publish
```bash
# Install/upgrade build tools
pip install --upgrade build twine

# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build the package
python -m build

# Check the built package
twine check dist/*

# Test on TestPyPI (recommended)
twine upload --repository testpypi dist/*

# Publish to PyPI
twine upload dist/*
```

## What You'll See on PyPI

Your PyPI page at [https://pypi.org/project/awdx/](https://pypi.org/project/awdx/) 

## Troubleshooting

### Build Errors
```bash
pip install --upgrade build setuptools wheel
```

### Authentication Issues
1. Create PyPI account at https://pypi.org/account/register/
2. Create API token at https://pypi.org/manage/account/token/
3. Use token when prompted

### Version Conflicts
Update version in `pyproject.toml`, then rebuild and upload.

## Verify Publication

Check your package at: https://pypi.org/project/awdx/ 