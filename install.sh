#!/bin/bash

# Define onde instalar os links (padrão do usuário)
BIN_DIR="$HOME/.local/bin"
COMP_DIR="$HOME/.zsh/completions"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "--- Instalando cptools ---"

# 1. Garante que as pastas de destino existem
mkdir -p "$BIN_DIR"
mkdir -p "$COMP_DIR"

# 2. Linka o executável + alias
echo "Criando links simbólicos..."
ln -sf "$REPO_DIR/cptools" "$BIN_DIR/cptools"
ln -sf "$REPO_DIR/cptools" "$BIN_DIR/cpt"
chmod +x "$REPO_DIR/cptools"

# 3. Linka o autocomplete
ln -sf "$REPO_DIR/completions/_cptools" "$COMP_DIR/_cptools"
ln -sf "$REPO_DIR/completions/_cptools" "$COMP_DIR/_cpt"

# 4. Remove links antigos do cp-cli (migração)
rm -f "$BIN_DIR/cp-cli"
rm -f "$COMP_DIR/_cp-cli"

# 5. Configura PATH e fpath no shell rc
SHELL_RC=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
fi

if [ -n "$SHELL_RC" ]; then
    # Adiciona ~/.local/bin ao PATH se não estiver
    if ! grep -q 'local/bin' "$SHELL_RC"; then
        echo '' >> "$SHELL_RC"
        echo '# cptools' >> "$SHELL_RC"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
        echo "  + PATH configurado em $SHELL_RC"
    fi

    # Adiciona fpath para completions do zsh
    if [ -f "$HOME/.zshrc" ] && ! grep -q '.zsh/completions' "$HOME/.zshrc"; then
        if grep -q 'compinit' "$HOME/.zshrc"; then
            sed -i '/autoload -Uz compinit/i fpath=(~/.zsh/completions $fpath)' "$HOME/.zshrc"
        else
            echo 'fpath=(~/.zsh/completions $fpath)' >> "$HOME/.zshrc"
            echo 'autoload -Uz compinit && compinit' >> "$HOME/.zshrc"
        fi
        echo "  + fpath configurado para autocomplete"
    fi
fi

echo ""
echo "--- Sucesso! ---"
echo "Comandos disponíveis: cptools, cpt"
echo "Reinicie o terminal ou rode: source $SHELL_RC"
