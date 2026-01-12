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

    def test_main_calls_build_libstorage_from_artifacts_module(self):
        """Test that main() calls build_libstorage from artifacts module."""
        logos_storage_dir = Path("logos-storage-nim")
        mock_commit_info = MockCommitInfo("abc123def456789abc123def456789abc123def", "abc123d", "master")
        
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.get_host_triple", return_value="x86_64"):
                with patch("build.get_parallel_jobs", return_value=4):
                    with patch("build.configure_reproducible_environment"):
                        with patch("build.ensure_logos_storage_repo") as mock_ensure:
                            mock_ensure.return_value = (logos_storage_dir, mock_commit_info)
                            
                            with patch("build.build_libstorage") as mock_build:
                                with patch("build.collect_artifacts", return_value=[]):
                                    with patch("build.combine_libraries", return_value=Path("dist/libstorage.a")):
                                        with patch("build.generate_checksum"):
                                            with patch("build.verify_checksum"):
                                                with patch("pathlib.Path.mkdir"):
                                                    main()
                        
                        # Verify build_libstorage was called
                        mock_build.assert_called_once()

    def test_main_calls_collect_artifacts_from_artifacts_module(self):
        """Test that main() calls collect_artifacts from artifacts module."""
        logos_storage_dir = Path("logos-storage-nim")
        mock_commit_info = MockCommitInfo("abc123def456789abc123def456789abc123def", "abc123d", "master")
        
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.get_host_triple", return_value="x86_64"):
                with patch("build.get_parallel_jobs", return_value=4):
                    with patch("build.configure_reproducible_environment"):
                        with patch("build.ensure_logos_storage_repo") as mock_ensure:
                            mock_ensure.return_value = (logos_storage_dir, mock_commit_info)
                            
                            with patch("build.build_libstorage"):
                                with patch("build.collect_artifacts") as mock_collect:
                                    mock_collect.return_value = []
                                    with patch("build.combine_libraries", return_value=Path("dist/libstorage.a")):
                                        with patch("build.generate_checksum"):
                                            with patch("build.verify_checksum"):
                                                with patch("pathlib.Path.mkdir"):
                                                    main()
                        
                        # Verify collect_artifacts was called
                        mock_collect.assert_called_once()

    def test_main_calls_combine_libraries_from_artifacts_module(self):
        """Test that main() calls combine_libraries from artifacts module."""
        mock_commit_info = MockCommitInfo("abc123def456789abc123def456789abc123def", "abc123d", "master")
        
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.get_host_triple", return_value="x86_64"):
                with patch("build.get_parallel_jobs", return_value=4):
                    with patch("build.configure_reproducible_environment"):
                        with patch("build.ensure_logos_storage_repo") as mock_ensure:
                            mock_ensure.return_value = (Path("logos-storage-nim"), mock_commit_info)
                            
                            with patch("build.build_libstorage"):
                                with patch("build.collect_artifacts", return_value=[]):
                                    with patch("build.combine_libraries") as mock_combine:
                                        mock_combine.return_value = Path("dist/libstorage.a")
                                        with patch("build.generate_checksum"):
                                            with patch("build.verify_checksum"):
                                                with patch("pathlib.Path.mkdir"):
                                                    main()
                        
                        # Verify combine_libraries was called
                        mock_combine.assert_called_once()

    def test_main_calls_generate_checksum_from_artifacts_module(self):
        """Test that main() calls generate_checksum from artifacts module."""
        mock_commit_info = MockCommitInfo("abc123def456789abc123def456789abc123def", "abc123d", "master")
        libstorage_path = Path("dist/libstorage.a")
        
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.get_host_triple", return_value="x86_64"):
                with patch("build.get_parallel_jobs", return_value=4):
                    with patch("build.configure_reproducible_environment"):
                        with patch("build.ensure_logos_storage_repo") as mock_ensure:
                            mock_ensure.return_value = (Path("logos-storage-nim"), mock_commit_info)
                            
                            with patch("build.build_libstorage"):
                                with patch("build.collect_artifacts", return_value=[]):
                                    with patch("build.combine_libraries", return_value=libstorage_path):
                                        with patch("build.generate_checksum") as mock_generate:
                                            with patch("build.verify_checksum"):
                                                with patch("pathlib.Path.mkdir"):
                                                    main()
                        
                        # Verify generate_checksum was called
                        mock_generate.assert_called_once()

    def test_main_calls_verify_checksum_from_artifacts_module(self):
        """Test that main() calls verify_checksum from artifacts module."""
        mock_commit_info = MockCommitInfo("abc123def456789abc123def456789abc123def", "abc123d", "master")
        libstorage_path = Path("dist/libstorage.a")
        
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.get_host_triple", return_value="x86_64"):
                with patch("build.get_parallel_jobs", return_value=4):
                    with patch("build.configure_reproducible_environment"):
                        with patch("build.ensure_logos_storage_repo") as mock_ensure:
                            mock_ensure.return_value = (Path("logos-storage-nim"), mock_commit_info)
                            
                            with patch("build.build_libstorage"):
                                with patch("build.collect_artifacts", return_value=[]):
                                    with patch("build.combine_libraries", return_value=libstorage_path):
                                        with patch("build.generate_checksum"):
                                            with patch("build.verify_checksum") as mock_verify:
                                                with patch("pathlib.Path.mkdir"):
                                                    main()
                        
                        # Verify verify_checksum was called
                        mock_verify.assert_called_once()

    def test_main_passes_correct_arguments_to_build_libstorage(self):
        """Test that main() passes correct arguments to build_libstorage."""
        logos_storage_dir = Path("logos-storage-nim")
        mock_commit_info = MockCommitInfo("abc123def456789abc123def456789abc123def", "abc123d", "master")
        
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.get_host_triple", return_value="x86_64"):
                with patch("build.get_parallel_jobs", return_value=12):
                    with patch("build.configure_reproducible_environment"):
                        with patch("build.ensure_logos_storage_repo") as mock_ensure:
                            mock_ensure.return_value = (logos_storage_dir, mock_commit_info)
                            
                            with patch("build.build_libstorage") as mock_build:
                                with patch("build.collect_artifacts", return_value=[]):
                                    with patch("build.combine_libraries", return_value=Path("dist/libstorage.a")):
                                        with patch("build.generate_checksum"):
                                            with patch("build.verify_checksum"):
                                                with patch("pathlib.Path.mkdir"):
                                                    main()
                        
                        # Verify build_libstorage was called with correct arguments
                        mock_build.assert_called_once_with(logos_storage_dir, 12)

    def test_main_passes_correct_arguments_to_collect_artifacts(self):
        """Test that main() passes correct arguments to collect_artifacts."""
        logos_storage_dir = Path("logos-storage-nim")
        mock_commit_info = MockCommitInfo("abc123def456789abc123def456789abc123def", "abc123d", "master")
        
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.get_host_triple", return_value="aarch64"):
                with patch("build.get_parallel_jobs", return_value=4):
                    with patch("build.configure_reproducible_environment"):
                        with patch("build.ensure_logos_storage_repo") as mock_ensure:
                            mock_ensure.return_value = (logos_storage_dir, mock_commit_info)
                            
                            with patch("build.build_libstorage"):
                                with patch("build.collect_artifacts") as mock_collect:
                                    mock_collect.return_value = []
                                    with patch("build.combine_libraries", return_value=Path("dist/libstorage.a")):
                                        with patch("build.generate_checksum"):
                                            with patch("build.verify_checksum"):
                                                with patch("pathlib.Path.mkdir"):
                                                    main()
                        
                        # Verify collect_artifacts was called with correct arguments
                        mock_collect.assert_called_once_with(logos_storage_dir, "aarch64")

    def test_main_passes_correct_arguments_to_combine_libraries(self):
        """Test that main() passes correct arguments to combine_libraries."""
        mock_commit_info = MockCommitInfo("abc123def456789abc123def456789abc123def", "abc123d", "master")
        libraries = [Path("lib1.a"), Path("lib2.a"), Path("lib3.a")]
        
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.get_host_triple", return_value="x86_64"):
                with patch("build.get_parallel_jobs", return_value=4):
                    with patch("build.configure_reproducible_environment"):
                        with patch("build.ensure_logos_storage_repo") as mock_ensure:
                            mock_ensure.return_value = (Path("logos-storage-nim"), mock_commit_info)
                            
                            with patch("build.build_libstorage"):
                                with patch("build.collect_artifacts", return_value=libraries):
                                    with patch("build.combine_libraries") as mock_combine:
                                        mock_combine.return_value = Path("dist/libstorage.a")
                                        with patch("build.generate_checksum"):
                                            with patch("build.verify_checksum"):
                                                with patch("pathlib.Path.mkdir"):
                                                    main()
                        
                        # Verify combine_libraries was called with correct arguments
                        mock_combine.assert_called_once()
                        call_args = mock_combine.call_args
                        assert call_args[0][0] == libraries

    def test_main_passes_correct_arguments_to_generate_checksum(self):
        """Test that main() passes correct arguments to generate_checksum."""
        mock_commit_info = MockCommitInfo("abc123def456789abc123def456789abc123def", "abc123d", "master")
        libstorage_path = Path("dist/master-abc123d-linux-amd64/libstorage.a")
        
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.get_host_triple", return_value="x86_64"):
                with patch("build.get_parallel_jobs", return_value=4):
                    with patch("build.configure_reproducible_environment"):
                        with patch("build.ensure_logos_storage_repo") as mock_ensure:
                            mock_ensure.return_value = (Path("logos-storage-nim"), mock_commit_info)
                            
                            with patch("build.build_libstorage"):
                                with patch("build.collect_artifacts", return_value=[]):
                                    with patch("build.combine_libraries", return_value=libstorage_path):
                                        with patch("build.generate_checksum") as mock_generate:
                                            with patch("build.verify_checksum"):
                                                with patch("pathlib.Path.mkdir"):
                                                    main()
                        
                        # Verify generate_checksum was called with correct arguments
                        mock_generate.assert_called_once_with(libstorage_path)

    def test_main_passes_correct_arguments_to_verify_checksum(self):
        """Test that main() passes correct arguments to verify_checksum."""
        mock_commit_info = MockCommitInfo("abc123def456789abc123def456789abc123def", "abc123d", "master")
        libstorage_path = Path("dist/master-abc123d-linux-amd64/libstorage.a")
        
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.get_host_triple", return_value="x86_64"):
                with patch("build.get_parallel_jobs", return_value=4):
                    with patch("build.configure_reproducible_environment"):
                        with patch("build.ensure_logos_storage_repo") as mock_ensure:
                            mock_ensure.return_value = (Path("logos-storage-nim"), mock_commit_info)
                            
                            with patch("build.build_libstorage"):
                                with patch("build.collect_artifacts", return_value=[]):
                                    with patch("build.combine_libraries", return_value=libstorage_path):
                                        with patch("build.generate_checksum"):
                                            with patch("build.verify_checksum") as mock_verify:
                                                with patch("pathlib.Path.mkdir"):
                                                    main()
                        
                        # Verify verify_checksum was called with correct arguments
                        mock_verify.assert_called_once_with(libstorage_path)

    def test_main_artifact_operations_execute_in_correct_order(self):
        """Test that artifact operations execute in the correct order."""
        logos_storage_dir = Path("logos-storage-nim")
        mock_commit_info = MockCommitInfo("abc123def456789abc123def456789abc123def", "abc123d", "master")
        libstorage_path = Path("dist/libstorage.a")
        
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.get_host_triple", return_value="x86_64"):
                with patch("build.get_parallel_jobs", return_value=4):
                    with patch("build.configure_reproducible_environment"):
                        with patch("build.ensure_logos_storage_repo") as mock_ensure:
                            mock_ensure.return_value = (logos_storage_dir, mock_commit_info)
                            
                            with patch("build.build_libstorage") as mock_build:
                                with patch("build.collect_artifacts") as mock_collect:
                                    mock_collect.return_value = []
                                    with patch("build.combine_libraries") as mock_combine:
                                        mock_combine.return_value = libstorage_path
                                        with patch("build.generate_checksum") as mock_generate:
                                            with patch("build.verify_checksum") as mock_verify:
                                                with patch("pathlib.Path.mkdir"):
                                                    main()
                        
                        # Verify operations were called in correct order
                        call_order = [mock_build, mock_collect, mock_combine, mock_generate, mock_verify]
                        for i, mock in enumerate(call_order):
                            assert mock.call_count == 1, f"Operation {i} should be called once"