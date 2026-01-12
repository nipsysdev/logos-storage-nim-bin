"""Tests for artifact cleaning functions in artifacts.py."""

import os
from pathlib import Path
from unittest.mock import patch, Mock

import pytest

from src.artifacts import clean_build_artifacts


class TestCleanBuildArtifacts:
    """Test clean_build_artifacts function."""

    def test_clean_build_artifacts_removes_nim_cache(self):
        """Test that clean_build_artifacts removes nim cache directory."""
        logos_storage_dir = Path("/tmp/test")
        
        with patch.dict(os.environ, {"HOME": "/home/test"}):
            with patch("shutil.rmtree") as mock_rmtree:
                with patch("pathlib.Path.exists", return_value=True):
                    clean_build_artifacts(logos_storage_dir)
        
        # Verify nim cache was removed
        nim_cache_calls = [
            call for call in mock_rmtree.call_args_list
            if "nim" in str(call[0][0]) and "libstorage_d" in str(call[0][0])
        ]
        assert len(nim_cache_calls) == 1

    def test_clean_build_artifacts_removes_build_directories(self):
        """Test that clean_build_artifacts removes all build directories."""
        logos_storage_dir = Path("/tmp/test")
        
        with patch("shutil.rmtree") as mock_rmtree:
            with patch("pathlib.Path.exists", return_value=True):
                clean_build_artifacts(logos_storage_dir)
        
        # Verify build directories were removed (at least 5)
        assert mock_rmtree.call_count >= 5

    def test_clean_build_artifacts_removes_o_files(self):
        """Test that clean_build_artifacts removes .o files."""
        logos_storage_dir = Path("/tmp/test")
        
        mock_path1 = Mock()
        mock_path1.unlink = Mock()
        mock_path2 = Mock()
        mock_path2.unlink = Mock()
        
        with patch("shutil.rmtree"):
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.rglob") as mock_rglob:
                    mock_rglob.return_value = [mock_path1, mock_path2]
                    clean_build_artifacts(logos_storage_dir)
        
        # Verify .o files were unlinked
        assert mock_path1.unlink.called
        assert mock_path2.unlink.called

    def test_clean_build_artifacts_restores_gitkeep(self):
        """Test that clean_build_artifacts restores .gitkeep files."""
        logos_storage_dir = Path("/tmp/test")
        
        with patch("shutil.rmtree"):
            with patch("pathlib.Path.exists", return_value=True):
                with patch("src.artifacts.run_command") as mock_run:
                    clean_build_artifacts(logos_storage_dir)
        
        # Verify git restore was called for .gitkeep files
        gitkeep_calls = [
            call for call in mock_run.call_args_list
            if "git" in str(call[0][0]) and "restore" in str(call[0][0]) and ".gitkeep" in str(call[0][0])
        ]
        assert len(gitkeep_calls) == 1

    def test_clean_build_artifacts_skips_nonexistent_cache(self):
        """Test that clean_build_artifacts skips nonexistent cache directory."""
        logos_storage_dir = Path("/tmp/test")
        
        exists_calls = [False] + [True] * 20
        
        with patch("shutil.rmtree") as mock_rmtree:
            with patch("pathlib.Path.exists", side_effect=exists_calls):
                clean_build_artifacts(logos_storage_dir)
        
        # Verify directories were removed (cache was skipped)
        assert mock_rmtree.call_count >= 5