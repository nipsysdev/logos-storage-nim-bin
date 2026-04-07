"""Utility functions for the build system."""

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import List


def run_command(cmd: List[str], cwd: Path = None, env: dict = None, check: bool = True, binary: bool = False) -> subprocess.CompletedProcess:
    """Run a command and return the result.
    
    Args:
        cmd: Command to run
        cwd: Working directory
        env: Environment variables
        check: Whether to raise exception on non-zero exit code
        binary: If True, return binary output instead of text
    """
    kwargs = {"check": check}
    if cwd:
        kwargs["cwd"] = cwd
    if env:
        kwargs["env"] = {**os.environ, **env}
    
    return subprocess.run(cmd, capture_output=True, text=not binary, **kwargs)


def get_host_triple() -> str:
    """
    Get the host architecture for compatibility checking.
    
    Returns the architecture identifier (e.g., x86_64, aarch64)
    which is used to check artifact compatibility with the 'file' command.
    The 'file' command outputs architecture info like "aarch64" or "x86-64",
    so we just need to match these keywords.
    """
    machine = platform.machine().lower()
    
    if machine in ("x86_64", "amd64"):
        return "x86_64"
    elif machine in ("aarch64", "arm64"):
        return "aarch64"
    elif machine in ("i686", "i386"):
        return "i686"
    else:
        return machine


def get_platform_identifier() -> str:
    """
    Get platform identifier for artifact naming.
    
    This uses a simple format (e.g., linux-amd64, linux-arm64, darwin-amd64, darwin-arm64, windows-amd64)
    which is used for naming artifact directories and release files.
    """
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    if system == "darwin":
        if machine in ("aarch64", "arm64"):
            return "darwin-arm64"
        elif machine in ("x86_64", "amd64"):
            return "darwin-amd64"
        else:
            return "darwin-unknown"
    elif system == "linux":
        if machine in ("aarch64", "arm64"):
            return "linux-arm64"
        elif machine in ("x86_64", "amd64"):
            return "linux-amd64"
        else:
            return "linux-unknown"
    elif system == "windows":
        if machine in ("x86_64", "amd64"):
            return "windows-amd64"
        elif machine in ("aarch64", "arm64"):
            return "windows-arm64"
        else:
            return "windows-unknown"
    else:
        return f"{system}-{machine}"


def get_parallel_jobs() -> int:
    """Get number of parallel jobs (leaves one core free)."""
    try:
        # Use sysctl on macOS, nproc on Linux
        system = platform.system().lower()
        if system == "darwin":
            cmd = ["sysctl", "-n", "hw.ncpu"]
        else:
            cmd = ["nproc"]
        
        result = run_command(cmd, check=False)
        if result.returncode == 0:
            cpu_count = int(result.stdout.strip())
            return max(1, cpu_count - 1)
    except (FileNotFoundError, ValueError):
        pass
    return 1


def get_android_ndk_root() -> str:
    """Get Android NDK root directory from environment."""
    ndk_root = os.environ.get("ANDROID_NDK_ROOT") or os.environ.get("NDK_ROOT")
    if not ndk_root:
        raise ValueError(
            "ANDROID_NDK_ROOT or NDK_ROOT environment variable must be set. "
            "Example: export ANDROID_NDK_ROOT=/home/lowkey/Android/Sdk/ndk/29.0.14206865"
        )
    
    if not Path(ndk_root).exists():
        raise ValueError(f"Android NDK not found at {ndk_root}")
    
    return ndk_root


def get_android_host_triple() -> str:
    """Get Android host triple for cross-compilation."""
    return "aarch64-unknown-linux-android"


def configure_android_environment(logos_storage_dir: Path) -> dict:
    """Configure Android NDK build environment for build.nims approach."""
    ndk_root = get_android_ndk_root()
    host_triple = get_android_host_triple()
    
    # NDK toolchain paths - try primary location first
    ndk_target = Path(ndk_root) / "toolchains/llvm/prebuilt/linux-x86_64"
    
    # If primary doesn't exist, try alternative location
    if not ndk_target.exists():
        ndk_target = Path(ndk_root) / "toolchains/llvm/prebuilt/linux-x86_64"
        if not ndk_target.exists():
            raise ValueError(f"NDK toolchain not found at {ndk_root}/toolchains/llvm/prebuilt/")
    
    # Extract architecture from host triple for compiler selection
    arch = host_triple.split("-")[0]  # e.g., "aarch64" from "aarch64-unknown-linux-android"
    
    # Android compilers based on architecture
    cc_path = ndk_target / f"bin/{arch}-linux-android21-clang"
    cxx_path = ndk_target / f"bin/{arch}-linux-android21-clang++"
    ar_path = ndk_target / "bin/llvm-ar"
    android_linker = ndk_target / "bin/ld.lld"
    
    for tool_path in [cc_path, cxx_path, ar_path, android_linker]:
        if not tool_path.exists():
            raise ValueError(f"Android tool not found: {tool_path}")
    
    # Detect Clang version for build.nims
    clang_lib_path = ndk_target / "lib/clang"
    clang_version = "14"  # Default fallback
    if clang_lib_path.exists():
        import re
        versions = []
        for item in clang_lib_path.iterdir():
            if item.is_dir() and re.match(r'^\d+$', item.name):
                versions.append(int(item.name))
        if versions:
            clang_version = str(max(versions))
    
    # Use ONLY embedded Nim - no system Nim fallback
    embedded_nim_bin = logos_storage_dir / "vendor/nimbus-build-system/vendor/Nim/bin"
    if not embedded_nim_bin.exists():
        raise ValueError(f"Embedded Nim not found at {embedded_nim_bin}. Make sure build_embedded_nim() was called first.")
    
    path_separator = ":"
    current_path = os.environ.get("PATH", "")
    new_path = path_separator.join([str(embedded_nim_bin), str(ndk_target / "bin"), current_path])
    
    # Build environment for build.nims
    env = {
        "STATIC": "1",
        "CLIENT_LITE": "1",
        "HOST_TRIPLE": host_triple,
        "CC": str(cc_path),
        "CXX": str(cxx_path),
        "AR": str(ar_path),
        "PATH": new_path,
        "USE_EMBEDDED_NIM": "1",
        
        # build.nims specific environment variables
        "ANDROID_NDK_HOME": ndk_root,
        "ANDROID_NDK_ROOT": ndk_root,
        "ANDROID_CLANG_VERSION": clang_version,
        "ANDROID_CC": str(cc_path),
        "ANDROID_AR": str(ar_path),
        "TARGET_ARCH": arch,
        
        # Architecture-specific flags
        "NO_X86_INTRINSICS": "1",
        "BR_NO_X86_INTRINSICS": "1",
        "BR_NO_X86": "1",
        "BR_NO_ASM": "1",
    }
    
    # Add architecture-specific environment variables
    if arch == "aarch64":
        env["ANDROID_ARM64_BUILD"] = "1"
    elif arch == "x86_64":
        env["ANDROID_X86_64_BUILD"] = "1"
    
    return env


def configure_reproducible_environment() -> None:
    """Set environment variables for reproducible builds."""
    try:
        result = run_command(["git", "log", "-1", "--format=%ct"], check=False)
        source_date_epoch = result.stdout.strip() if result.returncode == 0 else "0"
    except FileNotFoundError:
        source_date_epoch = "0"
    
    os.environ["SOURCE_DATE_EPOCH"] = source_date_epoch
    os.environ["TZ"] = "UTC"
    os.environ["LC_ALL"] = "C.UTF-8"


def get_target_platform() -> str:
    """Get target platform from environment or default to host."""
    return os.environ.get("TARGET_PLATFORM", "").lower()


def is_android_build() -> bool:
    """Check if this is an Android build."""
    return get_target_platform() == "android"


def apply_bitops_patch_for_android(logos_storage_dir: Path) -> None:
    """Apply bitops.nim patch for Android builds to fix x86 intrinsics issue.
    
    This function applies the same fix that was used in the old storage-rust-bindings
    project to prevent x86 intrinsics from being used on Android ARM64 builds.
    
    Args:
        logos_storage_dir: Path to the logos-storage-nim repository
    """
    # Get the patch file path - use absolute path from workspace root
    workspace_root = Path(__file__).parent.parent
    patch_file = workspace_root / "patches" / "client-lite" / "0007-bitops.nim.patch"
    
    if not patch_file.exists():
        print(f"Warning: bitops.nim patch not found at {patch_file}")
        return
    
    # Change to the Nim directory before applying the patch
    nim_dir = logos_storage_dir / "vendor/nimbus-build-system/vendor/Nim"
    
    try:
        # Check if the patch is already applied by looking for the key change
        bitops_file = nim_dir / "lib/pure/bitops.nim"
        if bitops_file.exists():
            content = bitops_file.read_text()
            if "not defined(android) and not defined(arm64) and not defined(arm)" in content:
                print("✓ bitops.nim Android patch already applied")
                return
        
        # Apply the patch using git apply in the correct directory
        result = run_command([
            "git", "apply", str(patch_file)
        ], cwd=nim_dir)
        
        if result.returncode == 0:
            print("✓ Applied bitops.nim Android patch")
        else:
            print(f"✗ Failed to apply bitops.nim patch: {result.stderr}")
            raise RuntimeError("Failed to apply bitops.nim patch for Android build")
        
    except Exception as e:
        print(f"Warning: Failed to apply bitops.nim patch: {e}")


def build_embedded_nim(logos_storage_dir: Path, jobs: int = None) -> Path:
    """Build embedded Nim using logos-storage-nim Makefile.
    
    Args:
        logos_storage_dir: Path to the logos-storage-nim repository
        jobs: Number of parallel jobs to use (defaults to system optimal)
        
    Returns:
        Path to built nim binary
        
    Raises:
        FileNotFoundError: If logos-storage-nim directory not found
        RuntimeError: If Nim build fails or binary not found after build
        
    Note: This takes 10-15 minutes.
    """
    if not logos_storage_dir.exists():
        raise FileNotFoundError(f"logos-storage-nim directory not found at {logos_storage_dir}")
    
    # The embedded Nim binary path based on nimbus-build-system variables
    nim_binary = logos_storage_dir / "vendor/nimbus-build-system/vendor/Nim/bin/nim"
    
    # Check if nim binary already exists
    if nim_binary.exists():
        print(f"✓ Embedded Nim already built at {nim_binary}")
        return nim_binary
    
    print("This is a one-time build that will only happen if the embedded Nim binary doesn't exist.")
    
    try:
        # First, ensure git submodules are initialized
        print("Initializing git submodules...")
        result = run_command(["git", "submodule", "update", "--init", "--recursive"],
                           cwd=logos_storage_dir)
        if result.returncode != 0:
            print(f"Warning: git submodule update returned exit code {result.returncode}")
            print("Continuing anyway...")
        
        # Apply bitops.nim patch early for Android builds to fix x86 intrinsics
        # NOTE: This patch will be removed by build_nim.sh git reset, so we'll reapply it later
        if os.environ.get("TARGET_PLATFORM") == "android":
            print("Applying early bitops.nim patch for Android build...")
            apply_bitops_patch_for_android(logos_storage_dir)
        
        # Use the logos-storage-nim Makefile to build dependencies (including Nim)
        # The deps target will build the Nim compiler via the build-nim target
        # Use check=False to handle warnings/tips that don't indicate actual failure
        print("Starting Nim compiler build...")
        
        # Determine number of parallel jobs
        if jobs is None:
            jobs = get_parallel_jobs()
        
        # For Android builds, we need to handle the fact that build_nim.sh does git reset
        # which removes our patch. We'll use a retry approach.
        build_attempts = 0
        max_attempts = 2
        
        while build_attempts < max_attempts:
            build_attempts += 1
            
            # For Android builds on retry attempts, re-apply the patch
            if os.environ.get("TARGET_PLATFORM") == "android" and build_attempts > 1:
                print(f"Attempt {build_attempts}: Re-applying bitops.nim patch for Android build...")
                apply_bitops_patch_for_android(logos_storage_dir)
            
            # Build with parallel jobs for faster compilation
            make_cmd = ["make", "-C", str(logos_storage_dir), "-j", str(jobs), "deps"]
            print(f"Running: {' '.join(make_cmd)} (attempt {build_attempts})")
            result = run_command(make_cmd, check=False)
            
            # Check if the build actually succeeded despite the exit code
            if nim_binary.exists():
                print(f"✓ Embedded Nim built successfully at {nim_binary}")
                return nim_binary
            elif result.returncode == 0:
                # Build completed successfully but binary not found
                raise RuntimeError("Nim build completed successfully but binary not found at expected location")
            else:
                # Build failed - for Android, try applying the patch and retry
                if os.environ.get("TARGET_PLATFORM") == "android" and build_attempts < max_attempts:
                    print(f"Build failed on attempt {build_attempts}, will retry with patch...")
                    continue
                else:
                    # Build failed with non-zero exit code and binary doesn't exist
                    error_msg = f"Nim build failed with exit code {result.returncode} after {build_attempts} attempts"
                    if result.stdout:
                        error_msg += f"\nSTDOUT:\n{result.stdout}"
                    if result.stderr:
                        error_msg += f"\nSTDERR:\n{result.stderr}"
                    raise RuntimeError(error_msg)
        
    except Exception as e:
        if not isinstance(e, RuntimeError):
            print(f"✗ Failed to build embedded Nim: {e}")
            raise RuntimeError(f"Failed to build embedded Nim: {e}") from e
        raise