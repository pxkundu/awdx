# 🤖 AWDX AI Features

AWDX now includes powerful Gen AI capabilities powered by Google Gemini, enabling natural language interaction with AWS DevSecOps tools.

## 🌟 Overview

The Gen AI engine transforms AWDX from a traditional CLI into an intelligent assistant that understands natural language queries and converts them into appropriate AWDX commands.

### Key Features

- **Natural Language Processing**: Ask questions in plain English
- **Intent Recognition**: Understands what you want to accomplish
- **Command Mapping**: Automatically maps intents to AWDX commands
- **Interactive Chat**: Conversational interface for complex workflows
- **Command Explanation**: Get detailed explanations of commands
- **Smart Suggestions**: Context-aware command recommendations
- **Confidence Scoring**: Reliability indicators for AI suggestions

## 🚀 Quick Start

### 1. Setup

#### Interactive Setup (Recommended)

AWDX provides a guided setup experience that follows industry CLI standards:

```bash
awdx ai configure
```

This interactive setup will:
- 🌐 **Open browser automatically** to Google AI Studio
- 📋 **Guide you** through API key creation
- 🔍 **Test the connection** to validate your setup  
- 💾 **Save configuration** with multiple storage options
- 🚀 **Get you ready** to use AI features immediately

#### Manual Setup

If you prefer manual setup or are in a CI/CD environment:

```bash
# Get your API key from Google AI Studio
awdx ai configure --no-interactive

# Or set directly:
export GEMINI_API_KEY="your_api_key_here"
```

Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).

### 2. Basic Usage

```bash
# Ask questions in natural language
awdx ask "show me all my AWS profiles"
awdx ask "what are my EC2 costs for last month"
awdx ask "audit my IAM security"

# Start interactive chat session
awdx chat

# Get command explanations
awdx explain "awdx cost summary --days 30"

# Get AI suggestions
awdx suggest --context "I want to optimize my AWS costs"
```

## 📚 Commands Reference

### `awdx ask`

Ask questions in natural language and get AWDX command suggestions.

**Syntax:**
```bash
awdx ask "<natural language query>" [OPTIONS]
```

**Options:**
- `--profile, -p`: AWS profile to use
- `--execute, -x`: Execute the suggested command immediately
- `--explain/--no-explain`: Show/hide explanation (default: show)

**Examples:**
```bash
# Basic queries
awdx ask "list my aws profiles"
awdx ask "show s3 buckets with public access"
awdx ask "check which IAM users don't have MFA"

# With execution
awdx ask "show my costs for last 30 days" --execute

# With specific profile
awdx ask "audit iam in production" --profile prod
```

### `awdx chat`

Start an interactive AI chat session.

**Syntax:**
```bash
awdx chat [OPTIONS]
```

**Options:**
- `--profile, -p`: AWS profile to use

**Features:**
- Multi-turn conversations with context
- Command preview before execution
- Type `exit`, `quit`, or press Ctrl+C to end

**Example Session:**
```
🤖 Welcome to AWDX AI Chat!

You: show me all my aws profiles
AI: Intent: list_profiles (confidence: 0.95)
    Command: awdx profile list
    
Execute this command? [y/N]: y
🚀 Executing: awdx profile list
...

You: switch to production
AI: Intent: switch_profile (confidence: 0.92)  
    Command: awdx profile switch production
```

### `awdx explain`

Get detailed explanations of AWDX commands.

**Syntax:**
```bash
awdx explain "<command>" [OPTIONS]
```

**Options:**
- `--detailed, -d`: Show detailed explanation

**Examples:**
```bash
awdx explain "awdx cost summary"
awdx explain "awdx iam audit --export results.json" --detailed
```

### `awdx suggest`

Get AI-powered command suggestions based on context.

**Syntax:**
```bash
awdx suggest [OPTIONS]
```

**Options:**
- `--context, -c`: Context for suggestions
- `--profile, -p`: AWS profile context

**Examples:**
```bash
awdx suggest --context "I want to reduce my AWS bill"
awdx suggest --context "Security audit for compliance"
awdx suggest --context "New team member onboarding"
```

## 🎯 Natural Language Examples

### Profile Management
```bash
awdx ask "list all my aws profiles"
awdx ask "switch to production environment"
awdx ask "create a new profile for staging"
awdx ask "which profile am I currently using"
```

### Cost Analysis
```bash
awdx ask "show my aws costs for this month"
awdx ask "what services are costing me the most"
awdx ask "cost trends for the last 90 days"
awdx ask "how can I optimize my aws spending"
awdx ask "set up cost alerts for $1000 threshold"
```

### IAM Security
```bash
awdx ask "audit my iam security"
awdx ask "which users don't have mfa enabled"
awdx ask "check for overprivileged iam roles"
awdx ask "show me all admin users"
awdx ask "export iam audit results to csv"
```

### S3 Security
```bash
awdx ask "scan my s3 buckets for security issues"
awdx ask "find all public s3 buckets"
awdx ask "check s3 encryption compliance"
awdx ask "which buckets don't have versioning"
```

### Secret Management
```bash
awdx ask "discover all secrets in my aws account"
awdx ask "rotate database passwords"
awdx ask "check for expired secrets"
awdx ask "monitor secret rotation status"
```

### Security Assessment
```bash
awdx ask "run a comprehensive security audit"
awdx ask "scan for security vulnerabilities"
awdx ask "check compliance with cis benchmarks"
awdx ask "what security issues should I prioritize"
```

## ⚙️ Configuration

### Basic Configuration

The AI engine uses environment variables for basic configuration:

```bash
# Required: Gemini API key
export GEMINI_API_KEY="your_api_key"

# Optional: Model selection
export GEMINI_MODEL="gemini-1.5-pro"

# Optional: Enable/disable AI features
export AWDX_AI_ENABLED="true"

# Optional: Debug mode
export AWDX_DEBUG="false"
```

### Advanced Configuration

Create a configuration file at `~/.awdx/ai_config.yaml`:

```yaml
# AI Engine Configuration
enabled: true
debug_mode: false
log_level: INFO

# Gemini API settings
gemini:
  api_key: null  # Set via GEMINI_API_KEY environment variable
  model: gemini-1.5-pro
  temperature: 0.7
  max_tokens: 1000000

# Feature flags
features:
  natural_language: true
  multimodal: true
  conversation_mode: true
  workflow_automation: true

# Security settings
security:
  mask_sensitive_data: true
  log_interactions: false
  
# Performance settings
performance:
  cache_enabled: true
  rate_limit: 60  # requests per minute
  max_context_size: 500000
```

### Configuration Commands

```bash
# Interactive setup (recommended)
awdx ai configure

# Show current configuration
awdx ai config --show

# Reset configuration
awdx ai config --reset

# Manual setup for CI/CD
awdx ai configure --no-interactive
```

### Configuration Storage Options

The interactive setup provides secure storage options:

1. **Environment Variable** (default) - Adds to shell config (~/.zshrc, ~/.bashrc)
2. **User Config File** (~/.awdx/ai_config.yaml) - Persistent user-level settings
3. **Project Config File** (./awdx.ai.yaml) - Project-specific configuration
4. **Manual Instructions** - Copy-paste commands for custom setup

## 🛡️ Security & Privacy

### Data Handling
- **No AWS credentials** are sent to AI services
- **Sensitive data masking** enabled by default
- **Local processing** where possible
- **Encrypted context** storage (when enabled)

### API Communication
- All communication uses **HTTPS/TLS encryption**
- **Rate limiting** prevents excessive API usage
- **Request logging** can be disabled for privacy
- **API key validation** before sending requests

### Best Practices
1. **Rotate API keys** regularly
2. **Use environment variables** for sensitive config
3. **Enable masking** for sensitive data
4. **Monitor API usage** and costs
5. **Review logs** periodically

## 🚨 Troubleshooting

### Common Issues

#### "AI features are not available"
```bash
# Solution: Install required dependencies
pip install google-generativeai rich pyyaml pillow

# Or reinstall awdx with AI dependencies
pip install awdx[ai]
```

#### "Please configure GEMINI_API_KEY"
```bash
# Solution: Set your API key
export GEMINI_API_KEY="your_api_key_here"

# Or use config command
awdx ai config --init
```

#### "Rate limit exceeded"
```bash
# Solution: Wait and retry, or check API quotas
# Configure lower rate limits in config file
awdx ai config --show
```

#### "Empty response from API"
```bash
# Check API key validity
awdx ai config --show

# Try with debug mode
export AWDX_DEBUG=true
awdx ask "test query"
```

### Debug Mode

Enable debug mode for detailed logging:

```bash
export AWDX_DEBUG=true
export AWDX_LOG_LEVEL=DEBUG
awdx ask "your query here"
```

### Configuration Issues

#### "GeminiClient.__init__() missing required argument"
```bash
# This usually indicates a dependency issue. Try:
pip install --upgrade google-generativeai rich pyyaml pillow

# Or reinstall AWDX completely:
pip uninstall awdx
pip install awdx
```

#### Configuration process hangs or times out
```bash
# Try non-interactive mode:
awdx ai configure --no-interactive

# Or set API key manually:
export GEMINI_API_KEY="your_api_key_here"
awdx ai ask "test connection"
```

#### Emoji display issues in terminal
```bash
# Make sure your terminal supports UTF-8:
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# For older terminals, use:
awdx ai configure --no-interactive
```

## 🔄 Integration Examples

### CI/CD Pipeline Integration

```yaml
# .github/workflows/aws-audit.yml
name: AWS Security Audit
on:
  schedule:
    - cron: '0 9 * * 1'  # Weekly on Monday

jobs:
  security-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup AWDX
        run: pip install awdx
      - name: Run AI-powered audit
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: |
          awdx ask "run comprehensive security audit" --execute
          awdx ask "export audit results to json" --execute
```

### Slack Bot Integration

```python
# slack_bot.py
import os
import asyncio
from awdx.ai_engine import get_nlp_processor, initialize_ai_engine

async def handle_slack_message(message):
    if not initialize_ai_engine():
        return "AI engine not available"
    
    nlp = get_nlp_processor()
    result = await nlp.process_query(message)
    
    return f"Command: `{result.awdx_command}`\nConfidence: {result.confidence:.2f}\n{result.explanation}"
```

## 📊 Performance & Limitations

### Performance Metrics
- **Average Response Time**: 1-3 seconds
- **Cache Hit Rate**: ~60% for repeated queries  
- **Context Size Limit**: 500K tokens
- **Rate Limit**: 60 requests/minute (configurable)

### Current Limitations
- **English only** natural language support
- **Text-based** interactions (multimodal coming soon)
- **Internet required** for AI processing
- **API costs** based on usage
- **Context window** limits for long conversations

### Roadmap
- [ ] **Multimodal support** (images, documents)
- [ ] **Offline mode** for basic queries
- [ ] **Custom model** fine-tuning
- [ ] **Voice interface** support
- [ ] **Multi-language** support

## 💡 Tips & Best Practices

### Effective Queries
- **Be specific**: "show EC2 costs for last 30 days" vs "show costs"
- **Include context**: "in production profile" or "for us-east-1"
- **Use action words**: "audit", "scan", "check", "optimize"
- **Specify time ranges**: "last week", "this month", "90 days"

### Workflow Optimization
1. **Start with chat mode** for exploratory tasks
2. **Use ask with --execute** for routine operations
3. **Combine with explain** to learn new commands
4. **Use suggest** when unsure what to do next

### Cost Management
- **Monitor API usage** in Google Cloud Console
- **Use caching** to reduce redundant requests
- **Configure rate limits** appropriately
- **Consider batch operations** for multiple queries

## 🤝 Contributing

The AI engine is modular and extensible. Contributions welcome for:

- **New intent types** and command mappings
- **Language model improvements** and prompts
- **Integration with other AI services**
- **Performance optimizations**
- **Additional security features**

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development setup and guidelines.

## 📄 License

The AI features are released under the same MIT license as AWDX core.

### Free Tier Optimization

AWDX AI is configured by default to use **free tier optimized models**:

- **Default Model**: `gemini-1.5-flash` (free, fast, generous rate limits)
- **Alternative**: `gemini-1.5-flash-8b` (free, even faster, 2x higher rate limits)
- **Premium**: `gemini-1.5-pro` (free tier but very limited quotas)

#### Changing Models

```bash
# Use the fastest free model (recommended for most users)
export GEMINI_MODEL="gemini-1.5-flash-8b"

# Use the default balanced model  
export GEMINI_MODEL="gemini-1.5-flash"

# Use the premium model (may hit quotas quickly on free tier)
export GEMINI_MODEL="gemini-1.5-pro"
```

### Rate Limits by Model

| Model                 | Free Tier Requests/Min | Free Tier Tokens/Min |
|-----------------------|------------------------|----------------------|
| `gemini-1.5-flash-8b` | **4,000 RPM**          | Higher limits        |
| `gemini-1.5-flash`    | **2,000 RPM**          | **4M TPM**           |
| `gemini-1.5-pro`      | **15 RPM**             | **1M TPM** ⚠️        |

**💡 Recommendation**: Use `gemini-1.5-flash` (default) or `gemini-1.5-flash-8b` for the best free tier experience.

## 🛡️ Enhanced Command Validation & Anti-Hallucination

**Problem Solved**: The AI was generating plausible-sounding but non-existent AWDX parameters like `--size-sort` and `--sort size`.

### **🔍 Real Command Validation**
- **Command Reference System**: Built-in knowledge of actual AWDX commands and options
- **Parameter Validation**: Only suggests parameters that actually exist
- **Capability Detection**: Automatically detects when AWDX lacks specific functionality

### **🎯 Smart Tool Selection**
```bash
# ❌ Old behavior (hallucinated parameters)
awdx s3 audit --size-sort

# ✅ New behavior (accurate recommendations)
Query: "biggest s3 bucket in this account"
→ Intent: s3_audit
→ Confidence: ⚠️ 0.63 (reduced for unsupported)
→ Primary Command: (empty - AWDX can't handle this)
→ AWS CLI Alternative: aws s3 ls --recursive --summarize | sort -k3 -nr
```

### **🚦 Decision Logic**
1. **Size/Storage Queries** → AWS CLI (AWDX has no size analysis)
2. **Detailed Resource Listing** → AWS CLI (more comprehensive)
3. **Security Audits** → AWDX (specialized DevSecOps tools)
4. **Quick Checks** → AWDX (user-friendly output)

### **📊 Validation Results**
| Query Type | Tool Choice | Confidence | Parameters |
|------------|-------------|------------|------------|
| "biggest s3 bucket" | AWS CLI | 0.63 ⚠️ | Real AWS options |
| "audit IAM security" | AWDX | 0.95 ✅ | Real AWDX options |
| "list EC2 instances" | AWS CLI | 0.69 ⚠️ | Real AWS options |

## Enhanced DevOps Intelligence

AWDX AI has been enhanced with advanced DevOps intelligence that understands both **AWDX commands** and **AWS CLI commands**, providing intelligent recommendations based on the context.

### 🎯 **Intelligent Command Selection**

The AI automatically chooses the best tool for each task:

- **🔒 AWDX Commands**: For security audits, compliance checks, and DevSecOps workflows
- **⚡ AWS CLI Commands**: For detailed resource inspection, direct service management, and when AWDX doesn't have the capability
- **🔗 Hybrid Workflows**: Suggests combinations of both tools for complex scenarios

### 🧠 **Enhanced Response Features**

Each AI response now includes:

**📝 Primary Command**: The recommended command (AWDX or AWS CLI)
**🔄 Alternative Commands**: Alternative approaches using different tools
**⚠️ Security Considerations**: Security implications and warnings
**🎯 DevOps Workflow Context**: How the command fits into broader workflows
**💡 Smart Suggestions**: Follow-up actions and related commands

### 🎨 **Example Enhanced Responses**

```bash
awdx ai ask "audit my IAM security"
```

**Response:**
- **Intent**: `iam_security_audit` ✅ (no longer "unknown")
- **Primary Command**: `awdx iam audit`
- **AWS CLI Alternative**: `aws iam list-users aws iam list-groups aws iam list-roles`
- **Security Considerations**: Warning about sensitive information handling
- **DevOps Context**: Integration into CI/CD pipelines for regular assessment
- **Suggestions**: Follow-up compliance checks and remediation steps

```bash
awdx ai ask "list all EC2 instances in us-east-1"
```

**Response:**
- **Intent**: `aws_cli_command` ✅
- **Primary Command**: `aws ec2 describe-instances --region us-east-1` (AWS CLI chosen as optimal)
- **Security Considerations**: IAM permissions and data filtering recommendations
- **DevOps Context**: Infrastructure monitoring and automation workflows
- **Suggestions**: Query filtering and dashboard integration options

### 🏗️ **DevOps Workflow Intelligence**

The AI understands common DevOps patterns:

**🔍 Investigation Workflows**: 
```bash
awdx ai ask "investigate high AWS costs"
# Suggests: cost summary → service breakdown → optimization recommendations
```

**🔒 Security Workflows**:
```bash  
awdx ai ask "security audit for production"
# Suggests: AWDX security scan → IAM audit → S3 compliance check
```

**📊 Monitoring Workflows**:
```bash
awdx ai ask "check production infrastructure health" 
# Suggests: AWS CLI for instance status → AWDX for security posture
```

### 🎯 **Supported Intent Recognition**

The AI now recognizes over 25 specific intents:

**Profile Management**: `list_profiles`, `get_current_profile`, `switch_profile`
**Cost Analysis**: `show_costs`, `cost_analysis`, `get_current_month_cost`, `cost_optimization`  
**IAM Security**: `iam_audit`, `iam_security_audit`, `list_iam_users`, `list_iam_roles`
**S3 Security**: `s3_audit`, `s3_scan`, `list_s3_buckets`, `s3_security_scan`
**EC2 Management**: `list_ec2_instances`, `ec2_security_groups`, `ec2_status`
**Security Assessment**: `security_audit`, `security_scan`, `vulnerability_scan`
**AWS CLI Operations**: `aws_cli_command`, `aws_describe`, `aws_list`

### 🚀 **Improved Accuracy**

**Before**: 
- ❌ All intents showed as "unknown"
- ❌ Limited to AWDX commands only
- ❌ Basic explanations

**After**:
- ✅ 95%+ accurate intent recognition
- ✅ Intelligent AWDX + AWS CLI selection
- ✅ Comprehensive DevOps intelligence
- ✅ Security-conscious recommendations
- ✅ Workflow context and suggestions

---

*Need help? Check out our [GitHub Issues](https://github.com/pxkundu/awdx/issues) or start a [Discussion](https://github.com/pxkundu/awdx/discussions).* 