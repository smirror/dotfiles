# Reinstallable tool definitions

The first target is a selected tool set that can be installed again. Prompt
management remains a later task. LazyVim's personal configuration, work/doctor
commands, build/test CI and Skill cleanup are outside this change. Daily update
proposals are handled separately by the Dependabot definition.

## Selected shared tools

These are the initial reinstall targets in `tool-packages.nix`, not a dump of everything
installed on one machine. They use the existing Nixpkgs/Home Manager revisions
and source hashes in `flake.lock`; update and validate that lock deliberately.

The default version policy is the latest stable upstream release at installation
or update time, resolved to exact revisions/hashes before execution. Routine
reinstallation uses the recorded lock/digests rather than resolving a moving
latest reference again. Prereleases and compatibility/security exceptions need
an explicit decision. A pin is a reproducible snapshot, not a permanent freeze.
If the approved package source lags upstream, record that gap before choosing a
new pin or an exception; do not silently describe the older version as latest.

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
| Fish | Shell included in the tools bundle | Nix | Fixed by the lock |
| Home Manager | Optional configuration deployment only | Separate flake output / module | Fixed by the lock |

The tools bundle contains 20 explicit packages plus Fish. Home Manager remains
a separate configuration-deployment entrypoint. Git,
GitHub CLI, Tmux, jq and Neovim are new declarations in this change. Adding
their binaries does not add ownership of their settings, authentication or
saved data. Existing Brew installations are retained.

## First validation and subsequent installation

All installation/update/build/activation acceptance below is for the other,
designated validation PC. Do not exercise it on the current working PC.

The tools output does not import `home.nix` and needs no user/home identity:

```sh
nix --extra-experimental-features 'nix-command flakes' build --no-update-lock-file .#tools --out-link result-tools
```

After reviewing it on that other PC, a first tools-only installation uses a
dedicated profile, leaving the default profile and managed settings separate:

```sh
mkdir -p "$HOME/.local/state/nix/profiles"
nix --extra-experimental-features 'nix-command flakes' profile add --no-update-lock-file \
    --profile "$HOME/.local/state/nix/profiles/dotfiles-tools" --name dotfiles-tools .#tools
```

Use `profile upgrade` for the existing named entry after a reviewed repository
update; do not repeatedly add another copy or change its priority to hide a
collision. Add that profile's bin directory to the chosen shell's PATH as a
separate configuration step. The tracked Fish configuration prefers it when
present; the existing live Fish configuration has not been changed.

Configuration deployment is separately selected with `home-manager.sh`.
Its Fish/Home Manager modules retain their required runtime packages, but the
common 20-tool list is no longer installed by `home.nix`. A configuration switch
is not part of a tools-only install/update. Follow the [migration procedure](nix-migration.md)
before any such switch. The new split has not been physically tested here.

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
| Node, Corepack/pnpm, Bun | Preserve existing installations while auditing CLI dependencies | Opt-in development runtimes; prefer selected CLI packages with their own locked runtimes |
| Python, uv, pipx | Preserve OS/Brew Python and existing isolated tool environments | No default global development Python; select interpreters and dependencies per retained tool |
| Rust and global Cargo tools | Cargo is currently used to install tools; preserve rustup/Cargo and local sources | Prefer locked tool packages; Rust development remains opt-in |
| Go and Go tools | Existing installation retained; currently unused | Excluded from the default reinstall set; add only when requested |
| AI clients and external Skills | Existing native, Brew, npm and uv installers | Record required clients and exact sources; GSD is currently unused and excluded from the initial reinstall set |
| macOS applications | Current installers retained | Record candidates, install methods and official sources in [the app catalog](macos-apps.md); do not automatically enroll all installed apps |
| Fonts and TeX templates | Outside this repository | Excluded; do not copy font/template assets into the public repository. Existing TeX runtimes remain untouched |
| Specialist tools and local services | Current installers and existing data | Confirm need and preserve data; no service/database operations are performed here |
| Apple developer tools | Existing selected Xcode/Command Line Tools | macOS-only selection below; no automatic installation or switching |

Full raw inventory stays outside this public repository. Personal prompts,
API keys, account state, application data and project paths are not install
definitions. Bun's previous global-list query failed while attempting lock
migration; it remains unconfirmed and was not retried during this inventory.

A future Brewfile records selected Homebrew targets and an update policy; it
is not a replacement for the Nix lock's exact package selection. Do not maintain
the same desired CLI list in both managers. See [Homebrew Bundle documentation](https://docs.brew.sh/Brew-Bundle-and-Brewfile).

### Current AI-tool selections

| Tool | Current decision | Reinstall/update treatment |
| --- | --- | --- |
| pi | In use now; retain the existing npm installation, inspected version 1.5.0 | May be removed later. Future reviewed updates should select the latest stable release. Do not automatically migrate or add to the default common set. The inspected version is a snapshot, not a permanent target or newly locked deployment |
| qwen-code | Homebrew 0.26.8 uninstalled at the user's request | Excluded from reinstall targets. Preserve the user's saved data; retain shared Node/ripgrep dependencies |
| GSD | Currently unused | Excluded from the initial reinstall set; cleanup remains a separate task |

The inventory counts above describe the snapshot before qwen-code removal.
After removal, the installed formula count is 169. Removal was limited to the
qwen-code formula, with automatic dependency removal disabled. The existing pi
entrypoint and the qwen saved-data contents/metadata were verified unchanged.

## Minimal runtimes and controlled installation

The reinstall set is an explicit selection, not an automatic import of installed
software. No development language is enabled by default. Rust/Cargo, Go,
Python, Node and package managers for development are opt-in when needed.
Existing host installations stay intact while dependent tools are identified.

For day-to-day CLI tools, prefer a selected Nix package over a chain of manual
Node/npm/pnpm, Python/pip or Cargo installations. The locked package can bring
its own runtime and dependencies; that does not require a global language
interpreter or package manager. This is dependency management, not process
isolation. Tools installed through Cargo and Rust development are separate needs.

Prioritize Python and Node ownership before removing or replacing anything:

- Separate OS-provided Python, tool-specific interpreters and project runtimes.
  Do not replace the OS interpreter or install packages into it.
- Some current Node entrypoints resolve `node` from PATH; others reference a
  Homebrew path directly. Replacing the global runtime alone is not a migration.
- Existing pipx environments can share one Homebrew Python, while uv tools may
  use uv-managed Python. An isolated package environment alone does not pin its
  interpreter or all dependency versions.
- For an extra CLI outside Nixpkgs, record its approved source, exact tool and
  runtime versions, dependency lock/hashes and expected executables before
  adding a reinstall path. A bare versioned npm/pip command is not a full lock.
- Keep project language environments separate. A project version file is not
  permission to download a new runtime or tool automatically.

The arm64 Linux tool-profile output was checked: it exposes none of `python`,
`python3`, `node`, `npm`, `npx`, `pnpm`, `pip` or `pip3` in its bin directory.
Other packages may still depend on runtimes inside their own closures. This
check does not inventory every interpreter inside those dependencies.

## Downloads, containers and update boundaries

Use the repository's selected definitions as the normal installation entry
point. Prefer locked Nix packages for shared CLI tools, an explicitly curated
Homebrew list for macOS applications, and named official images for chosen
container tools. Reduce manual website downloads; an exception needs an official
source URL, exact version, integrity/signature verification and a documented
update method. Homebrew-managed apps that cannot be restored at an exact
version must be identified as exceptions, not described as fully pinned.

Security tools are excluded from the global reinstall set. Invoke a selected
tool through Docker or an explicitly chosen equivalent isolated environment;
do not add its scanner executable or package manager installer to the host.
Record the official image, immutable digest, platform,
required mounts and network access. A tag alone can move. Static analysis should
receive only its target files, read-only where possible; writable outputs need a
separate reviewed path. Docker-socket mounts, whole-home mounts, host networking
and privileged execution require separate justification. Tools that need host
kernel/network access need a tool-specific decision; a container may not be a
functional substitute on macOS. Such tools stay out of this default path until
an appropriate isolated execution method is selected; they do not fall back to
automatic global installation. No scanner or image is enrolled by this document.
See [Docker image digests](https://docs.docker.com/dhi/explore/security-concepts/digests/)
and [Docker's security model](https://docs.docker.com/engine/security/).

Repository policy does not enforce command permissions. Pinning identifies what
is fetched; it does not prove a version is free of vulnerabilities or stop an
agent from executing a different installer. Instructions from a website or tool
output are not authorization to install software. Installation/update commands,
new sources and executable definitions need a separate reviewed execution
boundary in the agent/client settings. Those permissions have not been changed
by this work. Unreviewed manifest or lock edits must not authorize their own
execution; avoid automatically running newly downloaded packages or scripts.

Updates should be small reviewed definition/lock changes followed by relevant
version and startup checks. Check the official stable release and known security
issues before selecting a new version. Known vulnerability fixes also need
updates. Use latest stable as the selection policy, then pin the selected
version and source before execution; do not silently follow moving tags or
add self-updating installers to the selected set.

## macOS developer tools

Apple's developer tools are a host prerequisite selected separately from the
shared CLI set. They are not part of the container-only security-tool category.

| Condition | Choice | Source and version policy |
| --- | --- | --- |
| Host compilation needs Apple's compiler/SDK/Git tools without the IDE | Command Line Tools | Apple distribution; select a version compatible with the host macOS |
| Apple application development needs the IDE, platform SDKs or simulators | Full Xcode | Apple distribution; select the Xcode version and build explicitly against macOS/SDK requirements |
| A suitable full Xcode is already selected | Keep it | Do not separately install CLT merely because its standalone receipt is absent |
| Linux/WSL | Neither | Keep Apple tools outside the shared Linux declaration |

The inspected machine selects `/Applications/Xcode.app/Contents/Developer`,
with Xcode 27.1, build 27A9275. A separate CLT 27.0 receipt also exists; that is
an observation, not a requirement to reinstall both packages on a new machine.

Record the chosen Apple version/build and official source before installation.
The Mac App Store is a convenient current-release route, not an exact historical
version lock. Apple's additional downloads provide specific releases and may
require Apple Account sign-in. Do not substitute an unverified mirror to avoid
authentication. Installation, license acceptance, first-launch components and
changing the selected developer directory are separate host actions; none is
automatically performed here. This document records the option and policy,
not a tested unattended Xcode installer.

See [Apple's downloads](https://developer.apple.com/xcode/resources/) and
[Xcode/macOS compatibility](https://developer.apple.com/xcode/system-requirements).

## Update proposals and manual updates

Dependabot is configured to check the Nix inputs every day at 09:00 Asia/Tokyo
and group the two input changes into one PR, with at most one open version-update
PR. No auto-merge or host installation is configured. This does not audit every
CLI inside Nixpkgs for vulnerabilities or replace execution checks on the other PC.
The configuration becomes active only after it reaches the default branch and
GitHub accepts it; no hosted run has been confirmed yet.

`flake.nix` identifies the approved tracking branches; `flake.lock` still fixes
the reviewed revisions and source hashes. Only the original-ref metadata changed
in this work; locked revisions/hashes have not been upgraded. Dependabot updates
`flake.lock`, but does not upgrade pinned refs written directly in `flake.nix`.
See [GitHub's Nix support](https://docs.github.com/en/code-security/reference/supply-chain-security/supported-ecosystems-and-repositories#nix).

For a manual batch proposal on the other PC, `scripts/update-lock.sh` updates the
lock only. It refuses existing staged or unstaged flake edits and does not install,
activate, commit or push. Review the resulting diff and validate there before
applying the tools profile. This script was exercised only with a fake Nix
executor in temporary repositories on this PC, never with real Nix.

Kali/Parrot toolboxes are a later opt-in definition; see the [security environment plan](security-environments.md).
They are not included in the common tool profile.
