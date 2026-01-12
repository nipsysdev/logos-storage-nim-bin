"""Tests for build output and error handling in build.py."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from build import main
from src.repository import CommitInfo


class TestMainOutput:
    """Test main function output formatting and artifact naming."""

    def test_main_creates_correct_artifact_name(self):
        """Test that main() creates correct artifact directory name with branch, commit, and platform."""
        with patch("build.get_platform_identifier", return_value="linux-arm64"):
            with patch("build.ensure_logos_storage_repo") as mock_repo:
                mock_repo.return_value = (Path("logos-storage-nim"), CommitInfo("abc123def456", "abc123d", "develop"))
                with patch("build.get_parallel_jobs", return_value=4):
                    with patch("build.get_host_triple", return_value="aarch64"):
                        with patch("build.configure_reproducible_environment"):
                            with patch("build.build_libstorage"):
                                with patch("build.collect_artifacts", return_value=[]):
                                    with patch("build.combine_libraries") as mock_combine:
                                        mock_combine.return_value = Path("dist/libstorage.a")
                                        with patch("build.generate_checksum"):
                                            with patch("build.verify_checksum"):
                                                main()
                    
                    call_args = mock_combine.call_args[0]
                    dist_dir = call_args[1]
                    assert "develop" in str(dist_dir)
                    assert "abc123d" in str(dist_dir)
                    assert "linux-arm64" in str(dist_dir)

    def test_main_prints_build_info(self, capsys):
        """Test that main() prints build information to stdout."""
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.ensure_logos_storage_repo") as mock_repo:
                mock_repo.return_value = (Path("logos-storage-nim"), CommitInfo("abc123def456", "abc123d", "master"))
                with patch("build.get_parallel_jobs", return_value=4):
                    with patch("build.get_host_triple", return_value="x86_64"):
                        with patch("build.configure_reproducible_environment"):
                            with patch("build.build_libstorage"):
                                with patch("build.collect_artifacts", return_value=[]):
                                    with patch("build.combine_libraries", return_value=Path("dist/libstorage.a")):
                                        with patch("build.generate_checksum"):
                                            with patch("build.verify_checksum"):
                                                main()
        
        captured = capsys.readouterr()
        assert "Building logos-storage-nim" in captured.out
        assert "Platform:" in captured.out
        assert "Branch:" in captured.out
        assert "Commit:" in captured.out
        assert "Build completed successfully" in captured.out


class TestMainErrorHandling:
    """Test main function error handling and exception propagation."""

    def test_main_propagates_exception(self):
        """Test that main() propagates exceptions (doesn't catch them)."""
        with patch("build.get_platform_identifier", side_effect=Exception("Test error")):
            with pytest.raises(Exception) as exc_info:
                main()
        
        assert str(exc_info.value) == "Test error"

    def test_main_exits_on_success(self):
        """Test that main() completes successfully without raising exceptions."""
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