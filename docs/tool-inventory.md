# Tool inventory and additive migration

Machine snapshot: 2026-10-29; declaration updated 2026-10-30.
This compares the legacy `scripts/install.sh`, the shared
`home.nix` declaration and a read-only inventory of the current macOS machine.
It records declaration changes and a proposed order of adoption, not an installation receipt. WSL has not
been inventoried or tested. Raw machine/package-manager output stays outside Git.

## Current declaration

`home.nix` explicitly lists 15 packages:

```
bat coreutils fd findutils fzf gawk getopt ghq gnugrep gnused
lazygit peco perl ripgrep starship
```

The Fish and Home Manager modules install their respective programs as well:
17 direct components in total, excluding dependencies and the Nix bootstrap.
This change adds `fd` and `lazygit` to the published draft's 13 explicit packages.
It does not install either tool on the live machine.

The legacy installer names 30 distinct apt/Cargo packages. Five overlap with
the current declaration: `bat`, `ripgrep`, `fzf`, `fish` and `fd-find` (as `fd`).
The eleven other CLI entries above make GNU helper requirements, `ghq`, `peco`,
Perl, Starship and lazygit explicit; some were previously implicit OS tools.
Home Manager is the new deployment component. The remaining 25 legacy entries are not all packages
that should be added to the shared environment.

## Legacy list compared with the draft

| Legacy entries | Current Nix declaration | Proposed treatment |
| --- | --- | --- |
| `bat`, `ripgrep`, `fzf`, `fish` | Declared | Keep; review versions and command precedence before activation |
| `curl`, `wget`, `git`, `tmux`, `htop`, `tree`, `unzip`, `gnupg` | Not declared | Separate existing tools from missing commands; retain current installations |
| `vim` | Not declared | Current editor is Neovim + LazyVim; do not reintroduce the old editor configuration |
| `build-essential`, `ca-certificates`, `lsb-release` | Not declared | OS/bootstrap requirements; do not translate these apt names into a shared CLI list |
| `exa` | Not declared | Consider `eza` separately; the existing Fish aliases still check for `exa` |
| `fd-find` | Added as `pkgs.fd` | Command `fd`; also enables the existing Fish `find` alias |
| `du-dust` | Not declared | Existing Brew `dust`; eventual `pkgs.dust` adoption |
| `procs`, `tokei`, `hyperfine` | Not declared | Optional additions restoring legacy CLI coverage |
| `jq`, `httpie`, `silversearcher-ag` | Not declared | `jq` already exists; optional `pkgs.httpie` / `pkgs.silver-searcher` additions |
| `nodejs`, `python3-pip`, `python3-venv` | Not declared | Preserve runtime/package-manager ownership; choose versions before migration |
| `hub`, `gh` | Not declared | `gh` already exists; do not automatically restore `hub` |

The old script also bootstraps Rust/rustup and Fisher conditionally and upgrades
pip. Those actions are not included in the 30-package count and are not carried
out by the new declaration. Existing Fish helper sources are deployed directly
by Home Manager rather than refreshed through Fisher.

## Add first, then transfer ownership

“Missing” below means absent from the inspected normal shell PATH, not absent
from every project, editor or cache. Package availability is based on pinned
source inspection; evaluation/build on the four targets is still required.

| Order | Tools | Change and reason |
| --- | --- | --- |
| 1 | `fzf`, `ghq` | Already declared, missing from the current global PATH; supply existing Fish helper dependencies |
| 2 | `fd`, `lazygit` | Added to the declaration, missing globally in the snapshot; useful for the current LazyVim environment |
| 3 | `procs`, `tokei`, `hyperfine`, `wget`, `tree`, `httpie`, `silver-searcher` | Missing globally; optional legacy coverage, add only the tools still wanted |
| 4 | `eza` | Optional replacement for the legacy `exa` entry; review the related aliases together |
| Later | `neovim`, `gh`, `tmux`, `htop`, `dust`, `jq`, Git/GnuPG | Already usable; declaring them transfers command/version ownership rather than filling a missing-tool gap |

Adding `fd`, `procs` or `eza` can enable conditional Fish aliases and change
`find`, `ps` or `ls` behavior. Review that behavior as part of each addition.
With this change, activation will enable the existing `find='fd'` alias. Use
`command find` when the original find syntax is needed. The alias source itself
is unchanged; `procs` and `eza` remain undeclared.
Do not uninstall Brew packages during this phase. The Nix profile takes PATH
priority, so keeping the old package installed does not preserve the selected
binary or version after activation.

## Keep Neovim + LazyVim working

The current Neovim is Brew 0.12.6 with LuaJIT. `~/.config/nvim` contains the
LazyVim starter configuration and `lazy-lock.json`; plugins are managed by
lazy.nvim. This directory is currently outside Git management.

- Add only the Neovim binary when its version is accepted. Keep the current
  LazyVim configuration and plugin ownership during the initial migration.
- Do not enable an additional Home Manager Neovim configuration/plugin layer
  over the existing `init.lua` without a separate comparison.
- A Tree-sitter CLI 0.26.3 already exists in Mason's bin directory. The Brew
  Tree-sitter library is not evidence of a globally available CLI. Do not add
  a second CLI merely because the normal shell PATH does not contain one.
- Mason also supplies editor tools such as language servers and formatters.
  Review those before duplicating them in the global package list.
- Future management of the LazyVim source needs a writable-lockfile strategy:
  lazy.nvim updates `lazy-lock.json`, while ordinary Nix-store source links are
  read-only. Plugin caches, Mason downloads and editor state remain outside Git.
- Only the retired `.SpaceVim.d/init.toml` is removed in this change. The live
  LazyVim files, OS-provided Vim and Vim history are untouched.

The inspected Neovim version and LuaJIT build satisfy
[LazyVim's Neovim requirement](https://www.lazyvim.org/#%EF%B8%8F-requirements).
The complete environment has not been health-checked. Its optional tools are
not an instruction to replace every existing provider. No normal editor startup,
plugin update or health check was run during the inventory.

## Version changes need a separate decision

Pinned Nixpkgs: `08d3a97586f6b6343b3b5e799980773629432610`. The Nix column is
read from source, not from a built environment.

| Tool | Current provider/version | Pinned Nix source | Effect if adopted |
| --- | --- | --- | --- |
| Fish | Brew 4.9.3 | [4.7.1](https://github.com/NixOS/nixpkgs/blob/08d3a97586f6b6343b3b5e799980773629432610/pkgs/by-name/fi/fish/package.nix#L153) | Older version; already declared |
| ripgrep | Brew 15.2.0 | [15.1.0](https://github.com/NixOS/nixpkgs/blob/08d3a97586f6b6343b3b5e799980773629432610/pkgs/by-name/ri/ripgrep/package.nix#L20) | Older version; already declared |
| Starship | Existing standalone binary 1.24.2 | [1.25.1](https://github.com/NixOS/nixpkgs/blob/08d3a97586f6b6343b3b5e799980773629432610/pkgs/by-name/st/starship/package.nix#L15) | Newer version and new provider; already declared |
| Neovim | Brew 0.12.6 | [0.12.4](https://github.com/NixOS/nixpkgs/blob/08d3a97586f6b6343b3b5e799980773629432610/pkgs/by-name/ne/neovim-unwrapped/package.nix#L108) | Older version; not declared |
| Tree-sitter CLI | Mason 0.26.3 | [0.26.8](https://github.com/NixOS/nixpkgs/blob/08d3a97586f6b6343b3b5e799980773629432610/pkgs/by-name/tr/tree-sitter/package.nix#L115) | Competing provider; not declared |
| GitHub CLI | Brew 2.103.0 | [2.103.3](https://github.com/NixOS/nixpkgs/blob/08d3a97586f6b6343b3b5e799980773629432610/pkgs/by-name/gh/gh/package.nix#L17) | Patch update; not declared |
| fzf | Not on global PATH | [0.72.0](https://github.com/NixOS/nixpkgs/blob/08d3a97586f6b6343b3b5e799980773629432610/pkgs/by-name/fz/fzf/package.nix#L14) | Addition; already declared |
| fd | Not on global PATH | [10.4.2](https://github.com/NixOS/nixpkgs/blob/08d3a97586f6b6343b3b5e799980773629432610/pkgs/by-name/fd/fd/package.nix#L14) | Newly declared |
| lazygit | Not on global PATH | [0.61.1](https://github.com/NixOS/nixpkgs/blob/08d3a97586f6b6343b3b5e799980773629432610/pkgs/by-name/la/lazygit/package.nix#L11) | Newly declared |

Resolve the already-declared Fish/ripgrep version changes before live activation.
An updated pin also requires review of the matching Home Manager revision and
the resulting package versions; it is not silently changed by this inventory.

## Do not import the whole machine inventory

The inspected Brew installation has 162 formulae and four casks; 33 formulae
have `installed_on_request` metadata. This is historical metadata, not a reliable
list of desired top-level declarations. Importing every formula would duplicate
libraries and preserve accidental dependencies.

Keep existing Node/Corepack/pnpm, Bun, Python/pipx/uv, Rust/rustup and Go ownership
until their runtime versions and package dependencies are compared. In particular,
the current default `python3` is the OS version despite newer Brew Pythons being
installed. A new global Python declaration would change real behavior.

Global npm/Cargo/Python tools, agent clients, externally distributed Skills,
TeX/fonts and specialist applications are inventoried privately. They are not
automatically added, removed or redistributed here. Bun's global-list command
failed with `InvalidNPMLockfile`; its package inventory remains unconfirmed.
GUI applications outside Brew were not exhaustively inventoried.

## Verification of the declaration update

On 2026-10-30, all 29 existing isolated tests passed and both Nix source files
passed the available syntax parser. The pinned source definitions for `fd` and
`lazygit` were inspected. A separate isolated test with real Fish and a temporary
`fd` stub confirmed the conditional alias and the `command find` escape; it did
not test a Nix-built `fd` binary.

The real `home-manager.sh check` stopped because Nix is absent. No target was
evaluated or built, no Home Manager activation ran, and no tool was installed
or removed from the live environment. The Docker daemon was also unavailable;
it was not started for this check.

For these additions and any later choices, follow the [migration verification and restoration procedure](nix-migration.md).
Record declaration changes, real distribution checks and live application separately.
