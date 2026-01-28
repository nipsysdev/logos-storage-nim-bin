"""Tests for artifact collection in artifacts.py."""

from pathlib import Path
from unittest.mock import patch

import pytest

from src.artifacts import collect_artifacts


class TestCollectArtifacts:
    """Test collect_artifacts function."""

    def test_collect_artifacts_finds_all_libraries(self, sample_artifact_paths, mock_path_exists):
        """Test that collect_artifacts finds all 4 libraries when they exist."""
        mock_path_exists.return_value = True

        libraries = collect_artifacts(sample_artifact_paths, "x86_64")

        assert len(libraries) == 4

    def test_collect_artifacts_raises_file_not_found(self, sample_artifact_paths):
        """Test that collect_artifacts raises FileNotFoundError when libstorage.a is missing."""
        libstorage = sample_artifact_paths / "build" / "libstorage.a"

        # Create mock path_exists function that returns False for libstorage.a
        def mock_path_exists(path: Path) -> bool:
            return str(path) != str(libstorage)

        with pytest.raises(FileNotFoundError) as exc_info:
            collect_artifacts(sample_artifact_paths, "x86_64", path_exists=mock_path_exists)

        assert "libstorage.a not found" in str(exc_info.value)