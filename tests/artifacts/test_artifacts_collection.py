"""Tests for artifact collection in artifacts.py."""

from pathlib import Path
from unittest.mock import patch

import pytest

from src.artifacts import collect_artifacts


class TestCollectArtifacts:
    """Test collect_artifacts function."""

    def test_collect_artifacts_finds_all_libraries(self, sample_artifact_paths, mock_artifact_collection_setup):
        libraries = collect_artifacts(sample_artifact_paths, "x86_64")
        
        assert len(libraries) == 6

    def test_collect_artifacts_raises_file_not_found(self, sample_artifact_paths):
        libstorage = sample_artifact_paths / "build" / "libstorage.a"
        libstorage.unlink()
        
        with pytest.raises(FileNotFoundError) as exc_info:
            collect_artifacts(sample_artifact_paths, "x86_64")
        
        assert "libstorage.a not found" in str(exc_info.value)

    def test_collect_artifacts_raises_value_error_for_incompatible(self, sample_artifact_paths):
        with patch("src.artifacts.check_artifact_compatibility", return_value=False):
            with pytest.raises(ValueError) as exc_info:
                collect_artifacts(sample_artifact_paths, "x86_64")
        
        assert "not compatible with target architecture" in str(exc_info.value)

    def test_collect_artifacts_uses_release_leopard(self, sample_artifact_paths, mock_artifact_collection_setup):
        libraries = collect_artifacts(sample_artifact_paths, "x86_64")
        
        leopard_libs = [lib for lib in libraries if "liblibleopard.a" in str(lib)]
        assert len(leopard_libs) == 1
        assert "release" in str(leopard_libs[0])

    def test_collect_artifacts_uses_debug_leopard_when_release_missing(self, sample_artifact_paths):
        leopard_release = sample_artifact_paths / "nimcache" / "release" / "libstorage" / "vendor_leopard" / "liblibleopard.a"
        leopard_release.unlink()
        
        leopard_debug = sample_artifact_paths / "nimcache" / "debug" / "libstorage" / "vendor_leopard" / "liblibleopard.a"
        leopard_debug.parent.mkdir(parents=True, exist_ok=True)
        leopard_debug.write_bytes(b"fake libleopard debug content")
        
        with patch("src.artifacts.check_artifact_compatibility", return_value=True):
            libraries = collect_artifacts(sample_artifact_paths, "x86_64")
        
        leopard_libs = [lib for lib in libraries if "liblibleopard.a" in str(lib)]
        assert len(leopard_libs) == 1
        assert "debug" in str(leopard_libs[0])

    def test_collect_artifacts_raises_when_leopard_missing(self, sample_artifact_paths):
        leopard_release = sample_artifact_paths / "nimcache" / "release" / "libstorage" / "vendor_leopard" / "liblibleopard.a"
        leopard_release.unlink()
        
        leopard_debug = sample_artifact_paths / "nimcache" / "debug" / "libstorage" / "vendor_leopard" / "liblibleopard.a"
        if leopard_debug.exists():
            leopard_debug.unlink()
        
        with patch("src.artifacts.check_artifact_compatibility", return_value=True):
            with pytest.raises(FileNotFoundError) as exc_info:
                collect_artifacts(sample_artifact_paths, "x86_64")
        
        assert "liblibleopard.a not found" in str(exc_info.value)

    def test_collect_artifacts_checks_release_leopard_compatibility(self, sample_artifact_paths):
        """Test that collect_artifacts checks compatibility for release leopard library."""
        with patch("src.artifacts.check_artifact_compatibility") as mock_check:
            mock_check.return_value = True
            libraries = collect_artifacts(sample_artifact_paths, "x86_64")
        
        # Verify check_artifact_compatibility was called for release leopard
        leopard_release = sample_artifact_paths / "nimcache" / "release" / "libstorage" / "vendor_leopard" / "liblibleopard.a"
        leopard_calls = [call for call in mock_check.call_args_list if call[0][0] == leopard_release]
        assert len(leopard_calls) == 1
        assert leopard_calls[0][0][1] == "x86_64"

    def test_collect_artifacts_raises_when_release_leopard_incompatible(self, sample_artifact_paths):
        """Test that collect_artifacts raises ValueError when release leopard is incompatible."""
        leopard_release = sample_artifact_paths / "nimcache" / "release" / "libstorage" / "vendor_leopard" / "liblibleopard.a"
        
        with patch("src.artifacts.check_artifact_compatibility") as mock_check:
            # Make release leopard incompatible
            def side_effect(path, target):
                if path == leopard_release:
                    return False
                return True
            mock_check.side_effect = side_effect
            
            with pytest.raises(ValueError) as exc_info:
                collect_artifacts(sample_artifact_paths, "x86_64")
        
        assert "liblibleopard.a (release) is not compatible with target architecture" in str(exc_info.value)

    def test_collect_artifacts_checks_debug_leopard_compatibility(self, sample_artifact_paths):
        """Test that collect_artifacts checks compatibility for debug leopard library when release is missing."""
        leopard_release = sample_artifact_paths / "nimcache" / "release" / "libstorage" / "vendor_leopard" / "liblibleopard.a"
        leopard_release.unlink()
        
        leopard_debug = sample_artifact_paths / "nimcache" / "debug" / "libstorage" / "vendor_leopard" / "liblibleopard.a"
        leopard_debug.parent.mkdir(parents=True, exist_ok=True)
        leopard_debug.write_bytes(b"fake libleopard debug content")
        
        with patch("src.artifacts.check_artifact_compatibility") as mock_check:
            mock_check.return_value = True
            libraries = collect_artifacts(sample_artifact_paths, "x86_64")
        
        # Verify check_artifact_compatibility was called for debug leopard
        leopard_calls = [call for call in mock_check.call_args_list if call[0][0] == leopard_debug]
        assert len(leopard_calls) == 1
        assert leopard_calls[0][0][1] == "x86_64"

    def test_collect_artifacts_raises_when_debug_leopard_incompatible(self, sample_artifact_paths):
        """Test that collect_artifacts raises ValueError when debug leopard is incompatible."""
        leopard_release = sample_artifact_paths / "nimcache" / "release" / "libstorage" / "vendor_leopard" / "liblibleopard.a"
        leopard_release.unlink()
        
        leopard_debug = sample_artifact_paths / "nimcache" / "debug" / "libstorage" / "vendor_leopard" / "liblibleopard.a"
        leopard_debug.parent.mkdir(parents=True, exist_ok=True)
        leopard_debug.write_bytes(b"fake libleopard debug content")
        
        with patch("src.artifacts.check_artifact_compatibility") as mock_check:
            # Make debug leopard incompatible
            def side_effect(path, target):
                if path == leopard_debug:
                    return False
                return True
            mock_check.side_effect = side_effect
            
            with pytest.raises(ValueError) as exc_info:
                collect_artifacts(sample_artifact_paths, "x86_64")
        
        assert "liblibleopard.a (debug) is not compatible with target architecture" in str(exc_info.value)