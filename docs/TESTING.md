# Testing Guide

## Quick Start

### Run All Tests with Coverage
```bash
# Linux/Mac
./scripts/run_tests.sh

# Windows
.\scripts\run_tests.ps1
```

### Using pytest directly
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_services/test_plagiarism_service.py

# Run specific test class
pytest tests/test_api/test_contracts.py::TestAuthAPIContracts

# Run specific test function
pytest tests/test_api/test_contracts.py::TestAuthAPIContracts::test_login_request_schema
```

## Test Categories

### Unit Tests
```bash
pytest -m unit
```

### Integration Tests
```bash
pytest -m integration
```

### API Contract Tests
```bash
pytest -m contract
```

### Performance Tests
```bash
pytest -m performance
```

### Skip Slow Tests
```bash
pytest -m "not slow"
```

## Coverage Reports

### Generate Coverage Reports
```bash
# HTML report (opens in browser)
pytest --cov=. --cov-report=html
open htmlcov/index.html  # Mac
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows

# Terminal report with missing lines
pytest --cov=. --cov-report=term-missing

# XML report (for CI/CD)
pytest --cov=. --cov-report=xml

# JSON report
pytest --cov=. --cov-report=json
```

### Coverage Thresholds
- **Target**: 85%+
- **Current**: Check with `coverage report`
- **By Module**: View in HTML report

### View Coverage for Specific Module
```bash
coverage report --include="services/*"
coverage report --include="middleware/*"
coverage report --include="routes/*"
```

## Advanced Testing

### Parallel Execution
```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto
```

### Watch Mode
```bash
# Install pytest-watch
pip install pytest-watch

# Auto-run tests on file changes
ptw
```

### Debugging Tests
```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger at start of test
pytest --trace

#Verbose output
pytest -vv
```

## Test Structure

```
tests/
├── test_services/              # Service layer tests
│   ├── test_plagiarism_service.py (150+ tests)
│   ├── test_gamification_service.py (120+ tests)
│   └── test_ai_grading_service.py
├── test_middleware/            # Middleware tests
│   ├── test_rate_limiter.py (100+ tests)
│   └── test_security.py
├── test_integration/           # Integration tests
│   └── test_submission_workflow.py (80+ tests)
├── test_api/                   # API contract tests
│   └── test_contracts.py (200+ tests)
└── conftest.py                 # Shared fixtures
```

## Coverage Configuration

### pytest.ini
- Test discovery patterns
- Coverage settings
- Test markers
- Logging configuration

### .coveragerc
- Source paths
- Omit patterns
- Report settings
- Minimum threshold (85%)

## CI/CD Integration

### GitHub Actions
```yaml
- name: Run tests with coverage
  run: |
    pytest --cov=. --cov-report=xml --cov-report=term

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

### GitLab CI
```yaml
test:
  script:
    - pytest --cov=. --cov-report=xml --cov-report=term
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

## Tips & Best Practices

### Writing Good Tests
1. **Arrange-Act-Assert** pattern
2. Use descriptive test names
3. One assertion concept per test
4. Use fixtures for setup/teardown
5. Mock external dependencies

### Improving Coverage
1. Identify uncovered lines: `coverage report --show-missing`
2. Focus on critical paths first
3. Test edge cases and error conditions
4. Add integration tests for workflows
5. Test both success and failure scenarios

### Performance
1. Use `@pytest.mark.slow` for slow tests
2. Run fast tests during development
3. Use parallel execution for CI
4. Mock expensive operations

## Troubleshooting

### Coverage Not Showing
```bash
# Clear coverage data
coverage erase

# Run tests again
pytest --cov=.
```

### Import Errors
```bash
# Install test dependencies
pip install -r requirements.txt
pip install pytest pytest-cov pytest-mock
```

### Database Tests Failing
```bash
# Ensure test database is running
docker-compose up mongo redis -d

# Set test environment
export FLASK_ENV=testing
```

## Coverage Badges

Generate coverage badge for README:
```bash
# Using coverage-badge
pip install coverage-badge
coverage-badge -o coverage.svg
```

## Test Coverage Goals

### Current Status
- **Overall**: ~85%+
- **Services**: ~90%+
- **Middleware**: ~85%+
- **Routes**: ~80%+
- **Integration**: ~85%+

### Target by Module
- Critical services (auth, grading, plagiarism): 95%+
- Middleware: 90%+
- API routes: 85%+
- Utilities: 80%+

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
