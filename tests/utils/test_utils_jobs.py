"""Tests for parallel jobs in utils.py."""

import subprocess
from unittest.mock import patch

import pytest

from src.utils import get_parallel_jobs


class TestGetParallelJobs:
    """Test get_parallel_jobs function."""

    def test_get_parallel_jobs_returns_cpu_count_minus_one(self, mock_run_command):
        mock_run_command.return_value = subprocess.CompletedProcess(
            args=["nproc"],
            returncode=0,
            stdout="8\n",
            stderr=""
        )
        
        result = get_parallel_jobs()
        
        assert result == 7

    def test_get_parallel_jobs_with_single_cpu(self, mock_run_command):
        mock_run_command.return_value = subprocess.CompletedProcess(
            args=["nproc"],
            returncode=0,
            stdout="1\n",
            stderr=""
        )
        
        result = get_parallel_jobs()
        
        assert result == 1

    def test_get_parallel_jobs_with_two_cpus(self, mock_run_command):
        mock_run_command.return_value = subprocess.CompletedProcess(
            args=["nproc"],
            returncode=0,
            stdout="2\n",
            stderr=""
        )
        
        result = get_parallel_jobs()
        
        assert result == 1

    def test_get_parallel_jobs_when_nproc_fails(self, mock_run_command):
        mock_run_command.return_value = subprocess.CompletedProcess(
            args=["nproc"],
            returncode=1,
            stdout="",
            stderr="error"
        )
        
        result = get_parallel_jobs()
        
        assert result == 1

    def test_get_parallel_jobs_when_nproc_not_found(self, mock_run_command):
        mock_run_command.side_effect = FileNotFoundError()
        
        result = get_parallel_jobs()
        
        assert result == 1

    def test_get_parallel_jobs_with_invalid_output(self, mock_run_command):
        mock_run_command.return_value = subprocess.CompletedProcess(
            args=["nproc"],
            returncode=0,
            stdout="invalid\n",
            stderr=""
        )
        
        result = get_parallel_jobs()
        
        assert result == 1