"""Release notes generation module.

This module provides functionality to format commit messages for release notes,
including extracting PR numbers and creating formatted links.
"""

import re
import subprocess
from pathlib import Path
from typing import List, Optional


def extract_pr_number(commit_message: str) -> Optional[int]:
    """Extract PR number from commit message.

    Args:
        commit_message: The commit message to parse

    Returns:
        The PR number if found, None otherwise

    Examples:
        >>> extract_pr_number("feat: add feature (#123)")
        123
        >>> extract_pr_number("fix: bug fix")
        None
    """
    match = re.search(r"#(\d+)", commit_message)
    if match:
        return int(match.group(1))
    return None


def extract_author(commit_message: str) -> Optional[str]:
    """Extract author name from commit message.

    Args:
        commit_message: The commit message to parse

    Returns:
        The author name if found, None otherwise

    Examples:
        >>> extract_author("feat: add feature (John Doe)")
        "John Doe"
        >>> extract_author("fix: bug fix")
        None
    """
    # Try to match author in parentheses at the end
    match = re.search(r"\(([^)]+)\)$", commit_message)
    if match:
        return match.group(1)
    return None


def format_commit_entry(
    commit_hash: str,
    commit_message: str,
    author: str,
    repo_owner: str = "logos-storage",
    repo_name: str = "logos-storage-nim"
) -> str:
    """Format a single commit entry for release notes.

    Args:
        commit_hash: The short commit hash
        commit_message: The commit message
        author: The commit author
        repo_owner: The repository owner (default: logos-storage)
        repo_name: The repository name (default: logos-storage-nim)

    Returns:
        Formatted commit entry string

    Examples:
        >>> format_commit_entry("abc123", "feat: add feature (#123)", "johndoe")
        "* feat: add feature (#123) by @johndoe in https://github.com/logos-storage/logos-storage-nim/pull/123"
    """
    pr_number = extract_pr_number(commit_message)

    # Remove PR number from message if present
    clean_message = re.sub(r"\s*\(#\d+\)", "", commit_message).strip()

    # Format the entry
    if pr_number:
        pr_url = f"https://github.com/{repo_owner}/{repo_name}/pull/{pr_number}"
        return f"* {clean_message} by @{author} in {pr_url}"
    else:
        # If no PR number, just show commit hash
        commit_url = f"https://github.com/{repo_owner}/{repo_name}/commit/{commit_hash}"
        return f"* {clean_message} by @{author} in {commit_url}"


def get_commits_between(
    repo_path: Path,
    previous_commit: str,
    current_commit: str
) -> List[dict]:
    """Get commits between two commits.

    Args:
        repo_path: Path to the git repository
        previous_commit: The previous commit hash
        current_commit: The current commit hash

    Returns:
        List of commit dictionaries with keys: hash, message, author

    Raises:
        subprocess.CalledProcessError: If git command fails
    """
    # Get commit log with hash, message, and author
    result = subprocess.run(
        [
            "git",
            "log",
            "--pretty=format:%H|%s|%an",
            f"{previous_commit}..{current_commit}"
        ],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True
    )

    commits = []
    for line in result.stdout.strip().split("\n"):
        if line:
            parts = line.split("|", 2)
            if len(parts) == 3:
                commits.append({
                    "hash": parts[0][:7],  # Short hash
                    "message": parts[1],
                    "author": parts[2]
                })

    return commits


def format_release_notes(
    repo_path: Path,
    previous_commit: str,
    current_commit: str,
    repo_owner: str = "logos-storage",
    repo_name: str = "logos-storage-nim"
) -> str:
    """Generate formatted release notes for commits between two commits.

    Args:
        repo_path: Path to the git repository
        previous_commit: The previous commit hash
        current_commit: The current commit hash
        repo_owner: The repository owner (default: logos-storage)
        repo_name: The repository name (default: logos-storage-nim)

    Returns:
        Formatted release notes string

    Raises:
        subprocess.CalledProcessError: If git command fails
    """
    commits = get_commits_between(repo_path, previous_commit, current_commit)

    if not commits:
        return "No commits found between releases"

    # Format each commit
    formatted_commits = [
        format_commit_entry(
            commit["hash"],
            commit["message"],
            commit["author"],
            repo_owner,
            repo_name
        )
        for commit in commits
    ]

    return "\n".join(formatted_commits)


def main() -> None:
    """Main entry point for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate release notes from git commits"
    )
    parser.add_argument(
        "--repo-path",
        type=Path,
        default=Path.cwd(),
        help="Path to the git repository (default: current directory)"
    )
    parser.add_argument(
        "--previous-commit",
        required=True,
        help="Previous commit hash"
    )
    parser.add_argument(
        "--current-commit",
        required=True,
        help="Current commit hash"
    )
    parser.add_argument(
        "--repo-owner",
        default="logos-storage",
        help="Repository owner (default: logos-storage)"
    )
    parser.add_argument(
        "--repo-name",
        default="logos-storage-nim",
        help="Repository name (default: logos-storage-nim)"
    )

    args = parser.parse_args()

    try:
        notes = format_release_notes(
            args.repo_path,
            args.previous_commit,
            args.current_commit,
            args.repo_owner,
            args.repo_name
        )
        print(notes)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    import sys
    main()