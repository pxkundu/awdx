#!/bin/bash

# 🚀 AWDX Release Script
# Automates the release process for AWDX CLI tool

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="awdx"
GITHUB_REPO="pxkundu/awdx"
PYPI_PACKAGE="awdx"

# Functions
print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}🚀 AWDX Release Process${NC}"
    echo -e "${BLUE}================================${NC}"
}

print_step() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
check_environment() {
    print_step "Checking environment..."
    
    if [ ! -f "pyproject.toml" ]; then
        print_error "pyproject.toml not found. Please run this script from the project root."
        exit 1
    fi
    
    if [ ! -f "src/awdx/__init__.py" ]; then
        print_error "AWDX source not found. Please run this script from the project root."
        exit 1
    fi
    
    print_info "Environment check passed"
}

# Get current version
get_current_version() {
    grep 'version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'
}

# Get next version
get_next_version() {
    local current_version=$1
    local version_type=$2
    
    IFS='.' read -ra VERSION_PARTS <<< "$current_version"
    local major=${VERSION_PARTS[0]}
    local minor=${VERSION_PARTS[1]}
    local patch=${VERSION_PARTS[2]}
    
    case $version_type in
        "major")
            echo "$((major + 1)).0.0"
            ;;
        "minor")
            echo "$major.$((minor + 1)).0"
            ;;
        "patch")
            echo "$major.$minor.$((patch + 1))"
            ;;
        *)
            echo "$major.$minor.$((patch + 1))"
            ;;
    esac
}

# Update version in files
update_version() {
    local new_version=$1
    
    print_step "Updating version to $new_version..."
    
    # Update pyproject.toml
    sed -i.bak "s/version = \".*\"/version = \"$new_version\"/" pyproject.toml
    
    # Update __init__.py
    sed -i.bak "s/__version__ = \".*\"/__version__ = \"$new_version\"/" src/awdx/__init__.py
    
    # Update fallback version
    sed -i.bak "s/__version__ = \".*\"  # Fallback version/__version__ = \"$new_version\"  # Fallback version/" src/awdx/__init__.py
    
    # Clean up backup files
    rm -f pyproject.toml.bak src/awdx/__init__.py.bak
    
    print_info "Version updated in all files"
}

# Run tests
run_tests() {
    print_step "Running comprehensive test suite..."
    
    if ! python tests/run_tests.py --all --coverage; then
        print_error "Tests failed. Please fix issues before releasing."
        exit 1
    fi
    
    print_info "All tests passed"
}

# Build Python packages
build_python_packages() {
    print_step "Building Python packages..."
    
    # Clean previous builds
    rm -rf dist/ build/ *.egg-info/
    
    # Build packages
    python -m build
    
    print_info "Python packages built successfully"
}

# Build binaries
build_binaries() {
    print_step "Building binaries..."
    
    # Install PyInstaller if not present
    if ! python -c "import PyInstaller" 2>/dev/null; then
        print_info "Installing PyInstaller..."
        pip install pyinstaller
    fi
    
    # Build for current platform
    local platform=$(uname -s | tr '[:upper:]' '[:lower:]')
    local arch=$(uname -m)
    
    if [ "$platform" = "darwin" ]; then
        platform="macos"
    elif [ "$platform" = "linux" ]; then
        platform="linux"
    fi
    
    if [ "$arch" = "x86_64" ]; then
        arch="x86_64"
    elif [ "$arch" = "arm64" ] || [ "$arch" = "aarch64" ]; then
        arch="aarch64"
    fi
    
    local binary_name="awdx-${platform}-${arch}"
    
    print_info "Building binary for $platform-$arch..."
    pyinstaller awdx.spec --distpath dist/ --workpath build/
    
    # Rename binary
    if [ "$platform" = "windows" ]; then
        mv dist/awdx.exe "dist/${binary_name}.exe"
    else
        mv dist/awdx "dist/${binary_name}"
        chmod +x "dist/${binary_name}"
    fi
    
    print_info "Binary built: dist/${binary_name}"
}

# Test binary
test_binary() {
    print_step "Testing binary functionality..."
    
    local platform=$(uname -s | tr '[:upper:]' '[:lower:]')
    local arch=$(uname -m)
    
    if [ "$platform" = "darwin" ]; then
        platform="macos"
    elif [ "$platform" = "linux" ]; then
        platform="linux"
    fi
    
    if [ "$arch" = "x86_64" ]; then
        arch="x86_64"
    elif [ "$arch" = "arm64" ] || [ "$arch" = "aarch64" ]; then
        arch="aarch64"
    fi
    
    local binary_name="awdx-${platform}-${arch}"
    
    if [ "$platform" = "windows" ]; then
        if ! "./dist/${binary_name}.exe" --version; then
            print_error "Binary test failed"
            exit 1
        fi
    else
        if ! "./dist/${binary_name}" --version; then
            print_error "Binary test failed"
            exit 1
        fi
    fi
    
    print_info "Binary test passed"
}

# Create git tag
create_git_tag() {
    local version=$1
    
    print_step "Creating git tag v$version..."
    
    # Check if tag already exists
    if git tag -l "v$version" | grep -q "v$version"; then
        print_warning "Tag v$version already exists"
        read -p "Do you want to delete and recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git tag -d "v$version"
            git push origin ":refs/tags/v$version" 2>/dev/null || true
        else
            print_error "Release cancelled"
            exit 1
        fi
    fi
    
    # Create and push tag
    git add .
    git commit -m "Release version $version" || true
    git tag "v$version"
    git push origin "v$version"
    
    print_info "Git tag v$version created and pushed"
}

# Generate changelog
generate_changelog() {
    local version=$1
    
    print_step "Generating changelog..."
    
    # Get commits since last tag
    local last_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
    local commits_range=""
    
    if [ -n "$last_tag" ]; then
        commits_range="$last_tag..HEAD"
    else
        commits_range="HEAD"
    fi
    
    # Generate changelog
    cat > CHANGELOG.md << EOF
# Changelog for AWDX $version

## What's Changed

$(git log --oneline --pretty=format:"- %s" $commits_range | head -20)

## Installation

### Python Package
\`\`\`bash
pip install awdx
\`\`\`

### Binary Download
Download the appropriate binary for your platform from the [GitHub releases page](https://github.com/$GITHUB_REPO/releases/tag/v$version).

## Full Changelog
See the [full commit history](https://github.com/$GITHUB_REPO/compare/$last_tag...v$version) for complete details.
EOF
    
    print_info "Changelog generated: CHANGELOG.md"
}

# Main release process
main() {
    print_header
    
    # Parse arguments
    local version_type="patch"
    local skip_tests=false
    local skip_build=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --major)
                version_type="major"
                shift
                ;;
            --minor)
                version_type="minor"
                shift
                ;;
            --patch)
                version_type="patch"
                shift
                ;;
            --skip-tests)
                skip_tests=true
                shift
                ;;
            --skip-build)
                skip_build=true
                shift
                ;;
            --help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --major          Bump major version"
                echo "  --minor          Bump minor version"
                echo "  --patch          Bump patch version (default)"
                echo "  --skip-tests     Skip running tests"
                echo "  --skip-build     Skip building packages and binaries"
                echo "  --help           Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Check environment
    check_environment
    
    # Get current version
    local current_version=$(get_current_version)
    local new_version=$(get_next_version "$current_version" "$version_type")
    
    print_info "Current version: $current_version"
    print_info "New version: $new_version"
    print_info "Version type: $version_type"
    
    # Confirm release
    read -p "Do you want to proceed with releasing version $new_version? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Release cancelled"
        exit 0
    fi
    
    # Run tests
    if [ "$skip_tests" = false ]; then
        run_tests
    else
        print_warning "Skipping tests"
    fi
    
    # Build packages and binaries
    if [ "$skip_build" = false ]; then
        build_python_packages
        build_binaries
        test_binary
    else
        print_warning "Skipping build process"
    fi
    
    # Generate changelog
    generate_changelog "$new_version"
    
    # Update version
    update_version "$new_version"
    
    # Create git tag
    create_git_tag "$new_version"
    
    print_header
    print_step "Release process completed successfully!"
    print_info "Version $new_version has been tagged and pushed"
    print_info "GitHub Actions will now build and release the binaries"
    print_info "Check the releases page: https://github.com/$GITHUB_REPO/releases"
    
    if [ "$skip_build" = false ]; then
        print_info "Local builds are available in the dist/ directory"
    fi
}

# Run main function with all arguments
main "$@"
