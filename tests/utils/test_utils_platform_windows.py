"""Test Windows platform identifier functionality."""

import pytest
from unittest.mock import patch
from src.utils import get_platform_identifier


class TestPlatformIdentifierWindows:
    """Test get_platform_identifier for Windows platform."""

    @patch('platform.system', return_value='Windows')
    @patch('platform.machine', return_value='AMD64')
    def test_get_platform_identifier_windows_amd64(self, mock_machine, mock_system):
        """Test that get_platform_identifier returns windows-amd64 for Windows AMD64."""
        result = get_platform_identifier()
        assert result == "windows-amd64"

    @patch('platform.system', return_value='Windows')
    @patch('platform.machine', return_value='x86_64')
    def test_get_platform_identifier_windows_x86_64(self, mock_machine, mock_system):
        """Test that get_platform_identifier returns windows-amd64 for Windows x86_64."""
        result = get_platform_identifier()
        assert result == "windows-amd64"

    @patch('platform.system', return_value='Windows')
    @patch('platform.machine', return_value='amd64')
    def test_get_platform_identifier_windows_amd64_lowercase(self, mock_machine, mock_system):
        """Test that get_platform_identifier returns windows-amd64 for Windows amd64 (lowercase)."""
        result = get_platform_identifier()
        assert result == "windows-amd64"

    @patch('platform.system', return_value='Windows')
    @patch('platform.machine', return_value='ARM64')
    def test_get_platform_identifier_windows_arm64(self, mock_machine, mock_system):
        """Test that get_platform_identifier returns windows-arm64 for Windows ARM64."""
        result = get_platform_identifier()
        assert result == "windows-arm64"

    @patch('platform.system', return_value='Windows')
    @patch('platform.machine', return_value='aarch64')
    def test_get_platform_identifier_windows_aarch64(self, mock_machine, mock_system):
        """Test that get_platform_identifier returns windows-arm64 for Windows aarch64."""
        result = get_platform_identifier()
        assert result == "windows-arm64"

    @patch('platform.system', return_value='Windows')
    @patch('platform.machine', return_value='arm64')
    def test_get_platform_identifier_windows_arm64_lowercase(self, mock_machine, mock_system):
        """Test that get_platform_identifier returns windows-arm64 for Windows arm64 (lowercase)."""
        result = get_platform_identifier()
        assert result == "windows-arm64"

    @patch('platform.system', return_value='Windows')
    @patch('platform.machine', return_value='i686')
    def test_get_platform_identifier_windows_i686(self, mock_machine, mock_system):
        """Test that get_platform_identifier returns windows-unknown for Windows i686."""
        result = get_platform_identifier()
        assert result == "windows-unknown"

    @patch('platform.system', return_value='Windows')
    @patch('platform.machine', return_value='unknown')
    def test_get_platform_identifier_windows_unknown(self, mock_machine, mock_system):
        """Test that get_platform_identifier returns windows-unknown for unknown Windows architecture."""
        result = get_platform_identifier()
        assert result == "windows-unknown"