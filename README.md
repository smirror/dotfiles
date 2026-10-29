# Dotfiles

Personal dotfiles configuration for development environment.

## Features

- **Fish Shell**: Modern shell configuration with useful aliases and functions
- **Git**: Comprehensive git configuration with aliases
- **Tmux**: Terminal multiplexer configuration
- **Modern CLI Tools**: Replacements for traditional Unix tools (bat, exa, fd, rg, etc.)

## Quick Start

### Installation

1. Clone this repository:
```bash
git clone git@github.com:smirror/dotfiles.git ~/.dotfiles
cd ~/.dotfiles
```

2. Run the installation script:
```bash
# Install tools and setup dotfiles
./scripts/install.sh

# Or just setup dotfiles without installing tools (moves dotfiles to ~/.config)
./scripts/setup.sh
```

### Manual Setup

If you prefer to setup manually:

```bash
# Fish shell configuration
ln -sf ~/.dotfiles/fish/config.fish ~/.config/fish/config.fish
ln -sf ~/.dotfiles/fish/fish_plugins ~/.config/fish/fish_plugins

# Git configuration (update email in config/git/gitconfig first)
ln -sf ~/.dotfiles/config/git/gitconfig ~/.gitconfig

# Tmux configuration
ln -sf ~/.dotfiles/config/tmux/tmux.conf ~/.tmux.conf
```

## Current macOS configuration

- Git and Tmux use symlinks into `~/.dotfiles`; changing those source files changes the configuration used by this machine.
- Fish uses separate files under `~/.config/fish/`. The tracked `fish/config.fish` is a snapshot; editing it does not update the active configuration.
- The live `~/.config/fish/fish_variables` may contain API keys and is not copied into this snapshot update.
- Tool-generated completions (`bun.fish`, `copilot.fish`, `smg.fish`) and backup files are not included in this snapshot.
- `scripts/setup.sh` moves the Fish subdirectories out of this repository. Do not rerun it to synchronize this snapshot.

### Checking Fish changes

Run `python3 -B -m unittest discover -s tests` with Fish and Git installed. The tests use temporary homes and repositories; they do not load the active Fish configuration or credentials.

## Configuration Details

### Fish Shell

The Fish configuration includes:
- Modern command replacements (exa for ls, bat for cat, etc.)
- Git aliases for common operations
- FZF integration with preview
- Key bindings for history and directory navigation
- Fisher plugin manager integration

### Git Configuration

Pre-configured with:
- User settings (update email address)
- Useful aliases (st, co, br, lg, etc.)
- Color output
- Default pull/push behavior

### Tmux Configuration

Features:
- Mouse support enabled
- Custom key bindings for pane navigation
- Status bar customization
- 256 color support

## Tools Included

The install script will set up these modern CLI tools:

- **bat**: Better cat with syntax highlighting
- **exa**: Modern ls replacement
- **fd**: Fast and user-friendly find alternative
- **ripgrep (rg)**: Faster grep alternative
- **dust**: Better du
- **procs**: Modern ps replacement
- **fzf**: Fuzzy finder
- **fish**: User-friendly shell
- **tmux**: Terminal multiplexer

## Customization

### Git Configuration

Before using, update your email in `config/git/gitconfig`:

```ini
[user]
    name = smirror
    email = your-actual-email@example.com
```

### Fish Plugins

Edit `fish/fish_plugins` to add or remove Fisher plugins:

```
jorgebucaran/fisher
jethrokuan/z
jethrokuan/fzf
decors/fish-ghq
0rax/fish-bd
```

## Scripts

- `scripts/install.sh`: Full installation of tools and dotfiles
- `scripts/setup.sh`: Setup dotfiles only (moves files to ~/.config with backup of existing configs)

## Directory Structure

```
dotfiles/
├── config/
│   ├── git/
│   │   └── gitconfig
│   └── tmux/
│       └── tmux.conf
├── fish/
│   ├── config.fish
│   ├── fish_plugins
│   ├── functions/
│   ├── completions/
│   └── conf.d/
├── scripts/
│   ├── install.sh
│   └── setup.sh
└── README.md
```

## License

MIT License - see LICENSE file for details.

