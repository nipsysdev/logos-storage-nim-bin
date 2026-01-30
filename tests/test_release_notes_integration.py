"""Integration tests for release_notes module."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess

from src.release_notes import format_release_notes


class TestReleaseNotesIntegration:
    """Integration tests for release notes generation."""

    @patch("src.release_notes.get_commits_between")
    def test_format_release_notes_generates_correct_format(self, mock_get_commits):
        """Test that format_release_notes generates the expected format."""
        # Mock realistic commit data based on actual commits from logos-storage-nim
        mock_get_commits.return_value = [
            {
                "hash": "52d2748",
                "message": "fix(ci): Add version and tagged release variables to release workflow (#1391)",
                "author": "Eric"
            },
            {
                "hash": "1c970e9",
                "message": "chore(ci): Rename release artifacts (#1389)",
                "author": "Eric"
            },
            {
                "hash": "e596de7",
                "message": "build(docker): rename codex to logos-storage (#1387)",
                "author": "Adam Uhlíř"
            },
            {
                "hash": "7d51740",
                "message": "fix: correct zip name for libstorage zip (#1386)",
                "author": "Arnaud"
            },
        ]

        result = format_release_notes(Path("/tmp/repo"), "prev", "curr")

        # Verify the output format matches the expected format
        lines = result.split("\n")

        # Check first commit
        assert lines[0].startswith("* fix(ci): Add version and tagged release variables to release workflow")
        assert "by @Eric" in lines[0]
        assert "https://github.com/logos-storage/logos-storage-nim/pull/1391" in lines[0]

        # Check second commit
        assert lines[1].startswith("* chore(ci): Rename release artifacts")
        assert "by @Eric" in lines[1]
        assert "https://github.com/logos-storage/logos-storage-nim/pull/1389" in lines[1]

        # Check third commit
        assert lines[2].startswith("* build(docker): rename codex to logos-storage")
        assert "by @Adam Uhlíř" in lines[2]
        assert "https://github.com/logos-storage/logos-storage-nim/pull/1387" in lines[2]

        # Check fourth commit
        assert lines[3].startswith("* fix: correct zip name for libstorage zip")
        assert "by @Arnaud" in lines[3]
        assert "https://github.com/logos-storage/logos-storage-nim/pull/1386" in lines[3]

    @patch("src.release_notes.get_commits_between")
    def test_format_release_notes_without_pr_numbers(self, mock_get_commits):
        """Test that format_release_notes handles commits without PR numbers."""
        # Based on actual commits from logos-storage-nim that don't have PR numbers
        mock_get_commits.return_value = [
            {
                "hash": "a163156",
                "message": 'Revert "fix: remove cirdl from build.nims, remove marketplace from docker entrypoint"',
                "author": "gmega"
            },
            {
                "hash": "14e8fa7",
                "message": "fix: remove cirdl from build.nims, remove marketplace from docker entrypoint",
                "author": "gmega"
            },
        ]

        result = format_release_notes(Path("/tmp/repo"), "prev", "curr")

        lines = result.split("\n")

        # Check that commits without PR numbers use commit hash URLs
        assert lines[0].startswith('* Revert "fix: remove cirdl from build.nims, remove marketplace from docker entrypoint"')
        assert "by @gmega" in lines[0]
        assert "https://github.com/logos-storage/logos-storage-nim/commit/a163156" in lines[0]

        assert lines[1].startswith("* fix: remove cirdl from build.nims, remove marketplace from docker entrypoint")
        assert "by @gmega" in lines[1]
        assert "https://github.com/logos-storage/logos-storage-nim/commit/14e8fa7" in lines[1]

    @patch("src.release_notes.get_commits_between")
    def test_format_release_notes_mixed_pr_and_no_pr(self, mock_get_commits):
        """Test that format_release_notes handles mixed commits (with and without PR)."""
        # Based on actual commits from logos-storage-nim
        mock_get_commits.return_value = [
            {
                "hash": "52d2748",
                "message": "fix(ci): Add version and tagged release variables to release workflow (#1391)",
                "author": "Eric"
            },
            {
                "hash": "a163156",
                "message": 'Revert "fix: remove cirdl from build.nims, remove marketplace from docker entrypoint"',
                "author": "gmega"
            },
            {
                "hash": "1c970e9",
                "message": "chore(ci): Rename release artifacts (#1389)",
                "author": "Eric"
            },
        ]

        result = format_release_notes(Path("/tmp/repo"), "prev", "curr")

        lines = result.split("\n")

        # First commit has PR
        assert "https://github.com/logos-storage/logos-storage-nim/pull/1391" in lines[0]

        # Second commit has no PR
        assert "https://github.com/logos-storage/logos-storage-nim/commit/a163156" in lines[1]

        # Third commit has PR
        assert "https://github.com/logos-storage/logos-storage-nim/pull/1389" in lines[2]

    @patch("src.release_notes.get_commits_between")
    def test_format_release_notes_empty_range(self, mock_get_commits):
        """Test that format_release_notes handles empty commit range."""
        mock_get_commits.return_value = []

        result = format_release_notes(Path("/tmp/repo"), "prev", "curr")

        assert result == "No commits found between releases"

    @patch("src.release_notes.get_commits_between")
    def test_format_release_notes_custom_repository(self, mock_get_commits):
        """Test that format_release_notes uses custom repository parameters."""
        # Based on actual commit from logos-storage-nim
        mock_get_commits.return_value = [
            {
                "hash": "52d2748",
                "message": "fix(ci): Add version and tagged release variables to release workflow (#1391)",
                "author": "Eric"
            }
        ]

        result = format_release_notes(
            Path("/tmp/repo"),
            "prev",
            "curr",
            repo_owner="custom-owner",
            repo_name="custom-repo"
        )

        assert "https://github.com/custom-owner/custom-repo/pull/1391" in result