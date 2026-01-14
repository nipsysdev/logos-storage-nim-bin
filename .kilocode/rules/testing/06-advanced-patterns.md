# Advanced Patterns

This document covers advanced testing patterns including async handling, parametrization, and custom test utilities.

## 1. Async Handling

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

## 2. Test Naming Conventions

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

## 3. Testing with Parametrization

Use pytest's parametrize decorator to run the same test with multiple inputs:

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

## 4. Service Testing with Mock Implementations

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

## 5. Custom Test Utilities and Assertions

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

## 6. Testing with Realistic Test Data

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

## 7. Testing Complex Hierarchical Data

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

## 8. Testing Error Handling

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
