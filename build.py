"""
Main build script for logos-storage-nim binaries.

This script orchestrates the entire build process:
1. Clones/updates the logos-storage-nim repository
2. Builds the libstorage static library
3. Collects and combines artifacts
4. Generates checksums
"""

import os
import sys
from pathlib import Path

from src.utils import get_platform_identifier, get_host_triple, get_parallel_jobs, configure_reproducible_environment
from src.repository import ensure_logos_storage_repo
from src.artifacts import (
    clean_build_artifacts,
    build_libstorage,
    collect_artifacts,
    copy_libraries,
    copy_header_file,
    generate_sha256sums
)


def main() -> None:
    """Main entry point."""
    # Get configuration
    platform = get_platform_identifier()
    branch = os.environ.get("BRANCH")
    commit = os.environ.get("COMMIT")
    
    # Set default branch if not specified
    if not branch:
        branch = "master"
    
    print("Building logos-storage-nim")
    print(f"Platform: {platform}")
    if commit:
        print(f"Branch: {branch}")
        print(f"Commit: {commit}")
    else:
        print(f"Branch: {branch}")
    print("=" * 42)
    
    # Configure environment
    configure_reproducible_environment()
    
    # Ensure repository
    logos_storage_dir, commit_info = ensure_logos_storage_repo(branch, commit)

    print(f"Commit: {commit_info.commit} ({commit_info.commit_short})")
    print(f"Branch: {commit_info.branch}")
    print("=" * 42)
    
    # Build
    jobs = get_parallel_jobs()
    build_libstorage(logos_storage_dir, jobs)
    
    # Collect and combine artifacts
    host_triple = get_host_triple()
    libraries = collect_artifacts(logos_storage_dir, host_triple)
    
    # Create output directory
    artifact_name = f"{commit_info.branch}-{commit_info.commit_short}-{platform}"
    dist_dir = Path("dist") / artifact_name
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy libraries individually
    copied_libraries = copy_libraries(libraries, dist_dir)
    
    # Copy header file
    copy_header_file(logos_storage_dir, dist_dir)
    
    # Generate SHA256SUMS.txt for all files
    generate_sha256sums(dist_dir)
    
    print("=" * 42)
    print("Build completed successfully!")
    print("=" * 42)
    print(f"Output: {dist_dir}")
    print(f"Version: {commit_info.branch}-{commit_info.commit_short}")
    print("=" * 42)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)