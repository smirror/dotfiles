#!/bin/sh
set -eu

dotfiles_action=${1:-build}
if [ "$#" -gt 1 ]; then
    printf '%s\n' 'Usage: scripts/home-manager.sh [check|build|switch]' >&2
    exit 1
fi
case "$dotfiles_action" in
    check|build|switch) ;;
    *) printf '%s\n' 'Usage: scripts/home-manager.sh [check|build|switch]' >&2; exit 1 ;;
esac
case "$(uname -s)/$(uname -m)" in
    Darwin/arm64) dotfiles_system=aarch64-darwin ;;
    Darwin/x86_64) dotfiles_system=x86_64-darwin ;;
    Linux/aarch64|Linux/arm64) dotfiles_system=aarch64-linux ;;
    Linux/x86_64) dotfiles_system=x86_64-linux ;;
    *) printf '%s\n' 'Supported platforms: macOS or Linux on arm64/x86_64.' >&2; exit 1 ;;
esac
dotfiles_nix=$(command -v nix || true)
if [ -z "$dotfiles_nix" ]; then
    for dotfiles_path in /nix/var/nix/profiles/default/bin/nix "$HOME/.nix-profile/bin/nix"; do
        if [ -x "$dotfiles_path" ]; then dotfiles_nix=$dotfiles_path; break; fi
    done
fi
if [ -z "$dotfiles_nix" ]; then
    printf '%s\n' 'Nix is required. Review scripts/bootstrap.sh before installing it.' >&2
    exit 1
fi
DOTFILES_USER=${DOTFILES_USER:-$(id -un)}
DOTFILES_HOME=${DOTFILES_HOME:-$HOME}
case "$DOTFILES_HOME" in
    /) printf '%s\n' 'DOTFILES_HOME must not be the root directory.' >&2; exit 1 ;;
    /*) ;;
    *) printf '%s\n' 'DOTFILES_HOME must be an absolute path.' >&2; exit 1 ;;
esac
if [ "$dotfiles_action" = switch ] && {
    [ "$DOTFILES_USER" != "$(id -un)" ] || [ "$DOTFILES_HOME" != "$HOME" ];
}; then
    printf '%s\n' 'switch must target the current user and HOME; use check/build for other targets.' >&2
    exit 1
fi
export DOTFILES_USER DOTFILES_HOME
dotfiles_repo=$(CDPATH= cd "$(dirname "$0")/.." && pwd -P)
if [ "$dotfiles_action" = check ]; then
    for dotfiles_target in aarch64-darwin x86_64-darwin aarch64-linux x86_64-linux; do
        printf '%s: ' "$dotfiles_target"
        "$dotfiles_nix" --extra-experimental-features 'nix-command flakes' eval --impure --raw \
            "$dotfiles_repo#homeConfigurations.$dotfiles_target.activationPackage.drvPath"
        printf '\n'
    done
else
    exec "$dotfiles_nix" --extra-experimental-features 'nix-command flakes' run \
        "$dotfiles_repo#home-manager" -- "$dotfiles_action" --flake "$dotfiles_repo#$dotfiles_system" --impure
fi
