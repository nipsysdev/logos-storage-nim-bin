"""Focused file system operation fixtures."""

import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_path_exists():
    """Mock Path.exists() for testing."""
    with patch("pathlib.Path.exists") as mock:
        mock.return_value = True
        yield mock


@pytest.fixture
def mock_file_writing():
    """Mock file writing operations (write_bytes, write_text)."""
    with patch("pathlib.Path.write_bytes") as mock_bytes:
        with patch("pathlib.Path.write_text") as mock_text:
            yield {
                "write_bytes": mock_bytes,
                "write_text": mock_text,
            }


@pytest.fixture
def mock_file_reading():
    """Mock file reading operations (read_text, stat)."""
    with patch("pathlib.Path.read_text") as mock_read:
        with patch("pathlib.Path.stat") as mock_stat:
            # Configure stat mock
            mock_stat_result = MagicMock()
            mock_stat_result.st_size = 1000
            mock_stat.return_value = mock_stat_result
            yield {
                "read_text": mock_read,
                "stat": mock_stat,
            }


@pytest.fixture
def mock_directory_operations():
    """Mock directory operations (mkdir, iterdir, is_file)."""
    with patch("pathlib.Path.mkdir") as mock_mkdir:
        with patch("pathlib.Path.iterdir") as mock_iterdir:
            with patch("pathlib.Path.is_file") as mock_is_file:
                mock_iterdir.return_value = []
                mock_is_file.return_value = True
                yield {
                    "mkdir": mock_mkdir,
                    "iterdir": mock_iterdir,
                    "is_file": mock_is_file,
                }


@pytest.fixture
def mock_file_deletion():
    """Mock file deletion operations (unlink, rmtree)."""
    with patch("pathlib.Path.unlink") as mock_unlink:
        with patch("shutil.rmtree") as mock_rmtree:
            yield {
                "unlink": mock_unlink,
                "rmtree": mock_rmtree,
            }