# 🧪 AWDX Testing Framework
**Comprehensive Security & Quality Testing Suite**

This directory contains a complete testing framework for AWDX that combines security scanning, unit testing, integration testing, and code quality checks into a unified system.

## 📁 **Directory Structure**

```
tests/
├── README.md                    # This documentation
├── __init__.py                 # Testing package initialization
├── conftest.py                 # Pytest configuration and fixtures
├── security_scanner.py         # Automated security scanning tool
├── run_tests.py                # Comprehensive test runner
├── test_security_scanner.py    # Unit tests for security scanner
├── test_ai_integration.py      # AI engine integration tests
└── reports/                    # Generated test reports (auto-created)
    ├── security_report.md
    ├── test_summary.md
    └── coverage_html/
```

## 🚀 **Quick Start**

### **1. Install Test Dependencies**
```bash
# Install all testing and security dependencies
pip install -e ".[test]"

# Or install specific dependency groups
pip install -e ".[security]"  # Security tools only
pip install -e ".[dev]"        # Development dependencies
```

### **2. Run All Tests**
```bash
# Comprehensive test suite with coverage
python tests/run_tests.py --all --coverage --report test_report.md

# Quick security scan only
python tests/run_tests.py --security --quick

# Unit tests with coverage
python tests/run_tests.py --unit --coverage
```

### **3. Security Scan Only**
```bash
# Full security scan
python tests/security_scanner.py

# Quick security scan  
python tests/security_scanner.py --quick

# Generate detailed report
python tests/security_scanner.py --report security_report.md
```

## 🔒 **Security Testing**

### **Security Scanner Features**
- **🛡️ Vulnerability Scanning**: Bandit security analysis
- **📦 Dependency Checking**: Safety vulnerability database
- **🔑 Secret Detection**: Custom patterns for API keys, passwords
- **💉 Injection Detection**: Command and code injection patterns
- **📝 Code Quality**: Flake8, MyPy, Black formatting
- **🔍 Custom Checks**: AWDX-specific security validations

### **Security Test Categories**

| Category | Tool | Description |
|----------|------|-------------|
| **Critical Vulnerabilities** | Bandit | SQL injection, XSS, command injection |
| **Dependency Security** | Safety | Known CVEs in dependencies |
| **Secret Exposure** | Custom | API keys, passwords in code |
| **Command Injection** | Custom | Unsafe subprocess usage |
| **Code Quality** | Flake8/MyPy | Style, type safety |
| **AWDX-Specific** | Custom | AI engine security, config validation |

### **Running Security Tests**

```bash
# Complete security audit
python tests/security_scanner.py

# Quick scan (critical issues only) 
python tests/security_scanner.py --quick

# Generate detailed HTML report
python tests/security_scanner.py --report reports/security_audit.md

# Security tests only via test runner
python tests/run_tests.py --security --report security_summary.md
```

### **Security Score Calculation**
```
Security Score = 100 - (Critical×20 + High×10 + Medium×5 + Low×2 + Info×1)
```

## 🧪 **Unit & Integration Testing**

### **Test Organization**
Tests are organized using pytest markers:

- `@pytest.mark.unit` - Fast unit tests
- `@pytest.mark.integration` - Integration tests with AWS/AI services  
- `@pytest.mark.security` - Security-specific tests
- `@pytest.mark.slow` - Long-running tests

### **Available Fixtures**
```python
# AWS mocking
@pytest.fixture
def mock_aws_credentials(): ...

@pytest.fixture  
def mock_s3_buckets(): ...

@pytest.fixture
def mock_iam_users(): ...

# AI mocking
@pytest.fixture
def mock_gemini_api(): ...

@pytest.fixture
def ai_test_config(): ...

# Security testing
@pytest.fixture
def security_test_files(): ...
```

### **Running Unit Tests**
```bash
# All unit tests
pytest tests/ -m unit -v

# With coverage report
pytest tests/ -m unit --cov=src --cov-report=html

# Specific test file
pytest tests/test_security_scanner.py -v

# Via test runner with coverage
python tests/run_tests.py --unit --coverage
```

### **Running Integration Tests**  
```bash
# All integration tests
pytest tests/ -m integration -v

# Skip slow tests
pytest tests/ -m "integration and not slow" -v

# Via test runner
python tests/run_tests.py --integration
```

## 📊 **Test Reports & Coverage**

### **Automated Report Generation**
The test framework automatically generates comprehensive reports:

```bash
# Generate all reports
python tests/run_tests.py --all --coverage --report full_test_report.md

# Security report only
python tests/security_scanner.py --report security_audit.md

# Coverage HTML report
pytest --cov=src --cov-report=html
```

### **Report Types Generated**

| Report Type | File | Content |
|-------------|------|---------|
| **Security Audit** | `security_report.md` | Vulnerabilities, secrets, injections |
| **Test Summary** | `test_summary.md` | All test results, pass/fail rates |
| **Coverage HTML** | `coverage_html/` | Interactive code coverage |
| **Coverage XML** | `coverage.xml` | CI/CD compatible coverage |

### **Reading Security Reports**

Security reports include:
- **Executive Summary** with security score
- **Critical Issues** requiring immediate attention  
- **Detailed Findings** by category
- **Fix Suggestions** for each issue
- **Compliance Status** for production readiness

Example critical issue:
```markdown
### HIGH: Command Injection Vulnerability
**File**: `src/awdx/ai_engine/ai_commands.py:449`
**Issue**: `os.system()` usage without input validation
**Fix**: Use `subprocess.run()` with `shlex.split()`
```

## ⚙️ **Configuration**

### **Pytest Configuration** (`pyproject.toml`)
```toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers --strict-config"
testpaths = ["tests"]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests", 
    "security: marks tests as security tests",
    "unit: marks tests as unit tests"
]
```

### **Security Tool Configuration**
```toml
[tool.bandit]
exclude_dirs = ["tests", "venv"]
skips = ["B101"]  # Skip assert usage in tests

[tool.black]
line-length = 120
target-version = ['py38', 'py39', 'py310']

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/venv/*"]
```

### **Environment Variables**
```bash
# For integration tests
export AWS_ACCESS_KEY_ID=testing
export AWS_SECRET_ACCESS_KEY=testing  
export GEMINI_API_KEY=test-key-for-integration-tests
```

## 🔧 **Development Workflow**

### **Pre-commit Testing**
```bash
# Quick security check before commit
python tests/security_scanner.py --quick

# Format and lint code
black src/
isort src/
flake8 src/

# Run unit tests
python tests/run_tests.py --unit --quick
```

### **Pre-release Testing**
```bash
# Complete test suite with reports
python tests/run_tests.py --all --coverage --report release_readiness.md

# Review security score (should be >95)
python tests/security_scanner.py --report security_final.md

# Check test coverage (should be >80%)
pytest --cov=src --cov-report=term --cov-fail-under=80
```

### **CI/CD Integration**
```bash
# Install dependencies
pip install -e ".[test]"

# Run security checks (fail on critical issues)
python tests/security_scanner.py --quick

# Run all tests with coverage
python tests/run_tests.py --all --coverage --report ci_report.md

# Upload coverage to codecov (optional)
codecov -f coverage.xml
```

## 🚨 **Troubleshooting**

### **Common Issues**

**Missing Dependencies**
```bash
# Solution: Install test dependencies
pip install -e ".[test]"
```

**Security Tools Not Found**
```bash
# Solution: Install security tools specifically
pip install bandit safety flake8 mypy black isort
```

**Integration Tests Failing**
```bash
# Solution: Check AWS credentials and Gemini API key
export AWS_ACCESS_KEY_ID=testing
export AWS_SECRET_ACCESS_KEY=testing
export GEMINI_API_KEY=your-test-key
```

**Permission Errors**
```bash
# Solution: Make scripts executable
chmod +x tests/security_scanner.py
chmod +x tests/run_tests.py
```

### **Debug Mode**
```bash
# Verbose output for debugging
python tests/run_tests.py --all -v

# Pytest debugging
pytest tests/ -v -s --tb=long

# Security scanner with full output
python tests/security_scanner.py --report debug_security.md
```

## 📈 **Performance & Timing**

### **Typical Test Execution Times**

| Test Suite | Quick Mode | Full Mode |
|------------|------------|-----------|
| **Security Scan** | 30-60s | 2-5 min |
| **Unit Tests** | 10-30s | 1-2 min |
| **Integration Tests** | 1-3 min | 5-10 min |
| **Code Quality** | 20-40s | 1-2 min |
| **Total (All)** | 2-5 min | 10-20 min |

### **Optimization Tips**
- Use `--quick` for rapid feedback
- Run only specific test categories during development
- Use `-m "not slow"` to skip long-running tests
- Run security scans in parallel with other tests

## 🔄 **Continuous Integration**

### **GitHub Actions Example**
```yaml
name: AWDX Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      
      - name: Install dependencies
        run: pip install -e ".[test]"
      
      - name: Security scan
        run: python tests/security_scanner.py --quick
      
      - name: Run tests with coverage
        run: python tests/run_tests.py --all --coverage
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## 🎯 **Best Practices**

### **Writing Tests**
1. **Use descriptive test names**: `test_security_scan_detects_hardcoded_secrets`
2. **Mock external dependencies**: AWS, Gemini API, file system
3. **Test edge cases**: Empty inputs, network failures, timeouts
4. **Include security tests**: For new features, add security validations

### **Security Testing**
1. **Regular scans**: Run security scans before each commit
2. **Fix critical issues immediately**: Don't merge code with critical vulnerabilities
3. **Review security reports**: Understand each finding before dismissing
4. **Update dependencies**: Keep security tools and dependencies current

### **Code Coverage**
1. **Maintain >80% coverage**: Set coverage thresholds in CI/CD
2. **Test error paths**: Don't just test happy paths
3. **Mock properly**: Don't rely on external services for coverage
4. **Review coverage reports**: Identify untested code paths

---

## 📚 **Additional Resources**

- **Security Best Practices**: See `SECURITY.md` in project root
- **Contributing Guidelines**: See `CONTRIBUTING.md`
- **PyTest Documentation**: https://docs.pytest.org/
- **Bandit Documentation**: https://bandit.readthedocs.io/
- **Safety Documentation**: https://pyup.io/safety/

---

**✅ Ready for Production**: Run `python tests/run_tests.py --all --coverage` to verify complete readiness! 