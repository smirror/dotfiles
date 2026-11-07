function peco_select_history
  set -l peco_flags --layout=bottom-up
  if set -q argv[1]
    set -a peco_flags --query "$argv"
  end
  history | peco $peco_flags | read -l selection; or return 1
  test -n "$selection"; or return 1
  commandline -- "$selection"
end

function _peco_change_directory
  set -l peco_flags --layout=bottom-up
  if set -q argv[1]
    set -a peco_flags --query "$argv"
  end
  peco $peco_flags | read -l directory; or return 1
  test -d "$directory"; or return 1
  builtin cd -- "$directory"
end

function peco_change_directory
  set -l directories "$PWD"/*/
  # shortcut: peco candidates are line-delimited, use cd directly for names containing newlines.
  begin
    test -d "$HOME/.config"; and printf '%s\n' "$HOME/.config"
    if set -q directories[1]
      printf '%s\n' $directories[1..5]
    end
    if set -q Z_DATA[1]; and test -f "$Z_DATA"
      sort -t '|' -k3,3nr -- "$Z_DATA" | cut -d '|' -f1
    end
    if command -q ghq
      command ghq list -p
    end
    if set -q directories[1]
      printf '%s\n' $directories
    end
  end | sed -e 's/\/$//' | awk '!a[$0]++' | _peco_change_directory $argv
end

