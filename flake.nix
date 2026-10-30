{
  description = "Shared macOS and WSL user environment";

  inputs = {
    # Matching stable 26.05 inputs; update and review these together.
    nixpkgs.url = "github:NixOS/nixpkgs/08d3a97586f6b6343b3b5e799980773629432610";
    home-manager.url = "github:nix-community/home-manager/24f2190587513b9c2f73db112a17844ae912d965";
    home-manager.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { nixpkgs, home-manager, ... }:
    let
      systems = [ "aarch64-darwin" "x86_64-darwin" "aarch64-linux" "x86_64-linux" ];
      forSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      packages = forSystems (system: {
        home-manager = home-manager.packages.${system}.home-manager;
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
