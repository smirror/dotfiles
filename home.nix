{ config, lib, pkgs, username, homeDirectory, ... }:

let
  # Only these source files become managed links; runtime state stays writable.
  fishFiles = [
    "completions/bd.fish"
    "completions/fisher.fish"
    "completions/ghq.fish"
    "conf.d/fzf.fish"
    "conf.d/ghq_key_bindings.fish"
    "conf.d/z.fish"
    "functions/__fzf_cd.fish"
    "functions/__fzf_complete.fish"
    "functions/__fzf_complete_preview.fish"
    "functions/__fzf_find_file.fish"
    "functions/__fzf_get_dir.fish"
    "functions/__fzf_open.fish"
    "functions/__fzf_parse_commandline.fish"
    "functions/__fzf_reverse_isearch.fish"
    "functions/__fzfcmd.fish"
    "functions/__ghq_repository_search.fish"
    "functions/__z.fish"
    "functions/__z_add.fish"
    "functions/__z_clean.fish"
    "functions/__z_complete.fish"
    "functions/bd.fish"
    "functions/fisher.fish"
    "functions/peco_select_history.fish"
  ];
in
{
  assertions = [
    {
      assertion = username != "" && lib.hasPrefix "/" homeDirectory && homeDirectory != "/";
      message = "Use scripts/home-manager.sh, or set DOTFILES_USER and DOTFILES_HOME and pass --impure.";
    }
  ];

  home = {
    inherit username homeDirectory;
    stateVersion = "26.05";
    packages = with pkgs; [
      bat coreutils findutils fzf gawk getopt ghq gnugrep gnused
      peco perl ripgrep starship
    ];
    sessionPath = [ "${config.home.profileDirectory}/bin" ];
    file = {
      ".codex/AGENTS.md".source = ./agents/global.md;
      ".claude/CLAUDE.md".source = ./agents/global.md;
    };
  };

  programs.home-manager.enable = true;
  programs.fish = {
    enable = true;
    generateCompletions = false;
    shellInit = builtins.readFile ./fish/config.fish;
    shellInitLast = ''
      fish_add_path --path --move ${lib.escapeShellArg "${config.home.profileDirectory}/bin"}
    '';
  };

  xdg.configFile = builtins.listToAttrs (map (name: {
    name = "fish/${name}";
    value.source = ./fish + "/${name}";
  }) fishFiles);
}
