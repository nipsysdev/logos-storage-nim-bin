"""Tests for artifact collection in artifacts.py."""

from pathlib import Path
from unittest.mock import patch

import pytest

from src.artifacts import collect_artifacts


class TestCollectArtifacts:
    """Test collect_artifacts function."""

    def test_collect_artifacts_finds_all_libraries(self, sample_artifact_paths, mock_path_exists):
        """Test that collect_artifacts finds all 6 libraries when they exist."""
        mock_path_exists.return_value = True
        
        libraries = collect_artifacts(sample_artifact_paths, "x86_64")
        
        assert len(libraries) == 6

    def test_collect_artifacts_raises_file_not_found(self, sample_artifact_paths):
        """Test that collect_artifacts raises FileNotFoundError when libstorage.a is missing."""
        libstorage = sample_artifact_paths / "build" / "libstorage.a"
        
        # Create mock path_exists function that returns False for libstorage.a
        def mock_path_exists(path: Path) -> bool:
            return str(path) != str(libstorage)
        
        with pytest.raises(FileNotFoundError) as exc_info:
            collect_artifacts(sample_artifact_paths, "x86_64", path_exists=mock_path_exists)
        
        assert "libstorage.a not found" in str(exc_info.value)

    def test_collect_artifacts_uses_release_leopard(self, sample_artifact_paths, mock_path_exists):
        """Test that collect_artifacts uses release leopard library when available."""
        leopard_release = sample_artifact_paths / "nimcache" / "release" / "libstorage" / "vendor_leopard" / "liblibleopard.a"
        
        # Configure exists to return True for release leopard
        mock_path_exists.return_value = True
        
        libraries = collect_artifacts(sample_artifact_paths, "x86_64")
        
        leopard_libs = [lib for lib in libraries if "liblibleopard.a" in str(lib)]
        assert len(leopard_libs) == 1
        assert "release" in str(leopard_libs[0])

    def test_collect_artifacts_uses_debug_leopard_when_release_missing(self, sample_artifact_paths):
        """Test that collect_artifacts uses debug leopard when release is missing."""
        leopard_release = sample_artifact_paths / "nimcache" / "release" / "libstorage" / "vendor_leopard" / "liblibleopard.a"
        leopard_debug = sample_artifact_paths / "nimcache" / "debug" / "libstorage" / "vendor_leopard" / "liblibleopard.a"
        
        # Create mock path_exists function that returns False for release, True for debug
        def mock_path_exists(path: Path) -> bool:
            return str(path) != str(leopard_release)
        
        libraries = collect_artifacts(sample_artifact_paths, "x86_64", path_exists=mock_path_exists)
        
        leopard_libs = [lib for lib in libraries if "liblibleopard.a" in str(lib)]
        assert len(leopard_libs) == 1
        assert "debug" in str(leopard_libs[0])

    def test_collect_artifacts_raises_when_leopard_missing(self, sample_artifact_paths):
        """Test that collect_artifacts raises FileNotFoundError when leopard is missing."""
        leopard_release = sample_artifact_paths / "nimcache" / "release" / "libstorage" / "vendor_leopard" / "liblibleopard.a"
        leopard_debug = sample_artifact_paths / "nimcache" / "debug" / "libstorage" / "vendor_leopard" / "liblibleopard.a"
        
        # Create mock path_exists function that returns False for both release and debug leopard
        def mock_path_exists(path: Path) -> bool:
            return str(path) not in {str(leopard_release), str(leopard_debug)}
        
        with pytest.raises(FileNotFoundError) as exc_info:
            collect_artifacts(sample_artifact_paths, "x86_64", path_exists=mock_path_exists)
        
        assert "liblibleopard.a not found" in str(exc_info.value)