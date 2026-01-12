# Python Unit Testing Guidelines

This guide documents the testing patterns and best practices for Python unit testing in this project.

## Test File Organization

### Split Large Test Files into Focused Files

When a test file grows beyond ~300-400 lines or contains tests for multiple distinct concerns, split it into multiple focused test files.

**❌ BAD: Single large test file with all tests**

```python
# test_date_handler.py (500+ lines)
class TestDateHandler:
    def test_format_date_for_api(self):
        """6 tests"""
        pass

    def test_format_date_time(self):
        """5 tests"""
        pass

    def test_format_date(self):
        """5 tests"""
        pass

    def test_get_all_dates_between(self):
        """4 tests"""
        pass

    def test_get_all_weeks_between_dates(self):
        """7 tests"""
        pass

    def test_get_all_months_between(self):
        """7 tests"""
        pass

    def test_get_default_date_range(self):
        """4 tests"""
        pass

    def test_days_between(self):
        """6 tests"""
        pass

    def test_get_timestamp(self):
        """3 tests"""
        pass

    def test_format_yearly_period(self):
        """4 tests"""
        pass

    def test_format_quarterly_period(self):
        """7 tests"""
        pass

    def test_format_monthly_period(self):
        """5 tests"""
        pass
```

**✅ GOOD: Multiple focused test files organized by concern**

```python
# test_date_handler_formatting.py (~230 lines, 36 tests)
class TestDateHandlerFormatting:
    def test_format_date_for_api(self):
        """API formatting tests"""
        pass

    def test_format_date_time(self):
        """Date/time display tests"""
        pass

    def test_format_date(self):
        """Date display tests"""
        pass

    def test_get_timestamp(self):
        """Timestamp tests"""
        pass

# test_date_handler_ranges.py (~265 lines, 26 tests)
class TestDateHandlerRanges:
    def test_get_all_dates_between(self):
        """Date range tests"""
        pass

    def test_get_all_weeks_between_dates(self):
        """Week calculation tests"""
        pass

    def test_get_all_months_between(self):
        """Month aggregation tests"""
        pass

    def test_get_default_date_range(self):
        """Default range tests"""
        pass

    def test_days_between(self):
        """Day difference tests"""
        pass

# test_date_handler_periods.py (~157 lines, 16 tests)
class TestDateHandlerPeriods:
    def test_format_yearly_period(self):
        """Yearly period tests"""
        pass

    def test_format_quarterly_period(self):
        """Quarterly period tests"""
        pass

    def test_format_monthly_period(self):
        """Monthly period tests"""
        pass
```

**Benefits of Split Test Files:**

- ✅ **Easier navigation**: Quickly find relevant tests
- ✅ **Faster test runs**: Run specific test files during development
- ✅ **Better organization**: Related tests grouped together
- ✅ **Improved maintainability**: Smaller files are easier to understand
- ✅ **Clearer purpose**: File names indicate what's being tested
- ✅ **Parallel execution**: Multiple test files can run in parallel

**When to Split:**

- File exceeds 300-400 lines
- Contains tests for multiple distinct concerns (formatting vs ranges vs periods)
- Takes too long to find specific tests
- Different test files could run independently

**Naming Conventions:**

- Use descriptive suffixes: `test_module_formatting.py`, `test_module_ranges.py`, `test_module_periods.py`
- Keep related files together alphabetically
- Use consistent naming pattern across the project

**Example Split Strategy:**

For a utility module with multiple concerns:

```
src/
  date_handler.py
tests/
  test_date_handler_formatting.py
  test_date_handler_ranges.py
  test_date_handler_periods.py
```

## Running Tests

**✅ Use pytest for single test runs**

```bash
# Run a specific test file
pytest tests/test_date_handler_formatting.py

# Run a specific test class
pytest tests/test_date_handler_formatting.py::TestDateHandlerFormatting

# Run a specific test method
pytest tests/test_date_handler_formatting.py::TestDateHandlerFormatting::test_format_date_for_api

# Run with coverage
pytest --cov=src tests/

# Run with verbose output
pytest -v tests/
```

**✅ Use pytest markers for test categorization**

```bash
# Run only unit tests
pytest -m unit

# Run only slow tests
pytest -m slow
```

## Core Testing Principles

### 1. Test Expected Behavior, Not Implementation

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

### 2. Avoid Accessing Internal State

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

### 3. Use Descriptive Test Names

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

### 4. Create Helper Functions (DRY Principle)

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

### 5. Use Precise Assertions, Avoid Vague Checks

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

### 6. Async Handling

For async functions, use pytest-asyncio and properly await all async operations:

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_fetch_data_updates_state():
    async with AsyncClient() as client:
        response = await client.get('https://api.example.com/data')
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'success'
```

### 7. Test Naming Conventions

Use snake*case with descriptive names that follow the pattern: `test*<function>\_<expected_behavior>`

```python
# Good naming patterns
def test_add_filter_increases_filter_count(self):
    pass

def test_remove_filter_decreases_filter_count(self):
    pass

def test_invalid_filter_raises_value_error(self):
    pass

def test_format_date_with_timezone_returns_correct_offset(self):
    pass
```

## Testing Patterns

### Complete Example: Date Handler Test Structure

```python
import pytest
from datetime import datetime, timedelta
from src.date_handler import DateHandler

class TestDateHandlerFormatting:
    """Test date formatting functions"""

    def setup_method(self):
        """Setup method runs before each test"""
        self.handler = DateHandler()
        self.handler.set_timezone('UTC')

    def test_format_date_for_api_returns_iso8601(self):
        """Test that format_date_for_api returns ISO 8601 format"""
        result = self.handler.format_date_for_api('2024-01-15')
        assert result == '2024-01-15T00:00:00Z'

    def test_format_date_time_includes_time(self):
        """Test that format_date_time includes time component"""
        result = self.handler.format_date_time('2024-01-15 14:30:00')
        assert '14:30' in result

    def test_format_date_returns_readable_format(self):
        """Test that format_date returns human-readable format"""
        result = self.handler.format_date('2024-01-15')
        assert result == 'January 15, 2024'

    def test_format_date_short_returns_abbreviated_format(self):
        """Test that format_date_short returns abbreviated format"""
        result = self.handler.format_date_short('2024-01-15')
        assert result == 'Jan 15, 2024'

    def test_get_timestamp_returns_unix_timestamp(self):
        """Test that get_timestamp returns Unix timestamp"""
        result = self.handler.get_timestamp('2024-01-15 00:00:00')
        assert isinstance(result, int)
        assert result > 0


class TestDateHandlerRanges:
    """Test date range calculation functions"""

    def test_get_all_dates_between_returns_correct_dates(self):
        """Test that get_all_dates_between returns all dates in range"""
        dates = get_all_dates_between('2024-01-01', '2024-01-05')
        assert len(dates) == 5
        assert dates == ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05']

    def test_get_all_weeks_between_dates_returns_weeks(self):
        """Test that get_all_weeks_between_dates returns correct weeks"""
        weeks = get_all_weeks_between_dates('2024-03-04', '2024-03-10')
        assert len(weeks) == 1
        week_dates = list(weeks.values())[0]
        assert len(week_dates) == 7

    def test_get_all_months_between_returns_months(self):
        """Test that get_all_months_between returns correct months"""
        months = get_all_months_between('2024-01-01', '2024-03-01')
        assert len(months) == 3
        assert months == ['January 2024', 'February 2024', 'March 2024']

    def test_get_default_date_range_returns_30_days(self):
        """Test that get_default_date_range returns 30-day range"""
        range_data = get_default_date_range()
        start_date = range_data['start']
        end_date = range_data['end']

        expected_start = datetime.now() - timedelta(days=30)
        assert start_date.date() == expected_start.date()
        assert end_date.date() == datetime.now().date()

    def test_days_between_returns_correct_difference(self):
        """Test that days_between returns correct day difference"""
        result = days_between('2024-01-01', '2024-01-10')
        assert result == 9


class TestDateHandlerPeriods:
    """Test period formatting for reports"""

    def test_format_yearly_period_returns_correct_format(self):
        """Test that format_yearly_period returns correct format"""
        result = format_yearly_period(2024)
        assert result == '2024'

    def test_format_quarterly_period_returns_correct_format(self):
        """Test that format_quarterly_period returns correct format"""
        result = format_quarterly_period(2024, 1)
        assert result == 'Q1 2024'

    def test_format_monthly_period_returns_correct_format(self):
        """Test that format_monthly_period returns correct format"""
        result = format_monthly_period(2024, 1)
        assert result == 'January 2024'
```

## Advanced Patterns

### Service Testing with Mock Implementations

```python
from unittest.mock import Mock, AsyncMock
import pytest

class MockReportApiClient:
    """Mock implementation of ReportApiClient for testing"""

    def __init__(self):
        self.get_report_return_value = None
        self.get_report_exception = None
        self.get_report_calls = []

    def prepare_get_report_to_return(self, value):
        """Set the return value for get_report"""
        self.get_report_return_value = value

    def prepare_get_report_to_throw(self, error):
        """Set the exception to raise for get_report"""
        self.get_report_exception = error

    async def get_report(self, request):
        """Mock get_report method"""
        self.get_report_calls.append(request)

        if self.get_report_exception is not None:
            raise self.get_report_exception

        return self.get_report_return_value or {}

    def get_report_was_called_with(self, predicate):
        """Check if get_report was called with matching parameters"""
        return any(predicate(call) for call in self.get_report_calls)


def test_report_service_with_mock_client():
    """Test report service using mock client"""
    mock_client = MockReportApiClient()
    mock_client.prepare_get_report_to_return({'data': 'test'})

    service = ReportService(mock_client)
    result = service.get_report({'param': 'value'})

    assert result == {'data': 'test'}
    assert len(mock_client.get_report_calls) == 1
```

### Custom Test Utilities and Assertions

```python
def assert_dict_contains(actual, expected):
    """Assert that actual dict contains all key-value pairs from expected"""
    for key, value in expected.items():
        assert key in actual, f"Key '{key}' not found in actual dict"
        assert actual[key] == value, f"Value mismatch for key '{key}': expected {value}, got {actual[key]}"

def assert_list_contains_all(actual, expected):
    """Assert that actual list contains all items from expected"""
    for item in expected:
        assert item in actual, f"Item '{item}' not found in actual list"

def assert_datetime_approx_equal(actual, expected, tolerance_seconds=1):
    """Assert that two datetimes are approximately equal within tolerance"""
    diff = abs((actual - expected).total_seconds())
    assert diff <= tolerance_seconds, f"Datetimes differ by {diff} seconds, tolerance is {tolerance_seconds}"


# Usage in tests
def test_response_contains_expected_data():
    response = api_client.get_data()
    assert_dict_contains(response, {'status': 'success', 'count': 5})

def test_list_contains_all_items():
    items = get_items()
    assert_list_contains_all(items, ['item1', 'item2', 'item3'])
```

### Testing with Realistic Test Data

```python
import pytest

@pytest.fixture
def realistic_report_data():
    """Fixture providing realistic report data"""
    return {
        'buckets': [
            {
                'key': {'vendor': 'IQOR', 'driver': 'Bill - Inquiry'},
                'nb_documents': 21753,
                'resolutions': {
                    'nb_by_resolution': {
                        'Resolved': 9303,
                        'Partially Resolved': 12450,
                    }
                },
                'aht_avg': 11.04,
            },
            {
                'key': {'vendor': 'IQOR', 'driver': 'Technical Issue'},
                'nb_documents': 15420,
                'resolutions': {
                    'nb_by_resolution': {
                        'Resolved': 8200,
                        'Partially Resolved': 7220,
                    }
                },
                'aht_avg': 9.87,
            },
        ],
        'total_documents': 37173,
    }

def test_process_report_data(realistic_report_data):
    """Test report processing with realistic data"""
    processor = ReportProcessor()
    result = processor.process(realistic_report_data)

    assert result['total_buckets'] == 2
    assert result['total_documents'] == 37173
    assert result['average_aht'] == pytest.approx(10.455, rel=0.01)
```

### Testing Complex Hierarchical Data

```python
def test_process_three_levels_of_data():
    """Test processing of multi-level data structures"""
    level_one_data = build_level_one_data()
    level_two_data = build_level_two_data()
    level_three_data = build_level_three_data()

    processor = DataProcessor()
    processor.add_level(level_one_data)
    processor.add_level(level_two_data)
    processor.add_level(level_three_data)

    # Verify third level
    first_child = processor.get_children()[0]
    first_grandchild = first_child.get_children()[0]

    assert first_grandchild.get_children() == []
    assert first_grandchild.get_level() == 3
    assert first_grandchild.can_expand() is False
    assert first_grandchild.get_row_key() == 'IQOR-Some Site-Some Driver'
```

### Testing Error Handling

```python
import pytest

def test_invalid_date_raises_value_error():
    """Test that invalid date raises ValueError"""
    handler = DateHandler()

    with pytest.raises(ValueError) as exc_info:
        handler.format_date('invalid-date')

    assert 'Invalid date format' in str(exc_info.value)

def test_network_failure_raises_connection_error():
    """Test that network failure raises ConnectionError"""
    client = ApiClient()

    with pytest.raises(ConnectionError):
        client.fetch_data('https://invalid-url-that-does-not-exist.com')

def test_missing_required_field_raises_key_error():
    """Test that missing required field raises KeyError"""
    processor = DataProcessor()

    with pytest.raises(KeyError) as exc_info:
        processor.process({'incomplete': 'data'})

    assert 'required_field' in str(exc_info.value)
```

### Testing with Parametrization

```python
import pytest

@pytest.mark.parametrize('input_date,expected_output', [
    ('2024-01-01', 'January 1, 2024'),
    ('2024-02-15', 'February 15, 2024'),
    ('2024-12-31', 'December 31, 2024'),
])
def test_format_date_various_inputs(input_date, expected_output):
    """Test format_date with various inputs"""
    handler = DateHandler()
    result = handler.format_date(input_date)
    assert result == expected_output


@pytest.mark.parametrize('start,end,expected_days', [
    ('2024-01-01', '2024-01-10', 9),
    ('2024-01-01', '2024-01-02', 1),
    ('2024-01-01', '2024-01-01', 0),
])
def test_days_between_various_ranges(start, end, expected_days):
    """Test days_between with various date ranges"""
    result = days_between(start, end)
    assert result == expected_days
```

## Quality Principles

- Test realistic scenarios with real-world data
- Focus on business logic and data transformations
- Use descriptive test names
- Build comprehensive, reusable fixtures
- Verify behavior, not implementation
- Mock only external dependencies
- Avoid testing implementation details
- **Use precise assertions with exact expected values, not vague checks**
- Handle exceptions appropriately in tests
- Use parametrization for similar test cases
- Validate test assumptions against actual implementation
- Avoid `any` types - use proper type hints

## Common Pitfalls to Avoid

### 1. Testing Implementation Details

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

### 2. Writing Tests That Don't Test Anything

```python
# ❌ BAD: Test doesn't actually test the code
def test_addition(self):
    result = 2 + 2  # This doesn't use the codebase!
    assert result == 4

# ✅ GOOD: Test actually tests the code
def test_calculator_add(self):
    calculator = Calculator()
    result = calculator.add(2, 2)
    assert result == 4
```

### 3. Overly Complex Tests

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

### 4. Not Testing Edge Cases

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

### 5. Testing Fallback Cases

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

### 6. Not Testing All Branches of Conditional Logic

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

### 7. Not Testing All Branches

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

## Test Organization Best Practices

### Directory Structure

```
project/
├── src/
│   ├── module1.py
│   ├── module2.py
│   └── utils.py
├── tests/
│   ├── test_module1.py
│   ├── test_module2.py
│   ├── test_utils.py
│   ├── fixtures/
│   │   ├── sample_data.json
│   │   └── test_config.yaml
│   └── conftest.py
└── pytest.ini
```

### Using conftest.py for Shared Fixtures

```python
# tests/conftest.py
import pytest
from src.database import Database
from src.api_client import ApiClient

@pytest.fixture(scope='session')
def test_database():
    """Session-scoped database fixture"""
    db = Database(':memory:')
    db.create_tables()
    yield db
    db.close()

@pytest.fixture
def api_client():
    """API client fixture"""
    return ApiClient(base_url='https://api.example.com')

@pytest.fixture
def authenticated_client(api_client):
    """Authenticated API client fixture"""
    api_client.authenticate('test_user', 'test_password')
    return api_client
```

### pytest.ini Configuration

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=html
    --cov-report=term-missing

markers =
    unit: Unit tests
    slow: Slow running tests
    network: Tests that require network access
```

## Running Tests in CI/CD

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11"]

    steps:
      - uses: actions/checkout@v3
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      - name: Run tests
        run: pytest --cov=src --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## References

- [pytest Documentation](https://docs.pytest.org/)
- [Python unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)
