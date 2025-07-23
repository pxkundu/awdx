# AWDX Troubleshooting Guide

## 🔧 Common Issues and Solutions

### Browser Opening Issues

#### WSL (Windows Subsystem for Linux)
**Problem**: `xdg-open: no method available for opening 'https://aistudio.google.com/apikey'`

**Solutions**:
```bash
# Use the --no-browser flag
awdx ai configure --no-browser

# Or manually visit the URL
# https://aistudio.google.com/apikey
```

**Why this happens**: WSL doesn't have direct access to Windows browsers by default.

#### Linux (No GUI)
**Problem**: No default browser found

**Solutions**:
```bash
# Install a browser
sudo apt install firefox  # Ubuntu/Debian
sudo yum install firefox  # CentOS/RHEL

# Or use --no-browser flag
awdx ai configure --no-browser
```

#### macOS/Windows
**Problem**: Browser opening fails

**Solutions**:
```bash
# Check if browsers are installed
# macOS: Safari, Chrome, Firefox
# Windows: Edge, Chrome, Firefox

# Use --no-browser flag
awdx ai configure --no-browser
```

### API Connection Issues

#### Rate Limit/Quota Exceeded
**Error**: `429 Too Many Requests` or quota exceeded

**Solutions**:
- Wait 1-2 minutes and try again
- Check usage at: https://aistudio.google.com/
- Consider upgrading to paid Gemini API
- Use `gemini-1.5-flash` model (higher limits)

#### Invalid API Key
**Error**: `400 Bad Request` or `401 Unauthorized`

**Solutions**:
```bash
# Generate new API key
# Visit: https://aistudio.google.com/apikey

# Reconfigure AWDX
awdx ai configure

# Ensure key starts with 'AIza'
```

#### Network Connectivity
**Error**: Connection timeout or network errors

**Solutions**:
```bash
# Test connectivity
ping google.com

# Check if behind corporate firewall
# Disable VPN if using one
# Contact IT for proxy settings
```

### Environment-Specific Issues

#### Corporate Networks
**Common Issues**:
- Firewall blocking API calls
- SSL certificate issues
- Proxy interference

**Solutions**:
```bash
# Update certificates
pip install --upgrade certifi

# Check system time is correct
date

# Contact IT for:
# - Proxy configuration
# - Firewall exceptions
# - SSL certificate updates
```

#### Docker Containers
**Common Issues**:
- No browser access
- Network isolation
- Missing dependencies

**Solutions**:
```bash
# Use --no-browser flag
awdx ai configure --no-browser

# Ensure network access
docker run --network host ...

# Install dependencies
pip install google-generativeai
```

#### CI/CD Environments
**Common Issues**:
- No interactive prompts
- Missing environment variables
- Network restrictions

**Solutions**:
```bash
# Set environment variable directly
export GEMINI_API_KEY="your_api_key_here"

# Use non-interactive mode
awdx ai configure --no-interactive

# Test in CI
awdx ai test
```

### Dependency Issues

#### Missing Dependencies
**Error**: `ModuleNotFoundError` or import errors

**Solutions**:
```bash
# Update AWDX
pip install --upgrade awdx

# Install missing dependencies
pip install google-generativeai
pip install rich typer boto3

# Check Python version (requires 3.8+)
python --version
```

#### Version Conflicts
**Error**: Package version conflicts

**Solutions**:
```bash
# Create fresh virtual environment
python -m venv awdx_env
source awdx_env/bin/activate  # Linux/macOS
# or
awdx_env\Scripts\activate     # Windows

# Install AWDX
pip install awdx
```

### AWS Configuration Issues

#### Profile Not Found
**Error**: AWS profile not found or invalid

**Solutions**:
```bash
# List available profiles
awdx profile list

# Configure AWS credentials
aws configure

# Set profile
export AWS_PROFILE=your_profile_name
```

#### Permission Issues
**Error**: Access denied or insufficient permissions

**Solutions**:
- Check IAM permissions
- Verify AWS credentials
- Ensure profile has required access

### Performance Issues

#### Slow Response Times
**Causes**:
- Network latency
- API server load
- Large context size

**Solutions**:
```bash
# Check network speed
ping google.com

# Use faster model
# gemini-1.5-flash (default)

# Reduce context size in configuration
```

#### Memory Issues
**Error**: Out of memory or high memory usage

**Solutions**:
- Close other applications
- Reduce context size
- Use lighter model settings

## 🚀 Quick Diagnostic Commands

```bash
# Check AWDX version
awdx --version

# Check AI status
awdx ai --version

# Test AI configuration
awdx ai test

# Check AWS configuration
awdx profile list

# Test network connectivity
ping google.com

# Check Python environment
python --version
pip list | grep awdx
```

## 📞 Getting Help

### Self-Service
1. Check this troubleshooting guide
2. Run diagnostic commands above
3. Check GitHub issues: https://github.com/pxkundu/awdx/issues

### Community Support
- GitHub Discussions: https://github.com/pxkundu/awdx/discussions
- Create new issue with:
  - Error message
  - Environment details
  - Steps to reproduce

### Environment Information
When reporting issues, include:
```bash
# System info
uname -a
python --version
pip list

# AWDX info
awdx --version
awdx ai --version

# Environment
echo $SHELL
echo $PATH
```

## 🔄 Common Workflows

### Fresh Installation
```bash
# 1. Install AWDX
pip install awdx

# 2. Configure AI (with browser)
awdx ai configure

# 3. Configure AI (without browser)
awdx ai configure --no-browser

# 4. Test setup
awdx ai test
```

### Reconfiguration
```bash
# 1. Reset configuration
awdx ai config --reset

# 2. Reconfigure
awdx ai configure

# 3. Test
awdx ai test
```

### Environment Migration
```bash
# 1. Export configuration
export GEMINI_API_KEY="your_key"

# 2. Test in new environment
awdx ai test

# 3. Or save to file
awdx ai configure --no-interactive
```

---

*This guide covers the most common issues. For specific problems, check the error messages for targeted solutions.* 