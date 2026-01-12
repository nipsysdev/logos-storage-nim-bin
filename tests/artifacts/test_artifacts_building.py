"""Tests for artifact building functions in artifacts.py."""

from pathlib import Path
from unittest.mock import patch

import pytest

from src.artifacts import build_libstorage


class TestBuildLibstorage:
    """Test build_libstorage function."""

    def test_build_libstorage_runs_make_deps(self):
        """Test that build_libstorage runs make deps command."""
        logos_storage_dir = Path("/tmp/test")
        jobs = 4
        
        with patch("src.artifacts.run_command") as mock_run:
            build_libstorage(logos_storage_dir, jobs)
        
        # Verify make deps was called
        deps_calls = [call for call in mock_run.call_args_list if "deps" in str(call[0][0])]
        assert len(deps_calls) == 1
        assert "make" in deps_calls[0][0][0]
        assert "deps" in deps_calls[0][0][0]

    def test_build_libstorage_runs_make_libstorage(self):
        """Test that build_libstorage runs make libstorage command."""
        logos_storage_dir = Path("/tmp/test")
        jobs = 4
        
        with patch("src.artifacts.run_command") as mock_run:
            build_libstorage(logos_storage_dir, jobs)
        
        # Verify make libstorage was called
        libstorage_calls = [call for call in mock_run.call_args_list if "libstorage" in str(call[0][0])]
        assert len(libstorage_calls) == 1
        assert "make" in libstorage_calls[0][0][0]
        assert "libstorage" in libstorage_calls[0][0][0]

    def test_build_libstorage_passes_jobs_parameter(self):
        """Test that build_libstorage passes jobs parameter to make commands."""
        logos_storage_dir = Path("/tmp/test")
        jobs = 8
        
        with patch("src.artifacts.run_command") as mock_run:
            build_libstorage(logos_storage_dir, jobs)
        
        # Verify -j 8 was passed to make commands
        for call in mock_run.call_args_list:
            if "make" in str(call[0][0]) and "libstorage" in str(call[0][0]):
                assert "-j" in call[0][0]
                assert "8" in call[0][0]

    def test_build_libstorage_sets_static_env(self):
        """Test that build_libstorage sets STATIC=1 environment variable."""
        logos_storage_dir = Path("/tmp/test")
        jobs = 4
        
        with patch("src.artifacts.run_command") as mock_run:
            build_libstorage(logos_storage_dir, jobs)
        
        # Verify STATIC=1 was set for all make commands
        for call in mock_run.call_args_list:
            if "make" in str(call[0][0]) and len(call) > 1 and 'env' in call[1]:
                assert call[1]['env'] == {"STATIC": "1"}

    def test_build_libstorage_passes_cwd(self):
        """Test that build_libstorage passes correct working directory."""
        logos_storage_dir = Path("/tmp/test")
        jobs = 4
        
        with patch("src.artifacts.run_command") as mock_run:
            build_libstorage(logos_storage_dir, jobs)
        
        # Verify cwd was set to logos_storage_dir for all make commands
        for call in mock_run.call_args_list:
            if "make" in str(call[0][0]) and len(call) > 1 and 'cwd' in call[1]:
                assert call[1]['cwd'] == logos_storage_dir