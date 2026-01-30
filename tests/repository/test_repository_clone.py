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
            # Mock is_tag() to return False (not a tag)
            mock_run.return_value.returncode = 1
            clone_repository(target_dir, branch)

        # First call is is_tag() check, second is git clone
        assert mock_run.call_count == 2
        # Verify the clone call (second call)
        clone_call = mock_run.call_args_list[1][0][0]
        assert clone_call == [
            "git", "clone", "--branch", branch,
            "https://github.com/logos-storage/logos-storage-nim.git",
            str(target_dir)
        ]

    def test_clone_repository_with_master_branch(self):
        target_dir = Path("/tmp/test-repo")
        branch = "master"

        with patch("src.repository.run_command") as mock_run:
            # Mock is_tag() to return False (not a tag)
            mock_run.return_value.returncode = 1
            clone_repository(target_dir, branch)

        # First call is is_tag() check, second is git clone
        assert mock_run.call_count == 2
        call_args = mock_run.call_args_list[1][0][0]
        assert call_args[2] == "--branch"
        assert call_args[3] == "master"

    def test_clone_repository_with_custom_branch(self):
        target_dir = Path("/tmp/test-repo")
        branch = "feature/test"

        with patch("src.repository.run_command") as mock_run:
            # Mock is_tag() to return False (not a tag)
            mock_run.return_value.returncode = 1
            clone_repository(target_dir, branch)

        # First call is is_tag() check, second is git clone
        assert mock_run.call_count == 2
        call_args = mock_run.call_args_list[1][0][0]
        assert call_args[3] == "feature/test"

    def test_clone_repository_at_specific_commit(self):
        """Test that clone_repository clones at a specific commit."""
        target_dir = Path("/tmp/test-repo")
        commit = "abc123def456789abc123def456789abc123def"

        with patch("src.repository.run_command") as mock_run:
            # Mock is_tag() to return False (not a tag)
            mock_run.return_value.returncode = 1
            clone_repository(target_dir, "master", commit)

        # Now 4 calls: is_tag check + clone + fetch + checkout
        assert mock_run.call_count == 4

        # First call: is_tag() check
        first_call = mock_run.call_args_list[0][0][0]
        assert first_call[0] == "git"
        assert first_call[1] == "ls-remote"
        assert "--tags" in first_call

        # Second call: git clone --no-checkout
        second_call = mock_run.call_args_list[1][0][0]
        assert second_call[0] == "git"
        assert second_call[1] == "clone"
        assert "--no-checkout" in second_call

        # Third call: git fetch --all --tags
        third_call = mock_run.call_args_list[2][0][0]
        assert third_call[0] == "git"
        assert third_call[1] == "-C"
        assert third_call[3] == "fetch"
        assert "--all" in third_call
        assert "--tags" in third_call

        # Fourth call: git checkout <commit>
        fourth_call = mock_run.call_args_list[3][0][0]
        assert fourth_call[0] == "git"
        assert fourth_call[1] == "-C"
        assert fourth_call[3] == "checkout"
        assert fourth_call[4] == commit

    def test_clone_repository_at_commit_uses_no_checkout_flag(self):
        """Test that clone_repository uses --no-checkout flag when cloning at commit."""
        target_dir = Path("/tmp/test-repo")
        commit = "abc123def456789abc123def456789abc123def"

        with patch("src.repository.run_command") as mock_run:
            # Mock is_tag() to return False (not a tag)
            mock_run.return_value.returncode = 1
            clone_repository(target_dir, "master", commit)

        # Second call is the clone command (first is is_tag check)
        clone_call = mock_run.call_args_list[1][0][0]
        assert "--no-checkout" in clone_call
        assert "--branch" not in clone_call

    def test_clone_repository_at_commit_fetches_all_objects(self):
        """Test that clone_repository fetches all objects when cloning at commit."""
        target_dir = Path("/tmp/test-repo")
        commit = "abc123def456789abc123def456789abc123def"

        with patch("src.repository.run_command") as mock_run:
            # Mock is_tag() to return False (not a tag)
            mock_run.return_value.returncode = 1
            clone_repository(target_dir, "master", commit)

        # Third call is the fetch command (first is is_tag, second is clone)
        fetch_call = mock_run.call_args_list[2][0][0]
        assert "fetch" in fetch_call
        assert "--all" in fetch_call
        assert "--tags" in fetch_call

    def test_clone_repository_at_commit_checkouts_commit(self):
        """Test that clone_repository checkouts the specific commit."""
        target_dir = Path("/tmp/test-repo")
        commit = "abc123def456789abc123def456789abc123def"

        with patch("src.repository.run_command") as mock_run:
            # Mock is_tag() to return False (not a tag)
            mock_run.return_value.returncode = 1
            clone_repository(target_dir, "master", commit)

        # Fourth call is the checkout command (first is is_tag, second is clone, third is fetch)
        checkout_call = mock_run.call_args_list[3][0][0]
        assert checkout_call[3] == "checkout"
        assert checkout_call[4] == commit