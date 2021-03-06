function peco_select_history
  if test (count $argv) = 0
    set peco_flags --layout=bottom-up
  else
    set peco_flags --layout=bottom-up --query "$argv"
  end

  history|peco $peco_flags|read foo

  if [ $foo ]
    commandline $foo
  else
    commandline ''
  end
end

function _peco_change_directory
  if [ (count $argv) ]
    peco --layout=bottom-up --query "$argv "|perl -pe 's/([ ()])/\\\\$1/g'|read foo
  else
    peco --layout=bottom-up |perl -pe 's/([ ()])/\\\\$1/g'|read foo
  end
  if [ $foo ]
    builtin cd $foo
  else
    commandline ''
  end
end

function peco_change_directory
  begin
    echo $HOME/.config
    ls -ad */|perl -pe "s#^#$PWD/#"|egrep -v "^$PWD/\."|head -n 5
    sort -r -t '|' -k 3 ~/.z|sed -e 's/\|.*//'
    ghq list -p
    ls -ad */|perl -pe "s#^#$PWD/#"|grep -v \.git
  end | sed -e 's/\/$//' | awk '!a[$0]++' | _peco_change_directory $argv
end

