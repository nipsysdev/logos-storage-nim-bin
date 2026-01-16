"""Artifact management for build system."""

import os
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
        "vendor/nim-circom-compat/vendor/circom-compat-ffi/target",
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
    
    # Update submodules first
    print("Updating git submodules...")
    try:
        run_command(
            ["make", "-C", str(logos_storage_dir), "deps"],
            env={"STATIC": "1"}
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
            env={"STATIC": "1"}
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


def check_artifact_compatibility(artifact_path: Path, target: str) -> bool:
    """Check if an artifact is compatible with the target architecture."""
    # List archive contents
    result = run_command(["ar", "t", str(artifact_path)], check=False)
    if result.returncode != 0:
        print(f"Warning: Failed to list archive contents for {artifact_path}")
        return False
    
    # Get first object file
    first_obj = result.stdout.split('\n')[0].strip()
    if not first_obj:
        print(f"Warning: Archive appears to be empty: {artifact_path}")
        return False
    
    # Extract object file (binary output)
    extract_result = run_command(
        ["ar", "p", str(artifact_path), first_obj],
        check=False,
        binary=True
    )
    if extract_result.returncode != 0:
        print(f"Warning: Failed to extract {first_obj} from archive")
        return False
    
    # Write to temp file and check
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(extract_result.stdout)
        temp_path = temp_file.name
    
    try:
        file_result = run_command(["file", temp_path], check=False)
        if file_result.returncode != 0:
            return False
        
        file_info = file_result.stdout
        
        # Debug logging to help diagnose compatibility issues
        print(f"DEBUG: Checking compatibility for {artifact_path.name}")
        print(f"DEBUG: Target architecture: {target}")
        print(f"DEBUG: File command output: {file_info}")
        
        if "aarch64" in target:
            # Check for both aarch64 (Linux) and arm64 (macOS Mach-O)
            result = "aarch64" in file_info or "arm64" in file_info
            print(f"DEBUG: aarch64/arm64 check result: {result}")
            return result
        elif "x86_64" in target:
            result = "x86-64" in file_info or "Intel 80386" in file_info
            print(f"DEBUG: x86_64 check result: {result}")
            return result
        elif "i686" in target or "i386" in target:
            result = "Intel 80386" in file_info
            print(f"DEBUG: i686/i386 check result: {result}")
            return result
    finally:
        Path(temp_path).unlink(missing_ok=True)
    
    return False


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
    artifact_paths = [
        ("libstorage.a", logos_storage_dir / "build" / "libstorage.a"),
        ("libnatpmp.a", logos_storage_dir / "vendor" / "nim-nat-traversal" / "vendor" / "libnatpmp-upstream" / "libnatpmp.a"),
        ("libminiupnpc.a", logos_storage_dir / "vendor" / "nim-nat-traversal" / "vendor" / "miniupnp" / "miniupnpc" / "build" / "libminiupnpc.a"),
        ("libcircom_compat_ffi.a", logos_storage_dir / "vendor" / "nim-circom-compat" / "vendor" / "circom-compat-ffi" / "target" / "release" / "libcircom_compat_ffi.a"),
        ("libbacktrace.a", logos_storage_dir / "vendor" / "nim-libbacktrace" / "install" / "usr" / "lib" / "libbacktrace.a"),
    ]
    
    # Check standard libraries
    for name, path in artifact_paths:
        if not path_exists(path):
            raise FileNotFoundError(f"{name} not found at {path}")
        if not check_artifact_compatibility(path, target):
            raise ValueError(f"{name} is not compatible with target architecture: {target}")
        libraries.append(path)
        print(f"✓ Found {name} (compatible with {target})")
    
    # Handle leopard library (check release first, then debug)
    leopard_release = logos_storage_dir / "nimcache" / "release" / "libstorage" / "vendor_leopard" / "liblibleopard.a"
    leopard_debug = logos_storage_dir / "nimcache" / "debug" / "libstorage" / "vendor_leopard" / "liblibleopard.a"
    
    if path_exists(leopard_release):
        if not check_artifact_compatibility(leopard_release, target):
            raise ValueError(f"liblibleopard.a (release) is not compatible with target architecture: {target}")
        libraries.append(leopard_release)
        print(f"✓ Found liblibleopard.a (release, compatible with {target})")
    elif path_exists(leopard_debug):
        if not check_artifact_compatibility(leopard_debug, target):
            raise ValueError(f"liblibleopard.a (debug) is not compatible with target architecture: {target}")
        libraries.append(leopard_debug)
        print(f"✓ Found liblibleopard.a (debug, compatible with {target})")
    else:
        raise FileNotFoundError("liblibleopard.a not found (checked release and debug locations)")
    
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
        print(f"✓ Copied {lib_path.name} to {dest_path}")
    
    print(f"✓ Successfully copied {len(copied_libraries)} libraries")
    return copied_libraries


def generate_checksum(artifact_path: Path) -> None:
    """Generate SHA256 checksum for an artifact."""
    checksum_path = artifact_path.with_suffix(".a.sha256")
    result = run_command(["sha256sum", str(artifact_path)])
    checksum_path.write_text(result.stdout)
    print(f"✓ Generated checksum: {checksum_path}")


def verify_checksum(artifact_path: Path) -> bool:
    checksum_path = artifact_path.with_suffix(".a.sha256")
    
    if not checksum_path.exists():
        raise FileNotFoundError(f"Checksum file not found: {checksum_path}")
    
    print(f"Verifying {artifact_path.name} against checksum...")
    
    # Read expected checksum
    expected_checksum = checksum_path.read_text().strip()
    expected_hash = expected_checksum.split()[0]
    
    # Compute actual checksum
    result = run_command(["sha256sum", str(artifact_path)])
    actual_checksum = result.stdout.strip()
    actual_hash = actual_checksum.split()[0]
    
    # Compare
    if expected_hash == actual_hash:
        print(f"✓ Checksum verification passed for {artifact_path.name}")
        return True
    else:
        raise ValueError(
            f"Checksum verification failed for {artifact_path.name}!\n"
            f"  Expected: {expected_hash}\n"
            f"  Actual:   {actual_hash}"
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
    print(f"✓ Copied libstorage.h to {header_dest}")
    
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
    print(f"✓ Generated SHA256SUMS.txt with {len(checksums)} entries")
    
    return checksums_path