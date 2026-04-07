"""
Main build script for logos-storage-nim binaries.

This script orchestrates the entire build process:
1. Clones/updates the logos-storage-nim repository
2. Builds the libstorage static library
3. Collects and combines artifacts
4. Generates checksums
"""

import os
import subprocess
import sys
from pathlib import Path

from src.utils import (
    get_platform_identifier,
    get_host_triple,
    get_parallel_jobs,
    configure_reproducible_environment,
    is_android_build,
    get_target_platform,
    build_embedded_nim
)
from src.repository import ensure_logos_storage_repo
from src.artifacts import (
    clean_build_artifacts,
    build_libstorage,
    build_libstorage_android,
    collect_artifacts,
    copy_libraries,
    copy_header_file,
    generate_sha256sums
)
from src.repository import reset_repository


def main() -> None:
    """Main entry point."""
    # Get configuration
    platform = get_platform_identifier()
    branch = os.environ.get("BRANCH")
    commit = os.environ.get("COMMIT")
    tag = os.environ.get("TAG")
    
    # Validate mutually exclusive options
    if tag and (branch or commit):
        print("Error: TAG cannot be used with BRANCH or COMMIT", file=sys.stderr)
        sys.exit(1)
    
    if branch and commit:
        print("Error: BRANCH and COMMIT are mutually exclusive", file=sys.stderr)
        sys.exit(1)
    
    # Set default branch if not specified
    if not tag and not branch:
        branch = "master"
    
    if tag:
        print(f"Building logos-storage-nim from tag: {tag}")
    else:
        print("Building logos-storage-nim")
    
    print(f"Platform: {platform}")
    if tag:
        print(f"Tag: {tag}")
    elif commit:
        print(f"Branch: {branch}")
        print(f"Commit: {commit}")
    else:
        print(f"Branch: {branch}")
    print("=" * 42)
    
    # Configure environment
    configure_reproducible_environment()
    
    # Ensure repository
    if tag:
        logos_storage_dir, commit_info = ensure_logos_storage_repo(tag, None)
    else:
        logos_storage_dir, commit_info = ensure_logos_storage_repo(branch, commit)
    
    print(f"Commit: {commit_info.commit} ({commit_info.commit_short})")
    print(f"Branch: {commit_info.branch}")
    print("=" * 42)
    
    # Build
    jobs = get_parallel_jobs()
    
    # Build embedded Nim (Phase 0) - this is required and will fail if unable to build
    print("Building embedded Nim (required step)...")
    try:
        build_embedded_nim(logos_storage_dir, jobs)
        print("✓ Embedded Nim build completed successfully")
    except Exception as e:
        print(f"✗ Failed to build embedded Nim: {e}")
        print("Embedded Nim build is required - cannot proceed without it")
        sys.exit(1)
    
    # Reset repository to clean state before building (can be skipped with SKIP_REPO_RESET)
    # This preserves the embedded Nim compiler to avoid rebuilding every time
    if not os.environ.get("SKIP_REPO_RESET"):
        try:
            reset_repository(logos_storage_dir, preserve_nim=True)
            print("✓ Repository reset complete (embedded Nim preserved)")
        except (subprocess.CalledProcessError, OSError) as e:
            print(f"Warning: Failed to reset repository: {e}")
            print("Continuing with potentially dirty state...")
        except Exception as e:
            print(f"Unexpected error during repository reset: {e}")
            print("This may indicate a serious issue - consider running with SKIP_REPO_RESET=1")
            raise
    else:
        print("Skipping repository reset (SKIP_REPO_RESET is set)")
    
    if is_android_build():
        # Android build - use client-lite patches
        patch_dir = Path("patches")
        build_libstorage_android(logos_storage_dir, jobs, patch_dir)
    else:
        # Desktop build - full library
        build_libstorage(logos_storage_dir, jobs)
    
    # Collect and combine artifacts
    host_triple = get_host_triple()
    libraries = collect_artifacts(logos_storage_dir, host_triple)
    
    # Create output directory
    if tag:
        artifact_name = f"{tag}-{platform}"
    else:
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
    if tag:
        print(f"Version: {tag}")
    else:
        print(f"Version: {commit_info.branch}-{commit_info.commit_short}")
    print("=" * 42)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)