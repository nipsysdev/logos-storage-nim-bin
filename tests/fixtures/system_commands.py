"""Focused system command execution fixtures."""

import pytest
from unittest.mock import patch
from dataclasses import dataclass


@dataclass
class MockCompletedProcess:
    """Mock subprocess.CompletedProcess for testing."""
    returncode: int
    stdout: str
    stderr: str = ""


@pytest.fixture
def mock_run_command():
    """Mock the run_command utility function in src.artifacts."""
    with patch("src.artifacts.run_command") as mock:
        yield mock


@pytest.fixture
def mock_utils_run_command():
    """Mock the run_command utility function in src.utils."""
    with patch("src.utils.run_command") as mock:
        yield mock


@pytest.fixture
def mock_ar_commands():
    """Mock ar (archive) commands."""
    with patch("src.artifacts.run_command") as mock_run:
        def side_effect(cmd, check=True, binary=False):
            if "ar" in cmd:
                if "t" in cmd:  # ar t - list archive contents
                    return MockCompletedProcess(
                        returncode=0,
                        stdout="object.o\n",
                        stderr=""
                    )
                elif "p" in cmd:  # ar p - extract file
                    return MockCompletedProcess(
                        returncode=0,
                        stdout=b"fake object file content",
                        stderr=""
                    )
                else:  # ar rcs - create archive
                    return MockCompletedProcess(
                        returncode=0,
                        stdout="",
                        stderr=""
                    )
            return MockCompletedProcess(returncode=0, stdout="", stderr="")
        
        mock_run.side_effect = side_effect
        yield mock_run


@pytest.fixture
def mock_sha256sum_commands():
    """Mock sha256sum commands."""
    with patch("src.artifacts.run_command") as mock_run:
        def side_effect(cmd, check=True, binary=False):
            if "sha256sum" in cmd:
                # Extract filename from command and return it in the output
                filename = cmd[-1] if cmd else "filename"
                return MockCompletedProcess(
                    returncode=0,
                    stdout=f"abc123def456  {filename}\n",
                    stderr=""
                )
            return MockCompletedProcess(returncode=0, stdout="", stderr="")
        
        mock_run.side_effect = side_effect
        yield mock_run


@pytest.fixture
def mock_file_commands():
    """Mock file command."""
    with patch("src.artifacts.run_command") as mock_run:
        def side_effect(cmd, check=True, binary=False):
            if "file" in cmd:
                return MockCompletedProcess(
                    returncode=0,
                    stdout="ELF 64-bit LSB relocatable, x86-64",
                    stderr=""
                )
            return MockCompletedProcess(returncode=0, stdout="", stderr="")
        
        mock_run.side_effect = side_effect
        yield mock_run