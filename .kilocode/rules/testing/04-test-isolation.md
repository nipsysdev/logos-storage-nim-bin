# Test Isolation

This document covers how to ensure tests run in complete isolation without creating real files or side effects.

## 1. Ensure Test Isolation

Tests should run in complete isolation without creating real files in the project directory. This ensures tests are reproducible and don't interfere with each other or the development environment.

**❌ BAD: Tests create real files**

```python
def test_combine_libraries(self):
    """Test that combine_libraries creates output file."""
    libraries = [Path("lib1.a"), Path("lib2.a")]
    output_dir = Path("dist")

    result = combine_libraries(libraries, output_dir)

    # This creates real files in dist/ directory!
    assert result.exists()
```

**✅ GOOD: Tests mock all file operations**

```python
@patch("src.artifacts.run_command")
@patch("pathlib.Path.exists")
@patch("pathlib.Path.stat")
def test_combine_libraries_creates_output(self, mock_stat, mock_exists, mock_run, temp_dir):
    """Test that combine_libraries creates output file with correct path."""
    libraries = [temp_dir / "lib1.a", temp_dir / "lib2.a"]
    output_dir = temp_dir / "output"

    # Mock all file operations
    mock_exists.return_value = True
    mock_stat_result = MagicMock()
    mock_stat_result.st_size = 1000
    mock_stat.return_value = mock_stat_result

    result = combine_libraries(libraries, output_dir)

    assert result.name == "libstorage.a"
    assert result.parent == output_dir
```

**Why Test Isolation Matters:**

- **Reproducibility**: Tests produce the same results regardless of environment
- **No Side Effects**: Tests don't leave artifacts in the project directory
- **Parallel Execution**: Tests can run in parallel without conflicts
- **CI/CD Compatibility**: Tests work consistently in CI environments
- **Faster Execution**: No need for cleanup between test runs

**Guidelines:**

- Mock all file system operations (read, write, exists, stat, mkdir, etc.)
- Mock all system commands (run_command, subprocess calls, etc.)
- Use `temp_dir` fixture for temporary file paths
- Never create real files in the project root or dist/ directory
- Verify no real files are created after test runs

## 2. No Cleanup Needed When Tests Are Isolated

When tests are properly isolated with comprehensive mocking, cleanup fixtures are unnecessary. Tests should not create any real files that need cleanup.

**❌ BAD: Cleanup fixture for test artifacts**

```python
# tests/conftest.py
@pytest.fixture(autouse=True)
def cleanup_test_artifacts():
    """Automatically clean up test artifacts after each test."""
    yield
    # Clean up dist/ directory
    dist_dir = Path("dist")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)

    # Clean up logos-storage-nim directory
    logos_dir = Path("logos-storage-nim")
    if logos_dir.exists():
        shutil.rmtree(logos_dir)
```

**✅ GOOD: No cleanup needed - tests are isolated**

```python
# tests/conftest.py
# No cleanup fixture needed!
# Tests mock all operations and don't create real files.

@pytest.fixture
def temp_dir(tmp_path):
    """Temporary directory fixture."""
    return tmp_path
```

**Why No Cleanup Is Better:**

- **Simpler Code**: No need to track what needs cleanup
- **Faster Tests**: No cleanup overhead between tests
- **More Reliable**: No risk of cleanup failures
- **Clearer Intent**: Tests explicitly mock what they need

**Guidelines:**

- If you need a cleanup fixture, your tests are not properly isolated
- Mock all file operations instead of creating real files
- Use `temp_dir` fixture for any temporary paths
- Verify tests don't create real files by checking the project directory after test runs

## 3. Mocking All File Operations

To ensure test isolation, you must mock all file operations that your code performs. This includes:

### File Reading Operations

- `Path.read_text()`
- `Path.read_bytes()`
- `Path.stat()`
- `Path.exists()`

### File Writing Operations

- `Path.write_text()`
- `Path.write_bytes()`
- `Path.mkdir()`
- `Path.unlink()`

### Directory Operations

- `Path.iterdir()`
- `Path.is_file()`
- `Path.is_dir()`
- `shutil.rmtree()`

### System Commands

- `subprocess.run()`
- `subprocess.Popen()`
- Custom `run_command()` functions

**Example: Comprehensive Mocking**

```python
@patch("src.artifacts.run_command")
@patch("pathlib.Path.exists")
@patch("pathlib.Path.stat")
@patch("pathlib.Path.write_text")
@patch("pathlib.Path.mkdir")
def test_complete_isolation(self, mock_mkdir, mock_write, mock_stat, mock_exists, mock_run, temp_dir):
    """Test with comprehensive mocking of all file operations."""
    # Configure all mocks
    mock_exists.return_value = True
    mock_stat_result = MagicMock()
    mock_stat_result.st_size = 1000
    mock_stat.return_value = mock_stat_result

    # Run the function
    result = some_function(temp_dir / "test.txt")

    # Verify all operations were mocked
    mock_mkdir.assert_called_once()
    mock_write.assert_called_once()
    mock_stat.assert_called_once()
    mock_run.assert_called_once()
```

## 4. Verifying Test Isolation

After running tests, verify that no real files were created in the project directory:

```bash
# Run tests
pytest tests/

# Check for any created files
ls -la dist/ 2>/dev/null || echo "dist/ directory does not exist (good!)"
ls -la logos-storage-nim/ 2>/dev/null || echo "logos-storage-nim/ directory does not exist (good!)"
```

If any files were created, your tests are not properly isolated and need more comprehensive mocking.

## 5. Common Isolation Pitfalls

### 5.1. Forgetting to Mock stat()

```python
# ❌ BAD: Forgets to mock stat()
@patch("src.artifacts.run_command")
@patch("pathlib.Path.exists")
def test_combine_libraries(self, mock_exists, mock_run, temp_dir):
    mock_exists.return_value = True
    result = combine_libraries(libraries, output_dir)
    # This will fail because stat() is not mocked!
```

```python
# ✅ GOOD: Mocks stat() as well
@patch("src.artifacts.run_command")
@patch("pathlib.Path.exists")
@patch("pathlib.Path.stat")
def test_combine_libraries(self, mock_stat, mock_exists, mock_run, temp_dir):
    mock_exists.return_value = True
    mock_stat_result = MagicMock()
    mock_stat_result.st_size = 1000
    mock_stat.return_value = mock_stat_result
    result = combine_libraries(libraries, output_dir)
    # This works!
```

### 5.2. Using Real File Paths Instead of temp_dir

```python
# ❌ BAD: Uses real project paths
def test_with_real_paths(self):
    result = process_file(Path("data/input.txt"))
    # This creates real files in the project!
```

```python
# ✅ GOOD: Uses temp_dir for all paths
def test_with_temp_paths(self, temp_dir):
    input_file = temp_dir / "input.txt"
    result = process_file(input_file)
    # No real files created!
```

### 5.3. Not Mocking System Commands

```python
# ❌ BAD: Doesn't mock run_command
def test_without_mocking(self):
    result = build_library()
    # This actually runs the build command!
```

```python
# ✅ GOOD: Mocks run_command
@patch("src.artifacts.run_command")
def test_with_mocking(self, mock_run):
    mock_run.return_value = subprocess.CompletedProcess(
        args=["make"],
        returncode=0,
        stdout="",
        stderr=""
    )
    result = build_library()
    # No actual command run!
```
