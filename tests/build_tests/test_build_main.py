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

    def test_main_calls_get_platform_identifier(self):
        """Test that main() calls get_platform_identifier()."""
        with patch("build.get_platform_identifier", return_value="linux-amd64") as mock_platform:
            with patch("build.configure_reproducible_environment"):
                with patch("build.ensure_logos_storage_repo") as mock_repo:
                    mock_repo.return_value = (Path("logos-storage-nim"), MockCommitInfo("abc123", "abc123d", "master"))
                    with patch("build.get_parallel_jobs", return_value=4):
                        with patch("build.build_libstorage"):
                            with patch("build.get_host_triple", return_value="x86_64"):
                                with patch("build.collect_artifacts", return_value=[]):
                                    with patch("build.combine_libraries", return_value=Path("dist/libstorage.a")):
                                        with patch("build.generate_checksum"):
                                            with patch("build.verify_checksum"):
                                                main()
        
        mock_platform.assert_called_once()

    def test_main_calls_configure_reproducible_environment(self):
        """Test that main() calls configure_reproducible_environment()."""
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.configure_reproducible_environment") as mock_config:
                with patch("build.ensure_logos_storage_repo") as mock_repo:
                    mock_repo.return_value = (Path("logos-storage-nim"), MockCommitInfo("abc123", "abc123d", "master"))
                    with patch("build.get_parallel_jobs", return_value=4):
                        with patch("build.build_libstorage"):
                            with patch("build.get_host_triple", return_value="x86_64"):
                                with patch("build.collect_artifacts", return_value=[]):
                                    with patch("build.combine_libraries", return_value=Path("dist/libstorage.a")):
                                        with patch("build.generate_checksum"):
                                            with patch("build.verify_checksum"):
                                                main()
        
        mock_config.assert_called_once()

    def test_main_calls_ensure_logos_storage_repo_with_default_branch(self):
        """Test that main() calls ensure_logos_storage_repo() with default branch."""
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.configure_reproducible_environment"):
                with patch("build.ensure_logos_storage_repo") as mock_repo:
                    mock_repo.return_value = (Path("logos-storage-nim"), MockCommitInfo("abc123", "abc123d", "master"))
                    with patch("build.get_parallel_jobs", return_value=4):
                        with patch("build.build_libstorage"):
                            with patch("build.get_host_triple", return_value="x86_64"):
                                with patch("build.collect_artifacts", return_value=[]):
                                    with patch("build.combine_libraries", return_value=Path("dist/libstorage.a")):
                                        with patch("build.generate_checksum"):
                                            with patch("build.verify_checksum"):
                                                main()
        
        mock_repo.assert_called_once_with("master")

    def test_main_calls_ensure_logos_storage_repo_with_custom_branch(self):
        """Test that main() calls ensure_logos_storage_repo() with custom BRANCH env var."""
        with patch.dict(os.environ, {"BRANCH": "develop"}):
            with patch("build.get_platform_identifier", return_value="linux-amd64"):
                with patch("build.configure_reproducible_environment"):
                    with patch("build.ensure_logos_storage_repo") as mock_repo:
                        mock_repo.return_value = (Path("logos-storage-nim"), MockCommitInfo("abc123", "abc123d", "develop"))
                        with patch("build.get_parallel_jobs", return_value=4):
                            with patch("build.build_libstorage"):
                                with patch("build.get_host_triple", return_value="x86_64"):
                                    with patch("build.collect_artifacts", return_value=[]):
                                        with patch("build.combine_libraries", return_value=Path("dist/libstorage.a")):
                                            with patch("build.generate_checksum"):
                                                with patch("build.verify_checksum"):
                                                    main()
            
            mock_repo.assert_called_once_with("develop")

    def test_main_calls_get_parallel_jobs(self):
        """Test that main() calls get_parallel_jobs()."""
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.configure_reproducible_environment"):
                with patch("build.ensure_logos_storage_repo") as mock_repo:
                    mock_repo.return_value = (Path("logos-storage-nim"), MockCommitInfo("abc123", "abc123d", "master"))
                    with patch("build.get_parallel_jobs", return_value=8) as mock_jobs:
                        with patch("build.build_libstorage"):
                            with patch("build.get_host_triple", return_value="x86_64"):
                                with patch("build.collect_artifacts", return_value=[]):
                                    with patch("build.combine_libraries", return_value=Path("dist/libstorage.a")):
                                        with patch("build.generate_checksum"):
                                            with patch("build.verify_checksum"):
                                                main()
        
        mock_jobs.assert_called_once()

    def test_main_calls_build_libstorage_with_correct_arguments(self):
        """Test that main() calls build_libstorage() with correct directory and job count."""
        logos_storage_dir = Path("logos-storage-nim")
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.configure_reproducible_environment"):
                with patch("build.ensure_logos_storage_repo") as mock_repo:
                    mock_repo.return_value = (logos_storage_dir, MockCommitInfo("abc123", "abc123d", "master"))
                    with patch("build.get_parallel_jobs", return_value=4):
                        with patch("build.build_libstorage") as mock_build:
                            with patch("build.get_host_triple", return_value="x86_64"):
                                with patch("build.collect_artifacts", return_value=[]):
                                    with patch("build.combine_libraries", return_value=Path("dist/libstorage.a")):
                                        with patch("build.generate_checksum"):
                                            with patch("build.verify_checksum"):
                                                main()
        
        mock_build.assert_called_once_with(logos_storage_dir, 4)

    def test_main_calls_get_host_triple(self):
        """Test that main() calls get_host_triple()."""
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.configure_reproducible_environment"):
                with patch("build.ensure_logos_storage_repo") as mock_repo:
                    mock_repo.return_value = (Path("logos-storage-nim"), MockCommitInfo("abc123", "abc123d", "master"))
                    with patch("build.get_parallel_jobs", return_value=4):
                        with patch("build.build_libstorage"):
                            with patch("build.get_host_triple", return_value="x86_64") as mock_triple:
                                with patch("build.collect_artifacts", return_value=[]):
                                    with patch("build.combine_libraries", return_value=Path("dist/libstorage.a")):
                                        with patch("build.generate_checksum"):
                                            with patch("build.verify_checksum"):
                                                main()
        
        mock_triple.assert_called_once()

    def test_main_calls_collect_artifacts_with_correct_arguments(self):
        """Test that main() calls collect_artifacts() with correct directory and host triple."""
        logos_storage_dir = Path("logos-storage-nim")
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.configure_reproducible_environment"):
                with patch("build.ensure_logos_storage_repo") as mock_repo:
                    mock_repo.return_value = (logos_storage_dir, MockCommitInfo("abc123", "abc123d", "master"))
                    with patch("build.get_parallel_jobs", return_value=4):
                        with patch("build.build_libstorage"):
                            with patch("build.get_host_triple", return_value="x86_64"):
                                with patch("build.collect_artifacts", return_value=[]) as mock_collect:
                                    with patch("build.combine_libraries", return_value=Path("dist/libstorage.a")):
                                        with patch("build.generate_checksum"):
                                            with patch("build.verify_checksum"):
                                                main()
        
        mock_collect.assert_called_once_with(logos_storage_dir, "x86_64")

    def test_main_calls_combine_libraries_with_correct_arguments(self):
        """Test that main() calls combine_libraries() with correct libraries and output path."""
        logos_storage_dir = Path("logos-storage-nim")
        libraries = [Path("lib1.a"), Path("lib2.a")]
        commit_info = MockCommitInfo("abc123def456789abc123def456789abc123def", "abc123d", "master")
        
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.configure_reproducible_environment"):
                with patch("build.ensure_logos_storage_repo") as mock_repo:
                    mock_repo.return_value = (logos_storage_dir, commit_info)
                    with patch("build.get_parallel_jobs", return_value=4):
                        with patch("build.build_libstorage"):
                            with patch("build.get_host_triple", return_value="x86_64"):
                                with patch("build.collect_artifacts", return_value=libraries):
                                    with patch("build.combine_libraries", return_value=Path("dist/libstorage.a")) as mock_combine:
                                        with patch("build.generate_checksum"):
                                            with patch("build.verify_checksum"):
                                                main()
        
        # Verify the output directory path is correct
        expected_dist_dir = Path("dist") / "master-abc123d-linux-amd64"
        mock_combine.assert_called_once()
        call_args = mock_combine.call_args
        assert call_args[0][0] == libraries
        assert call_args[0][1] == expected_dist_dir

    def test_main_calls_generate_checksum_with_correct_path(self):
        """Test that main() calls generate_checksum() with correct library path."""
        libstorage_path = Path("dist/master-abc123d-linux-amd64/libstorage.a")
        logos_storage_dir = Path("logos-storage-nim")
        commit_info = MockCommitInfo("abc123def456789abc123def456789abc123def", "abc123d", "master")
        
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.configure_reproducible_environment"):
                with patch("build.ensure_logos_storage_repo") as mock_repo:
                    mock_repo.return_value = (logos_storage_dir, commit_info)
                    with patch("build.get_parallel_jobs", return_value=4):
                        with patch("build.build_libstorage"):
                            with patch("build.get_host_triple", return_value="x86_64"):
                                with patch("build.collect_artifacts", return_value=[]):
                                    with patch("build.combine_libraries", return_value=libstorage_path):
                                        with patch("build.generate_checksum") as mock_checksum:
                                            with patch("build.verify_checksum"):
                                                main()
        
        mock_checksum.assert_called_once_with(libstorage_path)

    def test_main_calls_verify_checksum_with_correct_path(self):
        """Test that main() calls verify_checksum() with correct library path."""
        libstorage_path = Path("dist/master-abc123d-linux-amd64/libstorage.a")
        logos_storage_dir = Path("logos-storage-nim")
        commit_info = MockCommitInfo("abc123def456789abc123def456789abc123def", "abc123d", "master")
        
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.configure_reproducible_environment"):
                with patch("build.ensure_logos_storage_repo") as mock_repo:
                    mock_repo.return_value = (logos_storage_dir, commit_info)
                    with patch("build.get_parallel_jobs", return_value=4):
                        with patch("build.build_libstorage"):
                            with patch("build.get_host_triple", return_value="x86_64"):
                                with patch("build.collect_artifacts", return_value=[]):
                                    with patch("build.combine_libraries", return_value=libstorage_path):
                                        with patch("build.generate_checksum"):
                                            with patch("build.verify_checksum") as mock_verify:
                                                main()
        
        mock_verify.assert_called_once_with(libstorage_path)

    def test_main_calls_functions_in_correct_order(self):
        """Test that main() calls functions in the correct order."""
        logos_storage_dir = Path("logos-storage-nim")
        commit_info = MockCommitInfo("abc123def456789abc123def456789abc123def", "abc123d", "master")
        libstorage_path = Path("dist/master-abc123d-linux-amd64/libstorage.a")
        
        with patch("build.get_platform_identifier", return_value="linux-amd64") as mock_platform:
            with patch("build.configure_reproducible_environment") as mock_config:
                with patch("build.ensure_logos_storage_repo") as mock_repo:
                    mock_repo.return_value = (logos_storage_dir, commit_info)
                    with patch("build.get_parallel_jobs", return_value=4) as mock_jobs:
                        with patch("build.build_libstorage") as mock_build:
                            with patch("build.get_host_triple", return_value="x86_64") as mock_triple:
                                with patch("build.collect_artifacts", return_value=[]) as mock_collect:
                                    with patch("build.combine_libraries", return_value=libstorage_path) as mock_combine:
                                        with patch("build.generate_checksum") as mock_checksum:
                                            with patch("build.verify_checksum") as mock_verify:
                                                main()
        
        # Verify call order
        expected_calls = [
            call.get_platform_identifier(),
            call.configure_reproducible_environment(),
            call.ensure_logos_storage_repo("master"),
            call.get_parallel_jobs(),
            call.build_libstorage(logos_storage_dir, 4),
            call.get_host_triple(),
            call.collect_artifacts(logos_storage_dir, "x86_64"),
            call.combine_libraries([], Path("dist/master-abc123d-linux-amd64")),
            call.generate_checksum(libstorage_path),
            call.verify_checksum(libstorage_path),
        ]
        
        # Check that all mocks were called in the expected order
        assert mock_platform.call_args_list == [expected_calls[0]]
        assert mock_config.call_args_list == [expected_calls[1]]
        assert mock_repo.call_args_list == [expected_calls[2]]
        assert mock_jobs.call_args_list == [expected_calls[3]]
        assert mock_build.call_args_list == [expected_calls[4]]
        assert mock_triple.call_args_list == [expected_calls[5]]
        assert mock_collect.call_args_list == [expected_calls[6]]
        assert mock_combine.call_args_list == [expected_calls[7]]
        assert mock_checksum.call_args_list == [expected_calls[8]]
        assert mock_verify.call_args_list == [expected_calls[9]]

    def test_main_propagates_exception_from_get_platform_identifier(self):
        """Test that main() propagates exceptions from get_platform_identifier()."""
        with patch("build.get_platform_identifier", side_effect=RuntimeError("Platform error")):
            with pytest.raises(RuntimeError) as exc_info:
                main()
        
        assert str(exc_info.value) == "Platform error"

    def test_main_propagates_exception_from_configure_reproducible_environment(self):
        """Test that main() propagates exceptions from configure_reproducible_environment()."""
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.configure_reproducible_environment", side_effect=RuntimeError("Config error")):
                with pytest.raises(RuntimeError) as exc_info:
                    main()
        
        assert str(exc_info.value) == "Config error"

    def test_main_propagates_exception_from_ensure_logos_storage_repo(self):
        """Test that main() propagates exceptions from ensure_logos_storage_repo()."""
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.configure_reproducible_environment"):
                with patch("build.ensure_logos_storage_repo", side_effect=RuntimeError("Repo error")):
                    with pytest.raises(RuntimeError) as exc_info:
                        main()
        
        assert str(exc_info.value) == "Repo error"

    def test_main_propagates_exception_from_build_libstorage(self):
        """Test that main() propagates exceptions from build_libstorage()."""
        logos_storage_dir = Path("logos-storage-nim")
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.configure_reproducible_environment"):
                with patch("build.ensure_logos_storage_repo") as mock_repo:
                    mock_repo.return_value = (logos_storage_dir, MockCommitInfo("abc123", "abc123d", "master"))
                    with patch("build.get_parallel_jobs", return_value=4):
                        with patch("build.build_libstorage", side_effect=RuntimeError("Build error")):
                            with pytest.raises(RuntimeError) as exc_info:
                                main()
        
        assert str(exc_info.value) == "Build error"

    def test_main_propagates_exception_from_collect_artifacts(self):
        """Test that main() propagates exceptions from collect_artifacts()."""
        logos_storage_dir = Path("logos-storage-nim")
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.configure_reproducible_environment"):
                with patch("build.ensure_logos_storage_repo") as mock_repo:
                    mock_repo.return_value = (logos_storage_dir, MockCommitInfo("abc123", "abc123d", "master"))
                    with patch("build.get_parallel_jobs", return_value=4):
                        with patch("build.build_libstorage"):
                            with patch("build.get_host_triple", return_value="x86_64"):
                                with patch("build.collect_artifacts", side_effect=RuntimeError("Collect error")):
                                    with pytest.raises(RuntimeError) as exc_info:
                                        main()
        
        assert str(exc_info.value) == "Collect error"

    def test_main_propagates_exception_from_combine_libraries(self):
        """Test that main() propagates exceptions from combine_libraries()."""
        logos_storage_dir = Path("logos-storage-nim")
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.configure_reproducible_environment"):
                with patch("build.ensure_logos_storage_repo") as mock_repo:
                    mock_repo.return_value = (logos_storage_dir, MockCommitInfo("abc123", "abc123d", "master"))
                    with patch("build.get_parallel_jobs", return_value=4):
                        with patch("build.build_libstorage"):
                            with patch("build.get_host_triple", return_value="x86_64"):
                                with patch("build.collect_artifacts", return_value=[]):
                                    with patch("build.combine_libraries", side_effect=RuntimeError("Combine error")):
                                        with pytest.raises(RuntimeError) as exc_info:
                                            main()
        
        assert str(exc_info.value) == "Combine error"

    def test_main_propagates_exception_from_generate_checksum(self):
        """Test that main() propagates exceptions from generate_checksum()."""
        libstorage_path = Path("dist/master-abc123d-linux-amd64/libstorage.a")
        logos_storage_dir = Path("logos-storage-nim")
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.configure_reproducible_environment"):
                with patch("build.ensure_logos_storage_repo") as mock_repo:
                    mock_repo.return_value = (logos_storage_dir, MockCommitInfo("abc123", "abc123d", "master"))
                    with patch("build.get_parallel_jobs", return_value=4):
                        with patch("build.build_libstorage"):
                            with patch("build.get_host_triple", return_value="x86_64"):
                                with patch("build.collect_artifacts", return_value=[]):
                                    with patch("build.combine_libraries", return_value=libstorage_path):
                                        with patch("build.generate_checksum", side_effect=RuntimeError("Checksum error")):
                                            with pytest.raises(RuntimeError) as exc_info:
                                                main()
        
        assert str(exc_info.value) == "Checksum error"

    def test_main_propagates_exception_from_verify_checksum(self):
        """Test that main() propagates exceptions from verify_checksum()."""
        libstorage_path = Path("dist/master-abc123d-linux-amd64/libstorage.a")
        logos_storage_dir = Path("logos-storage-nim")
        with patch("build.get_platform_identifier", return_value="linux-amd64"):
            with patch("build.configure_reproducible_environment"):
                with patch("build.ensure_logos_storage_repo") as mock_repo:
                    mock_repo.return_value = (logos_storage_dir, MockCommitInfo("abc123", "abc123d", "master"))
                    with patch("build.get_parallel_jobs", return_value=4):
                        with patch("build.build_libstorage"):
                            with patch("build.get_host_triple", return_value="x86_64"):
                                with patch("build.collect_artifacts", return_value=[]):
                                    with patch("build.combine_libraries", return_value=libstorage_path):
                                        with patch("build.generate_checksum"):
                                            with patch("build.verify_checksum", side_effect=RuntimeError("Verify error")):
                                                with pytest.raises(RuntimeError) as exc_info:
                                                    main()
        
        assert str(exc_info.value) == "Verify error"