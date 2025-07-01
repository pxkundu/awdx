"""
Pytest configuration and shared fixtures for AWDX testing.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import boto3
from moto import mock_iam, mock_s3, mock_ec2, mock_sts


@pytest.fixture(scope="session")
def project_root():
    """Get the project root directory."""
    current = Path(__file__).parent
    while current.parent != current:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")


@pytest.fixture
def temp_config_dir():
    """Create a temporary directory for configuration files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_aws_credentials():
    """Mock AWS credentials for testing."""
    with patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'testing',
        'AWS_SECRET_ACCESS_KEY': 'testing',
        'AWS_SECURITY_TOKEN': 'testing',
        'AWS_SESSION_TOKEN': 'testing',
        'AWS_DEFAULT_REGION': 'us-east-1'
    }):
        yield


@pytest.fixture
def mock_gemini_api():
    """Mock Google Gemini API for testing."""
    with patch('google.generativeai.configure') as mock_configure, \
         patch('google.generativeai.GenerativeModel') as mock_model:
        
        # Mock the model response
        mock_response = Mock()
        mock_response.text = "test response"
        mock_model.return_value.generate_content.return_value = mock_response
        
        yield {
            'configure': mock_configure,
            'model': mock_model,
            'response': mock_response
        }


@pytest.fixture
def aws_mocks():
    """Comprehensive AWS service mocking."""
    with mock_sts(), mock_iam(), mock_s3(), mock_ec2():
        yield


@pytest.fixture
def sample_aws_profiles():
    """Sample AWS profiles for testing."""
    return {
        'default': {
            'region': 'us-east-1',
            'aws_access_key_id': 'AKIATEST',
            'aws_secret_access_key': 'test-secret'
        },
        'prod': {
            'region': 'us-west-2',
            'aws_access_key_id': 'AKIAPROD',
            'aws_secret_access_key': 'prod-secret'
        },
        'dev': {
            'region': 'eu-west-1',
            'aws_access_key_id': 'AKIADEV',
            'aws_secret_access_key': 'dev-secret'
        }
    }


@pytest.fixture
def mock_s3_buckets():
    """Create mock S3 buckets for testing."""
    import boto3
    from moto import mock_s3
    
    with mock_s3():
        s3 = boto3.client('s3', region_name='us-east-1')
        
        # Create test buckets
        buckets = [
            {'name': 'test-bucket-1', 'region': 'us-east-1'},
            {'name': 'test-bucket-2', 'region': 'us-west-2'},
            {'name': 'public-bucket', 'region': 'us-east-1'},
        ]
        
        for bucket in buckets:
            s3.create_bucket(Bucket=bucket['name'])
            
            # Add some test objects
            s3.put_object(
                Bucket=bucket['name'],
                Key='test-file.txt',
                Body=b'test content'
            )
        
        # Make one bucket public
        s3.put_bucket_acl(
            Bucket='public-bucket',
            ACL='public-read'
        )
        
        yield buckets


@pytest.fixture
def mock_iam_users():
    """Create mock IAM users for testing."""
    import boto3
    from moto import mock_iam
    
    with mock_iam():
        iam = boto3.client('iam', region_name='us-east-1')
        
        users = [
            {'username': 'test-user-1', 'has_mfa': True},
            {'username': 'test-user-2', 'has_mfa': False},
            {'username': 'admin-user', 'has_mfa': True},
        ]
        
        for user in users:
            iam.create_user(UserName=user['username'])
            
            # Add access key
            iam.create_access_key(UserName=user['username'])
            
            # Add MFA device if specified
            if user['has_mfa']:
                iam.create_virtual_mfa_device(
                    VirtualMFADeviceName=f"{user['username']}-mfa"
                )
        
        yield users


@pytest.fixture
def ai_test_config():
    """Sample AI configuration for testing."""
    return {
        'gemini': {
            'api_key': 'test-api-key',
            'model': 'gemini-1.5-flash',
            'max_tokens': 1000,
            'temperature': 0.7
        },
        'features': {
            'command_validation': True,
            'intent_recognition': True,
            'conversation_history': True
        }
    }


@pytest.fixture
def security_test_files(temp_config_dir):
    """Create test files with various security issues."""
    files = {}
    
    # File with potential secret
    secret_file = temp_config_dir / "config_with_secret.py"
    secret_file.write_text("""
API_KEY = "AIzaSyDXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
PASSWORD = "super_secret_password_123"
""")
    files['secret'] = secret_file
    
    # File with command injection
    injection_file = temp_config_dir / "injection_example.py"
    injection_file.write_text("""
import os
import subprocess

def bad_function(user_input):
    os.system(f"echo {user_input}")
    subprocess.call(user_input, shell=True)
""")
    files['injection'] = injection_file
    
    # File with safe code
    safe_file = temp_config_dir / "safe_code.py"
    safe_file.write_text("""
import subprocess
import shlex

def safe_function(user_input):
    args = shlex.split(user_input)
    subprocess.run(args, timeout=30, shell=False)
""")
    files['safe'] = safe_file
    
    return files


# Custom markers for test organization
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "security: marks tests as security tests"  
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


# Pytest plugins
pytest_plugins = [
    "pytest_asyncio",
    "pytest_mock",
] 