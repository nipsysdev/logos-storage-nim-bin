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


@pytest.fixture
def logos_storage_dir(temp_dir):
    """Create a temporary directory representing logos-storage-nim repository."""
    return temp_dir


@pytest.fixture
def dist_dir(temp_dir):
    """Create a temporary directory for distribution files."""
    dist = temp_dir / "dist"
    dist.mkdir(parents=True, exist_ok=True)
    return dist


@pytest.fixture
def mock_build_setup():
    """Fixture that provides common mocks for build.py main() function.
    
    This fixture sets up all the common patches needed for testing the main()
    function, reducing duplication across tests.
    """
    from unittest.mock import patch
    from pathlib import Path
    from src.repository import CommitInfo
    
    logos_storage_dir = Path("logos-storage-nim")
    mock_commit_info = CommitInfo("abc123def456789abc123def456789abc123def", "abc123d", "master")
    
    with patch("build.get_platform_identifier", return_value="linux-amd64") as mock_platform:
        with patch("build.configure_reproducible_environment") as mock_config:
            with patch("build.ensure_logos_storage_repo") as mock_repo:
                mock_repo.return_value = (logos_storage_dir, mock_commit_info)
                with patch("build.get_parallel_jobs", return_value=4) as mock_jobs:
                    with patch("build.build_libstorage") as mock_build:
                        with patch("build.get_host_triple", return_value="x86_64") as mock_triple:
                            with patch("build.collect_artifacts", return_value=[]) as mock_collect:
                                with patch("build.combine_libraries", return_value=Path("dist/libstorage.a")) as mock_combine:
                                    with patch("build.copy_header_file") as mock_copy:
                                        with patch("build.generate_sha256sums") as mock_checksums:
                                            yield {
                                                "mock_platform": mock_platform,
                                                "mock_config": mock_config,
                                                "mock_repo": mock_repo,
                                                "mock_jobs": mock_jobs,
                                                "mock_build": mock_build,
                                                "mock_triple": mock_triple,
                                                "mock_collect": mock_collect,
                                                "mock_combine": mock_combine,
                                                "mock_copy": mock_copy,
                                                "mock_checksums": mock_checksums,
                                                "logos_storage_dir": logos_storage_dir,
                                                "mock_commit_info": mock_commit_info,
                                            }


@pytest.fixture
def mock_git_clone_responses():
    """Fixture that provides standard git clone subprocess responses.
    
    This fixture provides the subprocess.CompletedProcess objects needed
    for testing repository cloning operations.
    """
    import subprocess
    
    return [
        subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # git clone
        subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123def456789abc123def456789abc123def\n", stderr=""),  # git rev-parse HEAD
        subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123d\n", stderr=""),  # git rev-parse --short HEAD
        subprocess.CompletedProcess(args=[], returncode=0, stdout="master\n", stderr=""),  # git rev-parse --abbrev-ref HEAD
    ]


@pytest.fixture
def mock_git_update_responses():
    """Fixture that provides standard git update subprocess responses.
    
    This fixture provides the subprocess.CompletedProcess objects needed
    for testing repository update operations.
    """
    import subprocess
    
    return [
        subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # git fetch origin
        subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # git show-ref local branch
        subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # git show-ref remote branch
        subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # git checkout
        subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # git pull
    ]


@pytest.fixture
def mock_clean_setup():
    """Fixture that provides common mocks for clean.py functions.
    
    This fixture sets up the common patches needed for testing clean_all
    and clean_build_only functions.
    """
    from unittest.mock import patch
    
    with patch("pathlib.Path.exists", return_value=True) as mock_exists:
        with patch("clean.clean_build_artifacts") as mock_clean:
            yield {
                "mock_exists": mock_exists,
                "mock_clean": mock_clean,
            }


@pytest.fixture
def mock_artifact_collection_setup():
    """Fixture that provides common mocks for artifact collection tests.
    
    This fixture sets up the common patches needed for testing collect_artifacts.
    """
    from unittest.mock import patch
    
    with patch("src.artifacts.check_artifact_compatibility", return_value=True) as mock_check:
        yield {
            "mock_check": mock_check,
        }