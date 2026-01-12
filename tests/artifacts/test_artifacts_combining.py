"""Tests for library combining and checksum functions in artifacts.py."""

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from src.artifacts import combine_libraries, generate_checksum, verify_checksum


class TestCombineLibraries:
    """Test combine_libraries function."""

    def test_combine_libraries_creates_output(self, temp_dir):
        libraries = [
            temp_dir / "lib1.a",
            temp_dir / "lib2.a",
        ]
        output_dir = temp_dir / "output"
        
        with patch("src.artifacts.run_command") as mock_run:
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.stat") as mock_stat:
                    mock_stat.return_value.st_size = 12345
                    result = combine_libraries(libraries, output_dir)
        
        assert result.name == "libstorage.a"
        assert result.parent == output_dir

    def test_combine_libraries_creates_output_directory(self, temp_dir):
        """Test that combine_libraries creates output directory if it doesn't exist."""
        libraries = [temp_dir / "lib1.a"]
        output_dir = temp_dir / "output"
        
        with patch("src.artifacts.run_command") as mock_run:
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.stat") as mock_stat:
                    with patch("pathlib.Path.mkdir") as mock_mkdir:
                        mock_stat.return_value.st_size = 12345
                        combine_libraries(libraries, output_dir)
        
        # Verify mkdir was called on the output directory
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    def test_combine_libraries_runs_ar_command(self):
        """Test that combine_libraries runs ar command with correct arguments."""
        libraries = [Path("/tmp/lib1.a"), Path("/tmp/lib2.a")]
        output_dir = Path("/tmp/output")
        
        with patch("src.artifacts.run_command") as mock_run:
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.stat") as mock_stat:
                    mock_stat.return_value.st_size = 12345
                    combine_libraries(libraries, output_dir)
        
        # Verify ar command was called with rcs flag
        ar_calls = [call for call in mock_run.call_args_list if "ar" in str(call[0][0])]
        assert len(ar_calls) == 1
        assert "ar" in ar_calls[0][0][0]
        assert "rcs" in ar_calls[0][0][0]

    def test_combine_libraries_includes_all_libraries(self):
        """Test that combine_libraries includes all input libraries in ar command."""
        libraries = [Path("/tmp/lib1.a"), Path("/tmp/lib2.a"), Path("/tmp/lib3.a")]
        output_dir = Path("/tmp/output")
        
        with patch("src.artifacts.run_command") as mock_run:
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.stat") as mock_stat:
                    mock_stat.return_value.st_size = 12345
                    combine_libraries(libraries, output_dir)
        
        # Verify all libraries were included in the ar command
        ar_call = None
        for call in mock_run.call_args_list:
            if "ar" in str(call[0][0]):
                ar_call = call[0][0]
                break
        
        assert ar_call is not None
        assert "lib1.a" in str(ar_call)
        assert "lib2.a" in str(ar_call)
        assert "lib3.a" in str(ar_call)

    def test_combine_libraries_raises_when_output_not_created(self):
        libraries = [Path("/tmp/lib1.a")]
        output_dir = Path("/tmp/output")
        
        with patch("src.artifacts.run_command") as mock_run:
            with patch("pathlib.Path.exists", return_value=False):
                with pytest.raises(FileNotFoundError) as exc_info:
                    combine_libraries(libraries, output_dir)
        
        assert "Combined library not found" in str(exc_info.value)


class TestGenerateChecksum:
    """Test generate_checksum function."""

    def test_generate_checksum_creates_checksum_file(self, mock_path_write_text):
        artifact_path = Path("/tmp/libstorage.a")
        
        with patch("src.artifacts.run_command") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["sha256sum"],
                returncode=0,
                stdout="abc123def456  libstorage.a\n",
                stderr=""
            )
            
            generate_checksum(artifact_path)
        
        mock_path_write_text.assert_called_once()
        assert "abc123def456" in mock_path_write_text.call_args[0][0]

    def test_generate_checksum_calls_sha256sum(self):
        artifact_path = Path("/tmp/libstorage.a")
        
        with patch("src.artifacts.run_command") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["sha256sum"],
                returncode=0,
                stdout="abc123def456  libstorage.a\n",
                stderr=""
            )
            
            generate_checksum(artifact_path)
        
        mock_run.assert_called_once()
        assert mock_run.call_args[0][0] == ["sha256sum", str(artifact_path)]

    def test_generate_checksum_writes_correct_path(self, mock_path_write_text):
        artifact_path = Path("/tmp/libstorage.a")
        
        with patch("src.artifacts.run_command") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["sha256sum"],
                returncode=0,
                stdout="abc123def456  libstorage.a\n",
                stderr=""
            )
            
            generate_checksum(artifact_path)
        
        checksum_path = artifact_path.with_suffix(".a.sha256")
        assert mock_path_write_text.call_args[0][0] == "abc123def456  libstorage.a\n"


class TestVerifyChecksum:
    """Test verify_checksum function."""

    def test_verify_checksum_returns_true_when_match(self, mock_path_read_text, mock_path_exists):
        artifact_path = Path("/tmp/libstorage.a")
        
        mock_path_exists.return_value = True
        mock_path_read_text.return_value = "abc123def456  libstorage.a\n"
        
        with patch("src.artifacts.run_command") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["sha256sum"],
                returncode=0,
                stdout="abc123def456  libstorage.a\n",
                stderr=""
            )
            
            result = verify_checksum(artifact_path)
        
        assert result is True

    def test_verify_checksum_raises_when_checksum_file_missing(self, mock_path_exists):
        artifact_path = Path("/tmp/libstorage.a")
        
        mock_path_exists.return_value = False
        
        with pytest.raises(FileNotFoundError) as exc_info:
            verify_checksum(artifact_path)
        
        assert "Checksum file not found" in str(exc_info.value)

    def test_verify_checksum_raises_when_mismatch(self, mock_path_read_text, mock_path_exists):
        artifact_path = Path("/tmp/libstorage.a")
        
        mock_path_exists.return_value = True
        mock_path_read_text.return_value = "abc123def456  libstorage.a\n"
        
        with patch("src.artifacts.run_command") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["sha256sum"],
                returncode=0,
                stdout="fed654cba321  libstorage.a\n",
                stderr=""
            )
            
            with pytest.raises(ValueError) as exc_info:
                verify_checksum(artifact_path)
        
        assert "Checksum verification failed" in str(exc_info.value)

    def test_verify_checksum_reads_checksum_file(self, mock_path_read_text, mock_path_exists):
        artifact_path = Path("/tmp/libstorage.a")
        
        mock_path_exists.return_value = True
        mock_path_read_text.return_value = "abc123def456  libstorage.a\n"
        
        with patch("src.artifacts.run_command") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["sha256sum"],
                returncode=0,
                stdout="abc123def456  libstorage.a\n",
                stderr=""
            )
            
            verify_checksum(artifact_path)
        
        checksum_path = artifact_path.with_suffix(".a.sha256")
        mock_path_read_text.assert_called_once()

    def test_verify_checksum_computes_actual_checksum(self, mock_path_read_text, mock_path_exists):
        artifact_path = Path("/tmp/libstorage.a")
        
        mock_path_exists.return_value = True
        mock_path_read_text.return_value = "abc123def456  libstorage.a\n"
        
        with patch("src.artifacts.run_command") as mock_run:
            mock_run.return_value = subprocess.CompletedProcess(
                args=["sha256sum"],
                returncode=0,
                stdout="abc123def456  libstorage.a\n",
                stderr=""
            )
            
            verify_checksum(artifact_path)
        
        mock_run.assert_called_once()
        assert mock_run.call_args[0][0] == ["sha256sum", str(artifact_path)]