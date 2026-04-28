# 🧪 Testing Guide

Complete testing guide for PremiumHubBot.

---

## 📋 Table of Contents

- [Setup](#setup)
- [Running Tests](#running-tests)
- [Test Structure](#test-structure)
- [Writing Tests](#writing-tests)
- [Coverage](#coverage)
- [CI/CD](#cicd)

---

## Setup

### Install Dependencies

```bash
# Install testing dependencies
pip install -r requirements-dev.txt
```

### Test Dependencies

- **pytest** — Test framework
- **pytest-asyncio** — Async test support
- **pytest-cov** — Coverage reporting
- **pytest-mock** — Mocking utilities
- **black** — Code formatter
- **ruff** — Linter
- **mypy** — Type checker

---

## Running Tests

### All Tests

```bash
# Run all tests
pytest

# Verbose output
pytest -v

# Show print statements
pytest -s
```

### Specific Tests

```bash
# Single file
pytest tests/test_database/test_user_repo.py

# Single test function
pytest tests/test_database/test_user_repo.py::TestUserRepository::test_create_user

# By marker
pytest -m unit
pytest -m integration
pytest -m slow
```

### With Coverage

```bash
# Coverage report
pytest --cov=bot --cov-report=html

# Open HTML report
open htmlcov/index.html
```

### Watch Mode (for development)

```bash
# Install pytest-watch
pip install pytest-watch

# Run in watch mode
ptw
```

---

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── pytest.ini               # Pytest configuration
│
├── test_database/           # Database layer tests
│   ├── __init__.py
│   ├── test_user_repo.py
│   ├── test_balance_repo.py
│   └── test_referral_bonus.py
│
├── test_services/           # Service layer tests
│   ├── __init__.py
│   └── test_referral_service.py
│
├── test_handlers/           # Handler tests
│   ├── __init__.py
│   └── test_referral_handler.py
│
└── test_utils/              # Utility tests
    ├── __init__.py
    └── test_subscription_checker.py
```

---

## Writing Tests

### Basic Test Template

```python
import pytest
from bot.database.repositories.user_repo import user_repo

class TestUserRepository:
    """Test cases for UserRepository."""
    
    @pytest.mark.asyncio
    async def test_create_user(self, clean_db, sample_user_data):
        """Test creating a new user."""
        # Arrange
        user_data = sample_user_data
        
        # Act
        success = await user_repo.create(**user_data)
        
        # Assert
        assert success is True
        user = await user_repo.get_by_id(user_data['user_id'])
        assert user is not None
```

### Available Fixtures

#### Database Fixtures

```python
@pytest.mark.asyncio
async def test_example(clean_db):
    """clean_db - Fresh database for each test."""
    pass

@pytest.mark.asyncio
async def test_example2(create_test_user):
    """create_test_user - Factory to create users."""
    user_id = await create_test_user(user_id=123456)
```

#### Data Fixtures

```python
def test_with_data(
    sample_user_data,
    sample_balance_data,
    sample_premium_data,
    sample_channel_data,
    sample_promocode_data
):
    """All sample data fixtures."""
    pass
```

#### Mock Fixtures

```python
@pytest.mark.asyncio
async def test_with_mocks(mock_bot, mock_message, mock_callback):
    """Mock bot, message, and callback fixtures."""
    await mock_message.answer("Test")
    mock_message.answer.assert_called_once()
```

### Testing Async Functions

```python
@pytest.mark.asyncio
async def test_async_function(clean_db):
    """Always use @pytest.mark.asyncio for async tests."""
    result = await some_async_function()
    assert result == expected
```

### Testing with Mocks

```python
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_with_mock(clean_db):
    """Test using mocks."""
    # Mock bot
    bot = AsyncMock()
    bot.send_message = AsyncMock()
    
    # Call function
    await some_function(bot)
    
    # Verify
    bot.send_message.assert_called_once()
```

### Testing Exceptions

```python
@pytest.mark.asyncio
async def test_exception(clean_db):
    """Test exception handling."""
    with pytest.raises(ValueError):
        await function_that_raises()
```

---

## Coverage

### Generate Coverage Report

```bash
# Terminal report
pytest --cov=bot --cov-report=term

# HTML report
pytest --cov=bot --cov-report=html

# XML report (for CI)
pytest --cov=bot --cov-report=xml
```

### Coverage Goals

- **Overall:** >= 80%
- **Critical paths:** >= 90%
  - User registration
  - Balance operations
  - Referral bonus
  - Premium purchase

### View Coverage

```bash
# Open HTML report
open htmlcov/index.html

# Terminal summary
pytest --cov=bot --cov-report=term-missing
```

---

## Code Quality

### Format Code

```bash
# Black formatter
black bot/ tests/

# Check only (no changes)
black --check bot/ tests/
```

### Lint Code

```bash
# Ruff linter
ruff check bot/ tests/

# Auto-fix
ruff check --fix bot/ tests/
```

### Type Check

```bash
# mypy type checker
mypy bot/

# Specific file
mypy bot/database/repositories/user_repo.py
```

---

## CI/CD

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        pytest --cov=bot --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

## Best Practices

### 1. Test Naming

```python
# Good
def test_create_user_with_valid_data():
    pass

def test_create_user_fails_with_duplicate_id():
    pass

# Bad
def test1():
    pass

def test_user():
    pass
```

### 2. One Assert Per Concept

```python
# Good
def test_user_creation():
    user = create_user()
    assert user.id == 123
    assert user.name == "John"

# Better - split into separate tests if testing different concepts
def test_user_id_assignment():
    user = create_user()
    assert user.id == 123

def test_user_name_assignment():
    user = create_user()
    assert user.name == "John"
```

### 3. Use Fixtures

```python
# Good - reusable
@pytest.fixture
def user_data():
    return {'id': 123, 'name': 'John'}

def test_with_fixture(user_data):
    assert user_data['id'] == 123

# Bad - repetitive
def test_without_fixture():
    data = {'id': 123, 'name': 'John'}
    assert data['id'] == 123
```

### 4. Clean Database

```python
# Always use clean_db fixture for database tests
@pytest.mark.asyncio
async def test_database_operation(clean_db):
    # Database is fresh and empty
    pass
```

---

## Troubleshooting

### Tests Failing Randomly

```bash
# Run with more verbosity
pytest -vv

# Show full traceback
pytest --tb=long

# Run single test
pytest tests/test_file.py::test_function -vv
```

### Database Locked

```bash
# Check for hanging connections
lsof | grep database.db

# Or just delete test database
rm -f /tmp/test_*.db
```

### Import Errors

```bash
# Install in development mode
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

## Quick Reference

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=bot

# Run specific test
pytest tests/test_database/test_user_repo.py

# Run fast tests only (skip slow)
pytest -m "not slow"

# Run in parallel
pytest -n auto

# Format code
black bot/ tests/

# Lint code
ruff check bot/ tests/

# Type check
mypy bot/
```

---

<div align="center">
  <b>🧪 Test Coverage: Aim for 80%+</b>
</div>
