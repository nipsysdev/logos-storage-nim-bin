"""Tests for artifact compatibility checking in artifacts.py."""

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from src.artifacts import check_artifact_compatibility


class TestCheckArtifactCompatibility:
    """Test check_artifact_compatibility function."""

    def test_check_compatibility_returns_true_for_aarch64(self):
        artifact_path = Path("/tmp/test.a")
        target = "aarch64"
        
        with patch("src.artifacts.run_command") as mock_run:
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="object.o\n", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout=b"binary data", stderr=b""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="ELF 64-bit LSB executable, ARM aarch64", stderr=""),
            ]
            
            result = check_artifact_compatibility(artifact_path, target)
        
        assert result is True

    def test_check_compatibility_returns_true_for_aarch64_macos_macho(self):
        """Test that check_artifact_compatibility returns True for macOS Mach-O arm64 binaries."""
        artifact_path = Path("/tmp/test.a")
        target = "aarch64"
        
        with patch("src.artifacts.run_command") as mock_run:
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="object.o\n", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout=b"binary data", stderr=b""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="Mach-O 64-bit object arm64", stderr=""),
            ]
            
            result = check_artifact_compatibility(artifact_path, target)
        
        assert result is True

    def test_check_compatibility_returns_true_for_x86_64(self):
        artifact_path = Path("/tmp/test.a")
        target = "x86_64"
        
        with patch("src.artifacts.run_command") as mock_run:
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="object.o\n", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout=b"binary data", stderr=b""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="ELF 64-bit LSB executable, x86-64", stderr=""),
            ]
            
            result = check_artifact_compatibility(artifact_path, target)
        
        assert result is True

    def test_check_compatibility_returns_true_for_i686(self):
        artifact_path = Path("/tmp/test.a")
        target = "i686"
        
        with patch("src.artifacts.run_command") as mock_run:
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="object.o\n", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout=b"binary data", stderr=b""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="ELF 32-bit LSB executable, Intel 80386", stderr=""),
            ]
            
            result = check_artifact_compatibility(artifact_path, target)
        
        assert result is True

    def test_check_compatibility_returns_false_for_mismatch(self):
        artifact_path = Path("/tmp/test.a")
        target = "aarch64"
        
        with patch("src.artifacts.run_command") as mock_run:
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="object.o\n", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout=b"binary data", stderr=b""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="ELF 64-bit LSB executable, x86-64", stderr=""),
            ]
            
            result = check_artifact_compatibility(artifact_path, target)
        
        assert result is False

    def test_check_compatibility_returns_false_when_ar_fails(self):
        artifact_path = Path("/tmp/test.a")
        target = "x86_64"
        
        with patch("src.artifacts.run_command") as mock_run:
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr="error"),
            ]
            
            result = check_artifact_compatibility(artifact_path, target)
        
        assert result is False

    def test_check_compatibility_returns_false_when_archive_empty(self):
        artifact_path = Path("/tmp/test.a")
        target = "x86_64"
        
        with patch("src.artifacts.run_command") as mock_run:
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="\n", stderr=""),
            ]
            
            result = check_artifact_compatibility(artifact_path, target)
        
        assert result is False

    def test_check_compatibility_returns_false_when_extract_fails(self):
        artifact_path = Path("/tmp/test.a")
        target = "x86_64"
        
        with patch("src.artifacts.run_command") as mock_run:
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="object.o\n", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=1, stdout=b"", stderr=b"error"),
            ]
            
            result = check_artifact_compatibility(artifact_path, target)
        
        assert result is False

    def test_check_compatibility_returns_false_when_file_fails(self):
        artifact_path = Path("/tmp/test.a")
        target = "x86_64"
        
        with patch("src.artifacts.run_command") as mock_run:
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="object.o\n", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout=b"binary data", stderr=b""),
                subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr="error"),
            ]
            
            result = check_artifact_compatibility(artifact_path, target)
        
        assert result is False

    def test_check_compatibility_returns_false_for_unknown_architecture(self):
        """Test that check_artifact_compatibility returns False for unknown architecture (fallback case)."""
        artifact_path = Path("/tmp/test.a")
        target = "riscv64"  # Unknown architecture not in the known patterns
        
        with patch("src.artifacts.run_command") as mock_run:
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="object.o\n", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout=b"binary data", stderr=b""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="ELF 64-bit LSB executable, RISC-V", stderr=""),
            ]
            
            result = check_artifact_compatibility(artifact_path, target)
        
        assert result is False