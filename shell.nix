{ pkgs ? import <nixpkgs> {} }:
  pkgs.mkShell {
    # nativeBuildInputs is usually what you want -- tools you need to run
    nativeBuildInputs = with pkgs; [
      firefox
      python39Packages.paho-mqtt
      python39Packages.selenium
    ];

    shellHook = ''
       echo "nix shell ready"
    '';
}
