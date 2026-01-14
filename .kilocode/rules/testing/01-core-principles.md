# Core Testing Principles

This document covers the fundamental principles of writing effective unit tests.

## 1. Test Expected Behavior, Not Implementation

**What to Test:**

- ✅ Function outputs given specific inputs
- ✅ Side effects (file writes, network calls, state changes)
- ✅ Error handling and edge cases
- ✅ Business logic outcomes
- ✅ **Function calls and arguments** (for orchestrator functions)

**What NOT to Test:**

- ❌ Internal state variables
- ❌ Private methods or internal implementation details
- ❌ Framework internals
- ❌ Code structure
- ❌ **How called functions work internally** (for orchestrator functions)

```python
# ❌ BAD: Testing internal state
def test_sets_selected_label(self):
    handler = DateHandler()
    handler._selected_label = 'fcr7'  # Accessing private variable
    assert handler._selected_label == 'fcr7'

# ✅ GOOD: Testing expected behavior
def test_returns_formatted_date(self):
    handler = DateHandler()
    result = handler.format_date('2024-01-15')
    assert result == 'January 15, 2024'
```

### 1.1. Testing Orchestrator Functions

**Orchestrator functions** are functions that delegate work to other modules (e.g., `build.py`'s `main()` function). For these functions, tests should verify that the correct functions are called with the correct arguments in the correct order.

**Key Principles:**

- Mock all imported functions at the module level
- Verify function calls with `mock.assert_called_with()`
- Verify call order with `mock.call_args_list` or `mock.assert_has_calls()`
- Test exception propagation (verify exceptions from called functions propagate)
- **DO NOT** test how the called functions work internally

```python
# ❌ BAD: Testing implementation details of called functions
def test_main_builds_library(self):
    with patch("build.build_libstorage") as mock_build:
        main()
        # Checking internal state of mock_build
        assert mock_build.call_count == 1

# ✅ GOOD: Testing that main() calls build_libstorage with correct arguments
def test_main_calls_build_libstorage_with_correct_arguments(self):
    logos_storage_dir = Path("logos-storage-nim")
    with patch("build.get_platform_identifier", return_value="linux-amd64"):
        with patch("build.configure_reproducible_environment"):
            with patch("build.ensure_logos_storage_repo") as mock_repo:
                mock_repo.return_value = (logos_storage_dir, MockCommitInfo("abc123", "abc123d", "master"))
                with patch("build.get_parallel_jobs", return_value=4):
                    with patch("build.build_libstorage") as mock_build:
                        with patch("build.get_host_triple", return_value="x86_64"):
                            with patch("build.collect_artifacts", return_value=[]):
                                with patch("build.combine_libraries", return_value=Path("dist/libstorage.a")):
                                    with patch("build.generate_checksum"):
                                        with patch("build.verify_checksum"):
                                            main()

    mock_build.assert_called_once_with(logos_storage_dir, 4)

# ✅ GOOD: Testing that functions are called in correct order
def test_main_calls_functions_in_correct_order(self):
    with patch("build.get_platform_identifier", return_value="linux-amd64") as mock_platform:
        with patch("build.configure_reproducible_environment") as mock_config:
            with patch("build.ensure_logos_storage_repo") as mock_repo:
                mock_repo.return_value = (Path("logos-storage-nim"), MockCommitInfo("abc123", "abc123d", "master"))
                with patch("build.get_parallel_jobs", return_value=4) as mock_jobs:
                    with patch("build.build_libstorage") as mock_build:
                        with patch("build.get_host_triple", return_value="x86_64") as mock_triple:
                            with patch("build.collect_artifacts", return_value=[]) as mock_collect:
                                with patch("build.combine_libraries", return_value=Path("dist/libstorage.a")) as mock_combine:
                                    with patch("build.generate_checksum") as mock_checksum:
                                        with patch("build.verify_checksum") as mock_verify:
                                            main()

    # Verify call order
    expected_calls = [
        call.get_platform_identifier(),
        call.configure_reproducible_environment(),
        call.ensure_logos_storage_repo("master"),
        call.get_parallel_jobs(),
        call.build_libstorage(Path("logos-storage-nim"), 4),
        call.get_host_triple(),
        call.collect_artifacts(Path("logos-storage-nim"), "x86_64"),
        call.combine_libraries([], Path("dist/master-abc123d-linux-amd64")),
        call.generate_checksum(Path("dist/master-abc123d-linux-amd64/libstorage.a")),
        call.verify_checksum(Path("dist/master-abc123d-linux-amd64/libstorage.a")),
    ]

    assert mock_platform.call_args_list == [expected_calls[0]]
    assert mock_config.call_args_list == [expected_calls[1]]
    # ... and so on for each mock

# ✅ GOOD: Testing exception propagation
def test_main_propagates_exception_from_build_libstorage(self):
    logos_storage_dir = Path("logos-storage-nim")
    with patch("build.get_platform_identifier", return_value="linux-amd64"):
        with patch("build.configure_reproducible_environment"):
            with patch("build.ensure_logos_storage_repo") as mock_repo:
                mock_repo.return_value = (logos_storage_dir, MockCommitInfo("abc123", "abc123d", "master"))
                with patch("build.get_parallel_jobs", return_value=4):
                    with patch("build.build_libstorage", side_effect=RuntimeError("Build error")):
                        with pytest.raises(RuntimeError) as exc_info:
                            main()

    assert str(exc_info.value) == "Build error"
```

**Important Notes:**

- Always patch at the module level where the function is imported (e.g., `patch("build.get_platform_identifier")`, not `patch("utils.get_platform_identifier")`)
- Use `side_effect` for exceptions and multiple return values
- Use `return_value` for single return values
- Verify exact arguments, not just that the function was called

## 2. Avoid Accessing Internal State

**❌ BAD: Directly accessing object internals**

```python
def test_add_filter(self):
    handler = FilterHandler()
    handler._filters = []  # Directly modifying internal state
    handler._selected_filter = 'fcr7'
    handler.add_filter()
    assert len(handler._filters) == 1
```

**✅ GOOD: Testing through public interface**

```python
def test_add_filter(self):
    handler = FilterHandler()
    handler.select_filter('fcr7')
    handler.add_filter()
    assert handler.get_filter_count() == 1
    assert handler.has_filter('fcr7')
```

## 3. Use Descriptive Test Names

Test names must clearly describe what is being tested and what the expected outcome is.

**❌ BAD: Vague test names**

```python
def test_1(self):
    pass

def test_filter(self):
    pass

def test_date(self):
    pass
```

**✅ GOOD: Descriptive test names**

```python
def test_add_filter_increases_filter_count(self):
    pass

def test_format_date_returns_iso8601_format(self):
    pass

def test_invalid_date_raises_value_error(self):
    pass
```

### 3.1. Avoid Redundant Docstrings

Do not write docstrings that simply repeat the function or class name. Docstrings should provide additional context or explain what is being tested, not just restate the obvious.

**❌ BAD: Redundant docstrings that add no value**

```python
class TestMainOutput:
    """Test main function output."""
    pass

class TestMainErrorHandling:
    """Test main function error handling."""
    pass

class TestCombineLibraries:
    """Test combine_libraries function."""
    pass

class TestGenerateChecksum:
    """Test generate_checksum function."""
    pass

def test_main_calls_configure_reproducible_environment(self):
    """Test that main() calls configure_reproducible_environment()."""
    pass

def test_main_propagates_exception(self):
    """Test that main() propagates exception."""
    pass
```

**✅ GOOD: Docstrings that provide additional context**

```python
class TestMainOutput:
    """Test main function output formatting and artifact naming."""
    pass

class TestMainErrorHandling:
    """Test main function error handling and exception propagation."""
    pass

class TestCombineLibraries:
    """Test combining multiple static libraries into a single library."""
    pass

class TestGenerateChecksum:
    """Test SHA256 checksum generation for build artifacts."""
    pass

def test_main_calls_configure_reproducible_environment(self):
    """Test that main() calls configure_reproducible_environment() before building."""
    pass

def test_main_propagates_exception_from_build_libstorage(self):
    """Test that main() propagates exceptions from build_libstorage without catching them."""
    pass
```

**Guidelines:**

- If the docstring just repeats the function/class name, omit it entirely
- Use docstrings to explain **what** is being tested and **why**, not just restate the name
- For test methods, the test name should be descriptive enough to not need a docstring
- For test classes, use docstrings to explain the scope or purpose of the test group
- When in doubt, omit the docstring if it doesn't add value
