"""PyInstaller entry point.

Frozen builds target this script. It just calls the package main() so the
relative imports inside the folderbeam package resolve normally (running a
module file directly would break those).
"""
from folderbeam.app import main

if __name__ == "__main__":
    main()
