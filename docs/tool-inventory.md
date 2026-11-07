# Tool inventory and additive migration

Machine snapshot: 2026-10-29, refreshed 2026-11-07; declaration updated 2026-11-07.
This compares the legacy `scripts/install.sh`, the shared
`home.nix` declaration and a read-only inventory of the current macOS machine.
It records declaration changes and a proposed order of adoption, not an installation receipt. WSL has not
been inventoried or tested. Raw machine/package-manager output stays outside Git.

## Current declaration

`home.nix` explicitly lists 20 packages:

```
bat coreutils fd findutils fzf gawk getopt gh ghq git gnugrep gnused
jq lazygit neovim peco perl ripgrep starship tmux
```

The Fish and Home Manager modules install their respective programs as well:
22 direct components in total, excluding dependencies and the Nix bootstrap.
The first draft had 13 explicit packages; fd/lazygit raised that to 15.
This update adds Git, gh, tmux, jq and Neovim. No tool is installed on the live machine.
The [reinstall targets](tool-installation.md) record purpose, ownership and version policy.

The legacy installer names 30 distinct apt/Cargo packages. Nine overlap with
this declaration: bat, ripgrep, fzf, fish, fd-find (as fd), git, gh, tmux and jq.
The twelve other explicit CLI packages cover helper dependencies and newer
workflows. Home Manager is the new deployment component. The remaining 21 legacy
entries are not automatically required reinstall targets.

## Legacy list compared with the draft

| Legacy entries | Current Nix declaration | Proposed treatment |
| --- | --- | --- |
| `bat`, `ripgrep`, `fzf`, `fish` | Declared | Keep; review versions and command precedence before activation |
| `git`, `tmux` | Added | Binaries only; existing settings retained |
| `curl`, `wget`, `htop`, `tree`, `unzip`, `gnupg` | Not declared | Separate existing tools from missing commands; retain current installations |
| `vim` | Not declared | Current editor is Neovim + LazyVim; do not reintroduce the old editor configuration |
| `build-essential`, `ca-certificates`, `lsb-release` | Not declared | OS/bootstrap requirements; do not translate these apt names into a shared CLI list |
| `exa` | Not declared | Consider `eza` separately; the existing Fish aliases still check for `exa` |
| `fd-find` | Added as `pkgs.fd` | Command `fd`; also enables the existing Fish `find` alias |
| `du-dust` | Not declared | Existing Brew `dust`; eventual `pkgs.dust` adoption |
| `procs`, `tokei`, `hyperfine` | Not declared | Optional additions restoring legacy CLI coverage |
| `jq` | Added | Nix version differs from the current OS jq |
| `httpie`, `silversearcher-ag` | Not declared | Optional `pkgs.httpie` / `pkgs.silver-searcher` additions |
| `nodejs`, `python3-pip`, `python3-venv` | Not declared | Preserve runtime/package-manager ownership; choose versions before migration |
| `gh` | Added | Preserve authentication and client configuration |
| `hub` | Not declared | Do not automatically restore the legacy tool |

The old script also bootstraps Rust/rustup and Fisher conditionally and upgrades
pip. Those actions are not included in the 30-package count and are not carried
out by the new declaration. Existing Fish helper sources are deployed directly
by Home Manager rather than refreshed through Fisher.

## Add first, then transfer ownership

“Missing” below means absent from the inspected normal shell PATH, not absent
from every project, editor or cache. Package availability is based on pinned
source inspection; evaluation/build on the three targets is still required.

| Order | Tools | Change and reason |
| --- | --- | --- |
| 1 | `fzf`, `ghq` | Already declared, missing from the current global PATH; supply existing Fish helper dependencies |
| 2 | `fd`, `lazygit` | Added to the declaration, missing globally in the snapshot; useful for the current LazyVim environment |
| 3 | `procs`, `tokei`, `hyperfine`, `wget`, `tree`, `httpie`, `silver-searcher` | Missing globally; optional legacy coverage, add only the tools still wanted |
| 4 | `eza` | Optional replacement for the legacy `exa` entry; review the related aliases together |
| Added | `git`, `gh`, `tmux`, `jq`, `neovim` | Selected reinstall targets; existing implementations remain installed |
| Later | `htop`, `dust`, GnuPG | Existing tools; choose ownership separately |

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

- Neovim is now declared as a binary only. Keep the current LazyVim
  configuration and plugin ownership.
- Do not enable an additional Home Manager Neovim configuration/plugin layer
  over the existing `init.lua` without a separate comparison.
- A Tree-sitter CLI 0.26.3 already exists in Mason's bin directory. The Brew
  Tree-sitter library is not evidence of a globally available CLI. Do not add
  a second CLI merely because the normal shell PATH does not contain one.
- Mason also supplies editor tools such as language servers and formatters.
  Review those before duplicating them in the global package list.
- LazyVim configuration management is excluded from the plan. Only optional
  initialization on a new machine is documented. lazy.nvim keeps its writable
  lock file; plugins, Mason downloads and editor state remain outside Git.
- Only the retired `.SpaceVim.d/init.toml` is removed in this change. The live
  LazyVim files, OS-provided Vim and Vim history are untouched.

The inspected Neovim version and LuaJIT build satisfy
[LazyVim's Neovim requirement](https://www.lazyvim.org/#%EF%B8%8F-requirements).
The complete environment has not been health-checked. Its optional tools are
not an instruction to replace every existing provider. No normal editor startup,
plugin update or health check was run during the inventory.

## Version changes need a separate decision

Pinned Nixpkgs: `6dadaf4375be35033e1c84395adbd53ff5fded96`.
Home Manager: `b787c48e2ec57a9d098f5c2721882a3bc1e16f97`.
The development revisions and their source hashes are recorded in `flake.lock`.
The declared platforms are Apple Silicon macOS and arm64/x86_64 Linux (WSL);
Intel Mac support was explicitly excluded. The Nix versions below were read
by real Nix evaluation for Apple Silicon macOS; this does not prove a macOS build.
The machine's Fish, ripgrep and Neovim versions were rechecked on 2026-11-06.

| Tool | Current provider/version | Pinned Nix source | Effect if adopted |
| --- | --- | --- | --- |
| Fish | Brew 4.9.3 | [4.9.3](https://github.com/NixOS/nixpkgs/blob/6dadaf4375be35033e1c84395adbd53ff5fded96/pkgs/by-name/fi/fish/package.nix) | Matching source version; new provider |
| ripgrep | Brew 15.2.0 | [15.2.0](https://github.com/NixOS/nixpkgs/blob/6dadaf4375be35033e1c84395adbd53ff5fded96/pkgs/by-name/ri/ripgrep/package.nix) | Matching source version; new provider |
| Starship | Existing standalone binary 1.24.2 | [1.27.0](https://github.com/NixOS/nixpkgs/blob/6dadaf4375be35033e1c84395adbd53ff5fded96/pkgs/by-name/st/starship/package.nix#L15) | Newer version and new provider; already declared |
| Neovim | Brew 0.12.6 | [0.12.6](https://github.com/NixOS/nixpkgs/blob/6dadaf4375be35033e1c84395adbd53ff5fded96/pkgs/by-name/ne/neovim-unwrapped/package.nix#L108) | Matching version; binary newly declared |
| Tree-sitter CLI | Mason 0.26.3 | [0.26.11](https://github.com/NixOS/nixpkgs/blob/6dadaf4375be35033e1c84395adbd53ff5fded96/pkgs/by-name/tr/tree-sitter/package.nix#L115) | Competing provider; not declared |
| GitHub CLI | Brew 2.103.3 | [2.103.3](https://github.com/NixOS/nixpkgs/blob/6dadaf4375be35033e1c84395adbd53ff5fded96/pkgs/by-name/gh/gh/package.nix#L17) | Matching version; binary newly declared |
| fzf | Not on global PATH | [0.74.5](https://github.com/NixOS/nixpkgs/blob/6dadaf4375be35033e1c84395adbd53ff5fded96/pkgs/by-name/fz/fzf/package.nix#L14) | Addition; already declared |
| fd | Not on global PATH | [10.5.0](https://github.com/NixOS/nixpkgs/blob/6dadaf4375be35033e1c84395adbd53ff5fded96/pkgs/by-name/fd/fd/package.nix#L14) | Newly declared |
| lazygit | Not on global PATH | [0.66.2](https://github.com/NixOS/nixpkgs/blob/6dadaf4375be35033e1c84395adbd53ff5fded96/pkgs/by-name/la/lazygit/package.nix#L11) | Newly declared |

Verify native shell behavior and the selected command paths before live activation.
An updated pin also requires review of the matching Home Manager revision and
the resulting package versions; it is not silently changed by this inventory.

## Do not import the whole machine inventory

The refreshed Brew installation has 170 formulae and four casks; 34 formulae
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
The refresh also records 53 application bundles from /Applications and the user
Applications directory privately. This is a presence inventory, not a selected
reinstall list or proof of complete GUI coverage.

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

The 2026-11-07 update removes Intel Mac from the declared scope, advances both
pinned inputs and records a real generated lock file. All three profiles evaluated
successfully with Nix 2.35.4 in a disposable Docker container. The native arm64
Linux Home Manager build, disposable-home activation, collision protection and
first-activation restoration passed. The updated regression suite has 30 passing
tests. See the [validation record](nix-migration.md#validated-snapshot-2026-11-07)
for the tested scope. Native macOS and WSL runtime tests remain separate
acceptance steps. Host configuration has not been activated.

For these additions and any later choices, follow the [migration verification and restoration procedure](nix-migration.md).
Record declaration changes, real distribution checks and live application separately.

## Shared CLI reinstall update

The added Git, gh, tmux, jq and Neovim packages use the existing lock. Three-profile
evaluation and an arm64 Linux build passed. The five binaries started from the
built tool environment; jq processed a fixture and Neovim started headless with
LuaJIT using no user init, plugins or history. This does not test native macOS or
WSL execution and does not apply any host configuration.
