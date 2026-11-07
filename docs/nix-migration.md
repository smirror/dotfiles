# Nix migration boundaries and restoration

## Declared scope

One `home.nix` is used for macOS and WSL. `scripts/home-manager.sh` selects the OS/CPU target and supplies the current username/home as `DOTFILES_USER` and `DOTFILES_HOME`. The declarations do not contain a specific person's absolute home path.

- The independent `packages.<system>.tools` output installs the list in `tool-packages.nix` plus Fish. It does not deploy home files. Standard GNU tools cover the helpers' GNU-specific options.
- The standard Home Manager Fish module installs Fish and generates `~/.config/fish/config.fish` from the existing shell initialization. It also generates its session-variable integration. The Nix profile precedes other package managers on PATH.
- Only the 23 helper/completion/conf.d files explicitly listed in `home.nix` are managed. Directory-wide links are not used.
- `~/.codex/AGENTS.md` and `~/.claude/CLAUDE.md` use the same `agents/global.md`; this preserves the existing graphify instruction with its installed shared Skill path.
- Git/Tmux settings, Fish runtime variables, histories, sessions, API keys, external Skill directories and client permission/configuration files are excluded. The existing broken Linux `br.fish` link is excluded.

The Nix source and store are not a place for secrets. Do not add live runtime/authentication files to the repository or interpolate secret environment values into these declarations. External graphify installation and other externally distributed Skills remain separate prerequisites.

## Before installing Nix

`scripts/bootstrap.sh` is a new, explicit installation step. It does not run either legacy setup script. Its pinned installer is verified before execution. The official macOS installer creates a `/nix` APFS volume, build users and daemon and changes system shell initialization; this is broader than applying files in the home directory. On Linux it uses daemon mode when systemd is running, or single-user mode otherwise.

Review the official installer's proposed changes and its [uninstall documentation](https://nix.dev/manual/nix/2.35/installation/uninstall.html) before permitting this step. A Home Manager rollback does not uninstall the Nix daemon or remove its volume. Preserve the installer's backups and record its actual changes; do not overwrite existing system backups.

## Verification gates

1. Run the isolated Python tests and syntax checks. Fake installer/Nix executors prove routing and failure handling only.
2. Review the [tool/version inventory](tool-inventory.md), then with a real Nix runtime, run `scripts/home-manager.sh check`. Each of the three `homeConfigurations` must actually evaluate. This is not a cross-OS execution test.
3. Review the generated `flake.lock`, then build the native activation package with `scripts/home-manager.sh build`. Inspect the generated `result/home-files`, including the Home Manager-generated files beyond the explicitly imported sources.
4. Build for a disposable home and test activation there, with separate HOME/XDG/profile state. Verify normal shell startup, declared binaries, keys, candidate cancellation and missing-history handling. Activation in macOS and WSL must be recorded separately.
5. Before live activation, compare every generated destination, capture file contents/link targets/owners/modes and current Home Manager/Nix profile targets, and agree which existing files may be moved aside. Stop on unrecognized paths or concurrent edits.

Do not describe `home-manager switch -n` or `DRY_RUN=1` as a no-write guarantee. Home Manager's initialization/profile work can occur before the file-write checks. Even an activation collision can occur after the Home Manager profile has been updated.

## Backups and first activation

Use a private backup directory outside Git and the Nix source tree. Back up only the reviewed destination allowlist, preserving symlinks, owners and modes. Record absent targets too, so newly created links can be distinguished during restoration. Do not copy runtime credentials just to back up unrelated configuration files.

Home Manager refuses differing existing files by default. An identical regular file may remain a regular file instead of being replaced by a link. Do not set `force = true`, `HOME_MANAGER_BACKUP_OVERWRITE`, or use blanket deletion to bypass a collision. Its `-b` backup mechanism is not a general backup of existing symlinks. Resolve only the reviewed conflicting destinations using the prepared backups.

Run `scripts/home-manager.sh switch` only after the build, destination diff, backups and profile changes are accepted. It does not change the account's login shell; validate the installed Fish explicitly before considering a separate login-shell change.

## Restoration

- Record the previous Nix and Home Manager profile targets before activation. Restore their previous generation if a switch failed or the new environment is rejected; do not assume a failed activation left profiles untouched.
- For the first migration, there may be no previous Home Manager generation. Remove only links still pointing to the reviewed generated files, then restore the backed-up files/links with their original modes/ownership. Preserve any new local edits for comparison first.
- Remove newly generated files only if they were absent before and still match the recorded managed generation. Leave runtime files and unrelated directories intact.
- Start a new shell and verify the original command paths, Fish behavior, global agent instructions and unchanged Git/Tmux links.
- Removing Nix itself is a separate system operation governed by the actual installer records and official uninstall procedure. Home-directory restoration alone does not revert it.

## Evidence status

Record syntax, fake-executor tests, real evaluation, native build, isolated activation and live activation separately. Do not commit or push this migration until its diff has been reviewed. Do not report a macOS build as WSL execution evidence, or a local branch as a merged/pushed change.

### Validated snapshot: 2026-11-07

The committed lock uses Nixpkgs `6dadaf4375be35033e1c84395adbd53ff5fded96`
and Home Manager `b787c48e2ec57a9d098f5c2721882a3bc1e16f97`.
Intel Mac is excluded from the supported scope. Both scripts reject it before
running installation/evaluation commands; arm64 and x86_64 Linux remain supported.

Validation used an isolated container from `nixos/nix:2.35.4`, image digest
`sha256:f159a58f390677f41e8e900a74b6e2f9c7f27b364122ae6acf7a652ce6c551c0`.
No host home or credentials were mounted into it.

| Check | Result |
| --- | --- |
| Python regression suite | 30 passed, including Intel Mac rejection and child-process feature inheritance |
| Real Nix evaluation | All three declared profiles passed |
| Native build | arm64 Linux Home Manager generation passed |
| Collision protection | A differing existing instruction file blocked activation and remained intact |
| Disposable-home activation | Passed after explicit backup of the conflicting fixture |
| Fresh Fish startup | Required binaries, runtime fixture value, helper loading and PATH uniqueness passed; sourcing again kept PATH unique |
| Global instruction deployment | Codex/Claude files both linked to the reviewed common source |
| First-activation restoration | Restored the original instruction fixture, removed the new file/profile links and retained the runtime fixture |
| Native macOS build/activation | Not run |
| WSL runtime acceptance | Not run; Linux container execution is not WSL evidence |
| Live host activation | Not run |

The real build exposed a wrapper issue: outer `nix run` feature flags did not
reach Home Manager's child Nix process. The wrapper now exports the required
features through `NIX_CONFIG`, retaining any caller configuration. The build
and activation results above are from the corrected wrapper. Host Nix settings
were not edited. Interactive key selection under the Nix-built shell remains
part of native acceptance; startup checks do not stand in for that test.

### Current acceptance boundary

The snapshot above predates the tools/configuration split. New tools-only profile
installation, lock updates, native builds and activation/restoration checks must
be performed on a different PC, not the current working machine. Local syntax
checks and fake-executor tests are not physical acceptance evidence. The split
keeps `home-manager.sh switch` explicit and removes the common CLI list from
Home Manager's configuration deployment; Fish/Home Manager retain their module
runtime dependencies. No source edit here changes the current live settings.
