#!/bin/sh
set -eu

if [ "$#" -ne 0 ]; then
    printf '%s\n' 'Usage: scripts/update-lock.sh' >&2
    exit 1
fi
dotfiles_repo=$(CDPATH= cd "$(dirname "$0")/.." && pwd -P)
cd "$dotfiles_repo"
if ! git diff --quiet -- flake.nix flake.lock ||
    ! git diff --cached --quiet -- flake.nix flake.lock; then
    printf '%s\n' 'Preserve/review the existing flake changes before updating.' >&2
    exit 1
fi
dotfiles_nix=$(command -v nix || true)
if [ -z "$dotfiles_nix" ]; then
    printf '%s\n' 'Nix is required; run updates on the designated validation PC.' >&2
    exit 1
fi
# Update definitions only; never install packages, activate files or commit.
exec "$dotfiles_nix" --extra-experimental-features 'nix-command flakes' flake update
