#!/bin/bash

# Dotfiles setup script
# This script creates symlinks for dotfiles configuration

set -e

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

echo_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Create backup of existing config
backup_file() {
    local file="$1"
    if [[ -f "$file" ]] || [[ -L "$file" ]]; then
        local backup="${file}.backup.$(date +%Y%m%d_%H%M%S)"
        echo_warn "Backing up existing $file to $backup"
        mv "$file" "$backup"
    fi
}

# Create symlink with backup
create_symlink() {
    local source="$1"
    local target="$2"
    
    if [[ ! -f "$source" ]]; then
        echo_error "Source file $source does not exist"
        return 1
    fi
    
    # Create target directory if it doesn't exist
    local target_dir="$(dirname "$target")"
    mkdir -p "$target_dir"
    
    # Backup existing file
    backup_file "$target"
    
    # Create symlink
    ln -sf "$source" "$target"
    echo_info "Created symlink: $target -> $source"
}

# Setup Fish shell configuration
setup_fish() {
    echo_step "Setting up Fish shell configuration..."
    
    local fish_config_dir="$HOME/.config/fish"
    mkdir -p "$fish_config_dir"
    
    create_symlink "$DOTFILES_DIR/fish/config.fish" "$fish_config_dir/config.fish"
    create_symlink "$DOTFILES_DIR/fish/fish_plugins" "$fish_config_dir/fish_plugins"
    
    # Copy other fish files
    if [[ -d "$DOTFILES_DIR/fish/functions" ]]; then
        cp -r "$DOTFILES_DIR/fish/functions" "$fish_config_dir/"
        echo_info "Copied fish functions"
    fi
    
    if [[ -d "$DOTFILES_DIR/fish/completions" ]]; then
        cp -r "$DOTFILES_DIR/fish/completions" "$fish_config_dir/"
        echo_info "Copied fish completions"
    fi
    
    if [[ -d "$DOTFILES_DIR/fish/conf.d" ]]; then
        cp -r "$DOTFILES_DIR/fish/conf.d" "$fish_config_dir/"
        echo_info "Copied fish conf.d"
    fi
}

# Setup Git configuration
setup_git() {
    echo_step "Setting up Git configuration..."
    create_symlink "$DOTFILES_DIR/config/git/gitconfig" "$HOME/.gitconfig"
}

# Setup Tmux configuration
setup_tmux() {
    echo_step "Setting up Tmux configuration..."
    create_symlink "$DOTFILES_DIR/config/tmux/tmux.conf" "$HOME/.tmux.conf"
}

# Install Fish plugins using Fisher
install_fish_plugins() {
    if command -v fish &> /dev/null; then
        echo_step "Installing Fish plugins with Fisher..."
        fish -c "
            if not functions -q fisher
                curl -sL https://git.io/fisher | source && fisher install jorgebucaran/fisher
            end
            fisher update
        "
    else
        echo_warn "Fish shell not found. Skipping plugin installation."
    fi
}

# Main setup function
main() {
    echo_info "Starting dotfiles setup..."
    echo_info "Dotfiles directory: $DOTFILES_DIR"
    
    setup_fish
    setup_git
    setup_tmux
    install_fish_plugins
    
    echo_info "Setup completed successfully!"
    echo_info "To use Fish as your default shell, run: chsh -s /usr/bin/fish"
    echo_info "Restart your terminal or run 'source ~/.bashrc' to apply changes"
}

# Show help
show_help() {
    cat << EOF
Dotfiles Setup Script

Usage: $0 [OPTIONS]

Options:
    -h, --help      Show this help message
    --fish-only     Setup only Fish configuration
    --git-only      Setup only Git configuration
    --tmux-only     Setup only Tmux configuration

Examples:
    $0              # Setup all configurations
    $0 --fish-only  # Setup only Fish shell
EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        --fish-only)
            setup_fish
            install_fish_plugins
            exit 0
            ;;
        --git-only)
            setup_git
            exit 0
            ;;
        --tmux-only)
            setup_tmux
            exit 0
            ;;
        *)
            echo_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
    shift
done

# Run main function if no specific options provided
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main
fi