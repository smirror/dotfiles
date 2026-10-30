#!/bin/sh
set -eu

case "$(uname -s)/$(uname -m)" in
    Darwin/arm64|Darwin/x86_64|Linux/aarch64|Linux/x86_64) ;;
    *) printf '%s\n' 'Supported platforms: macOS or Linux on arm64/x86_64.' >&2; exit 1 ;;
esac
if [ "$#" -ne 0 ]; then
    printf '%s\n' 'Usage: scripts/bootstrap.sh' >&2
    exit 1
fi
if command -v nix >/dev/null 2>&1; then
    printf '%s\n' 'Nix is already available; nothing installed.'
    exit 0
fi
for dotfiles_command in git curl mktemp rm; do
    command -v "$dotfiles_command" >/dev/null 2>&1 || {
        printf 'Required command missing: %s\n' "$dotfiles_command" >&2
        exit 1
    }
done
if ! command -v sha256sum >/dev/null 2>&1 && ! command -v shasum >/dev/null 2>&1; then
    printf '%s\n' 'Required command missing: sha256sum or shasum.' >&2
    exit 1
fi

umask 077
dotfiles_tmp=$(mktemp -d "${TMPDIR:-/tmp}/dotfiles-nix.XXXXXX")
trap 'rm -rf "$dotfiles_tmp"' 0
trap 'exit 1' HUP INT TERM
dotfiles_sha256=118c3dfa04bdc946b3f577365b9a295607142c9b920e2c07b184e266d62b1ee1
curl --fail --location --silent --show-error --proto '=https' --tlsv1.2 --connect-timeout 10 --max-time 60 \
    --output "$dotfiles_tmp/install" https://releases.nixos.org/nix/nix-2.35.4/install
if command -v sha256sum >/dev/null 2>&1; then
    printf '%s  %s\n' "$dotfiles_sha256" "$dotfiles_tmp/install" | sha256sum -c -
else
    printf '%s  %s\n' "$dotfiles_sha256" "$dotfiles_tmp/install" | shasum -a 256 -c -
fi
dotfiles_mode=--daemon
if [ "$(uname -s)" = Linux ] && [ ! -d /run/systemd/system ]; then
    dotfiles_mode=--no-daemon
fi
sh "$dotfiles_tmp/install" "$dotfiles_mode"
printf '%s\n' 'Nix installation finished. Open a new shell, then run scripts/home-manager.sh build.'
