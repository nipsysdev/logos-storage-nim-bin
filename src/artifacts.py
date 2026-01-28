"""Artifact management for build system."""

import os
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Callable, Optional

from src.utils import run_command


def clean_build_artifacts(logos_storage_dir: Path) -> None:
    """Clean all build artifacts."""
    print("Cleaning all build artifacts...")
    
    # Clean Nim cache
    home = os.environ.get("HOME")
    if home:
        nim_cache = Path(home) / ".cache" / "nim" / "libstorage_d"
        if nim_cache.exists():
            print(f"Removing Nim cache: {nim_cache}")
            shutil.rmtree(nim_cache)
    
    # Clean build directories
    build_dirs = [
        "vendor/nim-nat-traversal/vendor/miniupnp/miniupnpc/build",
        "vendor/nim-nat-traversal/vendor/libnatpmp-upstream/build",
        "vendor/nim-leveldbstatic/build",
        "build",
        "nimcache/release",
        "nimcache/debug",
    ]
    
    for dir_name in build_dirs:
        dir_path = logos_storage_dir / dir_name
        if dir_path.exists():
            print(f"Removing build directory: {dir_name}")
            shutil.rmtree(dir_path)
    
    # Clean .o files
    for dir_name in [
        "vendor/nim-nat-traversal/vendor/libnatpmp-upstream",
        "vendor/nim-nat-traversal/vendor/miniupnp/miniupnpc",
    ]:
        dir_path = logos_storage_dir / dir_name
        if dir_path.exists():
            for path in dir_path.rglob("*.o"):
                path.unlink()
    
    # Restore .gitkeep
    gitkeep_dir = logos_storage_dir / "vendor" / "nim-leveldbstatic" / "build"
    if gitkeep_dir.exists():
        run_command(["git", "-C", str(gitkeep_dir), "restore", ".gitkeep"], check=False)
    
    print("Build artifacts cleaned")


def build_libstorage(logos_storage_dir: Path, jobs: int) -> None:
    """Build libstorage for host architecture."""
    print("Building libstorage for host architecture...")
    
    # Set CPU target flags for maximum compatibility based on architecture
    # This ensures binaries work on all CPUs of the target architecture
    from src.utils import get_host_triple
    
    arch = get_host_triple()
    build_env = {
        "STATIC": "1",
    }
    
    # Apply architecture-specific compiler flags
    if arch == "x86_64":
        build_env["CFLAGS"] = "-march=x86-64 -mtune=generic"
        build_env["CXXFLAGS"] = "-march=x86-64 -mtune=generic"
        print(f"Building for x86_64 with baseline compatibility flags")
    elif arch == "aarch64":
        build_env["CFLAGS"] = "-march=armv8-a -mtune=generic"
        build_env["CXXFLAGS"] = "-march=armv8-a -mtune=generic"
        print(f"Building for ARM64 with baseline compatibility flags")
    else:
        print(f"Building for {arch} with default compiler settings")
    
    # Update submodules first
    print("Updating git submodules...")
    try:
        run_command(
            ["make", "-C", str(logos_storage_dir), "deps"],
            env=build_env
        )
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to update git submodules")
        print(f"Command: {' '.join(e.cmd)}")
        print(f"Exit code: {e.returncode}")
        if e.stdout:
            print(f"STDOUT:\n{e.stdout}")
        if e.stderr:
            print(f"STDERR:\n{e.stderr}")
        raise
    
    # Build with parallel jobs
    print(f"Building libstorage with {jobs} parallel jobs...")
    try:
        run_command(
            ["make", "-j", str(jobs), "-C", str(logos_storage_dir), "libstorage"],
            env=build_env
        )
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to build libstorage")
        print(f"Command: {' '.join(e.cmd)}")
        print(f"Exit code: {e.returncode}")
        if e.stdout:
            print(f"STDOUT:\n{e.stdout}")
        if e.stderr:
            print(f"STDERR:\n{e.stderr}")
        raise
    
    print("libstorage build complete")



def collect_artifacts(
    logos_storage_dir: Path,
    target: str,
    path_exists: Optional[Callable[[Path], bool]] = None
) -> List[Path]:
    """Collect all required library artifacts.
    
    Args:
        logos_storage_dir: Path to the logos-storage-nim repository
        target: Target architecture (e.g., "x86_64", "aarch64")
        path_exists: Optional function to check if a path exists.
                    If None, uses the default Path.exists() method.
                    This parameter is primarily for testing purposes.
    
    Returns:
        List of Path objects for all collected libraries
    
    Raises:
        FileNotFoundError: If any required library is not found
        ValueError: If any library is incompatible with the target architecture
    """
    if path_exists is None:
        path_exists = lambda p: p.exists()
    
    libraries = []
    
    # Define all libraries to collect
    # Note: On Windows, libminiupnpc.a is built in the root of miniupnpc directory,
    # not in build/ subdirectory (uses Makefile.mingw)
    if platform.system().lower() == "windows":
        miniupnpc_path = logos_storage_dir / "vendor" / "nim-nat-traversal" / "vendor" / "miniupnp" / "miniupnpc" / "libminiupnpc.a"
    else:
        miniupnpc_path = logos_storage_dir / "vendor" / "nim-nat-traversal" / "vendor" / "miniupnp" / "miniupnpc" / "build" / "libminiupnpc.a"
    
    artifact_paths = [
        ("libstorage.a", logos_storage_dir / "build" / "libstorage.a"),
        ("libnatpmp.a", logos_storage_dir / "vendor" / "nim-nat-traversal" / "vendor" / "libnatpmp-upstream" / "libnatpmp.a"),
        ("libminiupnpc.a", miniupnpc_path),
        ("libbacktrace.a", logos_storage_dir / "vendor" / "nim-libbacktrace" / "install" / "usr" / "lib" / "libbacktrace.a"),
    ]
    
    # Check standard libraries
    for name, path in artifact_paths:
        if not path_exists(path):
            raise FileNotFoundError(f"{name} not found at {path}")
        libraries.append(path)
        print(f"[OK] Found {name}")
    
    return libraries


def copy_libraries(libraries: List[Path], output_dir: Path) -> List[Path]:
    """Copy individual static libraries to output directory.
    
    Args:
        libraries: List of Path objects for all libraries to copy
        output_dir: Path to the output directory
        
    Returns:
        List of Path objects for all copied libraries
        
    Raises:
        FileNotFoundError: If any library cannot be copied
    """
    print(f"Copying {len(libraries)} libraries...")
    copied_libraries = []
    
    for lib_path in libraries:
        dest_path = output_dir / lib_path.name
        shutil.copy2(lib_path, dest_path)
        copied_libraries.append(dest_path)
        print(f"[OK] Copied {lib_path.name} to {dest_path}")
    
    print(f"[OK] Successfully copied {len(copied_libraries)} libraries")
    return copied_libraries


def generate_checksum(artifact_path: Path) -> None:
    """Generate SHA256 checksum for an artifact."""
    checksum_path = artifact_path.with_suffix(".a.sha256")
    
    # Use certutil on Windows, sha256sum on Unix
    if platform.system().lower() == "windows":
        result = run_command(["certutil", "-hashfile", str(artifact_path), "SHA256"])
        # certutil output format is different
        checksum_line = result.stdout.strip().split('\n')[1].replace(' ', '')
        checksum_path.write_text(f"{checksum_line}  {artifact_path.name}")
    else:
        result = run_command(["sha256sum", str(artifact_path)])
        checksum_path.write_text(result.stdout)
    
    print(f"[OK] Generated checksum: {checksum_path}")


def verify_checksum(artifact_path: Path) -> bool:
    checksum_path = artifact_path.with_suffix(".a.sha256")
    
    if not checksum_path.exists():
        raise FileNotFoundError(f"Checksum file not found: {checksum_path}")
    
    print(f"Verifying {artifact_path.name} against checksum...")
    
    # Read expected checksum
    expected_checksum = checksum_path.read_text().strip()
    expected_hash = expected_checksum.split()[0]
    
    # Compute actual checksum
    if platform.system().lower() == "windows":
        result = run_command(["certutil", "-hashfile", str(artifact_path), "SHA256"])
        actual_checksum = result.stdout.strip().split('\n')[1].replace(' ', '')
    else:
        result = run_command(["sha256sum", str(artifact_path)])
        actual_checksum = result.stdout.strip()
        actual_hash = actual_checksum.split()[0]
    
    # Compare
    if expected_hash == actual_checksum:
        print(f"[OK] Checksum verification passed for {artifact_path.name}")
        return True
    else:
        raise ValueError(
            f"Checksum verification failed for {artifact_path.name}!\n"
            f"  Expected: {expected_hash}\n"
            f"  Actual:   {actual_checksum}"
        )


def copy_header_file(logos_storage_dir: Path, output_dir: Path) -> Path:
    """Copy libstorage.h from repository to output directory.
    
    Args:
        logos_storage_dir: Path to the logos-storage-nim repository
        output_dir: Path to the output directory where header should be copied
        
    Returns:
        Path to the copied header file
        
    Raises:
        FileNotFoundError: If libstorage.h is not found at expected location
    """
    header_source = logos_storage_dir / "library" / "libstorage.h"
    
    if not header_source.exists():
        raise FileNotFoundError(
            f"libstorage.h not found at {header_source}. "
        )
    
    header_dest = output_dir / "libstorage.h"
    shutil.copy2(header_source, header_dest)
    print(f"[OK] Copied libstorage.h to {header_dest}")
    
    return header_dest


def generate_sha256sums(output_dir: Path) -> Path:
    """Generate SHA256SUMS.txt for all files in output directory.
    
    Args:
        output_dir: Path to the directory containing artifacts
        
    Returns:
        Path to the generated SHA256SUMS.txt file
    """
    checksums_path = output_dir / "SHA256SUMS.txt"
    
    # Find all files to checksum (exclude the checksum file itself)
    files_to_checksum = [
        f for f in output_dir.iterdir()
        if f.is_file() and f.name != "SHA256SUMS.txt"
    ]
    
    if not files_to_checksum:
        raise FileNotFoundError(f"No files found in {output_dir} to generate checksums")
    
    # Generate checksums without changing directory
    checksums = []
    for file_path in sorted(files_to_checksum):
        # Use certutil on Windows, sha256sum on Unix
        if platform.system().lower() == "windows":
            result = run_command(["certutil", "-hashfile", str(file_path), "SHA256"])
            # certutil output format is different
            checksum_line = result.stdout.strip().split('\n')[1].replace(' ', '')
            checksums.append(f"{checksum_line}  {file_path.name}")
        else:
            result = run_command(["sha256sum", str(file_path)])
            # Extract just the filename from the output
            checksum_line = result.stdout.strip()
            # Replace full path with just filename
            checksum_parts = checksum_line.split()
            if len(checksum_parts) >= 2:
                checksum_parts[1] = file_path.name
                checksums.append("  ".join(checksum_parts))
    
    # Write checksums file
    checksums_path.write_text("\n".join(checksums) + "\n")
    print(f"[OK] Generated SHA256SUMS.txt with {len(checksums)} entries")
    
    return checksums_path