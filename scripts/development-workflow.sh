#!/bin/bash

# Development Workflow Script for awdx
# This script helps contributors follow the proper branching strategy

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Function to check if we're in a git repository
check_git_repo() {
    if [ ! -d ".git" ]; then
        print_error "Not in a git repository. Please run this script from the awdx project root."
        exit 1
    fi
}

# Function to check if we're on the development branch
check_development_branch() {
    current_branch=$(git branch --show-current)
    if [ "$current_branch" != "development" ]; then
        print_warning "You are not on the development branch. Current branch: $current_branch"
        read -p "Do you want to switch to development branch? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git checkout development
            git pull origin development
        else
            print_error "Please switch to development branch manually and run this script again."
            exit 1
        fi
    fi
}

# Function to create a new feature branch
create_feature_branch() {
    print_step "Creating new feature branch..."
    
    read -p "Enter feature name (e.g., profile-validation): " feature_name
    
    # Validate feature name
    if [[ ! $feature_name =~ ^[a-z0-9-]+$ ]]; then
        print_error "Feature name must contain only lowercase letters, numbers, and hyphens."
        exit 1
    fi
    
    branch_name="feature/$feature_name"
    
    # Check if branch already exists
    if git show-ref --verify --quiet refs/heads/$branch_name; then
        print_error "Branch $branch_name already exists. Please choose a different name."
        exit 1
    fi
    
    # Create and switch to new branch
    git checkout -b $branch_name
    print_status "Created and switched to branch: $branch_name"
    
    echo "$branch_name" > .current_branch
    print_status "Branch name saved to .current_branch"
}

# Function to create a new bugfix branch
create_bugfix_branch() {
    print_step "Creating new bugfix branch..."
    
    read -p "Enter bugfix description (e.g., fix-profile-switching): " bugfix_name
    
    # Validate bugfix name
    if [[ ! $bugfix_name =~ ^[a-z0-9-]+$ ]]; then
        print_error "Bugfix name must contain only lowercase letters, numbers, and hyphens."
        exit 1
    fi
    
    branch_name="bugfix/$bugfix_name"
    
    # Check if branch already exists
    if git show-ref --verify --quiet refs/heads/$branch_name; then
        print_error "Branch $branch_name already exists. Please choose a different name."
        exit 1
    fi
    
    # Create and switch to new branch
    git checkout -b $branch_name
    print_status "Created and switched to branch: $branch_name"
    
    echo "$branch_name" > .current_branch
    print_status "Branch name saved to .current_branch"
}

# Function to run pre-commit checks
run_pre_commit_checks() {
    print_step "Running pre-commit checks..."
    
    # Check if virtual environment is activated
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        print_warning "Virtual environment not activated. Activating..."
        source venv/bin/activate
    fi
    
    # Run tests
    print_status "Running tests..."
    python -m pytest tests/ -v
    
    # Run linting
    print_status "Running linting checks..."
    python -m flake8 src/
    python -m mypy src/
    
    # Build package
    print_status "Building package..."
    python -m build
    twine check dist/*
    
    print_status "All pre-commit checks passed!"
}

# Function to commit changes
commit_changes() {
    print_step "Committing changes..."
    
    # Check if there are changes to commit
    if git diff --cached --quiet && git diff --quiet; then
        print_warning "No changes to commit."
        return
    fi
    
    # Show status
    git status
    
    # Add all changes
    git add .
    
    # Get commit message
    read -p "Enter commit message (following conventional commits format): " commit_message
    
    # Validate commit message format
    if [[ ! $commit_message =~ ^(feat|fix|docs|style|refactor|test|chore)(\([a-z-]+\))?: ]]; then
        print_warning "Commit message should follow conventional commits format: type(scope): description"
        print_warning "Examples: feat(profilyze): add profile validation"
        read -p "Continue anyway? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Commit cancelled."
            exit 1
        fi
    fi
    
    # Commit changes
    git commit -m "$commit_message"
    print_status "Changes committed successfully!"
}

# Function to push changes
push_changes() {
    print_step "Pushing changes..."
    
    current_branch=$(git branch --show-current)
    
    # Push to remote
    git push origin $current_branch
    print_status "Changes pushed to remote branch: $current_branch"
    
    # Show PR creation instructions
    print_status "Next steps:"
    echo "1. Go to: https://github.com/pxkundu/awdx/pulls"
    echo "2. Click 'New Pull Request'"
    echo "3. Set base branch to 'development'"
    echo "4. Set compare branch to '$current_branch'"
    echo "5. Use the PR template and request reviews"
}

# Function to show current status
show_status() {
    print_step "Current development status..."
    
    current_branch=$(git branch --show-current)
    print_status "Current branch: $current_branch"
    
    # Show uncommitted changes
    if ! git diff --quiet; then
        print_warning "You have uncommitted changes:"
        git status --short
    else
        print_status "No uncommitted changes"
    fi
    
    # Show branch information
    if [ -f .current_branch ]; then
        saved_branch=$(cat .current_branch)
        if [ "$current_branch" = "$saved_branch" ]; then
            print_status "Working on saved branch: $saved_branch"
        else
            print_warning "Current branch ($current_branch) differs from saved branch ($saved_branch)"
        fi
    fi
}

# Function to show help
show_help() {
    echo "Development Workflow Script for awdx"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  feature     Create a new feature branch"
    echo "  bugfix      Create a new bugfix branch"
    echo "  check       Run pre-commit checks"
    echo "  commit      Commit changes with conventional commit message"
    echo "  push        Push changes to remote"
    echo "  status      Show current development status"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 feature    # Create a new feature branch"
    echo "  $0 check      # Run tests and linting"
    echo "  $0 commit     # Commit changes"
    echo "  $0 push       # Push to remote and show PR instructions"
}

# Main script logic
main() {
    check_git_repo
    
    case "${1:-help}" in
        "feature")
            check_development_branch
            create_feature_branch
            ;;
        "bugfix")
            check_development_branch
            create_bugfix_branch
            ;;
        "check")
            run_pre_commit_checks
            ;;
        "commit")
            commit_changes
            ;;
        "push")
            push_changes
            ;;
        "status")
            show_status
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function with all arguments
main "$@" 