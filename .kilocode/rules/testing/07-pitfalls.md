# Common Pitfalls

This document covers common mistakes to avoid when writing unit tests.

## 1. Testing Implementation Details

```python
# ❌ BAD: Testing internal implementation
def test_uses_internal_cache(self):
    handler = DateHandler()
    handler._cache = {}  # Testing internal cache
    handler.format_date('2024-01-01')
    assert '2024-01-01' in handler._cache

# ✅ GOOD: Testing behavior
def test_format_date_returns_correct_result(self):
    handler = DateHandler()
    result = handler.format_date('2024-01-01')
    assert result == 'January 1, 2024'
```

## 2. Writing Tests That Don't Test Anything

**❌ BAD: Test doesn't actually test the code**

```python
def test_addition(self):
    result = 2 + 2  # This doesn't use the codebase!
    assert result == 4
```

**❌ BAD: Test has no assertions**

```python
def test_main_calls_verify_checksum(self, mock_build_setup):
    """Test that main() calls copy_header_file and generate_sha256sums."""
    main()
    # No assertions! This test doesn't verify anything
```

**✅ GOOD: Test actually tests the code**

```python
def test_calculator_add(self):
    calculator = Calculator()
    result = calculator.add(2, 2)
    assert result == 4
```

**✅ GOOD: Test has proper assertions**

```python
def test_main_calls_verify_checksum(self, mock_build_setup):
    """Test that main() calls copy_header_file and generate_sha256sums."""
    main()

    # Verify the functions were called
    mock_build_setup["mock_copy"].assert_called_once()
    mock_build_setup["mock_checksums"].assert_called_once()
```

**Important Note**: Every test must have at least one assertion (either `assert` statements, mock assertions like `assert_called_once()`, or `pytest.raises()` for exception testing). Tests without assertions provide no value and should either be removed or have assertions added.

**Exception**: Tests that intentionally verify "no exception raised" are valid and don't need explicit assertions:

```python
# ✅ GOOD: Valid test pattern - verifies no exception is raised
def test_main_exits_on_success(self, mock_build_setup):
    """Test that main() completes successfully without raising exceptions."""
    main()  # If main() raises an exception, the test fails automatically
```

## 3. Overly Complex Tests

```python
# ❌ BAD: Test is too complex and hard to understand
def test_complex_scenario(self):
    data = {'a': 1, 'b': 2, 'c': 3}
    result = process_data(data)
    assert result['processed'] == True
    assert result['sum'] == 6
    assert result['avg'] == 2.0
    assert result['max'] == 3
    assert result['min'] == 1
    assert result['count'] == 3
    assert result['keys'] == ['a', 'b', 'c']
    # ... 20 more assertions

# ✅ GOOD: Split into multiple focused tests
def test_process_data_sets_processed_flag(self):
    data = {'a': 1, 'b': 2, 'c': 3}
    result = process_data(data)
    assert result['processed'] is True

def test_process_data_calculates_sum(self):
    data = {'a': 1, 'b': 2, 'c': 3}
    result = process_data(data)
    assert result['sum'] == 6

def test_process_data_calculates_average(self):
    data = {'a': 1, 'b': 2, 'c': 3}
    result = process_data(data)
    assert result['avg'] == 2.0
```

## 4. Not Testing Edge Cases

**❌ BAD: Only testing happy path**

```python
def test_divide_numbers(self):
    result = divide(10, 2)
    assert result == 5
```

**✅ GOOD: Testing edge cases**

```python
def test_divide_numbers(self):
    result = divide(10, 2)
    assert result == 5

def test_divide_by_zero_raises_error(self):
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_divide_negative_numbers(self):
    result = divide(-10, 2)
    assert result == -5

def test_divide_zero_by_number(self):
    result = divide(0, 5)
    assert result == 0
```

## 5. Testing Fallback Cases

For functions with multiple branches, ensure you test all branches including fallback cases.

**❌ BAD: Missing fallback case test**

```python
def test_check_compatibility_returns_true_for_aarch64(self):
    result = check_artifact_compatibility(artifact_path, "aarch64")
    assert result is True

def test_check_compatibility_returns_true_for_x86_64(self):
    result = check_artifact_compatibility(artifact_path, "x86_64")
    assert result is True
```

**✅ GOOD: Including fallback case test**

```python
def test_check_compatibility_returns_true_for_aarch64(self):
    result = check_artifact_compatibility(artifact_path, "aarch64")
    assert result is True

def test_check_compatibility_returns_true_for_x86_64(self):
    result = check_artifact_compatibility(artifact_path, "x86_64")
    assert result is True

def test_check_compatibility_returns_false_for_unknown_architecture(self):
    """Test that check_artifact_compatibility returns False for unknown architecture (fallback case)."""
    result = check_artifact_compatibility(artifact_path, "riscv64")
    assert result is False
```

## 6. Not Testing All Branches of Conditional Logic

**❌ BAD: Missing branch tests**

```python
def test_collect_artifacts_uses_release_leopard(self):
    libraries = collect_artifacts(sample_artifact_paths, "x86_64")
    leopard_libs = [lib for lib in libraries if "libleopard.a" in str(lib)]
    assert "release" in str(leopard_libs[0])
```

**✅ GOOD: Testing all branches**

```python
def test_collect_artifacts_uses_release_leopard(self):
    libraries = collect_artifacts(sample_artifact_paths, "x86_64")
    leopard_libs = [lib for lib in libraries if "libleopard.a" in str(lib)]
    assert "release" in str(leopard_libs[0])

def test_collect_artifacts_uses_debug_leopard_when_release_missing(self):
    leopard_release.unlink()
    leopard_debug.parent.mkdir(parents=True, exist_ok=True)
    leopard_debug.write_bytes(b"fake libleopard debug content")

    libraries = collect_artifacts(sample_artifact_paths, "x86_64")
    leopard_libs = [lib for lib in libraries if "libleopard.a" in str(lib)]
    assert "debug" in str(leopard_libs[0])

def test_collect_artifacts_raises_when_leopard_missing(self):
    leopard_release.unlink()
    if leopard_debug.exists():
        leopard_debug.unlink()

    with pytest.raises(FileNotFoundError) as exc_info:
        collect_artifacts(sample_artifact_paths, "x86_64")

    assert "libleopard.a not found" in str(exc_info.value)
```

## 7. Not Testing All Branches

```python
# ❌ BAD: Only testing happy path
def test_divide_numbers(self):
    result = divide(10, 2)
    assert result == 5

# ✅ GOOD: Testing edge cases
def test_divide_numbers(self):
    result = divide(10, 2)
    assert result == 5

def test_divide_by_zero_raises_error(self):
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_divide_negative_numbers(self):
    result = divide(-10, 2)
    assert result == -5

def test_divide_zero_by_number(self):
    result = divide(0, 5)
    assert result == 0
```
