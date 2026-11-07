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
| Node, Corepack/pnpm, Bun | Preserve existing installations while auditing CLI dependencies | Opt-in development runtimes; prefer selected CLI packages with their own locked runtimes |
| Python, uv, pipx | Preserve OS/Brew Python and existing isolated tool environments | No default global development Python; select interpreters and dependencies per retained tool |
| Rust and global Cargo tools | Cargo is currently used to install tools; preserve rustup/Cargo and local sources | Prefer locked tool packages; Rust development remains opt-in |
| Go and Go tools | Existing installation retained; currently unused | Excluded from the default reinstall set; add only when requested |
| AI clients and external Skills | Existing native, Brew, npm and uv installers | Record required clients and exact sources; GSD is currently unused and excluded from the initial reinstall set |
| macOS applications, fonts and TeX | Current installers, including Brew casks | Curate a Brewfile after choosing the wanted applications; do not export all dependencies or start services |
| Specialist tools and local services | Current installers and existing data | Confirm need and preserve data; no service/database operations are performed here |
| Apple developer tools | Existing selected Xcode/Command Line Tools | macOS-only selection below; no automatic installation or switching |

Full raw inventory stays outside this public repository. Personal prompts,
API keys, account state, application data and project paths are not install
definitions. Bun's previous global-list query failed while attempting lock
migration; it remains unconfirmed and was not retried during this inventory.

A future Brewfile records selected Homebrew targets and an update policy; it
is not a replacement for the Nix lock's exact package selection. Do not maintain
the same desired CLI list in both managers. See [Homebrew Bundle documentation](https://docs.brew.sh/Brew-Bundle-and-Brewfile).

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
version and startup checks. Known vulnerability fixes also need updates; a
permanent freeze is not the security policy. Do not silently track latest
releases or add self-updating installers to the selected set.

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
