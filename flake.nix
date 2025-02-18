{
  description = "Development environment for Perspicuity - An open source Perplexity AI alternative";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs { inherit system; };
        lib = pkgs.lib;
        stdenv = pkgs.stdenv;
        pythonPackages = pkgs.python312Packages;
      in
      {
        devShell = pkgs.mkShell {
          buildInputs = [
            pkgs.git
            pkgs.nodejs_20
            pkgs.nodePackages.npm
            pkgs.ollama
            pythonPackages.python
            pythonPackages.venvShellHook
          ];
          packages = [ pkgs.poetry ];
          venvDir = "./.venv";
          postVenvCreation = ''
            unset SOURCE_DATE_EPOCH
            poetry env use .venv/bin/python
            poetry install
          '';
          postShellHook = ''
            unset SOURCE_DATE_EPOCH
            export LD_LIBRARY_PATH=${lib.makeLibraryPath [ stdenv.cc.cc ]}
            poetry env info
          '';
        };
      }
    );
}
