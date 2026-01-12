"""Tests for environment configuration in utils.py."""

import os
import subprocess
from unittest.mock import patch

import pytest

from src.utils import configure_reproducible_environment


class TestConfigureReproducibleEnvironment:
    """Test configure_reproducible_environment function."""

    def test_sets_source_date_epoch_from_git(self, mock_run_command, mock_os_environ):
        mock_run_command.return_value = subprocess.CompletedProcess(
            args=["git", "log", "-1", "--format=%ct"],
            returncode=0,
            stdout="1234567890\n",
            stderr=""
        )
        
        configure_reproducible_environment()
        
        assert os.environ["SOURCE_DATE_EPOCH"] == "1234567890"

    def test_sets_source_date_epoch_to_zero_when_git_fails(self, mock_run_command, mock_os_environ):
        mock_run_command.return_value = subprocess.CompletedProcess(
            args=["git", "log", "-1", "--format=%ct"],
            returncode=1,
            stdout="",
            stderr="error"
        )
        
        configure_reproducible_environment()
        
        assert os.environ["SOURCE_DATE_EPOCH"] == "0"

    def test_sets_source_date_epoch_to_zero_when_git_not_found(self, mock_run_command, mock_os_environ):
        mock_run_command.side_effect = FileNotFoundError()
        
        configure_reproducible_environment()
        
        assert os.environ["SOURCE_DATE_EPOCH"] == "0"

    def test_sets_timezone_to_utc(self, mock_run_command, mock_os_environ):
        mock_run_command.return_value = subprocess.CompletedProcess(
            args=["git", "log", "-1", "--format=%ct"],
            returncode=0,
            stdout="1234567890\n",
            stderr=""
        )
        
        configure_reproducible_environment()
        
        assert os.environ["TZ"] == "UTC"

    def test_sets_locale_to_c_utf8(self, mock_run_command, mock_os_environ):
        mock_run_command.return_value = subprocess.CompletedProcess(
            args=["git", "log", "-1", "--format=%ct"],
            returncode=0,
            stdout="1234567890\n",
            stderr=""
        )
        
        configure_reproducible_environment()
        
        assert os.environ["LC_ALL"] == "C.UTF-8"

    def test_sets_all_environment_variables(self, mock_run_command, mock_os_environ):
        mock_run_command.return_value = subprocess.CompletedProcess(
            args=["git", "log", "-1", "--format=%ct"],
            returncode=0,
            stdout="1234567890\n",
            stderr=""
        )
        
        configure_reproducible_environment()
        
        assert os.environ["SOURCE_DATE_EPOCH"] == "1234567890"
        assert os.environ["TZ"] == "UTC"
        assert os.environ["LC_ALL"] == "C.UTF-8"