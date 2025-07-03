#!/bin/bash
# Advanced System Monitor Installation Script

set -e

PACKAGE_NAME="advanced-sysmon"
VERSION="1.0.0"
INSTALL_DIR="/usr/local"

echo "🖥️  Advanced System Monitor Installer v${VERSION}"
echo "=================================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    echo "⚠️  This script should not be run as root!"
    echo "Please run as a regular user. It will prompt for sudo when needed."
    exit 1
fi

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

echo "✅ pip3 found"

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install --user psutil rich colorama tabulate blessed click

# Optional dependencies
echo "📦 Installing optional dependencies (for GPU monitoring)..."
pip3 install --user pynvml GPUtil 2>/dev/null || echo "⚠️  GPU monitoring packages failed to install (this is normal if you don't have an NVIDIA GPU)"

# Create installation directory
INSTALL_PATH="${INSTALL_DIR}/lib/${PACKAGE_NAME}"
BIN_PATH="${INSTALL_DIR}/bin"

echo ""
echo "📁 Creating installation directories..."
sudo mkdir -p "${INSTALL_PATH}"
sudo mkdir -p "${BIN_PATH}"

# Copy core files
echo "📋 Installing application files..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
sudo cp "${PROJECT_ROOT}/src/advsysmon.py" "${INSTALL_PATH}/advanced_sysmon_core.py"

# Create launcher script
echo "🚀 Creating launcher script..."
sudo tee "${BIN_PATH}/advanced-sysmon" > /dev/null << 'EOF'
#!/usr/bin/env python3
import sys
import os

# Add the library path to sys.path
sys.path.insert(0, '/usr/local/lib/advanced-sysmon')

try:
    from advanced_sysmon_core import main
    main()
except ImportError as e:
    print(f"Error: Could not import system monitor: {e}")
    print("Please ensure all dependencies are installed:")
    print("pip3 install --user psutil rich colorama tabulate blessed click")
    sys.exit(1)
except KeyboardInterrupt:
    print("\nShutting down...")
    sys.exit(0)
EOF

# Make launcher executable
sudo chmod +x "${BIN_PATH}/advanced-sysmon"

# Create desktop entry
DESKTOP_DIR="$HOME/.local/share/applications"
mkdir -p "$DESKTOP_DIR"

echo "🖥️  Creating desktop entry..."
cat > "$DESKTOP_DIR/advanced-sysmon.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Advanced System Monitor
Comment=Feature-rich system monitor with beautiful terminal UI
Exec=gnome-terminal -e advanced-sysmon
Icon=utilities-system-monitor
Terminal=false
Categories=System;Monitor;
Keywords=system;monitor;cpu;memory;disk;network;process;
EOF

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "Usage:"
echo "  Command line: advanced-sysmon"
echo "  Desktop: Look for 'Advanced System Monitor' in your applications menu"
echo ""
echo "GitHub Repository: https://github.com/veroxsity/advsysmon"
echo "Author: Daniel (@veroxsity)"
echo ""
echo "To uninstall:"
echo "  sudo rm -rf ${INSTALL_PATH}"
echo "  sudo rm -f ${BIN_PATH}/advanced-sysmon"
echo "  rm -f $HOME/.local/share/applications/advanced-sysmon.desktop"
echo ""
echo "Enjoy monitoring your system! 🚀"
