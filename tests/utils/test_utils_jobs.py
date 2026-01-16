"""Tests for parallel jobs in utils.py."""

import subprocess
from unittest.mock import patch

import pytest

from src.utils import get_parallel_jobs


class TestGetParallelJobs:
    """Test get_parallel_jobs function on Linux."""

    @patch("platform.system", return_value="Linux")
    def test_get_parallel_jobs_returns_cpu_count_minus_one(self, mock_system, mock_utils_run_command):
        mock_utils_run_command.return_value = subprocess.CompletedProcess(
            args=["nproc"],
            returncode=0,
            stdout="8\n",
            stderr=""
        )
        
        result = get_parallel_jobs()
        
        assert result == 7
        mock_utils_run_command.assert_called_once_with(["nproc"], check=False)

    @patch("platform.system", return_value="Linux")
    def test_get_parallel_jobs_with_single_cpu(self, mock_system, mock_utils_run_command):
        mock_utils_run_command.return_value = subprocess.CompletedProcess(
            args=["nproc"],
            returncode=0,
            stdout="1\n",
            stderr=""
        )
        
        result = get_parallel_jobs()
        
        assert result == 1

    @patch("platform.system", return_value="Linux")
    def test_get_parallel_jobs_with_two_cpus(self, mock_system, mock_utils_run_command):
        mock_utils_run_command.return_value = subprocess.CompletedProcess(
            args=["nproc"],
            returncode=0,
            stdout="2\n",
            stderr=""
        )
        
        result = get_parallel_jobs()
        
        assert result == 1

    @patch("platform.system", return_value="Linux")
    def test_get_parallel_jobs_when_nproc_fails(self, mock_system, mock_utils_run_command):
        mock_utils_run_command.return_value = subprocess.CompletedProcess(
            args=["nproc"],
            returncode=1,
            stdout="",
            stderr="error"
        )
        
        result = get_parallel_jobs()
        
        assert result == 1

    @patch("platform.system", return_value="Linux")
    def test_get_parallel_jobs_when_nproc_not_found(self, mock_system, mock_utils_run_command):
        mock_utils_run_command.side_effect = FileNotFoundError()
        
        result = get_parallel_jobs()
        
        assert result == 1

    @patch("platform.system", return_value="Linux")
    def test_get_parallel_jobs_with_invalid_output(self, mock_system, mock_utils_run_command):
        mock_utils_run_command.return_value = subprocess.CompletedProcess(
            args=["nproc"],
            returncode=0,
            stdout="invalid\n",
            stderr=""
        )
        
        result = get_parallel_jobs()
        
        assert result == 1


class TestGetParallelJobsMacOS:
    """Test get_parallel_jobs function on macOS."""

    @patch("platform.system", return_value="Darwin")
    def test_get_parallel_jobs_returns_cpu_count_minus_one_macos(self, mock_system, mock_utils_run_command):
        mock_utils_run_command.return_value = subprocess.CompletedProcess(
            args=["sysctl", "-n", "hw.ncpu"],
            returncode=0,
            stdout="8\n",
            stderr=""
        )
        
        result = get_parallel_jobs()
        
        assert result == 7
        mock_utils_run_command.assert_called_once_with(["sysctl", "-n", "hw.ncpu"], check=False)

    @patch("platform.system", return_value="Darwin")
    def test_get_parallel_jobs_with_single_cpu_macos(self, mock_system, mock_utils_run_command):
        mock_utils_run_command.return_value = subprocess.CompletedProcess(
            args=["sysctl", "-n", "hw.ncpu"],
            returncode=0,
            stdout="1\n",
            stderr=""
        )
        
        result = get_parallel_jobs()
        
        assert result == 1

    @patch("platform.system", return_value="Darwin")
    def test_get_parallel_jobs_with_two_cpus_macos(self, mock_system, mock_utils_run_command):
        mock_utils_run_command.return_value = subprocess.CompletedProcess(
            args=["sysctl", "-n", "hw.ncpu"],
            returncode=0,
            stdout="2\n",
            stderr=""
        )
        
        result = get_parallel_jobs()
        
        assert result == 1

    @patch("platform.system", return_value="Darwin")
    def test_get_parallel_jobs_when_sysctl_fails_macos(self, mock_system, mock_utils_run_command):
        mock_utils_run_command.return_value = subprocess.CompletedProcess(
            args=["sysctl", "-n", "hw.ncpu"],
            returncode=1,
            stdout="",
            stderr="error"
        )
        
        result = get_parallel_jobs()
        
        assert result == 1

    @patch("platform.system", return_value="Darwin")
    def test_get_parallel_jobs_when_sysctl_not_found_macos(self, mock_system, mock_utils_run_command):
        mock_utils_run_command.side_effect = FileNotFoundError()
        
        result = get_parallel_jobs()
        
        assert result == 1

    @patch("platform.system", return_value="Darwin")
    def test_get_parallel_jobs_with_invalid_output_macos(self, mock_system, mock_utils_run_command):
        mock_utils_run_command.return_value = subprocess.CompletedProcess(
            args=["sysctl", "-n", "hw.ncpu"],
            returncode=0,
            stdout="invalid\n",
            stderr=""
        )
        
        result = get_parallel_jobs()
        
        assert result == 1