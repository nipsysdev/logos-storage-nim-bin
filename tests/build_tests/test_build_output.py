"""Tests for build output and error handling in build.py."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from build import main
from src.repository import CommitInfo


class TestMainOutput:
    """Test main function output formatting and artifact naming."""

    def test_main_creates_correct_artifact_name(self, mock_build_setup):
        """Test that main() creates correct artifact directory name with branch, commit, and platform."""
        mock_build_setup["mock_platform"].return_value = "linux-arm64"
        mock_build_setup["mock_triple"].return_value = "aarch64"
        mock_build_setup["mock_repo"].return_value = (
            Path("logos-storage-nim"),
            CommitInfo("abc123def456", "abc123d", "develop")
        )
        
        main()
        
        call_args = mock_build_setup["mock_copy_libs"].call_args[0]
        dist_dir = call_args[1]
        assert "develop" in str(dist_dir)
        assert "abc123d" in str(dist_dir)
        assert "linux-arm64" in str(dist_dir)

    def test_main_prints_build_info(self, mock_build_setup, capsys):
        """Test that main() prints build information to stdout."""
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

    def test_main_exits_on_success(self, mock_build_setup):
        """Test that main() completes successfully without raising exceptions."""
        main()