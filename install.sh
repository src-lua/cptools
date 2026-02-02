#!/bin/bash

# Define where to install the links (user default)
BIN_DIR="$HOME/.local/bin"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "--- Installing cptools ---"

# 1. Ensure target directories exist
mkdir -p "$BIN_DIR"

# 2. Link the executable + alias
echo "Creating symbolic links..."
ln -sf "$REPO_DIR/cptools" "$BIN_DIR/cptools"
ln -sf "$REPO_DIR/cptools" "$BIN_DIR/cpt"
chmod +x "$REPO_DIR/cptools"

# 4. Remove old cp-cli links (migration)
rm -f "$BIN_DIR/cp-cli"

# 5. Configure PATH in shell rc
SHELL_RC=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

if [ -n "$SHELL_RC" ]; then
    # Add ~/.local/bin to PATH if it's not there
    if ! grep -q 'local/bin' "$SHELL_RC"; then
        echo '' >> "$SHELL_RC"
        echo '# cptools' >> "$SHELL_RC"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
        echo "  + PATH configured in $SHELL_RC"
    fi
fi

echo ""
echo "--- Success! ---"
echo "Available commands: cptools, cpt"
echo "To enable autocompletion, run: cptools completion --install"
echo "Restart your terminal or run: source $SHELL_RC"
