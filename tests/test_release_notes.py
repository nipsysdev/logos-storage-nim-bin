"""Unit tests for release_notes module."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess

from src.release_notes import (
    extract_pr_number,
    extract_author,
    format_commit_entry,
    get_commits_between,
    format_release_notes,
)


class TestExtractPrNumber:
    """Test PR number extraction from commit messages."""

    def test_extract_pr_number_with_pr(self):
        """Test extracting PR number from commit message with PR."""
        result = extract_pr_number("feat: add feature (#123)")
        assert result == 123

    def test_extract_pr_number_with_pr_in_middle(self):
        """Test extracting PR number from commit message with PR in middle."""
        result = extract_pr_number("fix: bug (#456) fix")
        assert result == 456

    def test_extract_pr_number_without_pr(self):
        """Test extracting PR number from commit message without PR."""
        result = extract_pr_number("feat: add feature")
        assert result is None

    def test_extract_pr_number_with_multiple_prs(self):
        """Test extracting first PR number from commit message with multiple PRs."""
        result = extract_pr_number("feat: add feature (#123) and (#456)")
        assert result == 123

    def test_extract_pr_number_with_large_pr_number(self):
        """Test extracting large PR number."""
        result = extract_pr_number("feat: add feature (#9999)")
        assert result == 9999


class TestExtractAuthor:
    """Test author extraction from commit messages."""

    def test_extract_author_with_author(self):
        """Test extracting author from commit message with author."""
        result = extract_author("feat: add feature (John Doe)")
        assert result == "John Doe"

    def test_extract_author_without_author(self):
        """Test extracting author from commit message without author."""
        result = extract_author("feat: add feature")
        assert result is None

    def test_extract_author_with_pr_and_author(self):
        """Test extracting author from commit message with PR and author."""
        result = extract_author("feat: add feature (#123) (John Doe)")
        assert result == "John Doe"

    def test_extract_author_with_complex_name(self):
        """Test extracting author with complex name."""
        result = extract_author("feat: add feature (John A. Doe Jr.)")
        assert result == "John A. Doe Jr."

    def test_extract_author_with_username(self):
        """Test extracting author with username."""
        result = extract_author("feat: add feature (@johndoe)")
        assert result == "@johndoe"


class TestFormatCommitEntry:
    """Test commit entry formatting."""

    def test_format_commit_entry_with_pr(self):
        """Test formatting commit entry with PR number."""
        result = format_commit_entry(
            "abc123",
            "feat(marketplace): add status l2 (Linea) network (#1160)",
            "2-towns"
        )
        expected = (
            "* feat(marketplace): add status l2 (Linea) network "
            "by @2-towns in https://github.com/logos-storage/logos-storage-nim/pull/1160"
        )
        assert result == expected

    def test_format_commit_entry_without_pr(self):
        """Test formatting commit entry without PR number."""
        result = format_commit_entry(
            "def456",
            "chore: update dependencies",
            "johndoe"
        )
        expected = (
            "* chore: update dependencies "
            "by @johndoe in https://github.com/logos-storage/logos-storage-nim/commit/def456"
        )
        assert result == expected

    def test_format_commit_entry_with_custom_repo(self):
        """Test formatting commit entry with custom repository."""
        result = format_commit_entry(
            "abc123",
            "feat: add feature (#123)",
            "johndoe",
            repo_owner="custom-owner",
            repo_name="custom-repo"
        )
        expected = (
            "* feat: add feature "
            "by @johndoe in https://github.com/custom-owner/custom-repo/pull/123"
        )
        assert result == expected

    def test_format_commit_entry_with_pr_and_author_in_message(self):
        """Test formatting commit entry with PR and author in message."""
        result = format_commit_entry(
            "abc123",
            "fix(tests): auto import all tests files and fix forgotten tests (#1281)",
            "markspanbroek"
        )
        expected = (
            "* fix(tests): auto import all tests files and fix forgotten tests "
            "by @markspanbroek in https://github.com/logos-storage/logos-storage-nim/pull/1281"
        )
        assert result == expected

    def test_format_commit_entry_with_chore_type(self):
        """Test formatting commit entry with chore type."""
        result = format_commit_entry(
            "abc123",
            "chore(marketplace): use hardhat ignition (#1195)",
            "2-towns"
        )
        expected = (
            "* chore(marketplace): use hardhat ignition "
            "by @2-towns in https://github.com/logos-storage/logos-storage-nim/pull/1195"
        )
        assert result == expected

    def test_format_commit_entry_with_fix_type(self):
        """Test formatting commit entry with fix type."""
        result = format_commit_entry(
            "abc123",
            "fix(ci): remove \"update\" to gcc-14 on windows (#1288)",
            "markspanbroek"
        )
        expected = (
            "* fix(ci): remove \"update\" to gcc-14 on windows "
            "by @markspanbroek in https://github.com/logos-storage/logos-storage-nim/pull/1288"
        )
        assert result == expected


class TestGetCommitsBetween:
    """Test getting commits between two commits."""

    @patch("src.release_notes.subprocess.run")
    def test_get_commits_between_returns_commits(self, mock_run):
        """Test getting commits between two commits."""
        mock_run.return_value = MagicMock(
            stdout="abc123def456789|feat: add feature|John Doe\n"
                   "def456789abc123|fix: bug fix|Jane Smith\n",
            returncode=0
        )

        result = get_commits_between(Path("/tmp/repo"), "prev", "curr")

        assert len(result) == 2
        assert result[0]["hash"] == "abc123d"
        assert result[0]["message"] == "feat: add feature"
        assert result[0]["author"] == "John Doe"
        assert result[1]["hash"] == "def4567"
        assert result[1]["message"] == "fix: bug fix"
        assert result[1]["author"] == "Jane Smith"

    @patch("src.release_notes.subprocess.run")
    def test_get_commits_between_empty_range(self, mock_run):
        """Test getting commits when range is empty."""
        mock_run.return_value = MagicMock(
            stdout="",
            returncode=0
        )

        result = get_commits_between(Path("/tmp/repo"), "prev", "curr")

        assert len(result) == 0

    @patch("src.release_notes.subprocess.run")
    def test_get_commits_between_single_commit(self, mock_run):
        """Test getting single commit."""
        mock_run.return_value = MagicMock(
            stdout="abc123def456789|feat: add feature|John Doe\n",
            returncode=0
        )

        result = get_commits_between(Path("/tmp/repo"), "prev", "curr")

        assert len(result) == 1
        assert result[0]["hash"] == "abc123d"
        assert result[0]["message"] == "feat: add feature"
        assert result[0]["author"] == "John Doe"

    @patch("src.release_notes.subprocess.run")
    def test_get_commits_between_calls_git_correctly(self, mock_run):
        """Test that get_commits_between calls git with correct arguments."""
        mock_run.return_value = MagicMock(
            stdout="",
            returncode=0
        )

        get_commits_between(Path("/tmp/repo"), "prev123", "curr456")

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == "git"
        assert args[1] == "log"
        assert args[2] == "--pretty=format:%H|%s|%an"
        assert args[3] == "prev123..curr456"
        assert mock_run.call_args[1]["cwd"] == Path("/tmp/repo")
        assert mock_run.call_args[1]["capture_output"] is True
        assert mock_run.call_args[1]["text"] is True
        assert mock_run.call_args[1]["check"] is True

    @patch("src.release_notes.subprocess.run")
    def test_get_commits_between_propagates_error(self, mock_run):
        """Test that get_commits_between propagates git errors."""
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "git", stderr="fatal: bad revision"
        )

        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            get_commits_between(Path("/tmp/repo"), "prev", "curr")

        assert exc_info.value.returncode == 1


class TestFormatReleaseNotes:
    """Test release notes formatting."""

    @patch("src.release_notes.get_commits_between")
    def test_format_release_notes_with_commits(self, mock_get_commits):
        """Test formatting release notes with commits."""
        mock_get_commits.return_value = [
            {
                "hash": "abc123d",
                "message": "feat(marketplace): add status l2 (Linea) network (#1160)",
                "author": "2-towns"
            },
            {
                "hash": "def4567",
                "message": "chore(marketplace): use hardhat ignition (#1195)",
                "author": "2-towns"
            },
            {
                "hash": "ghi7890",
                "message": "fix(tests): auto import all tests files and fix forgotten tests (#1281)",
                "author": "markspanbroek"
            },
        ]

        result = format_release_notes(Path("/tmp/repo"), "prev", "curr")

        lines = result.split("\n")
        assert len(lines) == 3
        assert "* feat(marketplace): add status l2 (Linea) network" in lines[0]
        assert "by @2-towns" in lines[0]
        assert "https://github.com/logos-storage/logos-storage-nim/pull/1160" in lines[0]
        assert "* chore(marketplace): use hardhat ignition" in lines[1]
        assert "by @2-towns" in lines[1]
        assert "https://github.com/logos-storage/logos-storage-nim/pull/1195" in lines[1]
        assert "* fix(tests): auto import all tests files and fix forgotten tests" in lines[2]
        assert "by @markspanbroek" in lines[2]
        assert "https://github.com/logos-storage/logos-storage-nim/pull/1281" in lines[2]

    @patch("src.release_notes.get_commits_between")
    def test_format_release_notes_empty(self, mock_get_commits):
        """Test formatting release notes with no commits."""
        mock_get_commits.return_value = []

        result = format_release_notes(Path("/tmp/repo"), "prev", "curr")

        assert result == "No commits found between releases"

    @patch("src.release_notes.get_commits_between")
    def test_format_release_notes_with_custom_repo(self, mock_get_commits):
        """Test formatting release notes with custom repository."""
        mock_get_commits.return_value = [
            {
                "hash": "abc123d",
                "message": "feat: add feature (#123)",
                "author": "johndoe"
            }
        ]

        result = format_release_notes(
            Path("/tmp/repo"),
            "prev",
            "curr",
            repo_owner="custom-owner",
            repo_name="custom-repo"
        )

        assert "https://github.com/custom-owner/custom-repo/pull/123" in result

    @patch("src.release_notes.get_commits_between")
    def test_format_release_notes_without_pr(self, mock_get_commits):
        """Test formatting release notes with commits without PR numbers."""
        mock_get_commits.return_value = [
            {
                "hash": "abc123d",
                "message": "chore: update dependencies",
                "author": "johndoe"
            }
        ]

        result = format_release_notes(Path("/tmp/repo"), "prev", "curr")

        assert "* chore: update dependencies" in result
        assert "by @johndoe" in result
        assert "https://github.com/logos-storage/logos-storage-nim/commit/abc123d" in result

    @patch("src.release_notes.get_commits_between")
    def test_format_release_notes_calls_get_commits_between(self, mock_get_commits):
        """Test that format_release_notes calls get_commits_between with correct arguments."""
        mock_get_commits.return_value = []

        format_release_notes(Path("/tmp/repo"), "prev123", "curr456")

        mock_get_commits.assert_called_once_with(
            Path("/tmp/repo"),
            "prev123",
            "curr456"
        )

    @patch("src.release_notes.get_commits_between")
    def test_format_release_notes_propagates_error(self, mock_get_commits):
        """Test that format_release_notes propagates errors from get_commits_between."""
        mock_get_commits.side_effect = subprocess.CalledProcessError(
            1, "git", stderr="fatal: bad revision"
        )

        with pytest.raises(subprocess.CalledProcessError) as exc_info:
            format_release_notes(Path("/tmp/repo"), "prev", "curr")

        assert exc_info.value.returncode == 1