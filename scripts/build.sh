#!/bin/bash
# Build script for Advanced System Monitor packages

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VERSION="1.0.0"

echo "🏗️  Building Advanced System Monitor v${VERSION}"
echo "=============================================="

cd "$PROJECT_ROOT"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/ releases/*.deb releases/*.tar.gz

# Build Python package
echo "📦 Building Python package..."
python setup.py sdist bdist_wheel

# Create release directory
mkdir -p releases

# Copy built packages
echo "📋 Copying packages to releases..."
cp dist/*.tar.gz releases/ 2>/dev/null || true
cp dist/*.whl releases/ 2>/dev/null || true

# Create installation archive
echo "📦 Creating installation archive..."
tar -czf releases/advsysmon-install-${VERSION}.tar.gz \
    src/advsysmon.py \
    scripts/install.sh \
    requirements.txt \
    README.md \
    LICENSE

echo ""
echo "✅ Build completed successfully!"
echo ""
echo "📁 Generated files in releases/:"
ls -la releases/
echo ""
echo "🚀 Ready for distribution!"
