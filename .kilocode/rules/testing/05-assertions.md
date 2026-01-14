# Assertions and Edge Cases

This document covers how to write precise assertions and test all edge cases.

## 1. Use Precise Assertions, Avoid Vague Checks

Always write specific assertions that validate exact expected values rather than vague checks like "greater than zero" or "some data exists".

**❌ BAD: Vague assertions that provide little confidence**

```python
def test_returns_weeks_with_date_ranges(self):
    weeks = get_all_weeks_between_dates('2024-03-04', '2024-03-10')

    assert len(weeks) > 0  # Vague - how many exactly?

    all_dates = [date for week in weeks.values() for date in week]
    assert any(date >= '2024-03-04' for date in all_dates)  # Vague - which dates exactly?

def test_returns_months_between_dates(self):
    months = get_all_months_between('2024-01-01', '2024-03-01')

    assert len(months) > 0  # How many exactly?
    assert '2024' in months[0]  # Too vague - what's the full value?

def test_returns_date_range_with_30_days_ago_as_start(self):
    range_data = get_default_date_range()

    days_diff = (datetime.now() - range_data['start']).days
    assert 29 <= days_diff <= 31  # Approximately 30? Be exact!
```

**✅ GOOD: Precise assertions with exact expected values**

```python
def test_returns_single_week_for_dates_within_same_week(self):
    weeks = get_all_weeks_between_dates('2024-03-04', '2024-03-10')

    assert len(weeks) == 1  # Exact count

    week_dates = list(weeks.values())[0]
    assert len(week_dates) == 7  # Exact: Monday through Sunday

    # Verify exact dates present
    assert '2024-03-04' in week_dates  # Monday
    assert '2024-03-05' in week_dates  # Tuesday
    assert '2024-03-10' in week_dates  # Sunday

def test_returns_exact_months_between_dates(self):
    months = get_all_months_between('2024-01-01', '2024-03-01')

    assert len(months) == 3  # Exact count
    assert months == ['January 2024', 'February 2024', 'March 2024']  # Exact values

def test_returns_exactly_30_days_ago_as_start(self):
    range_data = get_default_date_range()

    start_date = range_data['start']
    thirty_days_ago = datetime.now() - timedelta(days=30)

    # Exact date match (ignore time portion)
    assert start_date.date() == thirty_days_ago.date()
```

**Why Precise Assertions Matter:**

- **Catch Regressions**: Exact values detect when logic changes unexpectedly
- **Document Behavior**: Tests clearly show what the function should return
- **Fail Fast**: Specific assertions fail immediately when behavior changes
- **Build Confidence**: Precise tests give confidence the code works correctly

**Guidelines:**

- Use `==` for exact numbers, not `>` or `>=` ranges
- Use `==` for complete list/dict matching, not `in` for partial checks
- Validate all expected items in collections, not just "at least one exists"
- Check exact string values, not just `in` for substrings
- For date calculations, verify exact day/month/year values, not approximate ranges

## 2. Test All Branches of Conditional Logic

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

## 3. Test All Branches Including Fallback

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

## 4. Test Edge Cases

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
