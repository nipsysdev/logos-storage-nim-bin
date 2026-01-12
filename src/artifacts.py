"""Artifact management for build system."""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List

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
        
        if "aarch64" in target:
            return "aarch64" in file_info
        elif "x86_64" in target:
            return "x86-64" in file_info or "Intel 80386" in file_info
        elif "i686" in target or "i386" in target:
            return "Intel 80386" in file_info
    finally:
        Path(temp_path).unlink(missing_ok=True)
    
    return False


def collect_artifacts(logos_storage_dir: Path, target: str) -> List[Path]:
    """Collect all required library artifacts."""
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
        if not path.exists():
            raise FileNotFoundError(f"{name} not found at {path}")
        if not check_artifact_compatibility(path, target):
            raise ValueError(f"{name} is not compatible with target architecture: {target}")
        libraries.append(path)
        print(f"✓ Found {name} (compatible with {target})")
    
    # Handle leopard library (check release first, then debug)
    leopard_release = logos_storage_dir / "nimcache" / "release" / "libstorage" / "vendor_leopard" / "liblibleopard.a"
    leopard_debug = logos_storage_dir / "nimcache" / "debug" / "libstorage" / "vendor_leopard" / "liblibleopard.a"
    
    if leopard_release.exists():
        if not check_artifact_compatibility(leopard_release, target):
            raise ValueError(f"liblibleopard.a (release) is not compatible with target architecture: {target}")
        libraries.append(leopard_release)
        print(f"✓ Found liblibleopard.a (release, compatible with {target})")
    elif leopard_debug.exists():
        if not check_artifact_compatibility(leopard_debug, target):
            raise ValueError(f"liblibleopard.a (debug) is not compatible with target architecture: {target}")
        libraries.append(leopard_debug)
        print(f"✓ Found liblibleopard.a (debug, compatible with {target})")
    else:
        raise FileNotFoundError("liblibleopard.a not found (checked release and debug locations)")
    
    return libraries


def combine_libraries(libraries: List[Path], output_dir: Path) -> Path:
    """Combine multiple static libraries into one."""
    print(f"Combining {len(libraries)} libraries...")
    
    output_path = Path.cwd() / output_dir / "libstorage.a"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Build ar command
    cmd = ["ar", "rcs", str(output_path)] + [str(lib) for lib in libraries]
    run_command(cmd)
    
    # Verify
    if output_path.exists():
        size = output_path.stat().st_size
        print(f"✓ Successfully created libstorage.a")
        print(f"  Library size: {size} bytes")
    else:
        raise FileNotFoundError(f"Combined library not found at {output_path}")
    
    return output_path


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