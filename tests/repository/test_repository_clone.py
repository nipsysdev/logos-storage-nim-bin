"""Tests for repository cloning in repository.py."""

from pathlib import Path
from unittest.mock import patch

import pytest

from src.repository import clone_repository


class TestCloneRepository:
    """Test clone_repository function."""

    def test_clone_repository_calls_git_clone(self):
        target_dir = Path("/tmp/test-repo")
        branch = "develop"
        
        with patch("src.repository.run_command") as mock_run:
            clone_repository(target_dir, branch)
        
        mock_run.assert_called_once_with([
            "git", "clone", "--branch", branch,
            "https://github.com/logos-storage/logos-storage-nim.git",
            str(target_dir)
        ])

    def test_clone_repository_with_master_branch(self):
        target_dir = Path("/tmp/test-repo")
        branch = "master"
        
        with patch("src.repository.run_command") as mock_run:
            clone_repository(target_dir, branch)
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[2] == "--branch"
        assert call_args[3] == "master"

    def test_clone_repository_with_custom_branch(self):
        target_dir = Path("/tmp/test-repo")
        branch = "feature/test"
        
        with patch("src.repository.run_command") as mock_run:
            clone_repository(target_dir, branch)
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[3] == "feature/test"