# Reinstallable tool definitions

The first target is a selected tool set that can be installed again. Prompt
management remains a later task. LazyVim's personal configuration, work/doctor
commands, CI and Skill cleanup are outside this change.

## Selected shared tools

These are the initial reinstall targets in `home.nix`, not a dump of everything
installed on one machine. They use the existing Nixpkgs/Home Manager revisions
and source hashes in `flake.lock`; update and validate that lock deliberately.

| Tools | Purpose | Installer | Version policy |
| --- | --- | --- | --- |
| `git`, `gh`, `ghq`, `lazygit` | Git operations, GitHub and repository navigation | Nix | Fixed by the lock |
| `tmux` | Terminal sessions | Nix | Fixed by the lock |
| `neovim` | Editor executable for the existing LazyVim setup | Nix | Fixed by the lock |
| `jq` | JSON inspection and transformation | Nix | Fixed by the lock |
| `fd`, `ripgrep`, `bat` | File search, text search and previews | Nix | Fixed by the lock |
| `fzf`, `peco` | Existing shell selection helpers | Nix | Fixed by the lock |
| `starship` | Shell prompt | Nix | Fixed by the lock |
| `coreutils`, `findutils`, `gawk`, `getopt`, `gnugrep`, `gnused`, `perl` | Portable helper dependencies and GNU options | Nix | Fixed by the lock |
| Fish, Home Manager | Shell and existing deployment mechanism | Home Manager modules | Fixed by the lock |

There are 20 explicit packages plus the two module-provided programs. Git,
GitHub CLI, Tmux, jq and Neovim are new declarations in this change. Adding
their binaries does not add ownership of their settings, authentication or
saved data. Existing Brew installations are retained.

## First validation and subsequent installation

With Nix available, use the existing commands:

```sh
./scripts/home-manager.sh check
./scripts/home-manager.sh build
```

Inspect `result/home-path/bin` to test the selected binaries without activating
the managed configuration. `scripts/home-manager.sh switch` also applies the
existing Fish/global-instruction file declarations; it is not a tools-only
installer. Follow [the migration procedure](nix-migration.md) before using it.
No host switch is part of this tool-list update.

Nix takes command precedence after activation. On the inspected machine,
Git changes from Apple Git 2.54.0 to Nix Git 2.56.0, and jq from Apple's 1.7.1
to Nix 1.8.2. gh 2.103.3, tmux 3.8 and Neovim 0.12.6 match the inspected
versions. Matching versions do not prove identical packaging or behavior.

## LazyVim on a new machine

Neovim and LazyVim are separate installation steps. The existing machine
already has LazyVim; leave its configuration, lock file, plugin downloads,
Mason tools and editor state under their present ownership.

For a new environment only, this optional starter initialization keeps any
existing configuration, including a symlink. Run it after Git is available:

```sh
dotfiles_nvim_config="${XDG_CONFIG_HOME:-$HOME/.config}/nvim"
if [ -e "$dotfiles_nvim_config" ] || [ -L "$dotfiles_nvim_config" ]; then
    printf '%s\n' 'Existing Neovim configuration retained.'
else
    git clone --no-checkout https://github.com/LazyVim/starter.git "$dotfiles_nvim_config" &&
        git -C "$dotfiles_nvim_config" checkout --detach 803bc181d7c0d6d5eeba9274d9be49b287294d99
fi
```

This pins the starter snapshot, not all future plugins. Normal first startup
downloads plugins through lazy.nvim; plugin updates and its writable lock file
remain outside dotfiles management. No automatic normal Neovim startup is run
against the existing machine. See the [official installation procedure](https://www.lazyvim.org/installation).

## Remaining inventory and ownership decisions

A refreshed private inventory records 170 Brew formulae, four casks and 34
formulae with direct-install history. It also records global npm, uv, pipx and
Cargo tools and 53 application bundles. Direct-install metadata is historical,
and application presence is not an instruction to reinstall it. Dependencies
are not copied into the top-level declaration automatically.

| Area | Current ownership to retain | Remaining decision |
| --- | --- | --- |
| Node, Corepack/pnpm, Bun | Existing Brew/Corepack/standalone installations | Runtime versions and package list; avoid replacing them alongside five unrelated CLI additions |
| Python, uv, pipx | OS/Brew Python and existing isolated tool environments | Choose the default Python explicitly; an installed newer Python is not necessarily the selected interpreter |
| Rust and global Cargo tools | rustup/Cargo and any local source repositories | Record toolchain/package versions and source restoration for local tools |
| Go and Go tools | Current Go installation and existing tool distribution | Choose the runtime version and required tools |
| AI clients and external Skills | Existing native, Brew, npm and uv installers | Record required clients and exact sources; GSD is currently unused and excluded from the initial reinstall set |
| macOS applications, fonts and TeX | Current installers, including Brew casks | Curate a Brewfile after choosing the wanted applications; do not export all dependencies or start services |
| Specialist tools and local services | Current installers and existing data | Confirm need and preserve data; no service/database operations are performed here |

Full raw inventory stays outside this public repository. Personal prompts,
API keys, account state, application data and project paths are not install
definitions. Bun's previous global-list query failed while attempting lock
migration; it remains unconfirmed and was not retried during this inventory.

A future Brewfile records selected Homebrew targets and an update policy; it
is not a replacement for the Nix lock's exact package selection. Do not maintain
the same desired CLI list in both managers. See [Homebrew Bundle documentation](https://docs.brew.sh/Brew-Bundle-and-Brewfile).
