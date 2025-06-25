# Contributing to awdx

Thank you for your interest in contributing to **awdx** (AWS DevOps X)! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Branching Strategy](#branching-strategy)
- [Contributing Guidelines](#contributing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Code Style and Standards](#code-style-and-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Release Process](#release-process)
- [Community](#community)

## Code of Conduct

### Our Pledge

We as members, contributors, and leaders pledge to make participation in our
community a harassment-free experience for everyone, regardless of age, body
size, visible or invisible disability, ethnicity, sex characteristics, gender
identity and expression, level of experience, education, socio-economic status,
nationality, personal appearance, race, religion, or sexual identity
and orientation.

### Our Standards

Examples of behavior that contributes to a positive environment for our
community include:

* Demonstrating empathy and kindness toward other people
* Being respectful of differing opinions, viewpoints, and experiences
* Giving and gracefully accepting constructive feedback
* Accepting responsibility and apologizing to those affected by our mistakes
* Focusing on what is best for the overall community

Examples of unacceptable behavior include:

* The use of sexualized language or imagery, and sexual attention or advances
* Trolling, insulting or derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information without explicit permission
* Other conduct which could reasonably be considered inappropriate

### Enforcement Responsibilities

Community leaders are responsible for clarifying and enforcing our standards of
acceptable behavior and will take appropriate and fair corrective action in
response to any behavior that they deem inappropriate, threatening, offensive,
or harmful.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- AWS CLI (for testing AWS functionality)
- Basic knowledge of AWS services and DevSecOps practices

### Quick Start

1. **Fork the repository**
   ```bash
   git clone https://github.com/pxkundu/awdx.git
   cd awdx
   ```

2. **Set up development environment**
   ```bash
   ./setup-dev.sh
   ```

3. **Activate virtual environment**
   ```bash
   source venv/bin/activate
   ```

4. **Install development dependencies**
   ```bash
   pip install -e .
   pip install -r requirements-dev.txt
   ```

## Development Setup

### Project Structure

```
awdx/
├── src/awdx/              # Main package source code
│   ├── __main__.py        # Entry point
│   ├── cli.py             # CLI interface
│   └── profilyze/         # Profile management module
├── docs/                  # Documentation
├── tests/                 # Test files
├── assests/               # Images and assets
├── .github/               # GitHub workflows and templates
├── pyproject.toml         # Project configuration
└── README.md              # Project documentation
```

## Branching Strategy

### Branch Structure

We follow a **GitFlow-inspired branching strategy** with the following branches:

- **`main`**: Production-ready code (stable releases)
- **`development`**: Integration branch for features (default development branch)
- **`feature/*`**: Feature development branches
- **`bugfix/*`**: Bug fix branches
- **`hotfix/*`**: Critical production fixes
- **`release/*`**: Release preparation branches

### Branch Naming Conventions

```
feature/descriptive-feature-name
bugfix/issue-description
hotfix/critical-fix-description
release/version-number
```

Examples:
- `feature/profile-validation`
- `bugfix/fix-profile-switching-issue`
- `hotfix/security-vulnerability-fix`
- `release/v0.0.5`

### Development Workflow

1. **Start from development branch**
   ```bash
   git checkout development
   git pull origin development
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the coding standards
   - Add comprehensive comments
   - Add tests for new functionality
   - Update documentation

4. **Test your changes**
   ```bash
   python -m pytest tests/
   python -m flake8 src/
   python -m mypy src/
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create Pull Request**
   - Target: `development` branch
   - Use the PR template
   - Request reviews from maintainers

## Contributing Guidelines

### Types of Contributions

We welcome various types of contributions:

- **Bug Reports**: Report bugs and issues
- **Feature Requests**: Suggest new features
- **Code Contributions**: Submit pull requests
- **Documentation**: Improve or add documentation
- **Testing**: Add or improve tests
- **Examples**: Share usage examples and tutorials

### Issue Guidelines

Before creating an issue, please:

1. **Search existing issues** to avoid duplicates
2. **Use the appropriate template** (bug report, feature request, etc.)
3. **Provide clear and detailed information**
4. **Include steps to reproduce** (for bugs)
5. **Add relevant labels**

### Pull Request Guidelines

1. **Fork the repository** and create a feature branch from `development`
2. **Follow the coding standards** and style guidelines
3. **Add comprehensive comments** to your code
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Ensure all tests pass** before submitting
7. **Write clear commit messages** following conventional commits
8. **Update the changelog** if applicable
9. **Target the `development` branch** for your PR

## Pull Request Process

### Before Submitting

1. **Run tests locally**
   ```bash
   python -m pytest tests/
   python -m flake8 src/
   python -m mypy src/
   ```

2. **Check code coverage**
   ```bash
   python -m pytest --cov=src/awdx tests/
   ```

3. **Build the package**
   ```bash
   python -m build
   twine check dist/*
   ```

4. **Update documentation**
   - Update relevant docstrings
   - Update README.md if needed
   - Update CHANGELOG.md

### PR Review Process

1. **Automated checks** must pass (CI/CD)
2. **Code review** by maintainers (minimum 1 approval required)
3. **Documentation review** for new features
4. **Testing review** for new functionality
5. **Final approval** and merge to `development`

### PR Approval Requirements

- **Minimum 1 maintainer approval** required
- **All automated checks must pass**
- **No merge conflicts**
- **Code follows style guidelines**
- **Tests pass and coverage is maintained**
- **Documentation is updated**

### After PR Approval

1. **Maintainers will merge** to `development` branch
2. **Feature branch will be deleted** (cleanup)
3. **Changes will be tested** in development environment
4. **Release process** will be initiated when ready

## Code Style and Standards

### Python Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use type hints for function parameters and return values
- Keep functions small and focused
- Use descriptive variable and function names
- Add comprehensive docstrings for all public functions and classes

### Code Comments

#### Function and Class Comments

```python
def validate_aws_profile(profile_name: str) -> bool:
    """
    Validate AWS profile credentials and permissions.
    
    This function checks if the specified AWS profile has valid credentials
    and sufficient permissions for basic AWS operations. It performs the
    following checks:
    - Credential validity
    - Permission to list S3 buckets
    - Permission to describe EC2 instances
    
    Args:
        profile_name (str): Name of the AWS profile to validate
        
    Returns:
        bool: True if profile is valid and has required permissions, False otherwise
        
    Raises:
        ProfileNotFoundError: If the specified profile doesn't exist
        CredentialError: If credentials are invalid or expired
        
    Example:
        >>> validate_aws_profile("production")
        True
        >>> validate_aws_profile("invalid-profile")
        False
    """
    # Implementation here
```

#### Inline Comments

```python
# Check if profile exists in AWS credentials file
if not os.path.exists(credentials_path):
    raise ProfileNotFoundError(f"Profile '{profile_name}' not found")

# Validate credentials by attempting to list S3 buckets
try:
    session = boto3.Session(profile_name=profile_name)
    s3_client = session.client('s3')
    s3_client.list_buckets()  # This will fail if credentials are invalid
except Exception as e:
    logger.error(f"Credential validation failed: {e}")
    return False
```

#### Complex Logic Comments

```python
def analyze_security_posture(profile_name: str) -> SecurityReport:
    """
    Analyze the security posture of an AWS profile.
    
    This function performs a comprehensive security analysis including:
    1. MFA status check
    2. Key rotation analysis
    3. Permission audit
    4. Compliance validation
    """
    
    # Step 1: Check MFA configuration
    # MFA is critical for security - check if enabled for all users
    mfa_status = check_mfa_configuration(profile_name)
    
    # Step 2: Analyze access key rotation
    # Keys should be rotated every 90 days for security
    key_rotation = analyze_key_rotation(profile_name)
    
    # Step 3: Audit IAM permissions
    # Check for overly permissive policies that could be security risks
    permission_audit = audit_iam_permissions(profile_name)
    
    # Step 4: Validate compliance
    # Ensure the profile meets our security compliance requirements
    compliance_status = validate_compliance(profile_name)
    
    return SecurityReport(
        mfa_status=mfa_status,
        key_rotation=key_rotation,
        permission_audit=permission_audit,
        compliance_status=compliance_status
    )
```

### Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Example Commit Messages

```
feat(profilyze): add profile validation functionality
fix(cli): resolve issue with profile switching
docs: update installation instructions
test(profilyze): add unit tests for profile validation
style: format code according to PEP 8
refactor(cli): improve error handling in profile commands
```

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest --cov=src/awdx tests/

# Run specific test file
python -m pytest tests/test_profilyze.py

# Run with verbose output
python -m pytest -v tests/

# Run tests with parallel execution
python -m pytest -n auto tests/
```

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern
- Mock external dependencies (AWS services)
- Test both success and failure scenarios
- Add comments explaining complex test logic

### Test Structure

```
tests/
├── unit/              # Unit tests
├── integration/       # Integration tests
├── fixtures/          # Test fixtures and data
└── conftest.py        # Pytest configuration
```

### Example Test with Comments

```python
def test_validate_aws_profile_with_valid_credentials():
    """
    Test profile validation with valid AWS credentials.
    
    This test verifies that the validate_aws_profile function correctly
    identifies a profile with valid credentials and permissions.
    """
    # Arrange: Set up test data and mocks
    profile_name = "test-profile"
    mock_session = Mock()
    mock_s3_client = Mock()
    mock_session.client.return_value = mock_s3_client
    
    # Mock successful S3 list_buckets call
    mock_s3_client.list_buckets.return_value = {"Buckets": []}
    
    with patch('boto3.Session', return_value=mock_session):
        # Act: Call the function under test
        result = validate_aws_profile(profile_name)
        
        # Assert: Verify the expected behavior
        assert result is True
        mock_s3_client.list_buckets.assert_called_once()
```

## Documentation

### Documentation Standards

- Write clear and concise documentation
- Use proper markdown formatting
- Include code examples
- Keep documentation up to date
- Add comprehensive docstrings to all public APIs
- Include inline comments for complex logic

### Documentation Structure

```
docs/
├── INSTALLATION.md     # Installation guide
├── USAGE.md           # Usage examples
├── API.md             # API documentation
├── CONTRIBUTING.md    # This file
└── CHANGELOG.md       # Release notes
```

### Docstring Standards

```python
def complex_function(param1: str, param2: Optional[int] = None) -> Dict[str, Any]:
    """
    Brief description of what the function does.
    
    Longer description explaining the purpose, behavior, and any important
    implementation details. This should be comprehensive enough for other
    developers to understand and use the function correctly.
    
    Args:
        param1 (str): Description of the first parameter, including any
                     constraints or special values
        param2 (Optional[int], optional): Description of the second parameter.
                                         Defaults to None.
    
    Returns:
        Dict[str, Any]: Description of the return value structure and content
    
    Raises:
        ValueError: When param1 is empty or invalid
        ConnectionError: When unable to connect to external service
    
    Example:
        Basic usage:
        >>> result = complex_function("test", 42)
        >>> print(result)
        {'status': 'success', 'data': 'test_42'}
        
        With default parameter:
        >>> result = complex_function("test")
        >>> print(result)
        {'status': 'success', 'data': 'test_None'}
    
    Note:
        This function performs expensive operations and should be used
        carefully in performance-critical code paths.
    """
```

## Release Process

### Version Management

We use [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Workflow

1. **Feature Development**: All features developed in `feature/*` branches
2. **Integration**: Features merged to `development` branch
3. **Testing**: Comprehensive testing in development environment
4. **Release Branch**: Create `release/vX.Y.Z` branch from `development`
5. **Final Testing**: Test release candidate thoroughly
6. **Merge to Main**: Merge release branch to `main` and tag
7. **Deploy**: Publish to PyPI and create GitHub release

### Publishing to PyPI

```bash
# Build package
python -m build

# Check package
twine check dist/*

# Upload to TestPyPI (for testing)
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## Community

### Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check the docs first
- **Examples**: Look at existing examples and tutorials

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community discussion
- **GitHub Pull Requests**: Code contributions and reviews

### Recognition

Contributors will be recognized in:

- **README.md**: Contributors section
- **GitHub Contributors**: Automatic recognition
- **Release Notes**: Credit for significant contributions
- **Documentation**: Attribution for major features

### Mentorship

We encourage mentorship and learning:

- **First-time contributors**: Special guidance and support
- **Code reviews**: Constructive feedback and learning opportunities
- **Documentation**: Help with writing and improving docs
- **Testing**: Guidance on writing effective tests

## License

By contributing to awdx, you agree that your contributions will be licensed under the [MIT License](LICENSE).

## Questions?

If you have questions about contributing, please:

1. Check the documentation first
2. Search existing issues and discussions
3. Create a new issue or discussion
4. Reach out to maintainers

Thank you for contributing to awdx! 🚀 