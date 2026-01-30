"""Integration tests for release_notes module."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess

from src.release_notes import format_release_notes


class TestReleaseNotesIntegration:
    """Integration tests for release notes generation."""

    @patch("src.release_notes.get_commits_between")
    @patch("src.release_notes.get_pr_author")
    def test_format_release_notes_generates_correct_format(self, mock_get_pr_author, mock_get_commits):
        """Test that format_release_notes generates the expected format."""
        # Mock commit data with fake names and usernames
        mock_get_commits.return_value = [
            {
                "hash": "abc123d",
                "message": "fix(ci): Add version and tagged release variables to release workflow (#123)",
                "author": "John Doe"
            },
            {
                "hash": "def4567",
                "message": "chore(ci): Rename release artifacts (#456)",
                "author": "Jane Smith"
            },
            {
                "hash": "ghi7890",
                "message": "build(docker): rename codex to logos-storage (#789)",
                "author": "Bob Johnson"
            },
            {
                "hash": "jkl0123",
                "message": "fix: correct zip name for libstorage zip (#101)",
                "author": "Alice Williams"
            },
        ]
        
        # Mock GitHub usernames for PRs
        mock_get_pr_author.side_effect = lambda pr, *args: {
            123: "johndoe",
            456: "janesmith",
            789: "bobjohnson",
            101: "alicewilliams",
        }.get(pr)

        result = format_release_notes(Path("/tmp/repo"), "prev", "curr")

        # Verify the output format matches the expected format
        lines = result.split("\n")

        # Check first commit - uses GitHub username from PR
        assert lines[0].startswith("* fix(ci): Add version and tagged release variables to release workflow")
        assert "by @johndoe" in lines[0]
        assert "https://github.com/logos-storage/logos-storage-nim/pull/123" in lines[0]

        # Check second commit - uses GitHub username from PR
        assert lines[1].startswith("* chore(ci): Rename release artifacts")
        assert "by @janesmith" in lines[1]
        assert "https://github.com/logos-storage/logos-storage-nim/pull/456" in lines[1]

        # Check third commit - uses GitHub username from PR
        assert lines[2].startswith("* build(docker): rename codex to logos-storage")
        assert "by @bobjohnson" in lines[2]
        assert "https://github.com/logos-storage/logos-storage-nim/pull/789" in lines[2]

        # Check fourth commit - uses GitHub username from PR
        assert lines[3].startswith("* fix: correct zip name for libstorage zip")
        assert "by @alicewilliams" in lines[3]
        assert "https://github.com/logos-storage/logos-storage-nim/pull/101" in lines[3]

    @patch("src.release_notes.get_commits_between")
    def test_format_release_notes_without_pr_numbers(self, mock_get_commits):
        """Test that format_release_notes handles commits without PR numbers."""
        # Mock commits without PR numbers
        mock_get_commits.return_value = [
            {
                "hash": "abc123d",
                "message": 'Revert "fix: remove cirdl from build.nims, remove marketplace from docker entrypoint"',
                "author": "Test User"
            },
            {
                "hash": "def4567",
                "message": "fix: remove cirdl from build.nims, remove marketplace from docker entrypoint",
                "author": "Test User"
            },
        ]

        result = format_release_notes(Path("/tmp/repo"), "prev", "curr")

        lines = result.split("\n")

        # Check that commits without PR numbers use commit hash URLs
        assert lines[0].startswith('* Revert "fix: remove cirdl from build.nims, remove marketplace from docker entrypoint"')
        assert "by @Test User" in lines[0]
        assert "https://github.com/logos-storage/logos-storage-nim/commit/abc123d" in lines[0]

        assert lines[1].startswith("* fix: remove cirdl from build.nims, remove marketplace from docker entrypoint")
        assert "by @Test User" in lines[1]
        assert "https://github.com/logos-storage/logos-storage-nim/commit/def4567" in lines[1]

    @patch("src.release_notes.get_commits_between")
    @patch("src.release_notes.get_pr_author")
    def test_format_release_notes_mixed_pr_and_no_pr(self, mock_get_pr_author, mock_get_commits):
        """Test that format_release_notes handles mixed commits (with and without PR)."""
        # Mock mixed commits
        mock_get_commits.return_value = [
            {
                "hash": "abc123d",
                "message": "fix(ci): Add version and tagged release variables to release workflow (#123)",
                "author": "John Doe"
            },
            {
                "hash": "def4567",
                "message": 'Revert "fix: remove cirdl from build.nims, remove marketplace from docker entrypoint"',
                "author": "Test User"
            },
            {
                "hash": "ghi7890",
                "message": "chore(ci): Rename release artifacts (#456)",
                "author": "Jane Smith"
            },
        ]
        
        # Mock GitHub username for PR
        mock_get_pr_author.side_effect = lambda pr, *args: {
            123: "johndoe",
            456: "janesmith",
        }.get(pr)

        result = format_release_notes(Path("/tmp/repo"), "prev", "curr")

        lines = result.split("\n")

        # First commit has PR - uses GitHub username from PR
        assert "https://github.com/logos-storage/logos-storage-nim/pull/123" in lines[0]
        assert "by @johndoe" in lines[0]

        # Second commit has no PR - uses display name
        assert "https://github.com/logos-storage/logos-storage-nim/commit/def4567" in lines[1]
        assert "by @Test User" in lines[1]

        # Third commit has PR - uses GitHub username from PR
        assert "https://github.com/logos-storage/logos-storage-nim/pull/456" in lines[2]
        assert "by @janesmith" in lines[2]

    @patch("src.release_notes.get_commits_between")
    def test_format_release_notes_empty_range(self, mock_get_commits):
        """Test that format_release_notes handles empty commit range."""
        mock_get_commits.return_value = []

        result = format_release_notes(Path("/tmp/repo"), "prev", "curr")

        assert result == "No commits found between releases"

    @patch("src.release_notes.get_commits_between")
    @patch("src.release_notes.get_pr_author")
    def test_format_release_notes_custom_repository(self, mock_get_pr_author, mock_get_commits):
        """Test that format_release_notes uses custom repository parameters."""
        # Mock commit data
        mock_get_commits.return_value = [
            {
                "hash": "abc123d",
                "message": "fix(ci): Add version and tagged release variables to release workflow (#123)",
                "author": "John Doe"
            }
        ]
        
        # Mock GitHub username for PR
        mock_get_pr_author.return_value = "johndoe"

        result = format_release_notes(
            Path("/tmp/repo"),
            "prev",
            "curr",
            repo_owner="custom-owner",
            repo_name="custom-repo"
        )

        assert "https://github.com/custom-owner/custom-repo/pull/123" in result
        assert "by @johndoe" in result