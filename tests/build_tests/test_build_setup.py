"""Tests for build setup in build.py."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from build import main
from src.repository import CommitInfo


class TestMainSetup:
    """Test main function setup and initialization."""

    def test_main_gets_platform_identifier(self, mock_build_setup):
        """Test that main() calls get_platform_identifier()."""
        main()
        
        mock_build_setup["mock_platform"].assert_called_once()

    def test_main_gets_branch_from_environment(self, mock_build_setup):
        """Test that main() uses BRANCH environment variable when set."""
        with patch.dict(os.environ, {"BRANCH": "develop"}, clear=False):
            os.environ.pop("COMMIT", None)
            main()
        
        mock_build_setup["mock_repo"].assert_called_once_with("develop", None)

    def test_main_uses_default_branch_when_not_set(self, mock_build_setup):
        """Test that main() uses 'master' as default branch when BRANCH is not set."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("BRANCH", None)
            os.environ.pop("COMMIT", None)
            
            main()
        
        mock_build_setup["mock_repo"].assert_called_once_with("master", None)

    def test_main_configures_reproducible_environment(self, mock_build_setup):
        """Test that main() calls configure_reproducible_environment()."""
        main()
        
        mock_build_setup["mock_config"].assert_called_once()

    def test_main_ensures_repository(self, mock_build_setup):
        """Test that main() calls ensure_logos_storage_repo()."""
        main()
        
        mock_build_setup["mock_repo"].assert_called_once()