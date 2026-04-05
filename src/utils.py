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


def configure_android_environment() -> dict:
    """Configure Android NDK build environment."""
    ndk_root = get_android_ndk_root()
    host_triple = get_android_host_triple()
    
    # NDK toolchain paths
    ndk_target = Path(ndk_root) / "toolchains/llvm/prebuilt/linux-x86_64"
    
    if not ndk_target.exists():
        raise ValueError(f"NDK toolchain not found at {ndk_target}")
    
    # Android compilers
    cc_path = ndk_target / "bin/aarch64-linux-android21-clang"
    cxx_path = ndk_target / "bin/aarch64-linux-android21-clang++"
    ar_path = ndk_target / "bin/llvm-ar"
    
    for tool_path in [cc_path, cxx_path, ar_path]:
        if not tool_path.exists():
            raise ValueError(f"Android tool not found: {tool_path}")
    
    # Secondary: traditional NDK path
    ndk_alt = Path(ndk_root) / "toolchains/llvm/prebuilt/linux-x86_64"
    if ndk_alt.exists():
        cc_path = ndk_alt / "bin/aarch64-linux-android21-clang"
        cxx_path = ndk_alt / "bin/aarch64-linux-android21-clang++"
        ar_path = ndk_alt / "bin/llvm-ar"
    
    # Add nim to PATH - use environment variables or sensible defaults
    nimble_bin = os.environ.get("NIMBLE_BIN", os.path.expanduser("~/.nimble/bin"))
    chosenim_toolchains = os.environ.get("CHOSENIM_TOOLCHAINS", os.path.expanduser("~/.choosenim/toolchains/nim-2.2.8/bin"))
    nim_paths = [nimble_bin, chosenim_toolchains]
    
    # Filter out paths that don't exist
    nim_paths = [path for path in nim_paths if Path(path).exists()]
    
    path_separator = ":"
    current_path = os.environ.get("PATH", "")
    new_path = path_separator.join(nim_paths + [current_path])
    
    return {
        "STATIC": "1",
        "CLIENT_LITE": "1",
        "HOST_TRIPLE": host_triple,
        "CC": str(cc_path),
        "CXX": str(cxx_path),
        "AR": str(ar_path),
        "PATH": new_path,
    }


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