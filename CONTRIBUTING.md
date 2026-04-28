# 🤝 Contributing Guide

Thanks for your interest in contributing to PremiumHubBot!

---

## 📋 Getting Started

### 1. Fork the Repository

Click the "Fork" button at the top right of the repository page.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/PremiumHubBot.git
cd PremiumHubBot
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

---

## 🛠 Development Setup

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install pytest pytest-asyncio pytest-cov black ruff mypy

# Setup .env
cp .env.example .env
# Edit .env with your test bot token
```

---

## 📝 Code Style

### Python Code Style

We use:
- **Black** for code formatting
- **Ruff** for linting
- **mypy** for type checking

```bash
# Format code
black bot/

# Lint code
ruff check bot/

# Type check
mypy bot/
```

### Coding Standards

- ✅ Use type hints everywhere
- ✅ Write docstrings for all functions
- ✅ Follow PEP 8
- ✅ Keep functions small and focused
- ✅ Use descriptive variable names
- ✅ Add comments for complex logic

**Example:**

```python
async def get_user_balance(user_id: int) -> Decimal:
    """
    Get user's current balance.
    
    Args:
        user_id: Telegram user ID
    
    Returns:
        Current balance as Decimal
    
    Raises:
        ValueError: If user not found
    """
    balance = await balance_repo.get_balance(user_id)
    if balance is None:
        raise ValueError(f"User {user_id} not found")
    return balance
```

---

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=bot --cov-report=html

# Specific test
pytest tests/test_user_repo.py
```

### Writing Tests

```python
import pytest
from bot.database.repositories.user_repo import user_repo

@pytest.mark.asyncio
async def test_create_user():
    """Test user creation."""
    success = await user_repo.create(
        user_id=999999,
        first_name="Test User"
    )
    assert success is True
    
    user = await user_repo.get_by_id(999999)
    assert user is not None
    assert user['first_name'] == "Test User"
```

---

## 📤 Submitting Changes

### 1. Commit Your Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add user statistics endpoint"
```

### Commit Message Format

Use conventional commits:

- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation
- `style:` — Code style (formatting)
- `refactor:` — Code refactoring
- `test:` — Adding tests
- `chore:` — Maintenance tasks

**Examples:**
- `feat: add referral bonus notification`
- `fix: resolve captcha timeout issue`
- `docs: update API reference`
- `refactor: improve database query performance`

### 2. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 3. Create Pull Request

1. Go to the original repository
2. Click "Pull requests"
3. Click "New pull request"
4. Select your fork and branch
5. Fill in the PR template
6. Submit!

---

## 🐛 Reporting Bugs

### Before Reporting

- Check existing issues
- Reproduce the bug
- Collect logs

### Bug Report Template

```markdown
**Describe the bug**
A clear description of the bug.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Logs**
```
Paste relevant logs here
```

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.11]
- Bot version: [e.g., 1.0.0]
```

---

## 💡 Feature Requests

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution**
How you'd like it to work.

**Additional context**
Any other context or screenshots.
```

---

## 📜 Code of Conduct

### Our Pledge

- Be respectful and inclusive
- Welcome newcomers
- Focus on what's best for the community
- Show empathy

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Political or religious debates
- Spam

---

## ❓ Questions

Have questions? Feel free to:
- Open a discussion
- Ask in issues
- Contact maintainers

---

Thank you for contributing! 🎉
