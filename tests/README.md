# Tests

## Structure

```
tests/
├── conftest.py                    # Shared fixtures
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

Shared fixtures in [`conftest.py`](conftest.py):

| Fixture                 | Purpose                                 |
| ----------------------- | --------------------------------------- |
| `temp_dir`              | Temporary directory for file operations |
| `mock_run_command`      | Mock for `run_command` utility          |
| `mock_subprocess_run`   | Mock for `subprocess.run`               |
| `mock_shutil_rmtree`    | Mock for `shutil.rmtree`                |
| `mock_path_*`           | Mocks for various `Path` methods        |
| `mock_os_environ`       | Mock for `os.environ`                   |
| `mock_platform_machine` | Mock for `platform.machine`             |
| `sample_commit_info`    | Sample `CommitInfo` dataclass           |
| `sample_artifact_paths` | Sample artifact file structure          |
