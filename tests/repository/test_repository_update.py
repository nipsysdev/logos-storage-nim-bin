"""Tests for repository updating in repository.py."""

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from src.repository import update_repository


class TestUpdateRepository:
    """Test update_repository function."""

    def test_update_repository_fetches_origin(self):
        """Test that update_repository fetches from origin."""
        repo_dir = Path("/tmp/test-repo")
        branch = "master"
        
        with patch("src.repository.run_command") as mock_run:
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # fetch
                subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # check local
                subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # check remote
                subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # checkout
                subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # pull
            ]
            
            update_repository(repo_dir, branch)
        
        assert mock_run.call_args_list[0][0][0] == ["git", "-C", str(repo_dir), "fetch", "origin"]

    def test_update_repository_checks_local_branch(self):
        """Test that update_repository checks if local branch exists."""
        repo_dir = Path("/tmp/test-repo")
        branch = "master"
        
        with patch("src.repository.run_command") as mock_run:
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # fetch
                subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # check local
                subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # check remote
                subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # checkout
                subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # pull
            ]
            
            update_repository(repo_dir, branch)
        
        assert mock_run.call_args_list[1][0][0] == [
            "git", "-C", str(repo_dir), "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"
        ]

    def test_update_repository_checks_remote_branch(self):
        """Test that update_repository checks if remote branch exists when local doesn't."""
        repo_dir = Path("/tmp/test-repo")
        branch = "master"
        
        with patch("src.repository.run_command") as mock_run:
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),
            ]
            
            update_repository(repo_dir, branch)
        
        assert mock_run.call_args_list[2][0][0] == [
            "git", "-C", str(repo_dir), "show-ref", "--verify", "--quiet", f"refs/remotes/origin/{branch}"
        ]

    def test_update_repository_raises_error_when_branch_not_found(self):
        """Test that update_repository raises ValueError when branch is not found locally or remotely."""
        repo_dir = Path("/tmp/test-repo")
        branch = "nonexistent"
        
        with patch("src.repository.run_command") as mock_run:
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr=""),
            ]
            
            with pytest.raises(ValueError) as exc_info:
                update_repository(repo_dir, branch)
        
        assert "Branch 'nonexistent' not found" in str(exc_info.value)

    def test_update_repository_checkouts_branch(self):
        """Test that update_repository checks out the specified branch."""
        repo_dir = Path("/tmp/test-repo")
        branch = "develop"
        
        with patch("src.repository.run_command") as mock_run:
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # fetch
                subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # check local
                subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # check remote
                subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # checkout
                subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # pull
            ]
            
            update_repository(repo_dir, branch)
        
        assert mock_run.call_args_list[3][0][0] == ["git", "-C", str(repo_dir), "checkout", branch]

    def test_update_repository_pulls_from_origin(self):
        """Test that update_repository pulls from origin for the specified branch."""
        repo_dir = Path("/tmp/test-repo")
        branch = "master"
        
        with patch("src.repository.run_command") as mock_run:
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # fetch
                subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # check local
                subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # check remote
                subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # checkout
                subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # pull
            ]
            
            update_repository(repo_dir, branch)
        
        assert mock_run.call_args_list[4][0][0] == ["git", "-C", str(repo_dir), "pull", "origin", branch]