"""Repository management for logos-storage-nim."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

from src.utils import run_command


@dataclass
class CommitInfo:
    """Simple container for commit information."""
    commit: str
    commit_short: str
    branch: str


def validate_commit_exists(repo_dir: Path, commit: str) -> bool:
    """Validate that a commit hash exists in the repository.
    
    Args:
        repo_dir: Path to the repository
        commit: Commit hash to validate
        
    Returns:
        True if commit exists, False otherwise
    """
    result = run_command(
        ["git", "-C", str(repo_dir), "cat-file", "-e", commit],
        check=False
    )
    return result.returncode == 0


def validate_commit_in_branch(repo_dir: Path, commit: str, branch: str) -> bool:
    """Validate that a commit exists in a specific branch.
    
    Args:
        repo_dir: Path to the repository
        commit: Commit hash to validate
        branch: Branch name to check
        
    Returns:
        True if commit exists in the branch, False otherwise
    """
    # Check if commit is reachable from the branch
    result = run_command(
        ["git", "-C", str(repo_dir), "branch", "--contains", commit],
        check=False
    )
    
    if result.returncode != 0:
        return False
    
    # Check if the branch is in the output
    return branch in result.stdout


def is_tag(ref: str) -> bool:
    """Check if a ref is a tag.
    
    Args:
        ref: Reference to check (branch name or tag)
        
    Returns:
        True if ref is a tag, False otherwise
    """
    # Check if the ref exists as a tag in the remote repository
    result = run_command(
        ["git", "ls-remote", "--tags", "https://github.com/logos-storage/logos-storage-nim.git", f"refs/tags/{ref}"],
        check=False
    )
    # git ls-remote returns exit code 0 even when no tags match
    # We need to check if stdout is non-empty to determine if the tag exists
    return result.returncode == 0 and result.stdout.strip() != ""


def clone_repository(target_dir: Path, branch: str, commit: Optional[str] = None) -> None:
    """Clone the logos-storage-nim repository.
    
    Args:
        target_dir: Directory to clone into
        branch: Branch to clone (used if commit is not specified)
        commit: Optional commit hash to checkout (mutually exclusive with branch)
    """
    # Check if branch is actually a tag
    if is_tag(branch):
        print(f"Cloning logos-storage-nim repository (tag: {branch})...")
        # Clone without checkout
        run_command([
            "git", "clone", "--no-checkout",
            "https://github.com/logos-storage/logos-storage-nim.git",
            str(target_dir)
        ])
        # Fetch all objects
        run_command(["git", "-C", str(target_dir), "fetch", "--all", "--tags"])
        # Checkout the tag
        run_command(["git", "-C", str(target_dir), "checkout", f"refs/tags/{branch}"])
    elif commit:
        print(f"Cloning logos-storage-nim repository (commit: {commit})...")
        # Clone without checkout
        run_command([
            "git", "clone", "--no-checkout",
            "https://github.com/logos-storage/logos-storage-nim.git",
            str(target_dir)
        ])
        # Fetch all objects
        run_command(["git", "-C", str(target_dir), "fetch", "--all", "--tags"])
        # Checkout specific commit
        run_command(["git", "-C", str(target_dir), "checkout", commit])
    else:
        print(f"Cloning logos-storage-nim repository (branch: {branch})...")
        run_command([
            "git", "clone", "--branch", branch,
            "https://github.com/logos-storage/logos-storage-nim.git",
            str(target_dir)
        ])


def update_repository(repo_dir: Path, branch: str, commit: Optional[str] = None) -> None:
    """Update the logos-storage-nim repository.
    
    Args:
        repo_dir: Path to the repository
        branch: Branch to update (used if commit is not specified)
        commit: Optional commit hash to checkout (mutually exclusive with branch)
    """
    # Check if branch is actually a tag
    if is_tag(branch):
        print(f"Updating logos-storage-nim repository (tag: {branch})...")
        # Fetch all objects
        run_command(["git", "-C", str(repo_dir), "fetch", "--all", "--tags"])
        # Checkout the tag
        run_command(["git", "-C", str(repo_dir), "checkout", f"refs/tags/{branch}"])
    elif commit:
        print(f"Updating logos-storage-nim repository (commit: {commit})...")
        # Fetch all objects
        run_command(["git", "-C", str(repo_dir), "fetch", "--all", "--tags"])
        
        # Validate commit exists
        if not validate_commit_exists(repo_dir, commit):
            raise ValueError(f"Commit '{commit}' not found in repository")
        
        # Checkout specific commit
        run_command(["git", "-C", str(repo_dir), "checkout", commit])
    else:
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


def reset_repository(repo_dir: Path) -> None:
    """Reset repository to clean state.
    
    Args:
        repo_dir: Path to the repository to reset
    """
    print("Resetting repository to clean state...")
    
    # Reset all changes
    run_command(["git", "-C", str(repo_dir), "reset", "--hard", "HEAD"])
    
    # Clean untracked files and directories
    run_command(["git", "-C", str(repo_dir), "clean", "-fd"])
    
    # Clean submodules
    run_command(["git", "-C", str(repo_dir), "submodule", "foreach", "--recursive", "git reset --hard HEAD"])
    run_command(["git", "-C", str(repo_dir), "submodule", "foreach", "--recursive", "git clean -fd"])
    
    print("Repository reset complete")


def apply_patches(repo_dir: Path, patch_dir: Path) -> None:
    """Apply client-lite patches to upstream repository.
    
    Args:
        repo_dir: Path to the logos-storage-nim repository
        patch_dir: Path to patches directory (should contain client-lite/ subdirectory)
    """
    if not patch_dir.exists():
        print(f"Warning: Patch directory {patch_dir} does not exist, skipping patches")
        return
    
    client_lite_patches = patch_dir / "client-lite"
    if not client_lite_patches.exists():
        print(f"Warning: Client-lite patch directory {client_lite_patches} does not exist, skipping patches")
        return
    
    print(f"Applying client-lite patches from {client_lite_patches}...")
    
    # Apply patches in alphabetical order
    patch_files = sorted(client_lite_patches.glob("*.patch"))
    
    if not patch_files:
        print("No patch files found in client-lite patch directory")
        return
    
    for patch_file in patch_files:
        print(f"  Applying {patch_file.name}...")
        
        # Check if patch has a working directory specification
        working_dir = None
        with open(patch_file, 'r') as f:
            first_line = f.readline().strip()
            if first_line.startswith("# PATCH_WORKING_DIR:"):
                working_dir = first_line.split(":", 1)[1].strip()
        
        # Determine the correct working directory and apply patch
        if working_dir:
            # Apply patch from within the specified subdirectory
            patch_cwd = repo_dir / working_dir
            # Use absolute path for the patch file
            result = run_command([
                "git", "apply", str(patch_file.absolute())	
            ], cwd=patch_cwd, check=False)
        else:
            # Apply patch from repository root (default behavior)
            result = run_command([
                "git", "apply", "-p1", str(patch_file.absolute())	
            ], cwd=repo_dir, check=False)
        
        if result.returncode != 0:
            print(f"  ✗ Failed to apply {patch_file.name}")
            if result.stdout:
                print(f"    stdout: {result.stdout}")
            if result.stderr:
                print(f"    stderr: {result.stderr}")
            raise RuntimeError(f"Failed to apply patch {patch_file.name}")
        else:
            print(f"  ✓ Applied {patch_file.name}")
    
    print("Patch application complete")


def get_commit_info(repo_dir: Path) -> CommitInfo:
    """Get commit information from the repository."""
    commit = run_command(["git", "-C", str(repo_dir), "rev-parse", "HEAD"]).stdout.strip()
    commit_short = run_command(["git", "-C", str(repo_dir), "rev-parse", "--short", "HEAD"]).stdout.strip()
    
    # Get branch name, or "HEAD" if in detached state
    branch_result = run_command(
        ["git", "-C", str(repo_dir), "rev-parse", "--abbrev-ref", "HEAD"],
        check=False
    )
    branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "HEAD"
    
    return CommitInfo(commit, commit_short, branch)


def ensure_logos_storage_repo(branch: str, commit: Optional[str] = None) -> Tuple[Path, CommitInfo]:
    """Ensure the logos-storage-nim repository exists and is up to date.
    
    Args:
        branch: Branch or tag to use
        commit: Optional commit hash to checkout (mutually exclusive with tags)
        
    Returns:
        Tuple of (repository path, commit info)
        
    Raises:
        ValueError: If commit is specified but doesn't exist in the branch
    """
    logos_storage_dir = Path("logos-storage-nim")
    
    if not logos_storage_dir.exists():
        clone_repository(logos_storage_dir, branch, commit)
    else:
        update_repository(logos_storage_dir, branch, commit)
    
    # If both branch and commit are specified, validate commit is in branch
    # Skip this validation if branch is a tag
    if branch and commit and not is_tag(branch):
        if not validate_commit_in_branch(logos_storage_dir, commit, branch):
            raise ValueError(
                f"Commit '{commit}' does not exist in branch '{branch}'. "
                f"Please verify the commit hash and branch name."
            )
    
    commit_info = get_commit_info(logos_storage_dir)
    
    # If branch is a tag, use the tag name as the branch
    # If both branch and commit are specified, override the branch name
    # This ensures artifact names use the actual branch/tag name instead of "HEAD"
    if is_tag(branch):
        commit_info.branch = branch
    elif branch and commit:
        commit_info.branch = branch
    
    return logos_storage_dir, commit_info


