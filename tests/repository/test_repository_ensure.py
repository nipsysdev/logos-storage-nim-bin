"""Tests for repository ensuring in repository.py."""

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from src.repository import ensure_logos_storage_repo, CommitInfo


class TestEnsureLogosStorageRepo:
    """Test ensure_logos_storage_repo function."""

    def test_ensure_logos_storage_repo_clones_when_not_exists(self, mock_git_clone_responses):
        """Test that ensure_logos_storage_repo clones repository when it doesn't exist."""
        branch = "master"

        with patch("pathlib.Path.exists", return_value=False):
            with patch("src.repository.run_command") as mock_run:
                # Add is_tag() response at the beginning (returncode=1 means not a tag)
                # Then add is_tag() response again at the end (for branch name override check)
                is_tag_response = subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr="")
                mock_run.side_effect = [is_tag_response] + mock_git_clone_responses + [is_tag_response]

                repo_dir, commit_info = ensure_logos_storage_repo(branch)

            assert repo_dir == Path("logos-storage-nim")
            assert isinstance(commit_info, CommitInfo)
            assert commit_info.branch == "master"

    def test_ensure_logos_storage_repo_updates_when_exists(self, mock_git_clone_responses, mock_git_update_responses):
        """Test that ensure_logos_storage_repo updates repository when it exists."""
        branch = "master"

        with patch("pathlib.Path.exists", return_value=True):
            with patch("src.repository.run_command") as mock_run:
                # Add is_tag() response at the beginning (returncode=1 means not a tag)
                # Then add is_tag() response again at the end (for branch name override check)
                is_tag_response = subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr="")
                mock_run.side_effect = [is_tag_response] + mock_git_update_responses + mock_git_clone_responses + [is_tag_response]

                repo_dir, commit_info = ensure_logos_storage_repo(branch)

            assert repo_dir == Path("logos-storage-nim")
            assert isinstance(commit_info, CommitInfo)

    def test_ensure_logos_storage_repo_returns_tuple(self, mock_git_clone_responses):
        """Test that ensure_logos_storage_repo returns a tuple of (Path, CommitInfo)."""
        branch = "develop"

        # Create custom responses for develop branch
        custom_responses = [
            subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=""),  # is_tag() in clone_repository - not a tag
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # git clone --branch develop
            subprocess.CompletedProcess(args=[], returncode=0, stdout="def456789abc123def456789abc123def456789abc\n", stderr=""),  # rev-parse HEAD
            subprocess.CompletedProcess(args=[], returncode=0, stdout="def4567\n", stderr=""),  # rev-parse --short HEAD
            subprocess.CompletedProcess(args=[], returncode=0, stdout="develop\n", stderr=""),  # rev-parse --abbrev-ref HEAD
            subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=""),  # is_tag() at end - not a tag
        ]

        with patch("pathlib.Path.exists", return_value=False):
            with patch("src.repository.run_command") as mock_run:
                mock_run.side_effect = custom_responses

                result = ensure_logos_storage_repo(branch)

            assert isinstance(result, tuple)
            assert len(result) == 2
            assert isinstance(result[0], Path)
            assert isinstance(result[1], CommitInfo)

    def test_ensure_logos_storage_repo_with_custom_branch(self, mock_git_clone_responses):
        """Test that ensure_logos_storage_repo works with custom branch name."""
        branch = "feature/test-branch"

        # Create custom responses for feature branch
        custom_responses = [
            subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=""),  # is_tag() in clone_repository - not a tag
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # git clone --branch feature/test-branch
            subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123def456789abc123def456789abc123def\n", stderr=""),  # rev-parse HEAD
            subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123d\n", stderr=""),  # rev-parse --short HEAD
            subprocess.CompletedProcess(args=[], returncode=0, stdout="feature/test-branch\n", stderr=""),  # rev-parse --abbrev-ref HEAD
            subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=""),  # is_tag() at end - not a tag
        ]

        with patch("pathlib.Path.exists", return_value=False):
            with patch("src.repository.run_command") as mock_run:
                mock_run.side_effect = custom_responses

                repo_dir, commit_info = ensure_logos_storage_repo(branch)

            assert commit_info.branch == "feature/test-branch"

    def test_ensure_logos_storage_repo_clones_at_commit(self):
        """Test that ensure_logos_storage_repo clones repository at specific commit."""
        commit = "abc123def456789abc123def456789abc123def"

        # Custom responses for commit-based clone
        custom_responses = [
            subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=""),  # is_tag() in clone_repository - not a tag
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # clone --no-checkout
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # fetch --all --tags
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # checkout commit
            subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123def456789abc123def456789abc123def\n", stderr=""),  # rev-parse HEAD
            subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123d\n", stderr=""),  # rev-parse --short HEAD
            subprocess.CompletedProcess(args=[], returncode=0, stdout="HEAD\n", stderr=""),  # rev-parse --abbrev-ref HEAD
            subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=""),  # is_tag() at end - not a tag
        ]

        with patch("pathlib.Path.exists", return_value=False):
            with patch("src.repository.run_command") as mock_run:
                mock_run.side_effect = custom_responses

                repo_dir, commit_info = ensure_logos_storage_repo("", commit)

        assert repo_dir == Path("logos-storage-nim")
        assert isinstance(commit_info, CommitInfo)
        assert commit_info.commit == "abc123def456789abc123def456789abc123def"
        assert commit_info.branch == "HEAD"

    def test_ensure_logos_storage_repo_updates_at_commit(self):
        """Test that ensure_logos_storage_repo updates repository to specific commit."""
        commit = "abc123def456789abc123def456789abc123def"

        # Custom responses for commit-based update
        custom_responses = [
            subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=""),  # is_tag() in update_repository - not a tag
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # fetch --all --tags
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # checkout commit
            subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123def456789abc123def456789abc123def\n", stderr=""),  # rev-parse HEAD
            subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123d\n", stderr=""),  # rev-parse --short HEAD
            subprocess.CompletedProcess(args=[], returncode=0, stdout="HEAD\n", stderr=""),  # rev-parse --abbrev-ref HEAD
            subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=""),  # is_tag() at end - not a tag
        ]

        with patch("pathlib.Path.exists", return_value=True):
            with patch("src.repository.validate_commit_exists", return_value=True):
                with patch("src.repository.run_command") as mock_run:
                    mock_run.side_effect = custom_responses

                    repo_dir, commit_info = ensure_logos_storage_repo("", commit)

        assert repo_dir == Path("logos-storage-nim")
        assert isinstance(commit_info, CommitInfo)
        assert commit_info.branch == "HEAD"

    def test_ensure_logos_storage_repo_validates_commit_in_branch(self):
        """Test that ensure_logos_storage_repo validates commit is in branch when both are provided."""
        branch = "master"
        commit = "abc123def456789abc123def456789abc123def"

        # Custom responses for branch + commit
        custom_responses = [
            subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=""),  # is_tag() in clone_repository - not a tag
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # clone --no-checkout
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # fetch --all --tags
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # checkout commit
            subprocess.CompletedProcess(args=[], returncode=0, stdout="  master\n", stderr=""),  # branch --contains
            subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123def456789abc123def456789abc123def\n", stderr=""),  # rev-parse HEAD
            subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123d\n", stderr=""),  # rev-parse --short HEAD
            subprocess.CompletedProcess(args=[], returncode=0, stdout="master\n", stderr=""),  # rev-parse --abbrev-ref HEAD
            subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=""),  # is_tag() at end - not a tag
        ]

        with patch("pathlib.Path.exists", return_value=False):
            with patch("src.repository.validate_commit_exists", return_value=True):
                with patch("src.repository.run_command") as mock_run:
                    mock_run.side_effect = custom_responses

                    repo_dir, commit_info = ensure_logos_storage_repo(branch, commit)

        assert repo_dir == Path("logos-storage-nim")
        assert isinstance(commit_info, CommitInfo)
        assert commit_info.branch == "master"

    def test_ensure_logos_storage_repo_raises_error_when_commit_not_in_branch(self):
        """Test that ensure_logos_storage_repo raises ValueError when commit is not in branch."""
        branch = "master"
        commit = "abc123def456789abc123def456789abc123def"

        # Custom responses where commit is not in master branch
        custom_responses = [
            subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=""),  # is_tag() in clone_repository - not a tag
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # clone --no-checkout
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # fetch --all --tags
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # checkout commit
            subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=""),  # is_tag() at end - not a tag
        ]

        with patch("pathlib.Path.exists", return_value=False):
            with patch("src.repository.validate_commit_exists", return_value=True):
                with patch("src.repository.validate_commit_in_branch", return_value=False):
                    with patch("src.repository.run_command") as mock_run:
                        mock_run.side_effect = custom_responses

                        with pytest.raises(ValueError) as exc_info:
                            ensure_logos_storage_repo(branch, commit)

        assert "does not exist in branch" in str(exc_info.value)

    def test_ensure_logos_storage_repo_with_commit_returns_detached_head_branch(self):
        """Test that ensure_logos_storage_repo returns 'HEAD' as branch when in detached state without branch."""
        commit = "abc123def456789abc123def456789abc123def"

        # Custom responses where rev-parse --abbrev-ref HEAD returns "HEAD"
        custom_responses = [
            subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=""),  # is_tag() in clone_repository - not a tag
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # clone --no-checkout
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # fetch --all --tags
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # checkout commit
            subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123def456789abc123def456789abc123def\n", stderr=""),  # rev-parse HEAD
            subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123d\n", stderr=""),  # rev-parse --short HEAD
            subprocess.CompletedProcess(args=[], returncode=0, stdout="HEAD\n", stderr=""),  # rev-parse --abbrev-ref HEAD
            subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=""),  # is_tag() at end - not a tag
        ]

        with patch("pathlib.Path.exists", return_value=False):
            with patch("src.repository.run_command") as mock_run:
                mock_run.side_effect = custom_responses

                repo_dir, commit_info = ensure_logos_storage_repo("", commit)

        assert commit_info.branch == "HEAD"

    def test_ensure_logos_storage_repo_with_branch_and_commit_preserves_branch_name(self):
        """Test that ensure_logos_storage_repo preserves branch name when both branch and commit are provided."""
        branch = "master"
        commit = "abc123def456789abc123def456789abc123def"

        # Custom responses where rev-parse --abbrev-ref HEAD returns "HEAD" (detached state)
        custom_responses = [
            subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=""),  # is_tag() in clone_repository - not a tag
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # clone --no-checkout
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # fetch --all --tags
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # checkout commit
            subprocess.CompletedProcess(args=[], returncode=0, stdout="  master\n", stderr=""),  # branch --contains
            subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123def456789abc123def456789abc123def\n", stderr=""),  # rev-parse HEAD
            subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123d\n", stderr=""),  # rev-parse --short HEAD
            subprocess.CompletedProcess(args=[], returncode=0, stdout="HEAD\n", stderr=""),  # rev-parse --abbrev-ref HEAD
            subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=""),  # is_tag() at end - not a tag
        ]

        with patch("pathlib.Path.exists", return_value=False):
            with patch("src.repository.run_command") as mock_run:
                mock_run.side_effect = custom_responses

                repo_dir, commit_info = ensure_logos_storage_repo(branch, commit)

        # Branch name should be preserved, not "HEAD"
        assert commit_info.branch == "master"

    def test_ensure_logos_storage_repo_clones_at_tag(self):
        """Test that ensure_logos_storage_repo clones repository at specific tag."""
        tag = "v0.2.5"

        # Custom responses for tag-based clone
        custom_responses = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # is_tag() in clone_repository - is a tag
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # clone --no-checkout
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # fetch --all --tags
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # checkout tag
            subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123def456789abc123def456789abc123def\n", stderr=""),  # rev-parse HEAD
            subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123d\n", stderr=""),  # rev-parse --short HEAD
            subprocess.CompletedProcess(args=[], returncode=0, stdout="HEAD\n", stderr=""),  # rev-parse --abbrev-ref HEAD
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # is_tag() at end - is a tag
        ]

        with patch("pathlib.Path.exists", return_value=False):
            with patch("src.repository.run_command") as mock_run:
                mock_run.side_effect = custom_responses

                repo_dir, commit_info = ensure_logos_storage_repo(tag)

        assert repo_dir == Path("logos-storage-nim")
        assert isinstance(commit_info, CommitInfo)
        assert commit_info.commit == "abc123def456789abc123def456789abc123def"
        assert commit_info.branch == "v0.2.5"

    def test_ensure_logos_storage_repo_updates_at_tag(self):
        """Test that ensure_logos_storage_repo updates repository to specific tag."""
        tag = "v0.2.5"

        # Custom responses for tag-based update
        custom_responses = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # is_tag() in update_repository - is a tag
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # fetch --all --tags
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # checkout tag
            subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123def456789abc123def456789abc123def\n", stderr=""),  # rev-parse HEAD
            subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123d\n", stderr=""),  # rev-parse --short HEAD
            subprocess.CompletedProcess(args=[], returncode=0, stdout="HEAD\n", stderr=""),  # rev-parse --abbrev-ref HEAD
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # is_tag() at end - is a tag
        ]

        with patch("pathlib.Path.exists", return_value=True):
            with patch("src.repository.run_command") as mock_run:
                mock_run.side_effect = custom_responses

                repo_dir, commit_info = ensure_logos_storage_repo(tag)

        assert repo_dir == Path("logos-storage-nim")
        assert isinstance(commit_info, CommitInfo)
        assert commit_info.branch == "v0.2.5"