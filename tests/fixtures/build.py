"""Build-related fixtures."""

import pytest
from unittest.mock import patch
from pathlib import Path
from src.repository import CommitInfo


@pytest.fixture
def mock_build_setup():
    """Fixture that provides common mocks for build.py main() function."""
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
                                with patch("build.copy_libraries", return_value=[]) as mock_copy_libs:
                                    with patch("build.copy_header_file") as mock_copy:
                                        with patch("build.generate_sha256sums") as mock_checksums:
                                            with patch("pathlib.Path.mkdir") as mock_mkdir:
                                                yield {
                                                    "mock_platform": mock_platform,
                                                    "mock_config": mock_config,
                                                    "mock_repo": mock_repo,
                                                    "mock_jobs": mock_jobs,
                                                    "mock_build": mock_build,
                                                    "mock_triple": mock_triple,
                                                    "mock_collect": mock_collect,
                                                    "mock_copy_libs": mock_copy_libs,
                                                    "mock_copy": mock_copy,
                                                    "mock_checksums": mock_checksums,
                                                    "mock_mkdir": mock_mkdir,
                                                    "logos_storage_dir": logos_storage_dir,
                                                    "mock_commit_info": mock_commit_info,
                                                }