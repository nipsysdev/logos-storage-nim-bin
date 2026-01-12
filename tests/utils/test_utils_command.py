"""Tests for command execution in utils.py."""

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from src.utils import run_command


class TestRunCommand:
    """Test run_command function."""

    def test_run_command_returns_completed_process(self, mock_subprocess_run):
        mock_subprocess_run.return_value = subprocess.CompletedProcess(
            args=["echo", "test"],
            returncode=0,
            stdout="test\n",
            stderr=""
        )
        
        result = run_command(["echo", "test"])
        
        assert isinstance(result, subprocess.CompletedProcess)
        assert result.returncode == 0
        assert result.stdout == "test\n"

    def test_run_command_with_cwd(self, mock_subprocess_run):
        mock_subprocess_run.return_value = subprocess.CompletedProcess(
            args=["ls"],
            returncode=0,
            stdout="",
            stderr=""
        )
        
        test_dir = Path("/tmp/test")
        run_command(["ls"], cwd=test_dir)
        
        mock_subprocess_run.assert_called_once()
        call_kwargs = mock_subprocess_run.call_args[1]
        assert call_kwargs["cwd"] == test_dir

    def test_run_command_with_env(self, mock_subprocess_run):
        mock_subprocess_run.return_value = subprocess.CompletedProcess(
            args=["env"],
            returncode=0,
            stdout="",
            stderr=""
        )
        
        custom_env = {"CUSTOM_VAR": "custom_value"}
        run_command(["env"], env=custom_env)
        
        mock_subprocess_run.assert_called_once()
        call_kwargs = mock_subprocess_run.call_args[1]
        assert "CUSTOM_VAR" in call_kwargs["env"]
        assert call_kwargs["env"]["CUSTOM_VAR"] == "custom_value"

    def test_run_command_with_check_false(self, mock_subprocess_run):
        mock_subprocess_run.return_value = subprocess.CompletedProcess(
            args=["false"],
            returncode=1,
            stdout="",
            stderr=""
        )
        
        result = run_command(["false"], check=False)
        
        assert result.returncode == 1

    def test_run_command_with_check_true_raises_on_error(self, mock_subprocess_run):
        def side_effect(*args, **kwargs):
            if kwargs.get("check", False):
                raise subprocess.CalledProcessError(
                    returncode=1,
                    cmd=args[0]
                )
            return subprocess.CompletedProcess(
                args=args[0],
                returncode=1,
                stdout="",
                stderr=""
            )
        
        mock_subprocess_run.side_effect = side_effect
        
        with pytest.raises(subprocess.CalledProcessError):
            run_command(["false"], check=True)

    def test_run_command_with_binary_mode(self, mock_subprocess_run):
        mock_subprocess_run.return_value = subprocess.CompletedProcess(
            args=["cat"],
            returncode=0,
            stdout=b"binary data",
            stderr=b""
        )
        
        result = run_command(["cat"], binary=True)
        
        assert isinstance(result.stdout, bytes)
        assert result.stdout == b"binary data"

    def test_run_command_with_text_mode(self, mock_subprocess_run):
        mock_subprocess_run.return_value = subprocess.CompletedProcess(
            args=["echo", "test"],
            returncode=0,
            stdout="test\n",
            stderr=""
        )
        
        result = run_command(["echo", "test"], binary=False)
        
        assert isinstance(result.stdout, str)
        assert result.stdout == "test\n"