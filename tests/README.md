# Tests

## Structure

```
tests/
├── conftest.py                    # Shared fixtures and test configuration
├── fixtures/                      # Focused fixture modules organized by concern
│   ├── build.py                   # Build orchestration fixtures
│   ├── file_operations.py         # File system operation fixtures
│   ├── repository.py              # Git operation fixtures
│   └── system_commands.py         # System command execution fixtures
├── utils/                         # Command execution, platform detection, jobs, environment
├── repository/                    # Git operations (clone, update, commit info)
├── artifacts/                     # Build artifacts (clean, build, collect, combine, checksums)
├── build_tests/                   # Build orchestration
└── clean/                         # Cleanup operations
```

## Running Tests

### Install Dependencies

```bash
pip install -r requirements-test.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/utils/test_utils_command.py
```

### Run Specific Test Class

```bash
pytest tests/utils/test_utils_command.py::TestRunCommand
```

### Run Specific Test Method

```bash
pytest tests/utils/test_utils_command.py::TestRunCommand::test_run_command_returns_completed_process
```

### Run All Tests for a Module

```bash
pytest tests/utils/
pytest tests/repository/
pytest tests/artifacts/
pytest tests/build_tests/
pytest tests/clean/
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
```

## Fixtures

### Shared Fixtures in [`conftest.py`](conftest.py)

| Fixture                          | Purpose                                              |
| -------------------------------- | ---------------------------------------------------- |
| `temp_dir`                       | Temporary directory for file operations              |
| `sample_commit_info`             | Sample `CommitInfo` dataclass                        |
| `sample_artifact_paths`          | Sample artifact file structure                       |
| `logos_storage_dir`              | Temporary directory for logos-storage-nim repository |
| `dist_dir`                       | Temporary directory for distribution files           |
| `mock_subprocess_run`            | Mock for `subprocess.run`                            |
| `mock_shutil_rmtree`             | Mock for `shutil.rmtree`                             |
| `mock_path_rglob`                | Mock for `Path.rglob`                                |
| `mock_path_unlink`               | Mock for `Path.unlink`                               |
| `mock_path_mkdir`                | Mock for `Path.mkdir`                                |
| `mock_path_write_text`           | Mock for `Path.write_text`                           |
| `mock_path_read_text`            | Mock for `Path.read_text`                            |
| `mock_path_stat`                 | Mock for `Path.stat`                                 |
| `mock_os_environ`                | Mock for `os.environ`                                |
| `mock_platform_machine`          | Mock for `platform.machine`                          |
| `mock_clean_setup`               | Common mocks for clean.py functions                  |
| `mock_artifact_collection_setup` | Common mocks for artifact collection tests           |

### Focused Fixture Modules

Fixtures are organized into focused modules in [`tests/fixtures/`](fixtures/):

#### [`fixtures/file_operations.py`](fixtures/file_operations.py)

| Fixture                     | Purpose                                                    |
| --------------------------- | ---------------------------------------------------------- |
| `mock_path_exists`          | Mock for `Path.exists()`                                   |
| `mock_file_writing`         | Mock for file writing operations (write_bytes, write_text) |
| `mock_file_reading`         | Mock for file reading operations (read_text, stat)         |
| `mock_directory_operations` | Mock for directory operations (mkdir, iterdir, is_file)    |
| `mock_file_deletion`        | Mock for file deletion operations (unlink, rmtree)         |

#### [`fixtures/system_commands.py`](fixtures/system_commands.py)

| Fixture                   | Purpose                              |
| ------------------------- | ------------------------------------ |
| `mock_run_command`        | Mock for `src.artifacts.run_command` |
| `mock_utils_run_command`  | Mock for `src.utils.run_command`     |
| `mock_ar_commands`        | Mock for ar (archive) commands       |
| `mock_sha256sum_commands` | Mock for sha256sum commands          |
| `mock_file_commands`      | Mock for file command                |

#### [`fixtures/build.py`](fixtures/build.py)

| Fixture            | Purpose                                   |
| ------------------ | ----------------------------------------- |
| `mock_build_setup` | Common mocks for build.py main() function |

#### [`fixtures/repository.py`](fixtures/repository.py)

| Fixture                     | Purpose                                  |
| --------------------------- | ---------------------------------------- |
| `mock_git_clone_responses`  | Standard git clone subprocess responses  |
| `mock_git_update_responses` | Standard git update subprocess responses |
