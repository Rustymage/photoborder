#!/bin/bash
# Install Quick Actions for photoborder
# This script copies the workflow files to ~/Library/Services/ to make them available
# as Quick Actions in Finder's right-click menu

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICES_DIR="$HOME/Library/Services"
WORKFLOWS_DIR="$SCRIPT_DIR/osx_services"

echo "📦 Installing photoborder Quick Actions..."
echo ""

# Check if Python dependencies are installed
echo "🔍 Checking Python dependencies..."
PYTHON=""
if [ -f ~/.pyenv/shims/python ]; then
    PYTHON=~/.pyenv/shims/python
elif command -v python3 &> /dev/null; then
    PYTHON=python3
else
    PYTHON=python
fi

echo "   Using Python: $PYTHON"

# Check if required packages are installed
if ! $PYTHON -c "import PIL, extcolors" 2>/dev/null; then
    echo "⚠️  Warning: Required Python packages not found!"
    echo "   Please install dependencies with:"
    echo "   $PYTHON -m pip install -r $SCRIPT_DIR/requirements.txt"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Python dependencies found"
fi

echo ""

# Create Services directory if it doesn't exist
if [ ! -d "$SERVICES_DIR" ]; then
    echo "📁 Creating Services directory..."
    mkdir -p "$SERVICES_DIR"
fi

# Copy all workflow files
echo "📋 Installing workflows:"
cd "$WORKFLOWS_DIR"
for workflow in *.workflow; do
    if [ -d "$workflow" ]; then
        echo "   • $workflow"
        # Remove existing if present
        if [ -d "$SERVICES_DIR/$workflow" ]; then
            rm -rf "$SERVICES_DIR/$workflow"
        fi
        # Copy new version
        cp -R "$workflow" "$SERVICES_DIR/"
    fi
done

echo ""
echo "✅ Installation complete!"
echo ""
echo "📝 Quick Actions installed:"
echo "   • Add Exif Border (small, medium, large, polaroid, instagram)"
echo "   • Add White Border (small, medium, large, polaroid, instagram)"
echo ""
echo "💡 To use:"
echo "   1. Right-click on any image in Finder"
echo "   2. Navigate to: Quick Actions"
echo "   3. Select your desired border option"
echo ""
echo "⚙️  Note: If Quick Actions don't appear immediately, you may need to:"
echo "   - Log out and log back in, or"
echo "   - Restart your Mac"
echo ""
echo "🔧 To uninstall, simply delete the workflows from:"
echo "   $SERVICES_DIR"
