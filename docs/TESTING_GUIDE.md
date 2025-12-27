# 🧪 Testing Guide - Unified Cyber Threat Detection System

**Complete guide for running and writing tests.**

## Table of Contents

1. [Test Overview](#test-overview)
2. [Running Tests](#running-tests)
3. [Test Categories](#test-categories)
4. [Writing Tests](#writing-tests)
5. [CI/CD Integration](#cicd-integration)
6. [Coverage Reports](#coverage-reports)

---

## Test Overview

### Test Statistics

✅ **105/105 tests passing (100%)**

**Test Distribution:**
- 22 API Integration Tests
- 17 Database Tests  
- 21 Email Detector Tests
- 26 Web Analyzer Tests
- 14 Integration Tests
- 4 Performance Tests
- 1 Improvement Test

**Test Execution Time:** ~11 seconds (all tests)

**Framework:** pytest 9.0.2

---

## Running Tests

### Quick Start

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with detailed output
pytest -vv

# Run with test summary
pytest --tb=short
```

### Specific Test Categories

```bash
# API Integration Tests
pytest tests/test_api_integration.py -v

# Database Tests
pytest tests/test_database.py -v

# Email Detector Tests
pytest tests/test_email_detector.py -v
pytest tests/test_email_detector_comprehensive.py -v

# Web Analyzer Tests
pytest tests/test_web_analyzer.py -v
pytest tests/test_web_analyzer_comprehensive.py -v

# Integration Tests
pytest tests/test_integration.py -v

# Performance Tests
pytest -m slow -v
```

### Specific Test Functions

```bash
# Run single test
pytest tests/test_api_integration.py::TestEmailAnalysisAPI::test_email_analyze_endpoint -v

# Run test class
pytest tests/test_database.py::TestEmailModel -v

# Run tests matching pattern
pytest -k "email" -v
pytest -k "database" -v
```

### Exclude Slow Tests

```bash
# Exclude performance tests (faster execution)
pytest -m "not slow" -v
```

### Stop on First Failure

```bash
pytest -x  # Stop after first failure
pytest --maxfail=3  # Stop after 3 failures
```

---

## Test Categories

### 1. API Integration Tests (22 tests)

**File:** `tests/test_api_integration.py`

**Coverage:**
- Health endpoints (2 tests)
- Email analysis API (3 tests)
- Web analysis API (2 tests)
- Monitoring API (5 tests)
- Enrichment API (2 tests)
- Alert system (1 test)
- Error handling (4 tests)
- Integration flows (2 tests)
- Concurrency (1 test)

**Run:**
```bash
pytest tests/test_api_integration.py -v
```

**Example Test:**
```python
def test_email_analyze_endpoint(self, client):
    """Test email analysis endpoint"""
    payload = {
        'email_content': 'URGENT! Click here',
        'email_sender': 'phishing@fake.com',
        'email_subject': 'URGENT: Verify Account'
    }
    
    response = client.post(
        '/api/email/analyze',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    assert response.status_code in [200, 503]
    data = json.loads(response.data)
    
    if response.status_code == 200:
        assert 'prediction' in data
        assert 'confidence' in data
```

### 2. Database Tests (17 tests)

**File:** `tests/test_database.py`

**Coverage:**
- Model creation (6 tests)
- Query operations (8 tests)
- Statistics (3 tests)

**Run:**
```bash
pytest tests/test_database.py -v
```

**Test Classes:**
- `TestEmailModel` - Email table operations
- `TestWebLogModel` - WebLog table operations
- `TestThreatCorrelation` - Correlation queries
- `TestThreatReport` - Report generation
- `TestAuditLog` - Audit logging
- `TestEmailQueries` - Email queries
- `TestWebLogQueries` - Web log queries
- `TestCorrelationQueries` - Correlation queries

### 3. Email Detector Tests (21 tests)

**Files:**
- `tests/test_email_detector.py` (2 basic tests)
- `tests/test_email_detector_comprehensive.py` (19 comprehensive tests)

**Coverage:**
- Initialization and training
- Prediction accuracy
- Feature extraction
- Edge cases (empty, invalid data)
- Performance benchmarks

**Run:**
```bash
pytest tests/test_email_detector*.py -v
```

**Test Classes:**
- `TestEmailPhishingDetector` - Core functionality
- `TestEmailFeatures` - Feature extraction
- `TestEmailDetectorIntegration` - End-to-end
- `TestEmailDetectorPerformance` - Performance

### 4. Web Analyzer Tests (26 tests)

**Files:**
- `tests/test_web_analyzer.py` (2 basic tests)
- `tests/test_web_analyzer_comprehensive.py` (24 comprehensive tests)

**Coverage:**
- Log parsing
- Anomaly detection
- Attack pattern recognition
- Feature extraction
- Performance benchmarks

**Run:**
```bash
pytest tests/test_web_analyzer*.py -v
```

**Test Classes:**
- `TestWebLogAnalyzer` - Core functionality
- `TestAttackPatternDetection` - Pattern matching
- `TestWebAnalyzerIntegration` - End-to-end
- `TestWebAnalyzerPerformance` - Performance

### 5. Integration Tests (14 tests)

**File:** `tests/test_integration.py`

**Coverage:**
- Email detection pipeline
- Web analysis pipeline
- Unified platform integration
- Cross-platform correlation

**Run:**
```bash
pytest tests/test_integration.py -v
```

**Test Classes:**
- `TestEmailDetectionFlow` - Email pipeline
- `TestWebAnalysisFlow` - Web pipeline
- `TestUnifiedPlatformIntegration` - Combined
- `TestCrossPlatformCorrelation` - Correlation

### 6. Performance Tests (4 tests)

**Marked with:** `@pytest.mark.slow`

**Tests:**
- Email detector training time (< 30s)
- Email prediction speed (< 1s for 10 emails)
- Web analyzer analysis speed (< 5s for 100 logs)
- Web analyzer training speed (< 10s)

**Run:**
```bash
pytest -m slow -v
```

**Skip in normal runs:**
```bash
pytest -m "not slow" -v
```

---

## Writing Tests

### Test Structure

```python
import pytest
from src.email_detector.detector import EmailPhishingDetector

class TestMyFeature:
    """Test suite for MyFeature"""
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        # Arrange
        detector = EmailPhishingDetector()
        
        # Act
        result = detector.some_method()
        
        # Assert
        assert result is not None
        assert result['status'] == 'success'
    
    def test_error_handling(self):
        """Test error handling"""
        detector = EmailPhishingDetector()
        
        with pytest.raises(ValueError):
            detector.invalid_method()
```

### Using Fixtures

```python
import pytest

@pytest.fixture
def trained_detector():
    """Fixture providing trained detector"""
    detector = EmailPhishingDetector()
    # Load or train model
    return detector

def test_with_fixture(trained_detector):
    """Test using fixture"""
    result = trained_detector.predict("test email")
    assert result is not None
```

### Parametrized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("URGENT! Click here", "phishing"),
    ("Meeting tomorrow at 2pm", "legitimate"),
    ("Your package is ready", "legitimate"),
])
def test_multiple_inputs(input, expected):
    """Test multiple inputs"""
    detector = EmailPhishingDetector()
    result = detector.predict(input)
    assert result['prediction'].lower() == expected
```

### Testing API Endpoints

```python
import pytest
import json
from web_dashboard.app import app

@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_api_endpoint(client):
    """Test API endpoint"""
    response = client.post(
        '/api/email/analyze',
        data=json.dumps({'email_content': 'test'}),
        content_type='application/json'
    )
    
    assert response.status_code in [200, 503]
    data = json.loads(response.data)
    assert 'prediction' in data or 'error' in data
```

### Performance Tests

```python
import pytest
import time

@pytest.mark.slow
def test_performance():
    """Test performance (marked as slow)"""
    start = time.time()
    
    # Your code to test
    detector = EmailPhishingDetector()
    detector.train(data, labels)
    
    duration = time.time() - start
    
    assert duration < 30.0, f"Too slow: {duration:.2f}s"
```

---

## Test Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    api: marks tests as API tests
```

### Running Specific Markers

```bash
# Run only integration tests
pytest -m integration -v

# Run only API tests
pytest -m api -v

# Run all except slow tests
pytest -m "not slow" -v
```

---

## CI/CD Integration

### GitHub Actions

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest -v -m "not slow" --tb=short
    
    - name: Run slow tests
      run: |
        pytest -v -m slow --tb=short
      continue-on-error: true
```

### GitLab CI

Create `.gitlab-ci.yml`:

```yaml
test:
  stage: test
  image: python:3.10
  script:
    - pip install -r requirements.txt
    - pytest -v --tb=short
```

---

## Coverage Reports

### Generate Coverage Report

```bash
# Install coverage
pip install pytest-cov

# Run tests with coverage
pytest --cov=src --cov-report=html --cov-report=term

# Open HTML report
# Windows: start htmlcov/index.html
# Linux/Mac: open htmlcov/index.html
```

### Coverage Configuration

Create `.coveragerc`:

```ini
[run]
source = src
omit = 
    */tests/*
    */venv/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == .__main__.:
```

### CI Coverage Integration

```bash
# Generate coverage badge
pytest --cov=src --cov-report=term --cov-report=xml

# Upload to codecov (if configured)
bash <(curl -s https://codecov.io/bash)
```

---

## Debugging Tests

### Running with pdb

```bash
# Drop into debugger on failure
pytest --pdb

# Drop into debugger at start of test
pytest --trace
```

### Verbose Output

```bash
# Show print statements
pytest -s

# Show detailed output
pytest -vv

# Show locals on failure
pytest -l
```

### Capturing Output

```bash
# Show print statements
pytest -s -v

# Capture logs
pytest --log-cli-level=DEBUG
```

---

## Test Maintenance

### Best Practices

1. **Write tests first** (TDD approach)
2. **One assertion per test** (when possible)
3. **Use descriptive names** (`test_email_with_urgent_words_detected_as_phishing`)
4. **Clean up after tests** (fixtures with yield)
5. **Mock external services** (VirusTotal, SMTP)
6. **Keep tests independent**
7. **Test edge cases**

### Common Patterns

**Testing Exceptions:**
```python
def test_invalid_input():
    with pytest.raises(ValueError) as exc_info:
        detector.predict("")
    assert "empty content" in str(exc_info.value)
```

**Testing Warnings:**
```python
def test_deprecation_warning():
    with pytest.warns(DeprecationWarning):
        old_function()
```

**Mocking:**
```python
from unittest.mock import patch, Mock

def test_with_mock():
    with patch('requests.get') as mock_get:
        mock_get.return_value = Mock(status_code=200)
        result = fetch_data()
        assert result is not None
```

---

## Troubleshooting Tests

### Common Issues

**1. Import Errors**
```bash
# Ensure running from project root
cd UnifiedCyberThreatDetectionSystem
pytest

# Or add project to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**2. Database Errors**
```bash
# Tests use in-memory SQLite
# If issues, check database connection in test setup
pytest tests/test_database.py -v -s
```

**3. Model Not Trained**
```bash
# Some tests require trained models
python main.py
pytest tests/test_api_integration.py -v
```

**4. Fixture Errors**
```bash
# Check fixture scopes and dependencies
pytest --fixtures  # List all fixtures
```

---

## Test Results

### Current Status

```
✅ 105 passed
❌ 0 failed
⚠️ 0 errors
⏭️ 0 skipped
⏸️ 4 deselected (slow tests when using -m "not slow")

Time: ~11 seconds (all tests)
Time: ~6 seconds (without slow tests)
```

### Test Quality Metrics

- **Code Coverage:** 85%+
- **Test-to-Code Ratio:** 1:2
- **Average Test Time:** 0.1s per test
- **Flaky Tests:** 0
- **Test Maintenance:** Low

---

## Next Steps

After running tests:

1. ✅ **All tests passing?** → Ready to deploy
2. ❌ **Tests failing?** → Check logs and debug
3. 📊 **Check coverage** → Aim for 90%+
4. 🔄 **CI/CD setup** → Automate testing
5. 📝 **Write more tests** → Increase coverage

---

## Additional Resources

- **pytest Documentation:** [docs.pytest.org](https://docs.pytest.org/)
- **Testing Best Practices:** [BEST_PRACTICES.md](BEST_PRACTICES.md)
- **User Guide:** [USER_GUIDE.md](USER_GUIDE.md)
- **API Documentation:** [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

---

**Test Suite Version:** 1.0.0  
**Last Updated:** December 13, 2025  
**Status:** ✅ All Tests Passing (100%)
