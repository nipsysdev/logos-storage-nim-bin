"""Repository-related fixtures."""

import pytest
import subprocess


@pytest.fixture
def mock_git_clone_responses():
    """Fixture that provides standard git clone subprocess responses."""
    return [
        subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # git clone
        subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123def456789abc123def456789abc123def\n", stderr=""),  # git rev-parse HEAD
        subprocess.CompletedProcess(args=[], returncode=0, stdout="abc123d\n", stderr=""),  # git rev-parse --short HEAD
        subprocess.CompletedProcess(args=[], returncode=0, stdout="master\n", stderr=""),  # git rev-parse --abbrev-ref HEAD
    ]


@pytest.fixture
def mock_git_update_responses():
    """Fixture that provides standard git update subprocess responses."""
    return [
        subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # git fetch origin
        subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # git show-ref local branch
        subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # git show-ref remote branch
        subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # git checkout
        subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""),  # git pull
    ]