"""Tests for library combining and checksum functions in artifacts.py."""

import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.artifacts import combine_libraries, generate_checksum, verify_checksum


class TestCombineLibraries:
    """Test combine_libraries function."""

    @patch("src.artifacts.run_command")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.stat")
    def test_combine_libraries_creates_output(self, mock_stat, mock_exists, mock_run, temp_dir):
        """Test that combine_libraries creates output file with correct path."""
        libraries = [
            temp_dir / "lib1.a",
            temp_dir / "lib2.a",
        ]
        output_dir = temp_dir / "output"
        output_path = output_dir / "libstorage.a"
        
        # Configure exists to return True for output file
        mock_exists.return_value = True
        
        # Configure stat to return a mock with st_size
        mock_stat_result = MagicMock()
        mock_stat_result.st_size = 1000
        mock_stat.return_value = mock_stat_result
        
        result = combine_libraries(libraries, output_dir)
        
        assert result.name == "libstorage.a"
        assert result.parent == output_dir

    @patch("src.artifacts.run_command")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.stat")
    @patch("pathlib.Path.mkdir")
    def test_combine_libraries_creates_output_directory(self, mock_mkdir, mock_stat, mock_exists, mock_run, temp_dir):
        """Test that combine_libraries creates output directory if it doesn't exist."""
        libraries = [temp_dir / "lib1.a"]
        output_dir = temp_dir / "output"
        
        # Configure exists to return True for output file
        mock_exists.return_value = True
        
        # Configure stat to return a mock with st_size
        mock_stat_result = MagicMock()
        mock_stat_result.st_size = 1000
        mock_stat.return_value = mock_stat_result
        
        combine_libraries(libraries, output_dir)
        
        # Verify mkdir was called on the output directory
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch("src.artifacts.run_command")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.stat")
    def test_combine_libraries_runs_ar_command(self, mock_stat, mock_exists, mock_run):
        """Test that combine_libraries runs ar command with correct arguments."""
        libraries = [Path("/tmp/lib1.a"), Path("/tmp/lib2.a")]
        output_dir = Path("/tmp/output")
        
        # Configure exists to return True for output file
        mock_exists.return_value = True
        
        # Configure stat to return a mock with st_size
        mock_stat_result = MagicMock()
        mock_stat_result.st_size = 1000
        mock_stat.return_value = mock_stat_result
        
        combine_libraries(libraries, output_dir)
        
        # Verify ar command was called with rcs flag
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "ar" in call_args
        assert "rcs" in call_args

    @patch("src.artifacts.run_command")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.stat")
    def test_combine_libraries_includes_all_libraries(self, mock_stat, mock_exists, mock_run):
        """Test that combine_libraries includes all input libraries in ar command."""
        libraries = [Path("/tmp/lib1.a"), Path("/tmp/lib2.a"), Path("/tmp/lib3.a")]
        output_dir = Path("/tmp/output")
        
        # Configure exists to return True for output file
        mock_exists.return_value = True
        
        # Configure stat to return a mock with st_size
        mock_stat_result = MagicMock()
        mock_stat_result.st_size = 1000
        mock_stat.return_value = mock_stat_result
        
        combine_libraries(libraries, output_dir)
        
        # Verify all libraries were included in the ar command
        call_args = mock_run.call_args[0][0]
        assert "lib1.a" in str(call_args)
        assert "lib2.a" in str(call_args)
        assert "lib3.a" in str(call_args)

    @patch("src.artifacts.run_command")
    @patch("pathlib.Path.exists")
    def test_combine_libraries_raises_when_output_not_created(self, mock_exists, mock_run):
        """Test that combine_libraries raises FileNotFoundError when output is not created."""
        libraries = [Path("/tmp/lib1.a")]
        output_dir = Path("/tmp/output")
        
        # Configure exists to return False
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError) as exc_info:
            combine_libraries(libraries, output_dir)
        
        assert "Combined library not found" in str(exc_info.value)


class TestGenerateChecksum:
    """Test generate_checksum function."""

    @patch("src.artifacts.run_command")
    @patch("pathlib.Path.write_text")
    def test_generate_checksum_creates_checksum_file(self, mock_write, mock_run):
        """Test that generate_checksum creates checksum file with correct content."""
        artifact_path = Path("/tmp/libstorage.a")
        
        mock_run.return_value = subprocess.CompletedProcess(
            args=["sha256sum"],
            returncode=0,
            stdout="abc123def456  libstorage.a\n",
            stderr=""
        )
        
        generate_checksum(artifact_path)
        
        mock_write.assert_called_once()
        assert "abc123def456" in mock_write.call_args[0][0]

    @patch("src.artifacts.run_command")
    def test_generate_checksum_calls_sha256sum(self, mock_run):
        """Test that generate_checksum calls sha256sum command."""
        artifact_path = Path("/tmp/libstorage.a")
        
        mock_run.return_value = subprocess.CompletedProcess(
            args=["sha256sum"],
            returncode=0,
            stdout="abc123def456  libstorage.a\n",
            stderr=""
        )
        
        generate_checksum(artifact_path)
        
        mock_run.assert_called_once()
        assert mock_run.call_args[0][0] == ["sha256sum", str(artifact_path)]

    @patch("src.artifacts.run_command")
    @patch("pathlib.Path.write_text")
    def test_generate_checksum_writes_correct_path(self, mock_write, mock_run):
        """Test that generate_checksum writes checksum to correct path."""
        artifact_path = Path("/tmp/libstorage.a")
        
        mock_run.return_value = subprocess.CompletedProcess(
            args=["sha256sum"],
            returncode=0,
            stdout="abc123def456  libstorage.a\n",
            stderr=""
        )
        
        generate_checksum(artifact_path)
        
        assert mock_write.call_args[0][0] == "abc123def456  libstorage.a\n"


class TestVerifyChecksum:
    """Test verify_checksum function."""

    @patch("src.artifacts.run_command")
    @patch("pathlib.Path.read_text")
    @patch("pathlib.Path.exists")
    def test_verify_checksum_returns_true_when_match(self, mock_exists, mock_read, mock_run):
        """Test that verify_checksum returns True when checksums match."""
        artifact_path = Path("/tmp/libstorage.a")
        
        mock_exists.return_value = True
        mock_read.return_value = "abc123def456  libstorage.a\n"
        
        mock_run.return_value = subprocess.CompletedProcess(
            args=["sha256sum"],
            returncode=0,
            stdout="abc123def456  libstorage.a\n",
            stderr=""
        )
        
        result = verify_checksum(artifact_path)
        
        assert result is True

    @patch("pathlib.Path.exists")
    def test_verify_checksum_raises_when_checksum_file_missing(self, mock_exists):
        """Test that verify_checksum raises FileNotFoundError when checksum file is missing."""
        artifact_path = Path("/tmp/libstorage.a")
        
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError) as exc_info:
            verify_checksum(artifact_path)
        
        assert "Checksum file not found" in str(exc_info.value)

    @patch("src.artifacts.run_command")
    @patch("pathlib.Path.read_text")
    @patch("pathlib.Path.exists")
    def test_verify_checksum_raises_when_mismatch(self, mock_exists, mock_read, mock_run):
        """Test that verify_checksum raises ValueError when checksums don't match."""
        artifact_path = Path("/tmp/libstorage.a")
        
        mock_exists.return_value = True
        mock_read.return_value = "abc123def456  libstorage.a\n"
        
        mock_run.return_value = subprocess.CompletedProcess(
            args=["sha256sum"],
            returncode=0,
            stdout="fed654cba321  libstorage.a\n",
            stderr=""
        )
        
        with pytest.raises(ValueError) as exc_info:
            verify_checksum(artifact_path)
        
        assert "Checksum verification failed" in str(exc_info.value)

    @patch("src.artifacts.run_command")
    @patch("pathlib.Path.read_text")
    @patch("pathlib.Path.exists")
    def test_verify_checksum_reads_checksum_file(self, mock_exists, mock_read, mock_run):
        """Test that verify_checksum reads the checksum file."""
        artifact_path = Path("/tmp/libstorage.a")
        
        mock_exists.return_value = True
        mock_read.return_value = "abc123def456  libstorage.a\n"
        
        mock_run.return_value = subprocess.CompletedProcess(
            args=["sha256sum"],
            returncode=0,
            stdout="abc123def456  libstorage.a\n",
            stderr=""
        )
        
        verify_checksum(artifact_path)
        
        mock_read.assert_called_once()

    @patch("src.artifacts.run_command")
    @patch("pathlib.Path.read_text")
    @patch("pathlib.Path.exists")
    def test_verify_checksum_computes_actual_checksum(self, mock_exists, mock_read, mock_run):
        """Test that verify_checksum computes actual checksum."""
        artifact_path = Path("/tmp/libstorage.a")
        
        mock_exists.return_value = True
        mock_read.return_value = "abc123def456  libstorage.a\n"
        
        mock_run.return_value = subprocess.CompletedProcess(
            args=["sha256sum"],
            returncode=0,
            stdout="abc123def456  libstorage.a\n",
            stderr=""
        )
        
        verify_checksum(artifact_path)
        
        mock_run.assert_called_once()
        assert mock_run.call_args[0][0] == ["sha256sum", str(artifact_path)]