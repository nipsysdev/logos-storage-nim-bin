"""Shared fixtures and test configuration."""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from dataclasses import dataclass

import pytest


@dataclass
class MockCompletedProcess:
    """Mock subprocess.CompletedProcess for testing."""
    returncode: int
    stdout: str
    stderr: str = ""


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_run_command():
    """Mock the run_command utility function."""
    with patch("src.utils.run_command") as mock:
        yield mock


@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run for testing."""
    with patch("subprocess.run") as mock:
        yield mock


@pytest.fixture
def mock_shutil_rmtree():
    """Mock shutil.rmtree for testing."""
    with patch("shutil.rmtree") as mock:
        yield mock


@pytest.fixture
def mock_path_exists():
    """Mock Path.exists for testing."""
    with patch("pathlib.Path.exists") as mock:
        yield mock


@pytest.fixture
def mock_path_rglob():
    """Mock Path.rglob for testing."""
    with patch("pathlib.Path.rglob") as mock:
        yield mock


@pytest.fixture
def mock_path_unlink():
    """Mock Path.unlink for testing."""
    with patch("pathlib.Path.unlink") as mock:
        yield mock


@pytest.fixture
def mock_path_mkdir():
    """Mock Path.mkdir for testing."""
    with patch("pathlib.Path.mkdir") as mock:
        yield mock


@pytest.fixture
def mock_path_write_text():
    """Mock Path.write_text for testing."""
    with patch("pathlib.Path.write_text") as mock:
        yield mock


@pytest.fixture
def mock_path_read_text():
    """Mock Path.read_text for testing."""
    with patch("pathlib.Path.read_text") as mock:
        yield mock


@pytest.fixture
def mock_path_stat():
    """Mock Path.stat for testing."""
    with patch("pathlib.Path.stat") as mock:
        yield mock


@pytest.fixture
def mock_os_environ():
    """Mock os.environ for testing."""
    with patch.dict(os.environ, {}, clear=True):
        yield os.environ


@pytest.fixture
def mock_platform_machine():
    """Mock platform.machine for testing."""
    with patch("platform.machine") as mock:
        yield mock


@pytest.fixture
def sample_commit_info():
    """Sample commit information for testing."""
    from src.repository import CommitInfo
    return CommitInfo(
        commit="abc123def456789abc123def456789abc123def",
        commit_short="abc123d",
        branch="master"
    )


@pytest.fixture
def sample_artifact_paths(temp_dir):
    """Create sample artifact files for testing."""
    # Create directory structure
    build_dir = temp_dir / "build"
    build_dir.mkdir(parents=True, exist_ok=True)
    
    vendor_dir = temp_dir / "vendor"
    vendor_dir.mkdir(parents=True, exist_ok=True)
    
    nimcache_dir = temp_dir / "nimcache"
    nimcache_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample library files
    libstorage = build_dir / "libstorage.a"
    libstorage.write_bytes(b"fake libstorage content")
    
    libnatpmp = vendor_dir / "nim-nat-traversal" / "vendor" / "libnatpmp-upstream" / "libnatpmp.a"
    libnatpmp.parent.mkdir(parents=True, exist_ok=True)
    libnatpmp.write_bytes(b"fake libnatpmp content")
    
    libminiupnpc = vendor_dir / "nim-nat-traversal" / "vendor" / "miniupnp" / "miniupnpc" / "build" / "libminiupnpc.a"
    libminiupnpc.parent.mkdir(parents=True, exist_ok=True)
    libminiupnpc.write_bytes(b"fake libminiupnpc content")
    
    libcircom = vendor_dir / "nim-circom-compat" / "vendor" / "circom-compat-ffi" / "target" / "release" / "libcircom_compat_ffi.a"
    libcircom.parent.mkdir(parents=True, exist_ok=True)
    libcircom.write_bytes(b"fake libcircom_compat_ffi content")
    
    libbacktrace = vendor_dir / "nim-libbacktrace" / "install" / "usr" / "lib" / "libbacktrace.a"
    libbacktrace.parent.mkdir(parents=True, exist_ok=True)
    libbacktrace.write_bytes(b"fake libbacktrace content")
    
    # Create leopard library - correct path structure
    leopard_dir = temp_dir / "nimcache" / "release" / "libstorage" / "vendor_leopard"
    leopard_dir.mkdir(parents=True, exist_ok=True)
    leopard = leopard_dir / "liblibleopard.a"
    leopard.write_bytes(b"fake libleopard content")
    
    return temp_dir