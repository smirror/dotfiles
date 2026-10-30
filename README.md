# Dotfiles

Personal dotfiles configuration for development environment.

## Features

- **Fish Shell**: Modern shell configuration with useful aliases and functions
- **Git**: Comprehensive git configuration with aliases
- **Tmux**: Terminal multiplexer configuration
- **Modern CLI Tools**: Replacements for traditional Unix tools (bat, exa, fd, rg, etc.)

## Nix + Home Manager (macOS and WSL)

The shared environment is declared in `flake.nix` and `home.nix`. Both macOS and WSL use the same declarations and commands; only OS/CPU detection and local user/home values differ. nix-darwin, NixOS and Ansible are not required.

- `home.nix` installs the declared CLI tools and Fish, and manages an explicit list of Fish helper files.
- Codex and Claude Code share `agents/global.md`. Existing external Skills keep their current installer ownership.
- Git/Tmux settings, `fish_variables`, histories, credentials and client permission settings are outside this migration.
- Home Manager normally links managed files into the Nix store; an identical existing regular file may be left in place. Parent directories and unrelated local files stay outside its ownership.

See the [tool inventory and proposed additions](docs/tool-inventory.md) before activation. The pinned Fish and ripgrep versions are currently older than the inspected machine's versions.

### Prepare and build

The initial shell script installs a pinned, checksum-verified official Nix release if Nix is absent. On macOS this adds the Nix volume, build users and daemon; review [the migration procedure](docs/nix-migration.md) before running it. It does not switch the login shell or apply Home Manager.

```sh
./scripts/bootstrap.sh
# Open a new shell after Nix installation.
./scripts/home-manager.sh check   # evaluate all four declared OS/CPU targets
./scripts/home-manager.sh build   # build the current target; do not activate it
```

`DOTFILES_USER` and `DOTFILES_HOME` default to the current user and home directory. The same shared declaration handles `aarch64-darwin`, `x86_64-darwin`, `aarch64-linux` and `x86_64-linux`. Explicit overrides are intended for isolated evaluation/build tests, not another person's live home.

Nixpkgs and Home Manager are pinned to matching stable 26.05 commits. The first real Nix evaluation creates `flake.lock`; review and commit that generated lock file before treating the migration as complete. A syntax check alone is not Nix evaluation or a successful build.

### Review and activate

Inspect `result/home-files`, compare every managed destination and prepare the backups described in [the migration procedure](docs/nix-migration.md). Existing differing files cause a collision; there is no automatic forced overwrite.

```sh
# Only after the file/profile changes and restoration procedure are reviewed:
./scripts/home-manager.sh switch
```

Do not run `fisher update` against the Nix-managed helper files. Change the tracked sources and rebuild instead. `fish_variables` is not an import source for Home Manager and must not be copied from the live machine into this repository.

### Checks without applying

```sh
python3 -B -m unittest discover -s tests -v
```

The tests use temporary homes and repositories. Installer and Nix command-routing tests use fakes and do not prove a real Nix install/build. They never load live Fish credentials.

### Existing deployment

The current Git/Tmux links into `~/.dotfiles` remain unchanged. The live Fish configuration remains separate until Home Manager is explicitly activated. The original `scripts/install.sh` is Linux-only; `scripts/setup.sh` moves Fish subdirectories out of the repository. Neither legacy script is part of the Nix workflow and neither should be run for this migration.

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

## Tool declarations

The Nix declaration currently contains 15 explicit CLI packages plus Fish and Home Manager. This adds `fd` and `lazygit` to the previously published draft. It is smaller than the legacy Linux install list. The [tool inventory](docs/tool-inventory.md) distinguishes declared tools, proposed additions and existing installations that need an ownership/version decision.

The current editor is Neovim + LazyVim. Its existing configuration remains separately managed; the retired SpaceVim configuration has been removed.

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

