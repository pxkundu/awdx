# AWDX Task Module

🚀 **High-level DevSecOps task automation and productivity commands**

The Task Module provides intelligent task automation for common DevSecOps activities with optional AI enhancement. It combines multiple AWS services into single, powerful commands to streamline your DevSecOps workflows.

## 🎯 Overview

The Task Module is designed to be a **productivity multiplier** for DevSecOps teams, offering:

- **40+ Automation Commands** - From basic security audits to complex infrastructure automation
- **AI-Enhanced Workflows** - Intelligent insights and recommendations when AI is configured
- **Multi-Service Integration** - Combines IAM, EC2, S3, RDS, Lambda, and more
- **Compliance Frameworks** - SOX, HIPAA, PCI-DSS, SOC2, ISO27001, NIST support
- **Rich Output Formats** - Table, JSON, CSV, and PDF reports
- **Graceful AI Fallback** - Works perfectly without AI configuration

## 🚀 Core Commands

### Security & Compliance
```bash
# Comprehensive security audit
awdx task security-audit --comprehensive --fix-safe

# Compliance validation
awdx task compliance-check --framework sox --output pdf

# Continuous security monitoring
awdx task security-monitor --continuous --alert

# Vulnerability scanning
awdx task vuln-scan --auto-remediate
```

### Cost Optimization
```bash
# Cost analysis and optimization
awdx task cost-optimize --auto-fix --dry-run

# Infrastructure cost analysis
awdx task infra-cost --estimate --optimize
```

### Secret Management
```bash
# Automated secret rotation
awdx task secret-rotate --auto --schedule
```

## 🔧 Service-Specific Commands

### Lambda Functions
```bash
# Lambda security audit
awdx task lambda-audit --security --permissions --runtime

# Lambda optimization
awdx task lambda-optimize --memory --timeout --cold-start

# Lambda monitoring
awdx task lambda-monitor --performance --errors --cost
```

### IAM Management
```bash
# IAM security audit
awdx task iam-audit --users --roles --policies --compliance

# IAM optimization
awdx task iam-optimize --permissions --least-privilege --rotation
```

### S3 Storage
```bash
# S3 security audit
awdx task s3-audit --buckets --policies --encryption --compliance

# S3 optimization
awdx task s3-optimize --storage --access --cost
```

### Infrastructure
```bash
# Infrastructure audit
awdx task infra-audit --templates --security --compliance

# Infrastructure drift detection
awdx task infra-drift --detect --remediate

# Template validation
awdx task template-validate --security --best-practices
```

### Containers & Kubernetes
```bash
# Container security scanning
awdx task container-scan --images --vulnerabilities --compliance

# Container optimization
awdx task container-optimize --resources --scaling --cost

# Kubernetes audit
awdx task k8s-audit --pods --services --rbac --network-policies

# Kubernetes compliance
awdx task k8s-compliance --cis --pci --sox
```

### CI/CD Pipelines
```bash
# Pipeline audit
awdx task pipeline-audit --comprehensive --fix-issues

# Pipeline optimization
awdx task pipeline-optimize --performance --cost

# Pipeline monitoring
awdx task pipeline-monitor --continuous --webhook
```

### Build & Monitoring
```bash
# Build optimization
awdx task build-optimize --cache --parallel --timeout

# Build security
awdx task build-security --scan --vulnerabilities

# Monitoring setup
awdx task monitoring-setup --auto --best-practices --alerts

# Alert configuration
awdx task alert-configure --auto --thresholds --escalation
```

### Networking
```bash
# Network audit
awdx task network-audit --vpc --subnets --security-groups --nacls

# Network optimization
awdx task network-optimize --routing --peering --cost

# Security group audit
awdx task sg-audit --rules --compliance --best-practices
```

## 🤖 AI Integration

The Task Module includes optional AI enhancement that provides:

- **Intelligent Recommendations** - AI-powered suggestions for optimization
- **Context-Aware Insights** - Understanding of your specific AWS environment
- **Automated Workflows** - Smart automation suggestions
- **Risk Assessment** - AI-enhanced security and compliance analysis

### AI Configuration
```bash
# Configure AI features
awdx ai configure

# Test AI integration
awdx ai test

# Get AI-powered suggestions
awdx ai suggest --context "I want to optimize my AWS costs"
```

## 📊 Output Formats

All task commands support multiple output formats:

```bash
# Table format (default)
awdx task security-audit --output table

# JSON format
awdx task security-audit --output json

# CSV format
awdx task security-audit --output csv

# PDF format (for compliance reports)
awdx task compliance-check --output pdf
```

## 🎯 Use Cases

### Daily DevSecOps Workflows
```bash
# Morning security check
awdx task security-audit --comprehensive

# Cost monitoring
awdx task cost-optimize --dry-run

# Compliance validation
awdx task compliance-check --framework sox
```

### Incident Response
```bash
# Quick security assessment
awdx task security-audit --comprehensive --fix-safe

# Vulnerability scanning
awdx task vuln-scan --auto-remediate

# Continuous monitoring
awdx task security-monitor --continuous --alert
```

### Infrastructure Management
```bash
# Infrastructure audit
awdx task infra-audit --templates --security

# Drift detection
awdx task infra-drift --detect --remediate

# Cost optimization
awdx task infra-cost --estimate --optimize
```

## 🔧 Configuration

### AWS Credentials
The Task Module uses your existing AWS credentials:
```bash
# Configure AWS credentials
aws configure

# Or use environment variables
export AWS_ACCESS_KEY_ID="your_key"
export AWS_SECRET_ACCESS_KEY="your_secret"
export AWS_DEFAULT_REGION="us-east-1"
```

### AI Configuration
```bash
# Interactive AI setup
awdx ai configure

# Manual AI setup
export GEMINI_API_KEY="your_gemini_api_key"
```

## 🧪 Testing

### Basic Testing
```bash
# Test task module help
awdx task --help

# Test specific command help
awdx task security-audit --help

# Test with dry-run
awdx task cost-optimize --dry-run
```

### AI Integration Testing
```bash
# Test AI configuration
awdx ai test

# Test AI suggestions
awdx ai suggest --context "security audit"
```

## 📚 Documentation

- **Main Documentation**: [Task Module Summary](../../docs/TASK_MODULE_SUMMARY.md)
- **AI Features**: [AI Features Documentation](../../docs/AI_FEATURES.md)
- **MCP Integration**: [MCP Integration Documentation](../../docs/MCP_INTEGRATION.md)

## 🚀 Examples

### Complete DevSecOps Workflow
```bash
# 1. Security audit
awdx task security-audit --comprehensive --fix-safe

# 2. Cost optimization
awdx task cost-optimize --auto-fix --dry-run

# 3. Compliance check
awdx task compliance-check --framework sox --output pdf

# 4. Continuous monitoring
awdx task security-monitor --continuous --alert
```

### Infrastructure Automation
```bash
# 1. Template validation
awdx task template-validate --security --best-practices

# 2. Infrastructure audit
awdx task infra-audit --templates --security --compliance

# 3. Drift detection
awdx task infra-drift --detect --remediate

# 4. Cost analysis
awdx task infra-cost --estimate --optimize --forecast
```

### Container Security
```bash
# 1. Container scanning
awdx task container-scan --images --vulnerabilities --compliance

# 2. Container optimization
awdx task container-optimize --resources --scaling --cost

# 3. Kubernetes audit
awdx task k8s-audit --pods --services --rbac --network-policies

# 4. Kubernetes compliance
awdx task k8s-compliance --cis --pci --sox
```

## 💡 Best Practices

1. **Start with Dry-Run**: Always use `--dry-run` first to preview changes
2. **Enable AI**: Configure AI for enhanced insights and recommendations
3. **Use Comprehensive Mode**: Use `--comprehensive` for thorough analysis
4. **Regular Monitoring**: Set up continuous monitoring for proactive issue detection
5. **Compliance Reports**: Generate PDF reports for compliance documentation
6. **Auto-Fix Carefully**: Review auto-fixes before applying in production

## 🐛 Troubleshooting

### Common Issues

**AWS Credentials Not Found**
```bash
# Configure AWS credentials
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID="your_key"
export AWS_SECRET_ACCESS_KEY="your_secret"
```

**AI Features Not Available**
```bash
# Configure AI
awdx ai configure

# Check AI status
awdx ai test
```

**Permission Errors**
```bash
# Check IAM permissions
aws iam get-user

# Verify profile
awdx profile validate
```

## 📈 Performance Tips

1. **Use Specific Regions**: Specify `--region` for faster execution
2. **Enable Caching**: AI responses are cached for better performance
3. **Batch Operations**: Use comprehensive mode for multiple services
4. **Parallel Processing**: Some commands use parallel processing for speed

## 🔄 Updates

The Task Module is actively developed with new features and improvements:

- **New Commands**: Regular addition of new automation commands
- **AI Enhancement**: Continuous improvement of AI integration
- **Performance**: Ongoing optimization for faster execution
- **Compliance**: Regular updates to compliance frameworks

---

**AWDX Task Module** - Making DevSecOps automation simple, intelligent, and efficient! 🚀 