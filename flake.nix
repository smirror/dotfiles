{
  description = "Shared macOS and WSL user environment";

  inputs = {
    # Track update sources here; flake.lock pins the reviewed revisions/hashes.
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    home-manager.url = "github:nix-community/home-manager/master";
    home-manager.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { nixpkgs, home-manager, ... }:
    let
      systems = [ "aarch64-darwin" "aarch64-linux" "x86_64-linux" ];
      forSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      packages = forSystems (system: let pkgs = nixpkgs.legacyPackages.${system}; in {
        home-manager = home-manager.packages.${system}.home-manager;
        tools = pkgs.buildEnv {
          name = "dotfiles-tools";
          paths = (import ./tool-packages.nix pkgs) ++ [ pkgs.fish ];
        };
      });

      homeConfigurations = forSystems (system:
        home-manager.lib.homeManagerConfiguration {
          pkgs = nixpkgs.legacyPackages.${system};
          extraSpecialArgs = {
            username = builtins.getEnv "DOTFILES_USER";
            homeDirectory = builtins.getEnv "DOTFILES_HOME";
          };
          modules = [ ./home.nix ];
        });
    };
}
