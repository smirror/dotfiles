{
  description = "Shared macOS and WSL user environment";

  inputs = {
    # Review these pinned development revisions together before updating.
    nixpkgs.url = "github:NixOS/nixpkgs/6dadaf4375be35033e1c84395adbd53ff5fded96";
    home-manager.url = "github:nix-community/home-manager/b787c48e2ec57a9d098f5c2721882a3bc1e16f97";
    home-manager.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { nixpkgs, home-manager, ... }:
    let
      systems = [ "aarch64-darwin" "aarch64-linux" "x86_64-linux" ];
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
