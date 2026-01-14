# Mocking Strategies

This document covers mocking patterns and techniques for effective unit testing.

## 1. Avoid Global Path Mocking

**CRITICAL**: Global `Path.exists()` mocks interfere with pytest's internal operations (e.g., traceback formatting, test discovery). Always use direct `@patch` decorators within test methods for Path operations.

**❌ BAD: Global Path.exists() fixture**

```python
# tests/fixtures/file_operations.py
@pytest.fixture
def mock_path_exists():
    """Mock Path.exists() for testing."""
    with patch("pathlib.Path.exists") as mock:
        mock.return_value = True
        yield mock

# This will cause pytest to fail with:
# TypeError: <lambda>() missing 1 required positional argument: 'self'
```

**✅ GOOD: Direct @patch decorators in test methods**

```python
@patch("src.artifacts.run_command")
@patch("pathlib.Path.exists")
@patch("pathlib.Path.stat")
def test_combine_libraries_creates_output(self, mock_stat, mock_exists, mock_run, temp_dir):
    """Test that combine_libraries creates output file with correct path."""
    libraries = [temp_dir / "lib1.a", temp_dir / "lib2.a"]
    output_dir = temp_dir / "output"

    # Configure exists to return True for output file
    mock_exists.return_value = True

    # Configure stat to return a mock with st_size
    mock_stat_result = MagicMock()
    mock_stat_result.st_size = 1000
    mock_stat.return_value = mock_stat_result

    result = combine_libraries(libraries, output_dir)

    assert result.name == "libstorage.a"
    assert result.parent == output_dir
```

**Why This Matters:**

- Pytest internally calls `Path.exists()` for test discovery and traceback formatting
- Global mocks intercept these internal calls and cause failures
- Direct `@patch` decorators are scoped to the test method only
- This approach avoids pytest internal conflicts

**Guidelines:**

- Use direct `@patch` decorators for Path operations (`exists()`, `stat()`, `mkdir()`, etc.)
- Never create global fixtures that mock `pathlib.Path` methods
- Keep Path mocking local to the test method that needs it
- Use fixture modules for other types of mocking (commands, file I/O, etc.)

## 2. Use Dependency Injection for Testability

When functions need to check file existence or perform other operations that are hard to mock, use dependency injection to make them testable.

**❌ BAD: Hard to test - directly calls Path.exists()**

```python
def collect_artifacts(logos_storage_dir: Path, target: str) -> List[Path]:
    """Collect all required library artifacts."""
    libraries = []

    # Directly calls Path.exists() - hard to mock
    if not (logos_storage_dir / "libstorage.a").exists():
        raise FileNotFoundError("libstorage.a not found")

    libraries.append(logos_storage_dir / "libstorage.a")
    return libraries
```

**✅ GOOD: Testable - uses dependency injection**

```python
def collect_artifacts(
    logos_storage_dir: Path,
    target: str,
    path_exists: Optional[Callable[[Path], bool]] = None
) -> List[Path]:
    """Collect all required library artifacts.

    Args:
        logos_storage_dir: Path to the logos-storage-nim repository
        target: Target architecture (e.g., "x86_64", "aarch64")
        path_exists: Optional function to check if a path exists.
                    If None, uses the default Path.exists() method.
                    This parameter is primarily for testing purposes.
    """
    if path_exists is None:
        path_exists = lambda p: p.exists()

    libraries = []

    # Uses injected path_exists function - easy to mock
    if not path_exists(logos_storage_dir / "libstorage.a"):
        raise FileNotFoundError("libstorage.a not found")

    libraries.append(logos_storage_dir / "libstorage.a")
    return libraries
```

**Testing with Dependency Injection:**

```python
def test_collect_artifacts_finds_library(self):
    """Test that collect_artifacts finds library when it exists."""
    logos_storage_dir = Path("logos-storage-nim")

    # Create custom path_exists function for testing
    def mock_path_exists(path):
        return "libstorage.a" in str(path)

    libraries = collect_artifacts(logos_storage_dir, "x86_64", path_exists=mock_path_exists)

    assert len(libraries) == 1
    assert "libstorage.a" in str(libraries[0])

def test_collect_artifacts_raises_when_missing(self):
    """Test that collect_artifacts raises when library is missing."""
    logos_storage_dir = Path("logos-storage-nim")

    # Create custom path_exists function that returns False
    def mock_path_exists(path):
        return False

    with pytest.raises(FileNotFoundError) as exc_info:
        collect_artifacts(logos_storage_dir, "x86_64", path_exists=mock_path_exists)

    assert "libstorage.a not found" in str(exc_info.value)
```

**Benefits of Dependency Injection:**

- **Testability**: Easy to mock external dependencies
- **Flexibility**: Can inject different implementations
- **Clear Dependencies**: Function explicitly declares what it needs
- **No Global Mocking**: Avoids global state issues

**Guidelines:**

- Use dependency injection for operations that are hard to mock (file I/O, network calls, etc.)
- Provide default implementation for production use
- Document that the parameter is primarily for testing
- Use `Optional[Callable[...]]` type hints for clarity

## 3. Mocking Patterns and Techniques

### 3.1. Mocking Return Values

```python
@patch("src.utils.run_command")
def test_with_return_value(self, mock_run):
    """Test with simple return value."""
    mock_run.return_value = subprocess.CompletedProcess(
        args=["command"],
        returncode=0,
        stdout="output",
        stderr=""
    )

    result = some_function()
    assert result == "output"
```

### 3.2. Mocking with Side Effects

```python
@patch("src.utils.run_command")
def test_with_side_effect(self, mock_run):
    """Test with side effect for multiple calls."""
    mock_run.side_effect = [
        subprocess.CompletedProcess(args=["cmd1"], returncode=0, stdout="output1", stderr=""),
        subprocess.CompletedProcess(args=["cmd2"], returncode=0, stdout="output2", stderr=""),
    ]

    result = some_function()
    assert result == "output1output2"
```

### 3.3. Mocking Exceptions

```python
@patch("src.utils.run_command")
def test_with_exception(self, mock_run):
    """Test with exception."""
    mock_run.side_effect = subprocess.CalledProcessError(
        returncode=1,
        cmd=["command"],
        stdout="",
        stderr="Error occurred"
    )

    with pytest.raises(subprocess.CalledProcessError):
        some_function()
```

### 3.4. Mocking with Callable Side Effects

```python
@patch("src.utils.run_command")
def test_with_callable_side_effect(self, mock_run):
    """Test with callable side effect."""
    def side_effect(cmd):
        if "ar" in cmd:
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")
        elif "sha256sum" in cmd:
            return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="abc123  file", stderr="")
        return subprocess.CompletedProcess(args=cmd, returncode=0, stdout="", stderr="")

    mock_run.side_effect = side_effect

    result = some_function()
    assert result is not None
```

## 4. Patch Location Best Practices

Always patch at the module level where the function is imported, not where it's defined.

**❌ BAD: Patching at definition location**

```python
# src/utils.py
def helper_function():
    return "helper"

# src/module.py
from src.utils import helper_function

def main_function():
    return helper_function()

# test_module.py
@patch("src.utils.helper_function")  # WRONG! This won't work
def test_main_function(self, mock_helper):
    mock_helper.return_value = "mocked"
    result = main_function()
    assert result == "mocked"  # This will fail!
```

**✅ GOOD: Patching at import location**

```python
# test_module.py
@patch("src.module.helper_function")  # CORRECT! Patch where it's imported
def test_main_function(self, mock_helper):
    mock_helper.return_value = "mocked"
    result = main_function()
    assert result == "mocked"  # This will work!
```

**Why This Matters:**

- When you import a function, you create a reference to it
- Patching at the definition location doesn't affect already-imported references
- Patching at the import location replaces the reference that the module uses

**Guidelines:**

- Always patch at the module where the function is imported
- Use the full import path (e.g., `src.module.function`, not `src.utils.function`)
- Check the import statements in the module you're testing to find the correct patch location
