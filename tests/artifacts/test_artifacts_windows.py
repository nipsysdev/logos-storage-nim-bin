"""Test Windows-specific artifact functionality."""

import pytest
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.artifacts import generate_checksum, verify_checksum, generate_sha256sums, build_libstorage


class TestWindowsChecksumGeneration:
    """Test SHA256 checksum generation on Windows."""

    @patch('src.artifacts.platform.system', return_value='Windows')
    @patch('src.artifacts.run_command')
    def test_generate_checksum_uses_certutil_on_windows(self, mock_run, mock_system, tmp_path):
        """Test that generate_checksum uses certutil on Windows."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=["certutil", "-hashfile", "test.a", "SHA256"],
            returncode=0,
            stdout="SHA256 hash of test.a:\nabc123def456  \n",
            stderr=""
        )
        
        artifact_path = tmp_path / "test.a"
        generate_checksum(artifact_path)
        
        mock_run.assert_called_once_with(["certutil", "-hashfile", str(artifact_path), "SHA256"])

    @patch('src.artifacts.platform.system', return_value='Windows')
    @patch('src.artifacts.run_command')
    def test_generate_checksum_parses_certutil_output(self, mock_run, mock_system, tmp_path):
        """Test that generate_checksum correctly parses certutil output."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=["certutil", "-hashfile", "test.a", "SHA256"],
            returncode=0,
            stdout="SHA256 hash of test.a:\nabc123def456789  \n",
            stderr=""
        )
        
        artifact_path = tmp_path / "test.a"
        artifact_path.write_text("test content")
        generate_checksum(artifact_path)
        
        checksum_path = artifact_path.with_suffix(".a.sha256")
        assert checksum_path.exists()
        content = checksum_path.read_text()
        assert "abc123def456789" in content
        assert "test.a" in content

    @patch('src.artifacts.platform.system', return_value='Windows')
    @patch('src.artifacts.run_command')
    def test_verify_checksum_uses_certutil_on_windows(self, mock_run, mock_system, tmp_path):
        """Test that verify_checksum uses certutil on Windows."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=["certutil", "-hashfile", "test.a", "SHA256"],
            returncode=0,
            stdout="SHA256 hash of test.a:\nabc123def456789  \n",
            stderr=""
        )
        
        artifact_path = tmp_path / "test.a"
        artifact_path.write_text("test content")
        checksum_path = artifact_path.with_suffix(".a.sha256")
        checksum_path.write_text("abc123def456789  test.a")
        
        result = verify_checksum(artifact_path)
        assert result is True

    @patch('src.artifacts.platform.system', return_value='Windows')
    @patch('src.artifacts.run_command')
    def test_verify_checksum_fails_on_mismatch(self, mock_run, mock_system, tmp_path):
        """Test that verify_checksum raises ValueError on checksum mismatch."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=["certutil", "-hashfile", "test.a", "SHA256"],
            returncode=0,
            stdout="SHA256 hash of test.a:\nwrongchecksum  \n",
            stderr=""
        )
        
        artifact_path = tmp_path / "test.a"
        artifact_path.write_text("test content")
        checksum_path = artifact_path.with_suffix(".a.sha256")
        checksum_path.write_text("abc123def456789  test.a")
        
        with pytest.raises(ValueError) as exc_info:
            verify_checksum(artifact_path)
        
        assert "Checksum verification failed" in str(exc_info.value)

    @patch('src.artifacts.platform.system', return_value='Windows')
    @patch('src.artifacts.run_command')
    def test_generate_sha256sums_uses_certutil_on_windows(self, mock_run, mock_system, tmp_path):
        """Test that generate_sha256sums uses certutil on Windows."""
        mock_run.return_value = subprocess.CompletedProcess(
            args=["certutil", "-hashfile", "test.a", "SHA256"],
            returncode=0,
            stdout="SHA256 hash of test.a:\nabc123def456789  \n",
            stderr=""
        )
        
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        test_file = output_dir / "test.a"
        test_file.write_text("test content")
        
        generate_sha256sums(output_dir)
        
        checksums_path = output_dir / "SHA256SUMS.txt"
        assert checksums_path.exists()
        content = checksums_path.read_text()
        assert "abc123def456789" in content
        assert "test.a" in content


class TestWindowsBuildCommand:
    """Test build command invocation on Windows."""

    @patch('src.artifacts.platform.system', return_value='Windows')
    @patch('src.utils.get_host_triple', return_value='x86_64')
    @patch('src.artifacts.run_command')
    def test_build_libstorage_uses_msys2_on_windows(self, mock_run, mock_triple, mock_system):
        """Test that build_libstorage uses MSYS2 on Windows."""
        logos_storage_dir = Path("C:/logos-storage-nim")
        
        build_libstorage(logos_storage_dir, 4)
        
        # Verify that MSYS2 is used for both deps and libstorage
        assert mock_run.call_count == 2
        
        # Check first call (deps)
        first_call = mock_run.call_args_list[0]
        assert first_call[0][0] == ["msys2", "-lc", "cd /c/logos-storage-nim && make deps"]
        
        # Check second call (libstorage)
        second_call = mock_run.call_args_list[1]
        assert second_call[0][0] == ["msys2", "-lc", "cd /c/logos-storage-nim && make -j4 libstorage"]

    @patch('src.artifacts.platform.system', return_value='Windows')
    @patch('src.utils.get_host_triple', return_value='x86_64')
    @patch('src.artifacts.run_command')
    def test_build_libstorage_converts_windows_path_to_msys2(self, mock_run, mock_triple, mock_system):
        """Test that build_libstorage converts Windows paths to MSYS2 format."""
        logos_storage_dir = Path("C:/logos-storage-nim")
        
        build_libstorage(logos_storage_dir, 4)
        
        # Check that the path was converted from C:/ to /c/
        first_call = mock_run.call_args_list[0]
        assert "/c/logos-storage-nim" in first_call[0][0][2]
        assert "C:" not in first_call[0][0][2]

    @patch('src.artifacts.platform.system', return_value='Windows')
    @patch('src.utils.get_host_triple', return_value='x86_64')
    @patch('src.artifacts.run_command')
    def test_build_libstorage_handles_backslashes(self, mock_run, mock_triple, mock_system):
        """Test that build_libstorage handles Windows backslashes."""
        logos_storage_dir = Path("C:\\logos-storage-nim")
        
        build_libstorage(logos_storage_dir, 4)
        
        # Check that backslashes were converted to forward slashes
        first_call = mock_run.call_args_list[0]
        assert "\\" not in first_call[0][0][2]
        assert "/" in first_call[0][0][2]

    @patch('src.artifacts.platform.system', return_value='Linux')
    @patch('src.utils.get_host_triple', return_value='x86_64')
    @patch('src.artifacts.run_command')
    def test_build_libstorage_uses_make_on_linux(self, mock_run, mock_triple, mock_system):
        """Test that build_libstorage uses make directly on Linux."""
        logos_storage_dir = Path("/logos-storage-nim")
        
        build_libstorage(logos_storage_dir, 4)
        
        # Verify that make is used directly (not MSYS2)
        assert mock_run.call_count == 2
        
        # Check first call (deps)
        first_call = mock_run.call_args_list[0]
        assert first_call[0][0] == ["make", "-C", str(logos_storage_dir), "deps"]
        
        # Check second call (libstorage)
        second_call = mock_run.call_args_list[1]
        assert second_call[0][0] == ["make", "-j", "4", "-C", str(logos_storage_dir), "libstorage"]