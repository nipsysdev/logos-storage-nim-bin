"""Tests for header file handling in artifacts.py."""

import os
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from src.artifacts import copy_header_file, generate_sha256sums
from src.utils import run_command


class TestHeaderFileHandling:
    """Test header file copying and validation."""

    def test_copy_header_file_success(self, logos_storage_dir, dist_dir, mock_path_exists):
        """Test successful header file copy."""
        header_source = logos_storage_dir / "library" / "libstorage.h"
        
        # Configure exists to return True for header source
        mock_path_exists.return_value = True
        
        with patch("shutil.copy2") as mock_copy:
            header_dest = copy_header_file(logos_storage_dir, dist_dir)
        
        # Verify shutil.copy2 was called
        mock_copy.assert_called_once()
        assert header_dest.name == "libstorage.h"

    def test_copy_header_file_missing(self, logos_storage_dir, dist_dir, mock_path_exists):
        """Test that missing header file raises FileNotFoundError."""
        # Configure exists to return False for header source
        mock_path_exists.return_value = False
        
        with pytest.raises(FileNotFoundError) as exc_info:
            copy_header_file(logos_storage_dir, dist_dir)
        
        assert "libstorage.h not found" in str(exc_info.value)

    def test_copy_header_file_overwrites_existing(self, logos_storage_dir, dist_dir, mock_path_exists):
        """Test that copy_header_file overwrites existing header file."""
        # Configure exists to return True for header source
        mock_path_exists.return_value = True
        
        with patch("shutil.copy2") as mock_copy:
            header_dest = copy_header_file(logos_storage_dir, dist_dir)
        
        # Verify shutil.copy2 was called (it will overwrite by default)
        mock_copy.assert_called_once()
        assert header_dest.name == "libstorage.h"


class TestSHA256SumsGeneration:
    """Test SHA256SUMS.txt generation."""

    def test_generate_sha256sums_with_multiple_files(self, dist_dir, mock_directory_operations, mock_file_writing, mock_sha256sum_commands):
        """Test SHA256SUMS.txt generation with multiple files."""
        # Create mock file paths
        lib_file = dist_dir / "libstorage.a"
        header_file = dist_dir / "libstorage.h"
        
        # Configure iterdir to return mock files
        mock_directory_operations["iterdir"].return_value = [lib_file, header_file]
        mock_directory_operations["is_file"].return_value = True
        
        # Configure sha256sum responses
        def sha256sum_side_effect(cmd, check=True, binary=False):
            if "libstorage.a" in str(cmd):
                return subprocess.CompletedProcess(
                    args=["sha256sum"],
                    returncode=0,
                    stdout="abc123def456789abc123def456789abc123def456789abc123def456789abc1  /full/path/libstorage.a\n",
                    stderr=""
                )
            elif "libstorage.h" in str(cmd):
                return subprocess.CompletedProcess(
                    args=["sha256sum"],
                    returncode=0,
                    stdout="fed654cba321789fed654cba321789fed654cba321789fed654cba321789fed6  /full/path/libstorage.h\n",
                    stderr=""
                )
            return subprocess.CompletedProcess(returncode=0, stdout="", stderr="")
        
        mock_sha256sum_commands.side_effect = sha256sum_side_effect
        checksums_path = generate_sha256sums(dist_dir)
        
        # Verify write_text was called
        mock_file_writing["write_text"].assert_called_once()
        written_content = mock_file_writing["write_text"].call_args[0][0]
        
        # Verify checksums file contains entries for both files
        assert "libstorage.a" in written_content
        assert "libstorage.h" in written_content
        
        # Verify checksums are valid
        lines = written_content.strip().split('\n')
        assert len(lines) == 2
        
        for line in lines:
            parts = line.split()
            assert len(parts) == 2  # checksum and filename
            assert len(parts[0]) == 64  # SHA256 is 64 hex chars

    def test_generate_sha256sums_with_single_file(self, dist_dir, mock_directory_operations, mock_file_writing, mock_sha256sum_commands):
        """Test SHA256SUMS.txt generation with single file."""
        # Create mock file path
        lib_file = dist_dir / "libstorage.a"
        
        # Configure iterdir to return mock file
        mock_directory_operations["iterdir"].return_value = [lib_file]
        mock_directory_operations["is_file"].return_value = True
        
        mock_sha256sum_commands.return_value = subprocess.CompletedProcess(
            args=["sha256sum"],
            returncode=0,
            stdout="abc123def456789abc123def456789abc123def456789abc123def456789abc1  /full/path/libstorage.a\n",
            stderr=""
        )
        
        checksums_path = generate_sha256sums(dist_dir)
        
        # Verify write_text was called
        written_content = mock_file_writing["write_text"].call_args[0][0]
        
        # Verify checksums file contains entry for the file
        assert "libstorage.a" in written_content
        
        # Verify single entry
        lines = written_content.strip().split('\n')
        assert len(lines) == 1

    def test_generate_sha256sums_raises_when_no_files(self, dist_dir, mock_directory_operations):
        """Test that generate_sha256sums raises FileNotFoundError when no files exist."""
        # Configure iterdir to return empty list
        mock_directory_operations["iterdir"].return_value = []
        
        with pytest.raises(FileNotFoundError) as exc_info:
            generate_sha256sums(dist_dir)
        
        assert "No files found" in str(exc_info.value)

    def test_generate_sha256sums_excludes_existing_checksums_file(self, dist_dir, mock_directory_operations, mock_file_writing, mock_sha256sum_commands):
        """Test that generate_sha256sums excludes existing SHA256SUMS.txt from checksums."""
        # Create mock file paths
        lib_file = dist_dir / "libstorage.a"
        header_file = dist_dir / "libstorage.h"
        checksums_file = dist_dir / "SHA256SUMS.txt"
        
        # Configure iterdir to return mock files including checksums file
        mock_directory_operations["iterdir"].return_value = [lib_file, header_file, checksums_file]
        mock_directory_operations["is_file"].return_value = True
        
        # Configure sha256sum responses
        def sha256sum_side_effect(cmd, check=True, binary=False):
            if "libstorage.a" in str(cmd):
                return subprocess.CompletedProcess(
                    args=["sha256sum"],
                    returncode=0,
                    stdout="abc123def456789abc123def456789abc123def456789abc123def456789abc1  /full/path/libstorage.a\n",
                    stderr=""
                )
            elif "libstorage.h" in str(cmd):
                return subprocess.CompletedProcess(
                    args=["sha256sum"],
                    returncode=0,
                    stdout="fed654cba321789fed654cba321789fed654cba321789fed654cba321789fed6  /full/path/libstorage.h\n",
                    stderr=""
                )
            return subprocess.CompletedProcess(returncode=0, stdout="", stderr="")
        
        mock_sha256sum_commands.side_effect = sha256sum_side_effect
        checksums_path = generate_sha256sums(dist_dir)
        
        # Verify write_text was called
        written_content = mock_file_writing["write_text"].call_args[0][0]
        
        # Verify only libstorage.a and libstorage.h are included (not SHA256SUMS.txt)
        lines = written_content.strip().split('\n')
        assert len(lines) == 2
        assert "libstorage.a" in written_content
        assert "libstorage.h" in written_content
        assert "SHA256SUMS.txt" not in written_content

    def test_generate_sha256sums_files_sorted_alphabetically(self, dist_dir, mock_directory_operations, mock_file_writing, mock_sha256sum_commands):
        """Test that generate_sha256sums sorts files alphabetically."""
        # Create mock file paths in non-alphabetical order
        z_file = dist_dir / "z_file.txt"
        a_file = dist_dir / "a_file.txt"
        m_file = dist_dir / "m_file.txt"
        
        # Configure iterdir to return files in non-alphabetical order
        mock_directory_operations["iterdir"].return_value = [z_file, a_file, m_file]
        mock_directory_operations["is_file"].return_value = True
        
        # Configure sha256sum responses
        def sha256sum_side_effect(cmd, check=True, binary=False):
            if "z_file.txt" in str(cmd):
                return subprocess.CompletedProcess(
                    args=["sha256sum"],
                    returncode=0,
                    stdout="zzz123def456789abc123def456789abc123def456789abc123def456789abc1  /full/path/z_file.txt\n",
                    stderr=""
                )
            elif "a_file.txt" in str(cmd):
                return subprocess.CompletedProcess(
                    args=["sha256sum"],
                    returncode=0,
                    stdout="aaa123def456789abc123def456789abc123def456789abc123def456789abc1  /full/path/a_file.txt\n",
                    stderr=""
                )
            elif "m_file.txt" in str(cmd):
                return subprocess.CompletedProcess(
                    args=["sha256sum"],
                    returncode=0,
                    stdout="mmm123def456789abc123def456789abc123def456789abc123def456789abc1  /full/path/m_file.txt\n",
                    stderr=""
                )
            return subprocess.CompletedProcess(returncode=0, stdout="", stderr="")
        
        mock_sha256sum_commands.side_effect = sha256sum_side_effect
        checksums_path = generate_sha256sums(dist_dir)
        
        # Verify write_text was called
        written_content = mock_file_writing["write_text"].call_args[0][0]
        lines = written_content.strip().split('\n')
        
        # Extract filenames
        filenames = [line.split()[1] for line in lines]
        
        # Verify alphabetical order
        assert filenames == ["a_file.txt", "m_file.txt", "z_file.txt"]

    def test_generate_sha256sums_uses_relative_paths_for_verification(self, dist_dir, mock_directory_operations, mock_file_writing, mock_sha256sum_commands):
        """Test that generate_sha256sums uses relative paths so sha256sum -c works from within the directory."""
        # Create mock file paths
        lib_file = dist_dir / "libstorage.a"
        header_file = dist_dir / "libstorage.h"
        
        # Configure iterdir to return mock files
        mock_directory_operations["iterdir"].return_value = [lib_file, header_file]
        mock_directory_operations["is_file"].return_value = True
        
        # Configure sha256sum responses with full paths
        def sha256sum_side_effect(cmd, check=True, binary=False):
            if "libstorage.a" in str(cmd):
                return subprocess.CompletedProcess(
                    args=["sha256sum"],
                    returncode=0,
                    stdout="abc123def456789abc123def456789abc123def456789abc123def456789abc1  /full/path/libstorage.a\n",
                    stderr=""
                )
            elif "libstorage.h" in str(cmd):
                return subprocess.CompletedProcess(
                    args=["sha256sum"],
                    returncode=0,
                    stdout="fed654cba321789fed654cba321789fed654cba321789fed654cba321789fed6  /full/path/libstorage.h\n",
                    stderr=""
                )
            return subprocess.CompletedProcess(returncode=0, stdout="", stderr="")
        
        mock_sha256sum_commands.side_effect = sha256sum_side_effect
        checksums_path = generate_sha256sums(dist_dir)
        
        # Verify write_text was called
        written_content = mock_file_writing["write_text"].call_args[0][0]
        lines = written_content.strip().split('\n')
        
        for line in lines:
            parts = line.split()
            # Should have exactly 2 parts: checksum and filename
            assert len(parts) == 2
            # Filename should be just the name, not a full path
            filename = parts[1]
            assert filename in ["libstorage.a", "libstorage.h"]
            # Should not contain directory separators
            assert "/" not in filename
            assert "\\" not in filename