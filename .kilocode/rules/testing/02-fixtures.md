# Fixtures Organization

This document covers how to organize and use pytest fixtures effectively.

## 1. Organize Fixtures into Focused Modules

When multiple tests use the same mocking/patching setup, extract the common logic into reusable fixtures. For better organization, split fixtures into focused modules by concern rather than keeping everything in `conftest.py`.

### Fixture Module Structure

```
tests/
├── fixtures/
│   ├── __init__.py
│   ├── file_operations.py      # File system operation fixtures
│   ├── system_commands.py      # System command fixtures
│   ├── build.py                # Build-related fixtures
│   └── repository.py           # Repository-related fixtures
└── conftest.py                 # Common utility fixtures + imports
```

### Creating Focused Fixture Modules

**`tests/fixtures/file_operations.py`** - File system operations:

```python
"""Focused file system operation fixtures."""

import pytest
from unittest.mock import patch

@pytest.fixture
def mock_file_writing():
    """Mock file writing operations (write_bytes, write_text)."""
    with patch("pathlib.Path.write_bytes") as mock_bytes:
        with patch("pathlib.Path.write_text") as mock_text:
            yield {
                "write_bytes": mock_bytes,
                "write_text": mock_text,
            }

@pytest.fixture
def mock_file_reading():
    """Mock file reading operations (read_text, stat)."""
    with patch("pathlib.Path.read_text") as mock_read:
        with patch("pathlib.Path.stat") as mock_stat:
            mock_stat_result = MagicMock()
            mock_stat_result.st_size = 1000
            mock_stat.return_value = mock_stat_result
            yield {
                "read_text": mock_read,
                "stat": mock_stat,
            }

@pytest.fixture
def mock_directory_operations():
    """Mock directory operations (mkdir, iterdir, is_file)."""
    with patch("pathlib.Path.mkdir") as mock_mkdir:
        with patch("pathlib.Path.iterdir") as mock_iterdir:
            with patch("pathlib.Path.is_file") as mock_is_file:
                mock_iterdir.return_value = []
                mock_is_file.return_value = True
                yield {
                    "mkdir": mock_mkdir,
                    "iterdir": mock_iterdir,
                    "is_file": mock_is_file,
                }

@pytest.fixture
def mock_file_deletion():
    """Mock file deletion operations (unlink, rmtree)."""
    with patch("pathlib.Path.unlink") as mock_unlink:
        with patch("shutil.rmtree") as mock_rmtree:
            yield {
                "unlink": mock_unlink,
                "rmtree": mock_rmtree,
            }
```

**`tests/fixtures/system_commands.py`** - System commands:

```python
"""Focused system command fixtures."""

import pytest
import subprocess
from unittest.mock import patch

@pytest.fixture
def mock_run_command():
    """Mock src.artifacts.run_command."""
    with patch("src.artifacts.run_command") as mock:
        yield mock

@pytest.fixture
def mock_utils_run_command():
    """Mock src.utils.run_command."""
    with patch("src.utils.run_command") as mock:
        yield mock

@pytest.fixture
def mock_ar_commands():
    """Mock ar (archive) commands."""
    with patch("src.artifacts.run_command") as mock:
        def side_effect(cmd):
            if "ar" in cmd:
                return subprocess.CompletedProcess(
                    args=cmd,
                    returncode=0,
                    stdout="",
                    stderr=""
                )
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=0,
                stdout="",
                stderr=""
            )
        mock.side_effect = side_effect
        yield mock

@pytest.fixture
def mock_sha256sum_commands():
    """Mock sha256sum commands."""
    with patch("src.artifacts.run_command") as mock:
        def side_effect(cmd):
            if "sha256sum" in cmd:
                # Extract filename from command
                filename = cmd[-1]
                return subprocess.CompletedProcess(
                    args=cmd,
                    returncode=0,
                    stdout=f"abc123def456  {filename}\n",
                    stderr=""
                )
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=0,
                stdout="",
                stderr=""
            )
        mock.side_effect = side_effect
        yield mock

@pytest.fixture
def mock_file_commands():
    """Mock file command."""
    with patch("src.artifacts.run_command") as mock:
        def side_effect(cmd):
            if "file" in cmd:
                return subprocess.CompletedProcess(
                    args=cmd,
                    returncode=0,
                    stdout="ELF 64-bit LSB executable, x86-64",
                    stderr=""
                )
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=0,
                stdout="",
                stderr=""
            )
        mock.side_effect = side_effect
        yield mock
```

**`tests/fixtures/build.py`** - Build-related fixtures:

```python
"""Build-related fixtures."""

import pytest
from unittest.mock import patch
from pathlib import Path
from src.repository import CommitInfo

@pytest.fixture
def mock_build_setup():
    """Fixture that provides common mocks for build.py main() function.

    This fixture sets up all the common patches needed for testing the main()
    function, reducing duplication across tests.
    """
    logos_storage_dir = Path("logos-storage-nim")
    mock_commit_info = CommitInfo("abc123def456789abc123def456789abc123def", "abc123d", "master")

    with patch("build.get_platform_identifier", return_value="linux-amd64") as mock_platform:
        with patch("build.configure_reproducible_environment") as mock_config:
            with patch("build.ensure_logos_storage_repo") as mock_repo:
                mock_repo.return_value = (logos_storage_dir, mock_commit_info)
                with patch("build.get_parallel_jobs", return_value=4) as mock_jobs:
                    with patch("build.build_libstorage") as mock_build:
                        with patch("build.get_host_triple", return_value="x86_64") as mock_triple:
                            with patch("build.collect_artifacts", return_value=[]) as mock_collect:
                                with patch("build.combine_libraries", return_value=Path("dist/libstorage.a")) as mock_combine:
                                    with patch("build.copy_header_file") as mock_copy:
                                        with patch("build.generate_sha256sums") as mock_checksums:
                                            yield {
                                                "mock_platform": mock_platform,
                                                "mock_config": mock_config,
                                                "mock_repo": mock_repo,
                                                "mock_jobs": mock_jobs,
                                                "mock_build": mock_build,
                                                "mock_triple": mock_triple,
                                                "mock_collect": mock_collect,
                                                "mock_combine": mock_combine,
                                                "mock_copy": mock_copy,
                                                "mock_checksums": mock_checksums,
                                                "logos_storage_dir": logos_storage_dir,
                                                "mock_commit_info": mock_commit_info,
                                            }
```

**`tests/fixtures/repository.py`** - Repository-related fixtures:

```python
"""Repository-related fixtures."""

import pytest
import subprocess
from unittest.mock import patch

@pytest.fixture
def mock_git_clone_responses():
    """Standard git clone subprocess responses."""
    with patch("src.utils.run_command") as mock:
        def side_effect(cmd):
            if "git clone" in cmd:
                return subprocess.CompletedProcess(
                    args=cmd,
                    returncode=0,
                    stdout="",
                    stderr=""
                )
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=0,
                stdout="",
                stderr=""
            )
        mock.side_effect = side_effect
        yield mock

@pytest.fixture
def mock_git_update_responses():
    """Standard git update subprocess responses."""
    with patch("src.utils.run_command") as mock:
        def side_effect(cmd):
            if "git fetch" in cmd:
                return subprocess.CompletedProcess(
                    args=cmd,
                    returncode=0,
                    stdout="",
                    stderr=""
                )
            elif "git rev-parse" in cmd:
                return subprocess.CompletedProcess(
                    args=cmd,
                    returncode=0,
                    stdout="abc123def456789abc123def456789abc123def\n",
                    stderr=""
                )
            elif "git checkout" in cmd:
                return subprocess.CompletedProcess(
                    args=cmd,
                    returncode=0,
                    stdout="",
                    stderr=""
                )
            elif "git pull" in cmd:
                return subprocess.CompletedProcess(
                    args=cmd,
                    returncode=0,
                    stdout="",
                    stderr=""
                )
            return subprocess.CompletedProcess(
                args=cmd,
                returncode=0,
                stdout="",
                stderr=""
            )
        mock.side_effect = side_effect
        yield mock
```

### Importing Fixtures into conftest.py

```python
# tests/conftest.py
# Import fixtures from modules to make them available to all tests
from tests.fixtures.file_operations import (
    mock_file_writing,
    mock_file_reading,
    mock_directory_operations,
    mock_file_deletion,
)
from tests.fixtures.system_commands import (
    mock_run_command,
    mock_utils_run_command,
    mock_ar_commands,
    mock_sha256sum_commands,
    mock_file_commands,
)
from tests.fixtures.build import mock_build_setup
from tests.fixtures.repository import (
    mock_git_clone_responses,
    mock_git_update_responses,
)

# Keep only common utility fixtures here
@pytest.fixture
def temp_dir(tmp_path):
    """Temporary directory fixture."""
    return tmp_path

@pytest.fixture
def sample_commit_info():
    """Sample commit info for testing."""
    from src.repository import CommitInfo
    return CommitInfo(
        "abc123def456789abc123def456789abc123def",
        "abc123d",
        "master"
    )
```

### Benefits of Focused Fixture Modules

- ✅ **Better Organization**: Fixtures grouped by concern
- ✅ **Easier Navigation**: Quickly find relevant fixtures
- ✅ **Reduced conftest.py Size**: Keeps conftest.py manageable
- ✅ **Reusability**: Fixtures can be imported across test files
- ✅ **Clearer Dependencies**: Tests explicitly declare which fixtures they need

### When to Create Fixture Modules

- When `conftest.py` exceeds 200-300 lines
- When fixtures can be grouped by concern (file ops, commands, etc.)
- When fixtures are used across multiple test files
- When you want to improve test organization

## 2. Extract Common Mocking/Patching Logic into Fixtures

When multiple tests use the same mocking/patching setup, extract the common logic into reusable fixtures. This reduces duplication and makes tests more maintainable.

**❌ BAD: Repeated patching across multiple tests**

```python
# test_build_main.py
def test_main_calls_get_platform_identifier(self):
    with patch("build.get_platform_identifier", return_value="linux-amd64") as mock_platform:
        with patch("build.configure_reproducible_environment"):
            with patch("build.ensure_logos_storage_repo") as mock_repo:
                mock_repo.return_value = (Path("logos-storage-nim"), CommitInfo("abc123", "abc123d", "master"))
                with patch("build.get_parallel_jobs", return_value=4):
                    with patch("build.build_libstorage"):
                        with patch("build.get_host_triple", return_value="x86_64"):
                            with patch("build.collect_artifacts", return_value=[]):
                                with patch("build.combine_libraries", return_value=Path("dist/libstorage.a")):
                                    with patch("build.copy_header_file"):
                                        with patch("build.generate_sha256sums"):
                                            main()

    mock_platform.assert_called_once()

def test_main_calls_configure_reproducible_environment(self):
    with patch("build.get_platform_identifier", return_value="linux-amd64"):
        with patch("build.configure_reproducible_environment") as mock_config:
            with patch("build.ensure_logos_storage_repo") as mock_repo:
                mock_repo.return_value = (Path("logos-storage-nim"), CommitInfo("abc123", "abc123d", "master"))
                with patch("build.get_parallel_jobs", return_value=4):
                    with patch("build.build_libstorage"):
                        with patch("build.get_host_triple", return_value="x86_64"):
                            with patch("build.collect_artifacts", return_value=[]):
                                with patch("build.combine_libraries", return_value=Path("dist/libstorage.a")):
                                    with patch("build.copy_header_file"):
                                        with patch("build.generate_sha256sums"):
                                            main()

    mock_config.assert_called_once()
```

**✅ GOOD: Extract common setup into fixture**

```python
# tests/conftest.py
@pytest.fixture
def mock_build_setup():
    """Fixture that provides common mocks for build.py main() function.

    This fixture sets up all the common patches needed for testing the main()
    function, reducing duplication across tests.
    """
    from unittest.mock import patch
    from pathlib import Path
    from src.repository import CommitInfo

    logos_storage_dir = Path("logos-storage-nim")
    mock_commit_info = CommitInfo("abc123def456789abc123def456789abc123def", "abc123d", "master")

    with patch("build.get_platform_identifier", return_value="linux-amd64") as mock_platform:
        with patch("build.configure_reproducible_environment") as mock_config:
            with patch("build.ensure_logos_storage_repo") as mock_repo:
                mock_repo.return_value = (logos_storage_dir, mock_commit_info)
                with patch("build.get_parallel_jobs", return_value=4) as mock_jobs:
                    with patch("build.build_libstorage") as mock_build:
                        with patch("build.get_host_triple", return_value="x86_64") as mock_triple:
                            with patch("build.collect_artifacts", return_value=[]) as mock_collect:
                                with patch("build.combine_libraries", return_value=Path("dist/libstorage.a")) as mock_combine:
                                    with patch("build.copy_header_file") as mock_copy:
                                        with patch("build.generate_sha256sums") as mock_checksums:
                                            yield {
                                                "mock_platform": mock_platform,
                                                "mock_config": mock_config,
                                                "mock_repo": mock_repo,
                                                "mock_jobs": mock_jobs,
                                                "mock_build": mock_build,
                                                "mock_triple": mock_triple,
                                                "mock_collect": mock_collect,
                                                "mock_combine": mock_combine,
                                                "mock_copy": mock_copy,
                                                "mock_checksums": mock_checksums,
                                                "logos_storage_dir": logos_storage_dir,
                                                "mock_commit_info": mock_commit_info,
                                            }

# test_build_main.py
def test_main_calls_get_platform_identifier(self, mock_build_setup):
    main()

    mock_build_setup["mock_platform"].assert_called_once()

def test_main_calls_configure_reproducible_environment(self, mock_build_setup):
    main()

    mock_build_setup["mock_config"].assert_called_once()
```

**Benefits of Extracting Common Mocking Logic:**

- ✅ **Reduced Duplication**: Eliminates hundreds of lines of repetitive patching code
- ✅ **Improved Maintainability**: Changes to mock setup only need to be made in one place
- ✅ **Better Test Focus**: Tests focus on assertions rather than setup
- ✅ **Consistency**: All tests use the same mock configuration
- ✅ **Easier to Add Tests**: New tests can reuse existing fixtures

**When to Create Fixtures:**

- When 3 or more tests use the same patching setup
- When patching setup is complex (5+ nested patches)
- When tests are in the same test file or module
- When the setup is reusable across multiple test files

**Guidelines:**

- Name fixtures descriptively (e.g., `mock_build_setup`, `mock_git_clone_responses`)
- Return a dictionary of mocks for easy access in tests
- Document what the fixture provides in the docstring
- Keep fixtures focused on a single concern
- Use `yield` instead of `return` for context manager fixtures

## 3. Create Helper Functions (DRY Principle)

**❌ BAD: Repeated setup code**

```python
def test_format_date_1(self):
    handler = DateHandler()
    handler.set_timezone('UTC')
    result = handler.format_date('2024-01-15')
    assert result == '2024-01-15T00:00:00Z'

def test_format_date_2(self):
    handler = DateHandler()
    handler.set_timezone('UTC')
    result = handler.format_date('2024-02-20')
    assert result == '2024-02-20T00:00:00Z'

def test_format_date_3(self):
    handler = DateHandler()
    handler.set_timezone('UTC')
    result = handler.format_date('2024-03-25')
    assert result == '2024-03-25T00:00:00Z'
```

**✅ GOOD: Organized helper functions**

```python
class TestDateHandler:
    def setup_method(self):
        """Setup method runs before each test"""
        self.handler = DateHandler()
        self.handler.set_timezone('UTC')

    def test_format_date_january(self):
        result = self.handler.format_date('2024-01-15')
        assert result == '2024-01-15T00:00:00Z'

    def test_format_date_february(self):
        result = self.handler.format_date('2024-02-20')
        assert result == '2024-02-20T00:00:00Z'

    def test_format_date_march(self):
        result = self.handler.format_date('2024-03-25')
        assert result == '2024-03-25T00:00:00Z'
```

**For complex test data, use fixtures:**

```python
import pytest

@pytest.fixture
def date_handler():
    """Fixture that provides a configured DateHandler instance"""
    handler = DateHandler()
    handler.set_timezone('UTC')
    return handler

@pytest.fixture
def sample_dates():
    """Fixture that provides sample date data"""
    return {
        'january': '2024-01-15',
        'february': '2024-02-20',
        'march': '2024-03-25',
    }

def test_format_date_january(date_handler, sample_dates):
    result = date_handler.format_date(sample_dates['january'])
    assert result == '2024-01-15T00:00:00Z'
```
