{ pkgs ? import <nixpkgs> {} }:
  pkgs.mkShell {
    # nativeBuildInputs is usually what you want -- tools you need to run
    nativeBuildInputs = with pkgs; [
      python39Packages.lxml
      python39Packages.requests
    ];

    shellHook = ''
       echo "nix shell ready"
    '';
}
