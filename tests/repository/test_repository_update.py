"""Tests for repository updating in repository.py."""

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from src.repository import update_repository


class TestUpdateRepository:
    """Test update_repository function."""

    def test_update_repository_fetches_origin(self, mock_git_update_responses):
        """Test that update_repository fetches from origin."""
        repo_dir = Path("/tmp/test-repo")
        branch = "master"
        
        with patch("src.repository.run_command") as mock_run:
            mock_run.side_effect = mock_git_update_responses
            
            update_repository(repo_dir, branch)
        
        assert mock_run.call_args_list[0][0][0] == ["git", "-C", str(repo_dir), "fetch", "origin"]

    def test_update_repository_checks_local_branch(self, mock_git_update_responses):
        """Test that update_repository checks if local branch exists."""
        repo_dir = Path("/tmp/test-repo")
        branch = "master"
        
        with patch("src.repository.run_command") as mock_run:
            mock_run.side_effect = mock_git_update_responses
            
            update_repository(repo_dir, branch)
        
        assert mock_run.call_args_list[1][0][0] == [
            "git", "-C", str(repo_dir), "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"
        ]

    def test_update_repository_checks_remote_branch(self):
        """Test that update_repository checks if remote branch exists when local doesn't."""
        repo_dir = Path("/tmp/test-repo")
        branch = "master"
        
        # Custom responses where local branch doesn't exist
        custom_responses = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # fetch
            subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=""),  # local branch not found
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # remote branch exists
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # checkout
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # pull
        ]
        
        with patch("src.repository.run_command") as mock_run:
            mock_run.side_effect = custom_responses
            
            update_repository(repo_dir, branch)
        
        assert mock_run.call_args_list[2][0][0] == [
            "git", "-C", str(repo_dir), "show-ref", "--verify", "--quiet", f"refs/remotes/origin/{branch}"
        ]

    def test_update_repository_raises_error_when_branch_not_found(self):
        """Test that update_repository raises ValueError when branch is not found locally or remotely."""
        repo_dir = Path("/tmp/test-repo")
        branch = "nonexistent"
        
        # Custom responses where branch doesn't exist anywhere
        custom_responses = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # fetch
            subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=""),  # local not found
            subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=""),  # remote not found
        ]
        
        with patch("src.repository.run_command") as mock_run:
            mock_run.side_effect = custom_responses
            
            with pytest.raises(ValueError) as exc_info:
                update_repository(repo_dir, branch)
        
        assert "Branch 'nonexistent' not found" in str(exc_info.value)

    def test_update_repository_checkouts_branch(self, mock_git_update_responses):
        """Test that update_repository checks out the specified branch."""
        repo_dir = Path("/tmp/test-repo")
        branch = "develop"
        
        with patch("src.repository.run_command") as mock_run:
            mock_run.side_effect = mock_git_update_responses
            
            update_repository(repo_dir, branch)
        
        assert mock_run.call_args_list[3][0][0] == ["git", "-C", str(repo_dir), "checkout", branch]

    def test_update_repository_pulls_from_origin(self, mock_git_update_responses):
        """Test that update_repository pulls from origin for the specified branch."""
        repo_dir = Path("/tmp/test-repo")
        branch = "master"
        
        with patch("src.repository.run_command") as mock_run:
            mock_run.side_effect = mock_git_update_responses
            
            update_repository(repo_dir, branch)
        
        assert mock_run.call_args_list[4][0][0] == ["git", "-C", str(repo_dir), "pull", "origin", branch]

    def test_update_repository_at_specific_commit(self):
        """Test that update_repository updates to a specific commit."""
        repo_dir = Path("/tmp/test-repo")
        commit = "abc123def456789abc123def456789abc123def"
        
        with patch("src.repository.validate_commit_exists", return_value=True):
            with patch("src.repository.run_command") as mock_run:
                update_repository(repo_dir, "master", commit)
        
        assert mock_run.call_count == 2
        
        # First call: git fetch --all --tags
        first_call = mock_run.call_args_list[0][0][0]
        assert first_call[0] == "git"
        assert first_call[1] == "-C"
        assert first_call[3] == "fetch"
        assert "--all" in first_call
        assert "--tags" in first_call
        
        # Second call: git checkout <commit>
        second_call = mock_run.call_args_list[1][0][0]
        assert second_call[0] == "git"
        assert second_call[1] == "-C"
        assert second_call[3] == "checkout"
        assert second_call[4] == commit

    def test_update_repository_at_commit_validates_commit_exists(self):
        """Test that update_repository validates commit exists before checkout."""
        repo_dir = Path("/tmp/test-repo")
        commit = "abc123def456789abc123def456789abc123def"
        
        with patch("src.repository.validate_commit_exists") as mock_validate:
            mock_validate.return_value = True
            with patch("src.repository.run_command"):
                update_repository(repo_dir, "master", commit)
        
        mock_validate.assert_called_once_with(repo_dir, commit)

    def test_update_repository_at_commit_raises_error_for_invalid_commit(self):
        """Test that update_repository raises ValueError for invalid commit."""
        repo_dir = Path("/tmp/test-repo")
        commit = "invalidcommit123"
        
        with patch("src.repository.validate_commit_exists", return_value=False):
            with patch("src.repository.run_command"):
                with pytest.raises(ValueError) as exc_info:
                    update_repository(repo_dir, "master", commit)
        
        assert "Commit 'invalidcommit123' not found in repository" in str(exc_info.value)

    def test_update_repository_at_commit_fetches_all_objects(self):
        """Test that update_repository fetches all objects when updating to commit."""
        repo_dir = Path("/tmp/test-repo")
        commit = "abc123def456789abc123def456789abc123def"
        
        with patch("src.repository.validate_commit_exists", return_value=True):
            with patch("src.repository.run_command") as mock_run:
                update_repository(repo_dir, "master", commit)
        
        first_call = mock_run.call_args_list[0][0][0]
        assert "fetch" in first_call
        assert "--all" in first_call
        assert "--tags" in first_call