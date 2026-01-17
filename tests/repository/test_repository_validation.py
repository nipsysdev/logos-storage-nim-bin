"""Tests for repository validation in repository.py."""

from pathlib import Path
from unittest.mock import patch

import pytest

from src.repository import validate_commit_exists


class TestValidateCommitExists:
    """Test validate_commit_exists function."""

    def test_validate_commit_exists_returns_true_for_valid_commit(self):
        """Test that validate_commit_exists returns True for a valid commit."""
        repo_dir = Path("/tmp/test-repo")
        commit = "abc123def456789abc123def456789abc123def"
        
        with patch("src.repository.run_command") as mock_run:
            mock_run.return_value.returncode = 0
            
            result = validate_commit_exists(repo_dir, commit)
        
        assert result is True
        mock_run.assert_called_once_with(
            ["git", "-C", str(repo_dir), "cat-file", "-e", commit],
            check=False
        )

    def test_validate_commit_exists_returns_false_for_invalid_commit(self):
        """Test that validate_commit_exists returns False for an invalid commit."""
        repo_dir = Path("/tmp/test-repo")
        commit = "invalidcommit123"
        
        with patch("src.repository.run_command") as mock_run:
            mock_run.return_value.returncode = 1
            
            result = validate_commit_exists(repo_dir, commit)
        
        assert result is False
        mock_run.assert_called_once_with(
            ["git", "-C", str(repo_dir), "cat-file", "-e", commit],
            check=False
        )

    def test_validate_commit_exists_with_short_hash(self):
        """Test that validate_commit_exists works with short commit hashes."""
        repo_dir = Path("/tmp/test-repo")
        commit = "abc123d"
        
        with patch("src.repository.run_command") as mock_run:
            mock_run.return_value.returncode = 0
            
            result = validate_commit_exists(repo_dir, commit)
        
        assert result is True
        mock_run.assert_called_once_with(
            ["git", "-C", str(repo_dir), "cat-file", "-e", commit],
            check=False
        )

    def test_validate_commit_exists_with_full_hash(self):
        """Test that validate_commit_exists works with full commit hashes."""
        repo_dir = Path("/tmp/test-repo")
        commit = "abc123def456789abc123def456789abc123def456"
        
        with patch("src.repository.run_command") as mock_run:
            mock_run.return_value.returncode = 0
            
            result = validate_commit_exists(repo_dir, commit)
        
        assert result is True
        mock_run.assert_called_once_with(
            ["git", "-C", str(repo_dir), "cat-file", "-e", commit],
            check=False
        )