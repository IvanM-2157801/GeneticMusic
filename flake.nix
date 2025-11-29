{
  description = "A Nix-flake-based Development Environment Python";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forEachSupportedSystem = f: nixpkgs.lib.genAttrs supportedSystems (system: f {
        pkgs = import nixpkgs { inherit system; };
      });
    in
    {
      devShells = forEachSupportedSystem ({ pkgs }: {
        default = pkgs.mkShell {
          packages = with pkgs; [ 
            python311
            # SuperCollider (required by supriya)
            supercollider
            # PipeWire JACK compatibility
            pipewire
            # Audio libraries
            portaudio
            libsndfile
            # Build dependencies
            pkg-config
            gcc
            stdenv.cc.cc.lib
          ] ++
            (with pkgs.python311Packages; [
              pip
              virtualenv
            ]);

          # Set environment variables for supriya
          LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.stdenv.cc.cc.lib
            pkgs.portaudio
            pkgs.libsndfile
            pkgs.pipewire
          ];

          shellHook = ''
            # Create venv if it doesn't exist
            if [ ! -d ".venv" ]; then
              echo "Creating Python virtual environment..."
              python -m venv .venv
            fi
            
            # Activate the venv
            source .venv/bin/activate
            
            echo "Python venv activated. Use 'pip install <package>' to install packages."
          '';
        };
      });
    };
}
