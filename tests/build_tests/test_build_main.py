"""Tests for build.py main() function - orchestration tests.

These tests verify that main() calls the correct functions with the correct
arguments in the correct order. They do NOT test the implementation details
of the called functions.
"""

import os
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from dataclasses import dataclass

import pytest

from build import main


@dataclass
class MockCommitInfo:
    """Mock CommitInfo for testing."""
    commit: str
    commit_short: str
    branch: str


class TestMainOrchestration:
    """Test main() function orchestration behavior."""

    def test_main_calls_get_platform_identifier(self, mock_build_setup):
        """Test that main() calls get_platform_identifier()."""
        main()
        
        mock_build_setup["mock_platform"].assert_called_once()

    def test_main_calls_configure_reproducible_environment(self, mock_build_setup):
        """Test that main() calls configure_reproducible_environment()."""
        main()
        
        mock_build_setup["mock_config"].assert_called_once()

    def test_main_calls_ensure_logos_storage_repo_with_default_branch(self, mock_build_setup):
        """Test that main() calls ensure_logos_storage_repo() with default branch."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("BRANCH", None)
            os.environ.pop("COMMIT", None)
            main()
        
        mock_build_setup["mock_repo"].assert_called_once_with("master", None)

    def test_main_calls_ensure_logos_storage_repo_with_custom_branch(self, mock_build_setup):
        """Test that main() calls ensure_logos_storage_repo() with custom BRANCH env var."""
        with patch.dict(os.environ, {"BRANCH": "develop"}, clear=False):
            os.environ.pop("COMMIT", None)
            main()
        
        mock_build_setup["mock_repo"].assert_called_once_with("develop", None)

    def test_main_calls_get_parallel_jobs(self, mock_build_setup):
        """Test that main() calls get_parallel_jobs()."""
        main()
        
        mock_build_setup["mock_jobs"].assert_called_once()

    def test_main_calls_build_libstorage_with_correct_arguments(self, mock_build_setup):
        """Test that main() calls build_libstorage() with correct directory and job count."""
        main()
        
        mock_build_setup["mock_build"].assert_called_once_with(
            mock_build_setup["logos_storage_dir"], 4
        )

    def test_main_calls_get_host_triple(self, mock_build_setup):
        """Test that main() calls get_host_triple()."""
        main()
        
        mock_build_setup["mock_triple"].assert_called_once()

    def test_main_calls_collect_artifacts_with_correct_arguments(self, mock_build_setup):
        """Test that main() calls collect_artifacts() with correct directory and host triple."""
        main()
        
        mock_build_setup["mock_collect"].assert_called_once_with(
            mock_build_setup["logos_storage_dir"], "x86_64"
        )

    def test_main_calls_copy_libraries_with_correct_arguments(self, mock_build_setup):
        """Test that main() calls copy_libraries() with correct libraries and output path."""
        libraries = [Path("lib1.a"), Path("lib2.a")]
        mock_build_setup["mock_collect"].return_value = libraries
        
        main()
        
        # Verify the output directory path is correct
        expected_dist_dir = Path("dist") / "master-abc123d-linux-amd64"
        mock_build_setup["mock_copy_libs"].assert_called_once()
        call_args = mock_build_setup["mock_copy_libs"].call_args
        assert call_args[0][0] == libraries
        assert call_args[0][1] == expected_dist_dir

    def test_main_calls_generate_checksum_with_correct_path(self, mock_build_setup):
        """Test that main() calls copy_header_file and generate_sha256sums with correct paths."""
        main()
        
        mock_build_setup["mock_copy"].assert_called_once()
        mock_build_setup["mock_checksums"].assert_called_once()

    def test_main_calls_verify_checksum_with_correct_path(self, mock_build_setup):
        """Test that main() calls copy_header_file and generate_sha256sums with correct paths."""
        main()
        
        mock_build_setup["mock_copy"].assert_called_once()
        mock_build_setup["mock_checksums"].assert_called_once()

    def test_main_calls_functions_in_correct_order(self, mock_build_setup):
        """Test that main() calls functions in the correct order."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("BRANCH", None)
            os.environ.pop("COMMIT", None)
            main()
        
        # Verify call order
        expected_calls = [
            call.get_platform_identifier(),
            call.configure_reproducible_environment(),
            call.ensure_logos_storage_repo("master", None),
            call.get_parallel_jobs(),
            call.build_libstorage(mock_build_setup["logos_storage_dir"], 4),
            call.get_host_triple(),
            call.collect_artifacts(mock_build_setup["logos_storage_dir"], "x86_64"),
            call.copy_libraries([], Path("dist/master-abc123d-linux-amd64")),
            call.copy_header_file(mock_build_setup["logos_storage_dir"], Path("dist/master-abc123d-linux-amd64")),
            call.generate_sha256sums(Path("dist/master-abc123d-linux-amd64")),
        ]
        
        # Check that all mocks were called in the expected order
        assert mock_build_setup["mock_platform"].call_args_list == [expected_calls[0]]
        assert mock_build_setup["mock_config"].call_args_list == [expected_calls[1]]
        assert mock_build_setup["mock_repo"].call_args_list == [expected_calls[2]]
        assert mock_build_setup["mock_jobs"].call_args_list == [expected_calls[3]]
        assert mock_build_setup["mock_build"].call_args_list == [expected_calls[4]]
        assert mock_build_setup["mock_triple"].call_args_list == [expected_calls[5]]
        assert mock_build_setup["mock_collect"].call_args_list == [expected_calls[6]]
        assert mock_build_setup["mock_copy_libs"].call_args_list == [expected_calls[7]]
        assert mock_build_setup["mock_copy"].call_args_list == [expected_calls[8]]
        assert mock_build_setup["mock_checksums"].call_args_list == [expected_calls[9]]

    def test_main_propagates_exception_from_get_platform_identifier(self, mock_build_setup):
        """Test that main() propagates exceptions from get_platform_identifier()."""
        mock_build_setup["mock_platform"].side_effect = RuntimeError("Platform error")
        
        with pytest.raises(RuntimeError) as exc_info:
            main()
        
        assert str(exc_info.value) == "Platform error"

    def test_main_propagates_exception_from_configure_reproducible_environment(self, mock_build_setup):
        """Test that main() propagates exceptions from configure_reproducible_environment()."""
        mock_build_setup["mock_config"].side_effect = RuntimeError("Config error")
        
        with pytest.raises(RuntimeError) as exc_info:
            main()
        
        assert str(exc_info.value) == "Config error"

    def test_main_propagates_exception_from_ensure_logos_storage_repo(self, mock_build_setup):
        """Test that main() propagates exceptions from ensure_logos_storage_repo()."""
        mock_build_setup["mock_repo"].side_effect = RuntimeError("Repo error")
        
        with pytest.raises(RuntimeError) as exc_info:
            main()
        
        assert str(exc_info.value) == "Repo error"

    def test_main_propagates_exception_from_build_libstorage(self, mock_build_setup):
        """Test that main() propagates exceptions from build_libstorage()."""
        mock_build_setup["mock_build"].side_effect = RuntimeError("Build error")
        
        with pytest.raises(RuntimeError) as exc_info:
            main()
        
        assert str(exc_info.value) == "Build error"

    def test_main_propagates_exception_from_collect_artifacts(self, mock_build_setup):
        """Test that main() propagates exceptions from collect_artifacts()."""
        mock_build_setup["mock_collect"].side_effect = RuntimeError("Collect error")
        
        with pytest.raises(RuntimeError) as exc_info:
            main()
        
        assert str(exc_info.value) == "Collect error"

    def test_main_propagates_exception_from_copy_libraries(self, mock_build_setup):
        """Test that main() propagates exceptions from copy_libraries()."""
        mock_build_setup["mock_copy_libs"].side_effect = RuntimeError("Copy error")
        
        with pytest.raises(RuntimeError) as exc_info:
            main()
        
        assert str(exc_info.value) == "Copy error"

    def test_main_propagates_exception_from_generate_checksum(self, mock_build_setup):
        """Test that main() propagates exceptions from copy_header_file()."""
        mock_build_setup["mock_copy"].side_effect = RuntimeError("Copy error")
        
        with pytest.raises(RuntimeError) as exc_info:
            main()
        
        assert str(exc_info.value) == "Copy error"

    def test_main_propagates_exception_from_verify_checksum(self, mock_build_setup):
        """Test that main() propagates exceptions from generate_sha256sums()."""
        mock_build_setup["mock_checksums"].side_effect = RuntimeError("Checksums error")
        
        with pytest.raises(RuntimeError) as exc_info:
            main()
        
        assert str(exc_info.value) == "Checksums error"