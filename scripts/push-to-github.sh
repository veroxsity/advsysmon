#!/bin/bash
# GitHub Push Script for Advanced System Monitor
# Author: Daniel (@veroxsity)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 Advanced System Monitor - GitHub Push Script"
echo "==============================================="

cd "$PROJECT_ROOT"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ This is not a Git repository!"
    echo "Please initialize Git first:"
    echo "  git init"
    echo "  git remote add origin https://github.com/veroxsity/advsysmon.git"
    exit 1
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 Uncommitted changes detected:"
    git status --short
    echo ""
    
    # Ask for commit message
    read -p "Enter commit message (or press Enter for auto-generated message): " commit_msg
    
    if [ -z "$commit_msg" ]; then
        # Generate automatic commit message based on changes
        timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        commit_msg="Update: $timestamp"
    fi
    
    echo "📦 Adding all changes..."
    git add .
    
    echo "💾 Committing changes..."
    git commit -m "$commit_msg"
    
    echo "✅ Changes committed with message: '$commit_msg'"
else
    echo "✅ No uncommitted changes found."
fi

# Check if remote exists
if ! git remote get-url origin >/dev/null 2>&1; then
    echo "❌ No remote 'origin' found!"
    echo "Please add the GitHub remote:"
    echo "  git remote add origin https://github.com/veroxsity/advsysmon.git"
    exit 1
fi

# Get current branch
current_branch=$(git branch --show-current)
echo "🌿 Current branch: $current_branch"

# Push to GitHub
echo "🚀 Pushing to GitHub..."
if git push origin "$current_branch"; then
    echo ""
    echo "🎉 Successfully pushed to GitHub!"
    echo "📍 Repository: https://github.com/veroxsity/advsysmon"
    echo "🌿 Branch: $current_branch"
else
    echo ""
    echo "❌ Failed to push to GitHub!"
    echo "This might be because:"
    echo "  1. You need to authenticate with GitHub"
    echo "  2. The remote repository doesn't exist"
    echo "  3. You don't have push permissions"
    echo ""
    echo "To set up authentication:"
    echo "  - Use SSH keys: https://docs.github.com/en/authentication/connecting-to-github-with-ssh"
    echo "  - Or use GitHub CLI: gh auth login"
    exit 1
fi

echo ""
echo "🔗 Next steps:"
echo "  - View your repository: https://github.com/veroxsity/advsysmon"
echo "  - Create a release: https://github.com/veroxsity/advsysmon/releases/new"
echo "  - Set up GitHub Actions for CI/CD"
echo ""
echo "Happy coding! 🎯"
