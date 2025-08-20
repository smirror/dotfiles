#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running on supported system
check_system() {
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        echo_error "This script is designed for Linux systems only"
        exit 1
    fi
}

# Install basic packages
install_basics() {
    echo_info "Installing basic packages..."
    sudo apt update
    sudo apt install -y \
        curl \
        wget \
        git \
        vim \
        tmux \
        htop \
        tree \
        unzip \
        build-essential \
        ca-certificates \
        gnupg \
        lsb-release
}

# Install modern CLI tools
install_modern_tools() {
    echo_info "Installing modern CLI tools..."
    
    # Rust-based tools
    if ! command -v cargo &> /dev/null; then
        echo_info "Installing Rust..."
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
        source ~/.cargo/env
    fi
    
    # Install rust tools
    cargo install \
        bat \
        exa \
        fd-find \
        ripgrep \
        du-dust \
        procs \
        tokei \
        hyperfine
    
    # Other tools
    sudo apt install -y \
        fzf \
        jq \
        httpie \
        silversearcher-ag
}

# Install Fish shell
install_fish() {
    echo_info "Installing Fish shell..."
    sudo apt install -y fish
    
    # Install Fisher
    if command -v fish &> /dev/null; then
        fish -c "curl -sL https://git.io/fisher | source && fisher install jorgebucaran/fisher"
    fi
}

# Install development tools
install_dev_tools() {
    echo_info "Installing development tools..."
    
    # Node.js
    if ! command -v node &> /dev/null; then
        curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
        sudo apt install -y nodejs
    fi
    
    # Python tools
    sudo apt install -y python3-pip python3-venv
    pip3 install --user --upgrade pip
    
    # Git tools
    sudo apt install -y hub gh
}

# Create symlinks for dotfiles
create_symlinks() {
    echo_info "Creating symlinks for dotfiles..."
    
    # Fish config
    mkdir -p ~/.config/fish
    if [[ -f ~/.config/fish/config.fish ]]; then
        mv ~/.config/fish/config.fish ~/.config/fish/config.fish.backup
    fi
    ln -sf "$PWD/fish/config.fish" ~/.config/fish/config.fish
    ln -sf "$PWD/fish/fish_plugins" ~/.config/fish/fish_plugins
    
    # Git config
    ln -sf "$PWD/config/git/gitconfig" ~/.gitconfig
    
    # Tmux config
    ln -sf "$PWD/config/tmux/tmux.conf" ~/.tmux.conf
}

# Change default shell to Fish
change_default_shell() {
    if command -v fish &> /dev/null; then
        local fish_path=$(which fish)
        
        # Check if fish is in /etc/shells
        if ! grep -q "$fish_path" /etc/shells; then
            echo_info "Adding fish to /etc/shells..."
            echo "$fish_path" | sudo tee -a /etc/shells
        fi
        
        # Ask user if they want to change default shell
        echo_info "Would you like to set Fish as your default shell? (y/N)"
        read -r response
        case "$response" in
            [yY][eE][sS]|[yY])
                chsh -s "$fish_path"
                echo_info "Default shell changed to Fish. Please log out and back in for changes to take effect."
                ;;
            *)
                echo_info "Keeping current shell. You can change it later with: chsh -s $fish_path"
                ;;
        esac
    else
        echo_warn "Fish shell not found. Cannot change default shell."
    fi
}

# Main installation function
main() {
    echo_info "Starting dotfiles installation..."
    
    check_system
    install_basics
    install_modern_tools
    install_fish
    install_dev_tools
    create_symlinks
    change_default_shell
    
    echo_info "Installation completed! Please restart your shell or run 'source ~/.bashrc'"
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi