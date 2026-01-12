"""Tests for commit information in repository.py."""

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from src.repository import CommitInfo, get_commit_info


class TestCommitInfo:
    """Test CommitInfo dataclass."""

    def test_commit_info_creation(self):
        """Test that CommitInfo can be created with correct values."""
        info = CommitInfo(
            commit="abc123def456789abc123def456789abc123def",
            commit_short="abc123d",
            branch="master"
        )
        
        assert info.commit == "abc123def456789abc123def456789abc123def"
        assert info.commit_short == "abc123d"
        assert info.branch == "master"

    def test_commit_info_equality(self):
        """Test that two CommitInfo objects with same values are equal."""
        info1 = CommitInfo(
            commit="abc123def456789abc123def456789abc123def",
            commit_short="abc123d",
            branch="master"
        )
        info2 = CommitInfo(
            commit="abc123def456789abc123def456789abc123def",
            commit_short="abc123d",
            branch="master"
        )
        
        assert info1 == info2


class TestGetCommitInfo:
    """Test get_commit_info function."""

    def test_get_commit_info_returns_commit_info(self):
        """Test that get_commit_info returns CommitInfo with correct values."""
        repo_dir = Path("/tmp/test-repo")
        
        with patch("src.repository.run_command") as mock_run:
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123def456789abc123def456789abc123def\n", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123d\n", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="master\n", stderr=""),
            ]
            
            result = get_commit_info(repo_dir)
        
        assert isinstance(result, CommitInfo)
        assert result.commit == "abc123def456789abc123def456789abc123def"
        assert result.commit_short == "abc123d"
        assert result.branch == "master"

    def test_get_commit_info_calls_rev_parse_head(self):
        """Test that get_commit_info calls git rev-parse HEAD."""
        repo_dir = Path("/tmp/test-repo")
        
        with patch("src.repository.run_command") as mock_run:
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123def456789abc123def456789abc123def\n", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123d\n", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="master\n", stderr=""),
            ]
            
            get_commit_info(repo_dir)
        
        assert mock_run.call_args_list[0][0][0] == ["git", "-C", str(repo_dir), "rev-parse", "HEAD"]

    def test_get_commit_info_calls_rev_parse_short_head(self):
        """Test that get_commit_info calls git rev-parse --short HEAD."""
        repo_dir = Path("/tmp/test-repo")
        
        with patch("src.repository.run_command") as mock_run:
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123def456789abc123def456789abc123def\n", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123d\n", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="master\n", stderr=""),
            ]
            
            get_commit_info(repo_dir)
        
        assert mock_run.call_args_list[1][0][0] == ["git", "-C", str(repo_dir), "rev-parse", "--short", "HEAD"]

    def test_get_commit_info_calls_rev_parse_abbrev_ref_head(self):
        """Test that get_commit_info calls git rev-parse --abbrev-ref HEAD."""
        repo_dir = Path("/tmp/test-repo")
        
        with patch("src.repository.run_command") as mock_run:
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123def456789abc123def456789abc123def\n", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123d\n", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="master\n", stderr=""),
            ]
            
            get_commit_info(repo_dir)
        
        assert mock_run.call_args_list[2][0][0] == ["git", "-C", str(repo_dir), "rev-parse", "--abbrev-ref", "HEAD"]

    def test_get_commit_info_with_detached_head(self):
        """Test that get_commit_info returns 'HEAD' as branch when in detached HEAD state."""
        repo_dir = Path("/tmp/test-repo")
        
        with patch("src.repository.run_command") as mock_run:
            mock_run.side_effect = [
                subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123def456789abc123def456789abc123def\n", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123d\n", stderr=""),
                subprocess.CompletedProcess(args=[], returncode=0, stdout="HEAD\n", stderr=""),
            ]
            
            result = get_commit_info(repo_dir)
        
        assert result.branch == "HEAD"