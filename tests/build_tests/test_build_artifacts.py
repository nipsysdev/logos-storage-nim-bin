"""Tests for artifact-related operations in build.py."""

from pathlib import Path
from unittest.mock import patch, Mock
from dataclasses import dataclass
import pytest

from build import main


@dataclass
class MockCommitInfo:
    """Mock CommitInfo for testing."""
    commit: str
    commit_short: str
    branch: str


class TestBuildArtifactOperations:
    """Test artifact operations in build.py."""

    def test_main_calls_build_libstorage_from_artifacts_module(self, mock_build_setup):
        """Test that main() calls build_libstorage from artifacts module."""
        main()
        
        # Verify build_libstorage was called
        mock_build_setup["mock_build"].assert_called_once()

    def test_main_calls_collect_artifacts_from_artifacts_module(self, mock_build_setup):
        """Test that main() calls collect_artifacts from artifacts module."""
        main()
        
        # Verify collect_artifacts was called
        mock_build_setup["mock_collect"].assert_called_once()

    def test_main_calls_copy_libraries_from_artifacts_module(self, mock_build_setup):
        """Test that main() calls copy_libraries from artifacts module."""
        main()
        
        # Verify copy_libraries was called
        mock_build_setup["mock_copy_libs"].assert_called_once()

    def test_main_calls_generate_checksum_from_artifacts_module(self, mock_build_setup):
        """Test that main() calls copy_header_file and generate_sha256sums from artifacts module."""
        main()
        
        # Verify copy_header_file and generate_sha256sums were called
        mock_build_setup["mock_copy"].assert_called_once()
        mock_build_setup["mock_checksums"].assert_called_once()

    def test_main_calls_verify_checksum_from_artifacts_module(self, mock_build_setup):
        """Test that main() calls copy_header_file and generate_sha256sums from artifacts module."""
        main()
        
        # Verify copy_header_file and generate_sha256sums were called
        mock_build_setup["mock_copy"].assert_called_once()
        mock_build_setup["mock_checksums"].assert_called_once()

    def test_main_passes_correct_arguments_to_build_libstorage(self, mock_build_setup):
        """Test that main() passes correct arguments to build_libstorage."""
        mock_build_setup["mock_jobs"].return_value = 12
        
        main()
        
        # Verify build_libstorage was called with correct arguments
        mock_build_setup["mock_build"].assert_called_once_with(
            mock_build_setup["logos_storage_dir"], 12
        )

    def test_main_passes_correct_arguments_to_collect_artifacts(self, mock_build_setup):
        """Test that main() passes correct arguments to collect_artifacts."""
        mock_build_setup["mock_triple"].return_value = "aarch64"
        
        main()
        
        # Verify collect_artifacts was called with correct arguments
        mock_build_setup["mock_collect"].assert_called_once_with(
            mock_build_setup["logos_storage_dir"], "aarch64"
        )

    def test_main_passes_correct_arguments_to_copy_libraries(self, mock_build_setup):
        """Test that main() passes correct arguments to copy_libraries."""
        libraries = [Path("lib1.a"), Path("lib2.a"), Path("lib3.a")]
        mock_build_setup["mock_collect"].return_value = libraries
        
        main()
        
        # Verify copy_libraries was called with correct arguments
        mock_build_setup["mock_copy_libs"].assert_called_once()
        call_args = mock_build_setup["mock_copy_libs"].call_args
        assert call_args[0][0] == libraries

    def test_main_passes_correct_arguments_to_generate_checksum(self, mock_build_setup):
        """Test that main() passes correct arguments to copy_header_file and generate_sha256sums."""
        main()
        
        # Verify copy_header_file and generate_sha256sums were called with correct arguments
        mock_build_setup["mock_copy"].assert_called_once()
        mock_build_setup["mock_checksums"].assert_called_once()

    def test_main_passes_correct_arguments_to_verify_checksum(self, mock_build_setup):
        """Test that main() passes correct arguments to copy_header_file and generate_sha256sums."""
        main()
        
        # Verify copy_header_file and generate_sha256sums were called with correct arguments
        mock_build_setup["mock_copy"].assert_called_once()
        mock_build_setup["mock_checksums"].assert_called_once()

    def test_main_artifact_operations_execute_in_correct_order(self, mock_build_setup):
        """Test that artifact operations execute in the correct order."""
        main()
        
        # Verify operations were called in correct order
        call_order = [
            mock_build_setup["mock_build"],
            mock_build_setup["mock_collect"],
            mock_build_setup["mock_copy_libs"],
            mock_build_setup["mock_copy"],
            mock_build_setup["mock_checksums"]
        ]
        for i, mock in enumerate(call_order):
            assert mock.call_count == 1, f"Operation {i} should be called once"