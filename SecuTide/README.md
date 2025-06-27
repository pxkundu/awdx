# SecuTide - AWS Security Assessment and Remediation Module

🛡️ **SecuTide** is a comprehensive security assessment and remediation module for AWDX, providing advanced DevSecOps capabilities for AWS environments.

## Overview

SecuTide offers both standard security assessments and innovative DevSecOps features including:

- **Comprehensive Security Posture Assessment** across all AWS services
- **Vulnerability Scanning** with service-specific checks
- **Incident Response** investigation and analysis
- **Threat Detection** using AWS security services
- **Compliance Assessment** for various standards (CIS, SOC2, PCI, HIPAA)
- **Smart Remediation** with automated fixes
- **Data Export** in multiple formats (JSON, CSV, HTML)

## Commands

### 1. Security Posture Assessment

Comprehensive security posture assessment across AWS services.

```bash
# Basic posture assessment
awdx security posture

# Assessment with specific profile and region
awdx security posture --profile prod --region us-east-1

# Export results to JSON
awdx security posture --export posture_report.json

# Export results to CSV
awdx security posture --export posture_report.csv
```

**Features:**
- Network security assessment (security groups, subnets)
- Storage security (S3 encryption, public access)
- Compute security (EC2 instances, IMDSv2)
- Database security (RDS encryption, public access)
- Identity and access management (root usage, MFA)
- Monitoring and logging (CloudTrail, AWS Config)

### 2. Vulnerability Scanning

Scan for security vulnerabilities across AWS services.

```bash
# Scan all services
awdx security vulnerabilities

# Scan specific service
awdx security vulnerabilities --service ec2
awdx security vulnerabilities --service s3
awdx security vulnerabilities --service rds
awdx security vulnerabilities --service iam

# Scan with export
awdx security vulnerabilities --service s3 --export vulns.csv
```

**Vulnerabilities Detected:**
- **EC2**: Outdated AMIs, missing detailed monitoring
- **S3**: Missing versioning, no access logging
- **RDS**: No automated backups, missing deletion protection
- **IAM**: Old access keys, unused users

### 3. Incident Response

Perform incident response investigation and analysis.

```bash
# General incident investigation
awdx security incident

# Specific incident types
awdx security incident --type breach
awdx security incident --type malware
awdx security incident --type unauthorized

# Export investigation results
awdx security incident --type breach --export incident_report.json
```

**Investigation Areas:**
- CloudTrail log analysis for suspicious activities
- GuardDuty findings review
- Security Hub findings analysis
- Network traffic pattern analysis
- Resource access pattern analysis

### 4. Threat Detection

Detect and analyze security threats across AWS environment.

```bash
# Default threat detection (last 7 days)
awdx security threats

# Custom time period
awdx security threats --days 30

# Export threat analysis
awdx security threats --export threats.json
```

**Threat Sources:**
- GuardDuty findings
- Security Hub findings
- Network threat analysis
- Access threat analysis

### 5. Compliance Assessment

Assess compliance with security standards and frameworks.

```bash
# CIS compliance assessment
awdx security compliance --standard CIS

# Export compliance report
awdx security compliance --export compliance_report.csv
```

**Supported Standards:**
- **CIS AWS Foundations Benchmark**
- SOC2 (planned)
- PCI DSS (planned)
- HIPAA (planned)

### 6. Smart Remediation

Smart security remediation with automated fixes and recommendations.

```bash
# Preview remediations (dry run)
awdx security remediate --dry-run

# Apply remediations automatically
awdx security remediate --auto

# Region-specific remediation
awdx security remediate --region us-west-2
```

**Remediation Types:**
- **S3**: Enable encryption, block public access
- **Security Groups**: Restrict overly permissive rules
- **IAM**: Enable MFA, rotate access keys
- **RDS**: Disable public access, enable encryption

### 7. Data Export

Export comprehensive security data and reports.

```bash
# Export to JSON
awdx security export --format json

# Export to CSV
awdx security export --format csv --output security_data

# Export to HTML
awdx security export --format html --findings --compliance
```

**Export Formats:**
- **JSON**: Programmatic access and integration
- **CSV**: Spreadsheet analysis
- **HTML**: Stakeholder reports

### 8. Help

Show detailed help and examples.

```bash
awdx security help
```

## Real-World DevSecOps Use Cases

### 1. Daily Security Operations

```bash
# Daily security check
awdx security posture --export daily_report.json

# Review high-priority findings
awdx security vulnerabilities --service ec2
```

### 2. Incident Response Workflow

```bash
# Initial investigation
awdx security incident --type breach --export incident.json

# Threat analysis
awdx security threats --days 7 --export threats.json

# Remediation planning
awdx security remediate --dry-run
```

### 3. Compliance Reporting

```bash
# Monthly compliance assessment
awdx security compliance --standard CIS --export compliance.csv

# Executive summary
awdx security export --format html --output executive_report
```

### 4. CI/CD Integration

```bash
# Pre-deployment security check
awdx security posture --region us-east-1

# Post-deployment vulnerability scan
awdx security vulnerabilities --service ec2 --export pre_deploy.json
```

### 5. Automated Remediation

```bash
# Preview changes
awdx security remediate --dry-run

# Apply critical fixes
awdx security remediate --auto
```

## Advanced Features

### 1. Risk Scoring

SecuTide calculates risk scores based on:
- Severity of findings
- Number of affected resources
- Compliance violations
- Threat indicators

### 2. Intelligent Recommendations

Each finding includes:
- Detailed impact analysis
- Specific remediation steps
- Best practice guidance
- Priority ranking

### 3. Multi-Format Export

Export data in formats suitable for:
- **Security teams**: JSON for automation
- **Management**: HTML for presentations
- **Compliance**: CSV for audits
- **Integration**: JSON for SIEM systems

### 4. Automated Remediation

Smart remediation features:
- **Dry-run mode**: Preview changes before applying
- **Auto-apply**: Automatically fix common issues
- **Safety checks**: Prevent service disruption
- **Audit trail**: Document all changes

## Security Best Practices

### 1. Regular Assessments

```bash
# Weekly security posture assessment
awdx security posture --export weekly_report.json

# Monthly compliance check
awdx security compliance --standard CIS
```

### 2. Incident Preparedness

```bash
# Document incident response procedures
awdx security incident --type breach --export procedures.json

# Regular threat hunting
awdx security threats --days 30
```

### 3. Continuous Monitoring

```bash
# Daily vulnerability scans
awdx security vulnerabilities --service ec2

# Weekly remediation reviews
awdx security remediate --dry-run
```

### 4. Compliance Management

```bash
# Regular compliance assessments
awdx security compliance --standard CIS --export compliance.csv

# Executive reporting
awdx security export --format html --output executive_report
```

## Integration Examples

### 1. GitHub Actions

```yaml
name: Security Assessment
on: [push, pull_request]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Security Posture Assessment
        run: |
          awdx security posture --export security_report.json
      - name: Upload Security Report
        uses: actions/upload-artifact@v2
        with:
          name: security-report
          path: security_report.json
```

### 2. Jenkins Pipeline

```groovy
pipeline {
    agent any
    stages {
        stage('Security Assessment') {
            steps {
                sh 'awdx security posture --export security_report.json'
                sh 'awdx security vulnerabilities --service ec2'
            }
        }
        stage('Remediation') {
            steps {
                sh 'awdx security remediate --dry-run'
            }
        }
    }
}
```

### 3. AWS Lambda

```python
import json
import subprocess

def lambda_handler(event, context):
    # Run security assessment
    result = subprocess.run([
        'awdx', 'security', 'posture', 
        '--export', '/tmp/security_report.json'
    ], capture_output=True, text=True)
    
    # Process results
    with open('/tmp/security_report.json', 'r') as f:
        report = json.load(f)
    
    return {
        'statusCode': 200,
        'body': json.dumps(report)
    }
```

## Configuration

### AWS Credentials

SecuTide uses standard AWS credential methods:

```bash
# AWS CLI configuration
aws configure

# Environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1

# IAM roles (recommended)
# Configure IAM role for EC2 instances or ECS tasks
```

### Required Permissions

Minimum IAM permissions for SecuTide:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:Describe*",
                "s3:List*",
                "s3:Get*",
                "rds:Describe*",
                "iam:List*",
                "iam:Get*",
                "cloudtrail:List*",
                "cloudtrail:LookupEvents",
                "config:Describe*",
                "guardduty:List*",
                "guardduty:Get*",
                "securityhub:Get*",
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

## Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   # Check AWS credentials
   aws sts get-caller-identity
   
   # Verify IAM permissions
   awdx security posture --profile your-profile
   ```

2. **Service Not Available**
   ```bash
   # Check if service is enabled in region
   aws guardduty list-detectors --region us-east-1
   ```

3. **Export Failures**
   ```bash
   # Check file permissions
   ls -la /path/to/export/directory
   
   # Use absolute paths
   awdx security export --output /tmp/security_report
   ```

### Debug Mode

Enable debug output for troubleshooting:

```bash
# Set debug environment variable
export AWS_DEBUG=true

# Run with verbose output
awdx security posture --profile debug
```
---

**SecuTide** - Making AWS security assessment and remediation simple, powerful, and DevSecOps-friendly! 🛡️ 