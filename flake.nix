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
        inherit system;
      });
    in
    {
      devShells = forEachSupportedSystem ({ pkgs, system }:
        let
          isLinux = pkgs.stdenv.isLinux;
          isDarwin = pkgs.stdenv.isDarwin;
          
          commonPackages = with pkgs; [
            python311
            libsndfile
            pkg-config
          ] ++ (with pkgs.python311Packages; [
            pip
            virtualenv
          ]);
          
          linuxPackages = with pkgs; [
            gcc
            stdenv.cc.cc.lib
            pipewire
          ];
          
          darwinPackages = with pkgs; [
            # Add macOS-specific packages here if needed
          ];
          
          allPackages = commonPackages 
            ++ (if isLinux then linuxPackages else [])
            ++ (if isDarwin then darwinPackages else []);
          
          libraryPath = pkgs.lib.makeLibraryPath ([
            pkgs.portaudio
            pkgs.libsndfile
          ] ++ (if isLinux then [
            pkgs.stdenv.cc.cc.lib
            pkgs.pipewire
          ] else []));
        in
        {
          default = pkgs.mkShell {
            packages = allPackages;
            
            LD_LIBRARY_PATH = if isLinux then libraryPath else null;
            
            shellHook = ''
              if [ ! -d ".venv" ]; then
                echo "Creating Python virtual environment..."
                python -m venv .venv
              fi
              
              source .venv/bin/activate
              
              echo "Python venv activated. Use 'pip install <package>' to install packages."
            '';
          };
        }
      );
    };
}
