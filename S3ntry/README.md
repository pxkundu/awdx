# S3ntry - AWS S3 Security and Compliance Module

🪣 **Comprehensive S3 Bucket Security with Intelligent Automation**

S3ntry is a powerful S3 security module for AWDX that provides comprehensive bucket security assessment, compliance validation, data protection analysis, and automated remediation with real-world DevSecOps use cases.

## 🚀 Features

### Core S3 Security
- **Security Audit**: Comprehensive S3 bucket security assessment
- **Targeted Scanning**: Specific security issue detection and analysis
- **Compliance Validation**: Multi-framework compliance checking
- **Access Monitoring**: Real-time access pattern analysis

### Advanced DevSecOps Features
- **Smart Remediation**: Automated issue resolution with risk-based prioritization
- **Intelligent Recommendations**: AI-powered optimization suggestions
- **Sensitive Data Detection**: Proactive detection of potentially sensitive data
- **Multi-Service Integration**: S3, CloudTrail, Config, Security Hub

## 📋 Commands

### Core Commands

#### `awdx s3 audit`
Comprehensive S3 bucket security audit.

```bash
# Basic audit
awdx s3 audit

# Region-specific audit
awdx s3 audit --region us-east-1

# Specific bucket audit
awdx s3 audit --bucket my-bucket-name

# Include object analysis
awdx s3 audit --include-objects

# Export results
awdx s3 audit --output json
```

**Options:**
- `--profile, -p`: AWS profile to use
- `--region, -r`: AWS region to scan
- `--bucket, -b`: Specific bucket to audit
- `--output, -o`: Output format (table, json, csv)
- `--include-objects`: Include object-level analysis
- `--risk-threshold`: Minimum risk level to report

#### `awdx s3 scan`
Scan S3 buckets for specific security issues.

```bash
# Basic scan
awdx s3 scan

# Scan specific types
awdx s3 scan --type public,encryption,versioning

# Include sensitive data detection
awdx s3 scan --include-sensitive

# Export results
awdx s3 scan --output csv
```

**Options:**
- `--profile, -p`: AWS profile to use
- `--region, -r`: AWS region to scan
- `--bucket, -b`: Specific bucket to scan
- `--type, -t`: Scan type (all, public, encryption, versioning, logging)
- `--output, -o`: Output format (table, json, csv)
- `--include-sensitive`: Include potentially sensitive data detection

#### `awdx s3 compliance`
Check S3 compliance against various frameworks.

```bash
# All frameworks
awdx s3 compliance

# Specific framework
awdx s3 compliance --framework pci

# Export compliance report
awdx s3 compliance --output csv
```

**Options:**
- `--profile, -p`: AWS profile to use
- `--region, -r`: AWS region
- `--framework, -f`: Compliance framework (all, sox, pci, hipaa, gdpr)
- `--output, -o`: Output format (table, json, csv)

#### `awdx s3 monitor`
Monitor S3 bucket access patterns and security events.

```bash
# Basic monitoring
awdx s3 monitor

# Custom time range
awdx s3 monitor --days 60

# Specific bucket monitoring
awdx s3 monitor --bucket my-bucket-name
```

**Options:**
- `--profile, -p`: AWS profile to use
- `--region, -r`: AWS region
- `--days, -d`: Number of days to look back (default: 30)
- `--bucket, -b`: Specific bucket to monitor
- `--output, -o`: Output format (table, json, csv)

### Advanced Commands

#### `awdx s3 remediate`
Automated remediation of S3 security issues.

```bash
# Dry run remediation
awdx s3 remediate --dry-run

# Auto-fix issues
awdx s3 remediate --auto-fix

# Risk-based remediation
awdx s3 remediate --risk-threshold MEDIUM
```

**Options:**
- `--profile, -p`: AWS profile to use
- `--region, -r`: AWS region
- `--bucket, -b`: Specific bucket to remediate
- `--auto-fix`: Automatically fix issues where possible
- `--dry-run`: Show what would be fixed without doing it
- `--risk-threshold`: Minimum risk level to remediate

#### `awdx s3 recommend`
Get intelligent recommendations for S3 optimization.

```bash
# Security recommendations
awdx s3 recommend --include-security

# Cost optimization
awdx s3 recommend --include-cost

# All recommendations
awdx s3 recommend --include-security --include-cost
```

**Options:**
- `--profile, -p`: AWS profile to use
- `--region, -r`: AWS region
- `--include-cost`: Include cost optimization recommendations
- `--include-security`: Include security recommendations
- `--output, -o`: Output format (table, json, csv)

#### `awdx s3 export`
Export S3 bucket data for analysis and reporting.

```bash
# JSON export
awdx s3 export --format json

# CSV export with metadata
awdx s3 export --format csv --include-metadata

# Export to file
awdx s3 export --output s3-report.json
```

**Options:**
- `--profile, -p`: AWS profile to use
- `--region, -r`: AWS region
- `--format, -f`: Export format (json, csv, yaml)
- `--output, -o`: Output file path
- `--include-metadata`: Include bucket metadata
- `--include-objects`: Include object information

#### `awdx s3 help`
Show detailed help for S3ntry commands.

```bash
awdx s3 help
```

## 🎯 Real-World DevSecOps Use Cases

### 1. **Data Breach Response**
```bash
# Rapid assessment during incident
awdx s3 audit --output json

# Check for public buckets
awdx s3 scan --type public

# Force remediation of critical issues
awdx s3 remediate --auto-fix --risk-threshold CRITICAL

# Monitor for unusual access patterns
awdx s3 monitor --days 7
```

### 2. **Compliance Audits**
```bash
# Generate compliance report
awdx s3 compliance --framework all --output csv

# Export detailed bucket inventory
awdx s3 export --format json --include-metadata

# Remediate compliance issues
awdx s3 remediate --dry-run
```

### 3. **CI/CD Security Integration**
```bash
# Pre-deployment security check
awdx s3 audit --bucket production-data --risk-threshold HIGH

# Automated remediation in pipeline
awdx s3 remediate --auto-fix --risk-threshold HIGH

# Post-deployment compliance validation
awdx s3 compliance --framework pci
```

### 4. **Cost Optimization**
```bash
# Get optimization recommendations
awdx s3 recommend --include-cost

# Analyze bucket usage patterns
awdx s3 monitor --days 30

# Export for cost analysis
awdx s3 export --format csv
```

### 5. **Multi-Environment Management**
```bash
# Development environment
awdx s3 audit --profile dev --region us-east-1

# Production environment
awdx s3 audit --profile prod --region us-west-2

# Compare environments
awdx s3 export --profile dev --output dev-s3.json
awdx s3 export --profile prod --output prod-s3.json
```

## 🔧 Advanced Features

### Intelligent Automation
- **Risk-based Prioritization**: Automatically prioritize remediation based on risk level
- **Smart Scanning**: Intelligent detection of security issues and compliance gaps
- **Anomaly Detection**: Proactive detection of unusual access patterns
- **Automated Remediation**: Self-healing capabilities with safety checks

### Multi-Service Integration
- **AWS S3**: Primary bucket security and configuration analysis
- **CloudTrail**: Access pattern analysis and audit trails
- **AWS Config**: Configuration compliance and drift detection
- **Security Hub**: Security findings integration and correlation

### Compliance Frameworks
- **SOX**: Financial reporting compliance
- **PCI DSS**: Payment card industry standards
- **HIPAA**: Healthcare data protection
- **GDPR**: European data protection regulation

## 📊 Monitoring and Alerting

### Key Metrics
- Public bucket detection and remediation
- Encryption status and configuration
- Access pattern anomalies
- Compliance violation counts
- Remediation action success rates

### Alert Thresholds
- Public bucket detection
- Unencrypted bucket identification
- Unusual access patterns
- Compliance violations
- Failed remediation attempts

## 🔒 Security Best Practices

### S3 Bucket Security
- ✅ Block public access by default
- ✅ Enable encryption for all data
- ✅ Use KMS encryption for sensitive data
- ✅ Enable versioning for data protection
- ❌ Never use public read/write permissions
- ✅ Configure comprehensive logging and monitoring

### Access Control
- **Principle of Least Privilege**: Grant minimum required access
- **Bucket Policies**: Use bucket policies for fine-grained control
- **IAM Roles**: Use IAM roles instead of user access
- **Access Logging**: Enable comprehensive access logging

### Data Protection
- **Encryption at Rest**: Enable server-side encryption
- **Encryption in Transit**: Use HTTPS for all S3 operations
- **Versioning**: Enable versioning for data protection
- **Lifecycle Policies**: Implement intelligent data lifecycle management

## 🚀 Innovation Highlights

### Smart Automation
- **Risk-based Prioritization**: Automatically prioritize actions based on security risk
- **Intelligent Analysis**: AI-powered analysis of access patterns and security trends
- **Automated Remediation**: Self-healing with safety checks and dry-run capabilities
- **Proactive Detection**: Early detection of security issues and compliance gaps

### DevSecOps Integration
- **CI/CD Pipeline Integration**: Seamless integration with deployment pipelines
- **Monitoring Integration**: Integration with existing monitoring and alerting systems
- **Compliance Automation**: Automated compliance reporting for audits
- **Security Tool Integration**: Integration with security tools and SIEM systems

### Real-World Scenarios
- **Data Breach Response**: Rapid assessment and remediation during security incidents
- **Compliance Audits**: Automated compliance validation and reporting
- **Cost Optimization**: Intelligent cost optimization recommendations
- **Multi-Environment Management**: Consistent security across environments

## 📈 Performance and Scalability

### Optimization Features
- **Parallel Processing**: Concurrent scanning across multiple buckets
- **Caching**: Intelligent caching of frequently accessed data
- **Batch Operations**: Efficient batch processing for large environments
- **Incremental Updates**: Only process changed data

### Resource Management
- **Memory Efficient**: Optimized memory usage for large environments
- **API Rate Limiting**: Respectful API usage with built-in rate limiting
- **Error Handling**: Robust error handling and retry mechanisms
- **Progress Tracking**: Real-time progress updates for long-running operations

## 🔧 Configuration

### Environment Variables
```bash
# AWS Configuration
AWS_PROFILE=production
AWS_REGION=us-west-2

# S3ntry Configuration
S3NTRY_RISK_THRESHOLD=HIGH
S3NTRY_AUTO_FIX=false
S3NTRY_DRY_RUN=true
```

### Configuration File
```yaml
# ~/.awdx/s3ntry.yaml
defaults:
  risk_threshold: MEDIUM
  auto_fix: false
  dry_run: true

monitoring:
  lookback_days: 30
  alert_threshold: 1000

compliance:
  frameworks: [sox, pci, hipaa, gdpr]
  auto_remediate: false
```

## 🛠️ Troubleshooting

### Common Issues

#### Access Denied Errors
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify IAM permissions
awdx s3 audit --dry-run
```

#### Public Access Issues
```bash
# Check bucket public access
awdx s3 scan --type public

# Remediate public access
awdx s3 remediate --auto-fix --risk-threshold CRITICAL
```

#### Compliance Violations
```bash
# Generate compliance report
awdx s3 compliance --framework all

# Remediate issues
awdx s3 remediate --dry-run
```

### Debug Mode
```bash
# Enable debug logging
export AWS_SDK_LOAD_CONFIG=1
export AWS_LOG_LEVEL=debug

# Run with verbose output
awdx s3 audit --output json
```

## 📚 Examples

### Complete Workflow Example
```bash
# 1. Audit S3 buckets
awdx s3 audit --region us-east-1 --output json

# 2. Check compliance
awdx s3 compliance --framework pci

# 3. Get recommendations
awdx s3 recommend --include-security --include-cost

# 4. Remediate issues
awdx s3 remediate --dry-run

# 5. Monitor changes
awdx s3 monitor --days 1

# 6. Export report
awdx s3 export --format csv --output s3-audit.csv
```

### Automated Script Example
```bash
#!/bin/bash
# Daily S3 security check

echo "🪣 Starting daily S3 security audit..."

# Audit and analyze
awdx s3 audit --output json > daily-audit.json

# Check compliance
awdx s3 compliance --framework all > compliance-report.json

# Get recommendations
awdx s3 recommend --include-security > recommendations.json

# Auto-remediate high-risk issues
awdx s3 remediate --auto-fix --risk-threshold HIGH

# Generate summary report
awdx s3 export --format csv --output daily-summary.csv

echo "✅ Daily S3 security audit completed"
```

## 🤝 Contributing

We welcome contributions to S3ntry! Please see our contributing guidelines for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

🪣 **Secure your S3 buckets with intelligent automation!** 