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
    
    This uses a simple format (e.g., linux-amd64, linux-arm64, darwin-amd64, darwin-arm64)
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