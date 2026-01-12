"""
Clean script for logos-storage-nim build artifacts.

This script provides cleaning functionality for the build system:
- Default: Clean build artifacts (Nim cache, build directories, .o files)
- --all: Clean everything including dist/ and logos-storage-nim/ directories
"""

import argparse
import shutil
import sys
from pathlib import Path

from src.repository import ensure_logos_storage_repo
from src.artifacts import clean_build_artifacts


def clean_all() -> None:
    """Clean everything including dist/ and logos-storage-nim/ directories."""
    print("=" * 42)
    print("Cleaning all artifacts and directories")
    print("=" * 42)
    
    # Clean build artifacts
    logos_storage_dir = Path("logos-storage-nim")
    if logos_storage_dir.exists():
        clean_build_artifacts(logos_storage_dir)
    else:
        print("logos-storage-nim directory not found, skipping build artifact cleanup")
    
    # Remove dist directory
    dist_dir = Path("dist")
    if dist_dir.exists():
        print(f"Removing dist directory: {dist_dir}")
        shutil.rmtree(dist_dir)
    else:
        print("dist directory not found, skipping")
    
    # Remove logos-storage-nim directory
    if logos_storage_dir.exists():
        print(f"Removing logos-storage-nim directory: {logos_storage_dir}")
        shutil.rmtree(logos_storage_dir)
    else:
        print("logos-storage-nim directory not found, skipping")
    
    print("=" * 42)
    print("All cleanup complete!")
    print("=" * 42)


def clean_build_only() -> None:
    """Clean only build artifacts (Nim cache, build directories, .o files)."""
    logos_storage_dir = Path("logos-storage-nim")
    
    if not logos_storage_dir.exists():
        print("logos-storage-nim directory not found, skipping clean")
        return
    
    clean_build_artifacts(logos_storage_dir)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Clean logos-storage-nim build artifacts"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Clean everything including dist/ and logos-storage-nim/ directories"
    )
    
    args = parser.parse_args()
    
    if args.all:
        clean_all()
    else:
        clean_build_only()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)