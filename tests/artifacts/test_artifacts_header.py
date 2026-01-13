"""Tests for header file handling in artifacts.py."""

import os
import subprocess
from pathlib import Path

import pytest

from src.artifacts import copy_header_file, generate_sha256sums
from src.utils import run_command


class TestHeaderFileHandling:
    """Test header file copying and validation."""

    def test_copy_header_file_success(self, logos_storage_dir, dist_dir):
        """Test successful header file copy."""
        # Create header file in repository
        header_source = logos_storage_dir / "library" / "libstorage.h"
        header_source.parent.mkdir(parents=True, exist_ok=True)
        header_source.write_text("// libstorage header")
        
        # Copy header
        header_dest = copy_header_file(logos_storage_dir, dist_dir)
        
        # Verify header was copied
        assert header_dest.exists()
        assert header_dest.name == "libstorage.h"
        assert header_dest.read_text() == "// libstorage header"

    def test_copy_header_file_missing(self, logos_storage_dir, dist_dir):
        """Test that missing header file raises FileNotFoundError."""
        # Don't create header file
        with pytest.raises(FileNotFoundError) as exc_info:
            copy_header_file(logos_storage_dir, dist_dir)
        
        assert "libstorage.h not found" in str(exc_info.value)

    def test_copy_header_file_overwrites_existing(self, logos_storage_dir, dist_dir):
        """Test that copy_header_file overwrites existing header file."""
        # Create header file in repository
        header_source = logos_storage_dir / "library" / "libstorage.h"
        header_source.parent.mkdir(parents=True, exist_ok=True)
        header_source.write_text("// new header content")
        
        # Create existing header file in dist_dir
        existing_header = dist_dir / "libstorage.h"
        existing_header.write_text("// old header content")
        
        # Copy header
        header_dest = copy_header_file(logos_storage_dir, dist_dir)
        
        # Verify header was overwritten
        assert header_dest.exists()
        assert header_dest.read_text() == "// new header content"


class TestSHA256SumsGeneration:
    """Test SHA256SUMS.txt generation."""

    def test_generate_sha256sums_with_multiple_files(self, dist_dir):
        """Test SHA256SUMS.txt generation with multiple files."""
        # Create test files
        lib_file = dist_dir / "libstorage.a"
        header_file = dist_dir / "libstorage.h"
        lib_file.write_bytes(b"fake library content")
        header_file.write_text("// header content")
        
        # Generate checksums
        checksums_path = generate_sha256sums(dist_dir)
        
        # Verify checksums file exists
        assert checksums_path.exists()
        assert checksums_path.name == "SHA256SUMS.txt"
        
        # Verify checksums file contains entries for both files
        checksums_content = checksums_path.read_text()
        assert "libstorage.a" in checksums_content
        assert "libstorage.h" in checksums_content
        
        # Verify checksums are valid
        lines = checksums_content.strip().split('\n')
        assert len(lines) == 2
        
        for line in lines:
            parts = line.split()
            assert len(parts) == 2  # checksum and filename
            assert len(parts[0]) == 64  # SHA256 is 64 hex chars

    def test_generate_sha256sums_with_single_file(self, dist_dir):
        """Test SHA256SUMS.txt generation with single file."""
        # Create test file
        lib_file = dist_dir / "libstorage.a"
        lib_file.write_bytes(b"fake library content")
        
        # Generate checksums
        checksums_path = generate_sha256sums(dist_dir)
        
        # Verify checksums file exists
        assert checksums_path.exists()
        
        # Verify checksums file contains entry for the file
        checksums_content = checksums_path.read_text()
        assert "libstorage.a" in checksums_content
        
        # Verify single entry
        lines = checksums_content.strip().split('\n')
        assert len(lines) == 1

    def test_generate_sha256sums_raises_when_no_files(self, dist_dir):
        """Test that generate_sha256sums raises FileNotFoundError when no files exist."""
        # Don't create any files
        with pytest.raises(FileNotFoundError) as exc_info:
            generate_sha256sums(dist_dir)
        
        assert "No files found" in str(exc_info.value)

    def test_generate_sha256sums_excludes_existing_checksums_file(self, dist_dir):
        """Test that generate_sha256sums excludes existing SHA256SUMS.txt from checksums."""
        # Create test files
        lib_file = dist_dir / "libstorage.a"
        header_file = dist_dir / "libstorage.h"
        lib_file.write_bytes(b"fake library content")
        header_file.write_text("// header content")
        
        # Create existing checksums file
        existing_checksums = dist_dir / "SHA256SUMS.txt"
        existing_checksums.write_text("old checksums")
        
        # Generate checksums
        checksums_path = generate_sha256sums(dist_dir)
        
        # Verify checksums file was overwritten
        assert checksums_path.exists()
        checksums_content = checksums_path.read_text()
        assert checksums_content != "old checksums"
        
        # Verify only libstorage.a and libstorage.h are included
        lines = checksums_content.strip().split('\n')
        assert len(lines) == 2
        assert "libstorage.a" in checksums_content
        assert "libstorage.h" in checksums_content

    def test_generate_sha256sums_files_sorted_alphabetically(self, dist_dir):
        """Test that generate_sha256sums sorts files alphabetically."""
        # Create test files in non-alphabetical order
        z_file = dist_dir / "z_file.txt"
        a_file = dist_dir / "a_file.txt"
        m_file = dist_dir / "m_file.txt"
        
        z_file.write_text("z content")
        a_file.write_text("a content")
        m_file.write_text("m content")
        
        # Generate checksums
        checksums_path = generate_sha256sums(dist_dir)
        
        # Verify files are sorted alphabetically
        checksums_content = checksums_path.read_text()
        lines = checksums_content.strip().split('\n')
        
        # Extract filenames (sha256sum returns absolute paths)
        filenames = [Path(line.split()[1]).name for line in lines]
        
        # Verify alphabetical order
        assert filenames == ["a_file.txt", "m_file.txt", "z_file.txt"]

    def test_generate_sha256sums_uses_relative_paths_for_verification(self, dist_dir):
        """Test that generate_sha256sums uses relative paths so sha256sum -c works from within the directory."""
        # Create test files
        lib_file = dist_dir / "libstorage.a"
        header_file = dist_dir / "libstorage.h"
        lib_file.write_bytes(b"fake library content")
        header_file.write_text("// header content")
        
        # Generate checksums
        checksums_path = generate_sha256sums(dist_dir)
        
        # Verify checksums file contains relative paths (just filenames)
        checksums_content = checksums_path.read_text()
        lines = checksums_content.strip().split('\n')
        
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
        
        # Verify that sha256sum -c works from within the directory
        original_cwd = Path.cwd()
        try:
            os.chdir(dist_dir)
            result = run_command(["sha256sum", "-c", "SHA256SUMS.txt"])
            # Both files should verify successfully
            assert result.returncode == 0
            assert "libstorage.a: OK" in result.stdout
            assert "libstorage.h: OK" in result.stdout
        finally:
            os.chdir(original_cwd)