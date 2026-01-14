"""Tests for library copying function in artifacts.py."""

import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.artifacts import copy_libraries


class TestCopyLibraries:
    """Test copy_libraries function."""

    @patch("shutil.copy2")
    @patch("pathlib.Path.mkdir")
    def test_copy_libraries_copies_all_libraries(self, mock_mkdir, mock_copy2, temp_dir):
        """Test that copy_libraries copies all input libraries."""
        libraries = [
            temp_dir / "lib1.a",
            temp_dir / "lib2.a",
            temp_dir / "lib3.a",
        ]
        output_dir = temp_dir / "output"
        
        result = copy_libraries(libraries, output_dir)
        
        # Verify all libraries were copied
        assert len(result) == 3
        assert mock_copy2.call_count == 3

    @patch("shutil.copy2")
    @patch("pathlib.Path.mkdir")
    def test_copy_libraries_preserves_library_names(self, mock_mkdir, mock_copy2, temp_dir):
        """Test that copy_libraries preserves library names."""
        libraries = [
            temp_dir / "libstorage.a",
            temp_dir / "libnatpmp.a",
        ]
        output_dir = temp_dir / "output"
        
        result = copy_libraries(libraries, output_dir)
        
        # Verify library names are preserved
        assert result[0].name == "libstorage.a"
        assert result[1].name == "libnatpmp.a"

    @patch("shutil.copy2")
    def test_copy_libraries_creates_output_directory(self, mock_copy2, temp_dir):
        """Test that copy_libraries creates output directory if needed."""
        libraries = [temp_dir / "lib1.a"]
        output_dir = temp_dir / "output"
        
        copy_libraries(libraries, output_dir)
        
        # Verify copy2 was called (shutil.copy2 creates parent directories automatically)
        assert mock_copy2.call_count == 1

    @patch("shutil.copy2", side_effect=FileNotFoundError("Source not found"))
    @patch("pathlib.Path.mkdir")
    def test_copy_libraries_propagates_file_not_found_error(self, mock_mkdir, mock_copy2, temp_dir):
        """Test that copy_libraries propagates FileNotFoundError."""
        libraries = [temp_dir / "lib1.a"]
        output_dir = temp_dir / "output"
        
        with pytest.raises(FileNotFoundError) as exc_info:
            copy_libraries(libraries, output_dir)
        
        assert "Source not found" in str(exc_info.value)

    @patch("shutil.copy2")
    @patch("pathlib.Path.mkdir")
    def test_copy_libraries_returns_correct_paths(self, mock_mkdir, mock_copy2, temp_dir):
        """Test that copy_libraries returns correct destination paths."""
        libraries = [
            temp_dir / "libstorage.a",
            temp_dir / "libnatpmp.a",
        ]
        output_dir = temp_dir / "output"
        
        result = copy_libraries(libraries, output_dir)
        
        # Verify returned paths are in output directory
        assert all(path.parent == output_dir for path in result)
        assert result[0] == output_dir / "libstorage.a"
        assert result[1] == output_dir / "libnatpmp.a"

    @patch("shutil.copy2")
    @patch("pathlib.Path.mkdir")
    def test_copy_libraries_handles_empty_list(self, mock_mkdir, mock_copy2, temp_dir):
        """Test that copy_libraries handles empty library list."""
        libraries = []
        output_dir = temp_dir / "output"
        
        result = copy_libraries(libraries, output_dir)
        
        # Verify empty list is handled correctly
        assert len(result) == 0
        assert mock_copy2.call_count == 0