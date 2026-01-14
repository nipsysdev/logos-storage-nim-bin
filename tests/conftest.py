"""Shared fixtures and test configuration."""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from dataclasses import dataclass

import pytest

# Import fixtures from fixtures modules
from tests.fixtures.file_operations import (
    mock_path_exists,
    mock_file_writing,
    mock_file_reading,
    mock_directory_operations,
    mock_file_deletion,
)
from tests.fixtures.system_commands import (
    mock_run_command,
    mock_utils_run_command,
    mock_ar_commands,
    mock_sha256sum_commands,
    mock_file_commands,
)
from tests.fixtures.build import mock_build_setup
from tests.fixtures.repository import (
    mock_git_clone_responses,
    mock_git_update_responses,
)


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
    """Create sample artifact paths for testing without creating real files.
    
    This fixture returns the temp_dir path structure. Tests should use
    focused fixtures from tests/fixtures/ to mock file system operations.
    """
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


# Common utility fixtures that are used across many tests
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
def mock_clean_setup():
    """Fixture that provides common mocks for clean.py functions."""
    with patch("pathlib.Path.exists", return_value=True) as mock_exists:
        with patch("clean.clean_build_artifacts") as mock_clean:
            yield {
                "mock_exists": mock_exists,
                "mock_clean": mock_clean,
            }


@pytest.fixture
def mock_artifact_collection_setup():
    """Fixture that provides common mocks for artifact collection tests."""
    with patch("src.artifacts.check_artifact_compatibility", return_value=True) as mock_check:
        yield {
            "mock_check": mock_check,
        }