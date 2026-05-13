# ILNET TELECOM Network Monitoring Platform - Test Suite

This directory contains all test cases for the ILNET monitoring platform.

## Test Structure

```
tests/
├── conftest.py           # Pytest configuration and fixtures
├── test_auth.py          # Authentication tests
├── test_devices.py       # Device management tests
├── test_collector.py     # SNMP collector tests
└── test_health.py        # Health check tests
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=src --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_auth.py -v
```

### Run specific test
```bash
pytest tests/test_auth.py::TestAuthManager::test_generate_token -v
```

## Test Coverage

Target coverage: > 80%

### Coverage by module:
- `src/api/auth.py` - 100%
- `src/api/routes.py` - 85%
- `src/snmp_collector/device_manager.py` - 90%
- `src/snmp_collector/collector.py` - 80%

## Mocking

Tests use fixtures from `conftest.py` for:
- Flask test client
- Temporary configuration files
- Device manager instances
- SNMP collector instances

## CI/CD Integration

Tests are run automatically on:
- Push to any branch
- Pull requests
- Scheduled daily runs

See `.github/workflows/` for CI/CD configuration.
