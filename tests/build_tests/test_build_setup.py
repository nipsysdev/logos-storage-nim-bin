"""Tests for build setup in build.py."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from build import main
from src.repository import CommitInfo


class TestMainSetup:
    """Test main function setup and initialization."""

    def test_main_gets_platform_identifier(self):
        """Test that main() calls get_platform_identifier()."""
        with patch("build.get_platform_identifier", return_value="linux-amd64") as mock_platform:
            with patch("build.ensure_logos_storage_repo") as mock_repo:
                mock_repo.return_value = (Path("logos-storage-nim"), CommitInfo("abc123", "abc123", "master"))
                with patch("build.get_parallel_jobs", return_value=4):
                    with patch("build.get_host_triple", return_value="x86_64"):
                        with patch("build.configure_reproducible_environment"):
                            with patch("build.build_libstorage"):
                                with patch("build.collect_artifacts", return_value=[]):
                                    with patch("build.combine_libraries", return_value=Path("dist/libstorage.a")):
                                        with patch("build.generate_checksum"):
                                            with patch("build.verify_checksum"):
                                                main()
        
        mock_platform.assert_called_once()

    def test_main_gets_branch_from_environment(self):
        """Test that main() uses BRANCH environment variable when set."""
        with patch.dict(os.environ, {"BRANCH": "develop"}):
            with patch("build.get_platform_identifier", return_value="linux-amd64"):
                with patch("build.ensure_logos_storage_repo") as mock_repo:
                    mock_repo.return_value = (Path("logos-storage-nim"), CommitInfo("abc123", "abc123", "develop"))
                    with patch("build.get_parallel_jobs", return_value=4):
                        with patch("build.get_host_triple", return_value="x86_64"):
                            with patch("build.configure_reproducible_environment"):
                                with patch("build.build_libstorage"):
                                    with patch("build.collect_artifacts", return_value=[]):
                                        with patch("build.combine_libraries", return_value=Path("dist/libstorage.a")):
                                            with patch("build.generate_checksum"):
                                                with patch("build.verify_checksum"):
                                                    main()
                    
                    mock_repo.assert_called_once_with("develop")

    def test_main_uses_default_branch_when_not_set(self):
        """Test that main() uses 'master' as default branch when BRANCH is not set."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("BRANCH", None)
            
            with patch("build.get_platform_identifier", return_value="linux-amd64"):
                with patch("build.ensure_logos_storage_repo") as mock_repo:
                    mock_repo.return_value = (Path("logos-storage-nim"), CommitInfo("abc123", "abc123", "master"))
                    with patch("build.get_parallel_jobs", return_value=4):
                        with patch("build.get_host_triple", return_value="x86_64"):
                            with patch("build.configure_reproducible_environment"):
                                with patch("build.build_libstorage"):
                                    with patch("build.collect_artifacts", return_value=[]):
                                        with patch("build.combine_libraries", return_value=Path("dist/libstorage.a")):
                                            with patch("build.generate_checksum"):
                                                with patch("build.verify_checksum"):
                                                    main()
                    
                    mock_repo.assert_called_once_with("master")

    def test_main_configures_reproducible_environment(self):
        """Test that main() calls configure_reproducible_environment()."""
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.ensure_logos_storage_repo") as mock_repo:
                mock_repo.return_value = (Path("logos-storage-nim"), CommitInfo("abc123", "abc123", "master"))
                with patch("build.get_parallel_jobs", return_value=4):
                    with patch("build.get_host_triple", return_value="x86_64"):
                        with patch("build.configure_reproducible_environment") as mock_config:
                            with patch("build.build_libstorage"):
                                with patch("build.collect_artifacts", return_value=[]):
                                    with patch("build.combine_libraries", return_value=Path("dist/libstorage.a")):
                                        with patch("build.generate_checksum"):
                                            with patch("build.verify_checksum"):
                                                main()
                    
                    mock_config.assert_called_once()

    def test_main_ensures_repository(self):
        """Test that main() calls ensure_logos_storage_repo()."""
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.ensure_logos_storage_repo") as mock_repo:
                mock_repo.return_value = (Path("logos-storage-nim"), CommitInfo("abc123", "abc123", "master"))
                with patch("build.get_parallel_jobs", return_value=4):
                    with patch("build.get_host_triple", return_value="x86_64"):
                        with patch("build.configure_reproducible_environment"):
                            with patch("build.build_libstorage"):
                                with patch("build.collect_artifacts", return_value=[]):
                                    with patch("build.combine_libraries", return_value=Path("dist/libstorage.a")):
                                        with patch("build.generate_checksum"):
                                            with patch("build.verify_checksum"):
                                                main()
                    
                    mock_repo.assert_called_once()