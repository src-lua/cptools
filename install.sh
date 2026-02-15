#!/bin/bash

# Define where to install the links (user default)
BIN_DIR="$HOME/.local/bin"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "--- Installing cptools ---"

# 1. Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.10+ and try again."
    echo ""
    echo "On Ubuntu/Debian: sudo apt install python3 python3-pip"
    exit 1
fi

# 2. Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ -n "$PYTHON_MAJOR" ] && [ -n "$PYTHON_MINOR" ]; then
    if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]; }; then
        echo "❌ Error: Python 3.10+ is required (found: $PYTHON_VERSION)"
        echo "Please upgrade Python and try again."
        exit 1
    fi
    echo "  ✓ Python $PYTHON_VERSION detected"
else
    echo "  ⚠️  Warning: Could not detect Python version"
fi

# 3. Ensure target directories exist
mkdir -p "$BIN_DIR"

# 4. Make original script executable
chmod +x "$REPO_DIR/cptools"

# 4b. Link the executable + alias (will be replaced by wrappers if using venv)
echo "Creating symbolic links..."
ln -sf "$REPO_DIR/cptools" "$BIN_DIR/cptools"
ln -sf "$REPO_DIR/cptools" "$BIN_DIR/cpt"

# 5. Install Python dependencies
echo "Installing Python dependencies..."

# Check if browser-cookie3 is already installed with correct version
if python3 -c "import browser_cookie3; assert browser_cookie3.__version__ >= '0.19.1'" 2>/dev/null; then
    echo "  ✓ browser-cookie3 already installed"
else
    # Try to install
    ERROR_OUTPUT=$(python3 -m pip install --user "browser-cookie3>=0.19.1" 2>&1)
    if [ $? -eq 0 ]; then
        echo "  ✓ Dependencies installed successfully"
    else
        if echo "$ERROR_OUTPUT" | grep -q "externally-managed-environment"; then
            # PEP 668: System restricts pip
            echo ""
            echo "  ⚠️  Your system restricts pip (PEP 668 - externally-managed-environment)"
            echo ""
            echo "  Choose installation method:"
            echo "    1) Create virtual environment (recommended, safer)"
            echo "    2) Use --break-system-packages (simpler, but not best practice)"
            echo ""
            read -p "  Choice [1/2]: " -n 1 -r
            echo

            if [[ $REPLY == "1" ]]; then
                # Create venv
                VENV_DIR="$HOME/.venvs/cptools"
                echo "  → Creating virtual environment at $VENV_DIR..."

                if python3 -m venv "$VENV_DIR" 2>/dev/null; then
                    echo "  ✓ Virtual environment created"

                    # Install dependencies in venv
                    if "$VENV_DIR/bin/pip" install "browser-cookie3>=0.19.1" >/dev/null 2>&1; then
                        echo "  ✓ Dependencies installed in venv"

                        # Replace symlinks with wrapper scripts that use venv Python
                        echo "  → Creating wrapper scripts to use venv..."

                        # Verify original script before proceeding
                        if [ ! -f "$REPO_DIR/cptools" ]; then
                            echo "  ❌ Error: Original cptools not found at: $REPO_DIR/cptools"
                            exit 1
                        fi

                        # Check if original is still a Python script
                        if ! head -1 "$REPO_DIR/cptools" | grep -q python; then
                            echo "  ❌ Error: Original cptools was corrupted!"
                            echo "     This script has a bug. Please report at:"
                            echo "     https://github.com/your-repo/issues"
                            exit 1
                        fi

                        # Remove symlinks first (CRITICAL: must happen before creating files)
                        rm -f "$BIN_DIR/cptools" "$BIN_DIR/cpt"

                        # CRITICAL: Verify symlinks are actually gone
                        if [ -e "$BIN_DIR/cptools" ] || [ -L "$BIN_DIR/cptools" ]; then
                            echo "  ❌ Error: Failed to remove old symlink: $BIN_DIR/cptools"
                            ls -la "$BIN_DIR/cptools"
                            exit 1
                        fi

                        # Create wrapper scripts using printf for safety
                        # Use a temp file first to ensure we never write to a symlink
                        TEMP_WRAPPER=$(mktemp)
                        printf '#!/bin/bash\nexec "%s/bin/python3" "%s/cptools" "$@"\n' \
                            "$VENV_DIR" "$REPO_DIR" > "$TEMP_WRAPPER"

                        mv "$TEMP_WRAPPER" "$BIN_DIR/cptools"

                        TEMP_WRAPPER=$(mktemp)
                        printf '#!/bin/bash\nexec "%s/bin/python3" "%s/cptools" "$@"\n' \
                            "$VENV_DIR" "$REPO_DIR" > "$TEMP_WRAPPER"

                        mv "$TEMP_WRAPPER" "$BIN_DIR/cpt"

                        chmod +x "$BIN_DIR/cptools" "$BIN_DIR/cpt"

                        # Verify everything is correct
                        if [ ! -f "$BIN_DIR/cptools" ] || [ ! -f "$REPO_DIR/cptools" ]; then
                            echo "  ❌ Failed to create wrappers correctly"
                            exit 1
                        fi

                        # Double-check original wasn't corrupted
                        if ! head -1 "$REPO_DIR/cptools" | grep -q python; then
                            echo "  ❌ BUG: Original script was corrupted during wrapper creation!"
                            echo "     Please report this at: https://github.com/your-repo/issues"
                            exit 1
                        fi

                        echo "  ✓ Wrapper scripts created"
                    else
                        echo "  ❌ Failed to install dependencies in venv"
                        exit 1
                    fi
                else
                    echo "  ❌ Failed to create virtual environment"
                    exit 1
                fi

            elif [[ $REPLY == "2" ]]; then
                # Use --break-system-packages
                echo "  → Installing with --break-system-packages..."
                if python3 -m pip install --user --break-system-packages "browser-cookie3>=0.19.1" >/dev/null 2>&1; then
                    echo "  ✓ Dependencies installed"
                else
                    echo "  ❌ Installation failed"
                    exit 1
                fi
            else
                echo "  ❌ Invalid choice. Installation cancelled."
                exit 1
            fi
        else
            echo "  ⚠️  Failed to install dependencies"
            echo "  Please install manually: pip install --user browser-cookie3>=0.19.1"
            exit 1
        fi
    fi
fi

# 6. Remove old cp-cli links (migration)
rm -f "$BIN_DIR/cp-cli"

# 7. Configure PATH in shell rc
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

# 8. Install shell completions
echo ""
echo "Installing shell completions..."
if "$BIN_DIR/cptools" completion --install >/dev/null 2>&1; then
    echo "  ✓ Completions installed"
else
    echo "  ⚠️  Completions will be available after restart (run 'cptools completion --install' if needed)"
fi

echo ""
echo "--- Success! ---"
echo "Available commands: cptools, cpt"
echo ""
if [ -n "$SHELL_RC" ]; then
    echo "Restart your terminal or run: source $SHELL_RC"
fi
