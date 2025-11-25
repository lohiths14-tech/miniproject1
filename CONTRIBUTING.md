# Contributing to AI-Powered Grading System

## Development Setup

### 1. Clone and Install
```bash
git clone <repository-url>
cd ai-grading-system
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Install Pre-commit Hooks
```bash
pre-commit install
```

### 3. Run Tests
```bash
pytest --cov=.
```

## Code Quality Standards

### Testing
- Minimum 70% code coverage required
- All new features must include tests
- Run tests before committing: `pytest`

### Linting
Code must pass all linting checks:
```bash
black .                # Format code
flake8 .              # Check style
pylint **/*.py        # Analyze code quality
```

### Security
Run security scans:
```bash
bandit -r .           # Security vulnerabilities
safety check          # Dependency vulnerabilities
```

## Pull Request Process

1. Create feature branch from `develop`
2. Write tests for new features
3. Ensure all tests pass
4. Run linting and fix issues
5. Update documentation
6. Submit PR with clear description

## Commit Messages

Follow conventional commits:
```
feat: Add new feature
fix: Bug fix
docs: Documentation
test: Add tests
refactor: Code refactoring
```

## Questions?

Contact the maintainers or open an issue.
