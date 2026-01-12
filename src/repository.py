"""Repository management for logos-storage-nim."""

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

from src.utils import run_command


@dataclass
class CommitInfo:
    """Simple container for commit information."""
    commit: str
    commit_short: str
    branch: str


def clone_repository(target_dir: Path, branch: str) -> None:
    """Clone the logos-storage-nim repository."""
    print(f"Cloning logos-storage-nim repository (branch: {branch})...")
    run_command([
        "git", "clone", "--branch", branch,
        "https://github.com/logos-storage/logos-storage-nim.git",
        str(target_dir)
    ])


def update_repository(repo_dir: Path, branch: str) -> None:
    """Update the logos-storage-nim repository."""
    print(f"Updating logos-storage-nim repository (branch: {branch})...")
    
    # Fetch all branches
    run_command(["git", "-C", str(repo_dir), "fetch", "origin"])
    
    # Check if branch exists
    has_local = run_command(
        ["git", "-C", str(repo_dir), "show-ref", "--verify", "--quiet", f"refs/heads/{branch}"],
        check=False
    ).returncode == 0
    
    has_remote = run_command(
        ["git", "-C", str(repo_dir), "show-ref", "--verify", "--quiet", f"refs/remotes/origin/{branch}"],
        check=False
    ).returncode == 0
    
    if not has_local and not has_remote:
        raise ValueError(f"Branch '{branch}' not found")
    
    # Checkout and pull
    run_command(["git", "-C", str(repo_dir), "checkout", branch])
    run_command(["git", "-C", str(repo_dir), "pull", "origin", branch])


def get_commit_info(repo_dir: Path) -> CommitInfo:
    """Get commit information from the repository."""
    commit = run_command(["git", "-C", str(repo_dir), "rev-parse", "HEAD"]).stdout.strip()
    commit_short = run_command(["git", "-C", str(repo_dir), "rev-parse", "--short", "HEAD"]).stdout.strip()
    branch = run_command(["git", "-C", str(repo_dir), "rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
    
    return CommitInfo(commit, commit_short, branch)


def ensure_logos_storage_repo(branch: str) -> Tuple[Path, CommitInfo]:
    """Ensure the logos-storage-nim repository exists and is up to date."""
    logos_storage_dir = Path("logos-storage-nim")
    
    if not logos_storage_dir.exists():
        clone_repository(logos_storage_dir, branch)
    else:
        update_repository(logos_storage_dir, branch)
    
    commit_info = get_commit_info(logos_storage_dir)
    return logos_storage_dir, commit_info