"""Tests for platform detection in utils.py."""

from unittest.mock import patch

import pytest

from src.utils import get_host_triple, get_platform_identifier


class TestGetHostTriple:
    """Test get_host_triple function."""

    def test_get_host_triple_x86_64(self, mock_platform_machine):
        mock_platform_machine.return_value = "x86_64"
        
        result = get_host_triple()
        
        assert result == "x86_64"

    def test_get_host_triple_amd64(self, mock_platform_machine):
        mock_platform_machine.return_value = "AMD64"
        
        result = get_host_triple()
        
        assert result == "x86_64"

    def test_get_host_triple_aarch64(self, mock_platform_machine):
        mock_platform_machine.return_value = "aarch64"
        
        result = get_host_triple()
        
        assert result == "aarch64"

    def test_get_host_triple_arm64(self, mock_platform_machine):
        mock_platform_machine.return_value = "arm64"
        
        result = get_host_triple()
        
        assert result == "aarch64"

    def test_get_host_triple_i686(self, mock_platform_machine):
        mock_platform_machine.return_value = "i686"
        
        result = get_host_triple()
        
        assert result == "i686"

    def test_get_host_triple_i386(self, mock_platform_machine):
        mock_platform_machine.return_value = "i386"
        
        result = get_host_triple()
        
        assert result == "i686"

    def test_get_host_triple_unknown(self, mock_platform_machine):
        mock_platform_machine.return_value = "riscv64"
        
        result = get_host_triple()
        
        assert result == "riscv64"


class TestGetPlatformIdentifier:
    """Test get_platform_identifier function."""

    def test_get_platform_identifier_aarch64(self, mock_platform_machine):
        mock_platform_machine.return_value = "aarch64"
        
        result = get_platform_identifier()
        
        assert result == "linux-arm64"

    def test_get_platform_identifier_arm64(self, mock_platform_machine):
        mock_platform_machine.return_value = "arm64"
        
        result = get_platform_identifier()
        
        assert result == "linux-arm64"

    def test_get_platform_identifier_x86_64(self, mock_platform_machine):
        mock_platform_machine.return_value = "x86_64"
        
        result = get_platform_identifier()
        
        assert result == "linux-amd64"

    def test_get_platform_identifier_amd64(self, mock_platform_machine):
        mock_platform_machine.return_value = "amd64"
        
        result = get_platform_identifier()
        
        assert result == "linux-amd64"

    def test_get_platform_identifier_unknown(self, mock_platform_machine):
        mock_platform_machine.return_value = "riscv64"
        
        result = get_platform_identifier()
        
        assert result == "linux-unknown"