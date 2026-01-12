"""Tests for clean.py module."""

from pathlib import Path
from unittest.mock import patch, Mock
import sys

import pytest

from clean import clean_all, clean_build_only, main


class TestCleanAll:
    """Test clean_all function."""

    def test_clean_all_removes_dist_directory(self, mock_shutil_rmtree):
        """Test that clean_all removes the dist directory."""
        with patch("pathlib.Path.exists", return_value=True):
            clean_all()
        
        # Verify dist directory was removed
        dist_calls = [call for call in mock_shutil_rmtree.call_args_list if "dist" in str(call[0][0])]
        assert len(dist_calls) == 1

    def test_clean_all_removes_logos_storage_directory(self, mock_shutil_rmtree):
        """Test that clean_all removes the logos-storage-nim directory."""
        with patch("pathlib.Path.exists", return_value=True):
            clean_all()
        
        # Verify logos-storage-nim directory was removed (exact match)
        repo_calls = [call for call in mock_shutil_rmtree.call_args_list if call[0][0] == Path("logos-storage-nim")]
        assert len(repo_calls) == 1

    def test_clean_all_calls_clean_build_artifacts(self, mock_shutil_rmtree):
        """Test that clean_all calls clean_build_artifacts."""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("clean.clean_build_artifacts") as mock_clean:
                clean_all()
        
        mock_clean.assert_called_once()

    def test_clean_all_skips_build_artifacts_when_repo_missing(self, mock_shutil_rmtree):
        """Test that clean_all skips clean_build_artifacts when repo directory doesn't exist."""
        exists_calls = [False, True, True]
        
        with patch("pathlib.Path.exists", side_effect=exists_calls):
            with patch("clean.clean_build_artifacts") as mock_clean:
                clean_all()
        
        mock_clean.assert_not_called()

    def test_clean_all_skips_dist_when_missing(self, mock_shutil_rmtree):
        """Test that clean_all skips dist directory when it doesn't exist."""
        exists_calls = [True, False, True]
        
        with patch("pathlib.Path.exists", side_effect=exists_calls):
            with patch("clean.clean_build_artifacts"):
                clean_all()
        
        # Verify only logos-storage-nim was removed
        assert mock_shutil_rmtree.call_count == 1

    def test_clean_all_skips_logos_storage_when_missing(self, mock_shutil_rmtree):
        """Test that clean_all skips logos-storage-nim directory when it doesn't exist."""
        exists_calls = [True, True, False]
        
        with patch("pathlib.Path.exists", side_effect=exists_calls):
            with patch("clean.clean_build_artifacts"):
                clean_all()
        
        # Verify only dist was removed
        assert mock_shutil_rmtree.call_count == 1

    def test_clean_all_removes_all_directories(self, mock_shutil_rmtree):
        """Test that clean_all removes both dist and logos-storage-nim directories."""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("clean.clean_build_artifacts"):
                clean_all()
        
        # Verify both directories were removed
        assert mock_shutil_rmtree.call_count == 2


class TestCleanBuildOnly:
    """Test clean_build_only function."""

    def test_clean_build_only_calls_clean_build_artifacts(self):
        """Test that clean_build_only calls clean_build_artifacts."""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("clean.clean_build_artifacts") as mock_clean:
                clean_build_only()
        
        mock_clean.assert_called_once()

    def test_clean_build_only_skips_when_repo_missing(self, capsys):
        """Test that clean_build_only skips gracefully when repo directory doesn't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            with patch("clean.clean_build_artifacts") as mock_clean:
                clean_build_only()
        
        # Verify clean_build_artifacts was not called
        mock_clean.assert_not_called()
        
        # Verify appropriate message was printed
        captured = capsys.readouterr()
        assert "logos-storage-nim directory not found, skipping clean" in captured.out

    def test_clean_build_only_passes_correct_directory(self):
        """Test that clean_build_only passes correct directory to clean_build_artifacts."""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("clean.clean_build_artifacts") as mock_clean:
                clean_build_only()
        
        call_arg = mock_clean.call_args[0][0]
        assert call_arg == Path("logos-storage-nim")


class TestMain:
    """Test main function."""

    def test_main_calls_clean_build_only_by_default(self):
        """Test that main() calls clean_build_only when no arguments provided."""
        with patch("sys.argv", ["clean.py"]):
            with patch("clean.clean_build_only") as mock_clean:
                main()
        
        mock_clean.assert_called_once()

    def test_main_calls_clean_all_with_flag(self):
        """Test that main() calls clean_all when --all flag is provided."""
        with patch("sys.argv", ["clean.py", "--all"]):
            with patch("clean.clean_all") as mock_clean:
                main()
        
        mock_clean.assert_called_once()

    def test_main_handles_exception(self, capsys):
        """Test that main() propagates exceptions from clean functions."""
        with patch("sys.argv", ["clean.py"]):
            with patch("clean.clean_build_only", side_effect=Exception("Test error")):
                with pytest.raises(Exception) as exc_info:
                    main()
        
        assert str(exc_info.value) == "Test error"

    def test_main_exits_on_success(self):
        """Test that main() completes successfully without raising exceptions."""
        with patch("sys.argv", ["clean.py"]):
            with patch("clean.clean_build_only"):
                main()  # Should complete without raising SystemExit

    def test_main_exits_on_error(self, capsys):
        """Test that main() propagates RuntimeError from clean functions."""
        with patch("sys.argv", ["clean.py"]):
            with patch("clean.clean_build_only", side_effect=RuntimeError("Runtime error")):
                with pytest.raises(RuntimeError) as exc_info:
                    main()
        
        assert str(exc_info.value) == "Runtime error"