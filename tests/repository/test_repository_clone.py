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

    def test_clone_repository_at_specific_commit(self):
        """Test that clone_repository clones at a specific commit."""
        target_dir = Path("/tmp/test-repo")
        commit = "abc123def456789abc123def456789abc123def"
        
        with patch("src.repository.run_command") as mock_run:
            clone_repository(target_dir, "master", commit)
        
        assert mock_run.call_count == 3
        
        # First call: git clone --no-checkout
        first_call = mock_run.call_args_list[0][0][0]
        assert first_call[0] == "git"
        assert first_call[1] == "clone"
        assert "--no-checkout" in first_call
        
        # Second call: git fetch --all --tags
        second_call = mock_run.call_args_list[1][0][0]
        assert second_call[0] == "git"
        assert second_call[1] == "-C"
        assert second_call[3] == "fetch"
        assert "--all" in second_call
        assert "--tags" in second_call
        
        # Third call: git checkout <commit>
        third_call = mock_run.call_args_list[2][0][0]
        assert third_call[0] == "git"
        assert third_call[1] == "-C"
        assert third_call[3] == "checkout"
        assert third_call[4] == commit

    def test_clone_repository_at_commit_uses_no_checkout_flag(self):
        """Test that clone_repository uses --no-checkout flag when cloning at commit."""
        target_dir = Path("/tmp/test-repo")
        commit = "abc123def456789abc123def456789abc123def"
        
        with patch("src.repository.run_command") as mock_run:
            clone_repository(target_dir, "master", commit)
        
        first_call = mock_run.call_args_list[0][0][0]
        assert "--no-checkout" in first_call
        assert "--branch" not in first_call

    def test_clone_repository_at_commit_fetches_all_objects(self):
        """Test that clone_repository fetches all objects when cloning at commit."""
        target_dir = Path("/tmp/test-repo")
        commit = "abc123def456789abc123def456789abc123def"
        
        with patch("src.repository.run_command") as mock_run:
            clone_repository(target_dir, "master", commit)
        
        second_call = mock_run.call_args_list[1][0][0]
        assert "fetch" in second_call
        assert "--all" in second_call
        assert "--tags" in second_call

    def test_clone_repository_at_commit_checkouts_commit(self):
        """Test that clone_repository checkouts the specific commit."""
        target_dir = Path("/tmp/test-repo")
        commit = "abc123def456789abc123def456789abc123def"
        
        with patch("src.repository.run_command") as mock_run:
            clone_repository(target_dir, "master", commit)
        
        third_call = mock_run.call_args_list[2][0][0]
        assert third_call[3] == "checkout"
        assert third_call[4] == commit