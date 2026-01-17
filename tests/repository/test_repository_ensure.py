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
                mock_run.side_effect = mock_git_clone_responses
                
                repo_dir, commit_info = ensure_logos_storage_repo(branch)
            
            assert repo_dir == Path("logos-storage-nim")
            assert isinstance(commit_info, CommitInfo)
            assert commit_info.branch == "master"

    def test_ensure_logos_storage_repo_updates_when_exists(self, mock_git_clone_responses, mock_git_update_responses):
        """Test that ensure_logos_storage_repo updates repository when it exists."""
        branch = "master"
        
        with patch("pathlib.Path.exists", return_value=True):
            with patch("src.repository.run_command") as mock_run:
                mock_run.side_effect = mock_git_update_responses + mock_git_clone_responses
                
                repo_dir, commit_info = ensure_logos_storage_repo(branch)
            
            assert repo_dir == Path("logos-storage-nim")
            assert isinstance(commit_info, CommitInfo)

    def test_ensure_logos_storage_repo_returns_tuple(self, mock_git_clone_responses):
        """Test that ensure_logos_storage_repo returns a tuple of (Path, CommitInfo)."""
        branch = "develop"
        
        # Create custom responses for develop branch
        custom_responses = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout="def456789abc123def456789abc123def456789abc\n", stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout="def4567\n", stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout="develop\n", stderr=""),
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
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123def456789abc123def456789abc123def\n", stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123d\n", stderr=""),
            subprocess.CompletedProcess(args=[], returncode=0, stdout="feature/test-branch\n", stderr=""),
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
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # clone --no-checkout
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # fetch --all --tags
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # checkout commit
            subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123def456789abc123def456789abc123def\n", stderr=""),  # rev-parse HEAD
            subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123d\n", stderr=""),  # rev-parse --short HEAD
            subprocess.CompletedProcess(args=[], returncode=0, stdout="HEAD\n", stderr=""),  # rev-parse --abbrev-ref HEAD
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
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # fetch --all --tags
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # checkout commit
            subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123def456789abc123def456789abc123def\n", stderr=""),  # rev-parse HEAD
            subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123d\n", stderr=""),  # rev-parse --short HEAD
            subprocess.CompletedProcess(args=[], returncode=0, stdout="HEAD\n", stderr=""),  # rev-parse --abbrev-ref HEAD
        ]
        
        with patch("pathlib.Path.exists", return_value=True):
            with patch("src.repository.validate_commit_exists", return_value=True):
                with patch("src.repository.run_command") as mock_run:
                    mock_run.side_effect = custom_responses
                    
                    repo_dir, commit_info = ensure_logos_storage_repo("", commit)
        
        assert repo_dir == Path("logos-storage-nim")
        assert isinstance(commit_info, CommitInfo)
        assert commit_info.branch == "HEAD"

    def test_ensure_logos_storage_repo_raises_error_when_both_branch_and_commit(self):
        """Test that ensure_logos_storage_repo raises ValueError when both branch and commit are specified."""
        branch = "master"
        commit = "abc123def456789abc123def456789abc123def"
        
        with pytest.raises(ValueError) as exc_info:
            ensure_logos_storage_repo(branch, commit)
        
        assert "Cannot specify both branch and commit" in str(exc_info.value)

    def test_ensure_logos_storage_repo_with_commit_returns_detached_head_branch(self):
        """Test that ensure_logos_storage_repo returns 'HEAD' as branch when in detached state."""
        commit = "abc123def456789abc123def456789abc123def"
        
        # Custom responses where rev-parse --abbrev-ref HEAD returns "HEAD"
        custom_responses = [
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # clone --no-checkout
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # fetch --all --tags
            subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # checkout commit
            subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123def456789abc123def456789abc123def\n", stderr=""),  # rev-parse HEAD
            subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123d\n", stderr=""),  # rev-parse --short HEAD
            subprocess.CompletedProcess(args=[], returncode=0, stdout="HEAD\n", stderr=""),  # rev-parse --abbrev-ref HEAD
        ]
        
        with patch("pathlib.Path.exists", return_value=False):
            with patch("src.repository.run_command") as mock_run:
                mock_run.side_effect = custom_responses
                
                repo_dir, commit_info = ensure_logos_storage_repo("", commit)
        
        assert commit_info.branch == "HEAD"