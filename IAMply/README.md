# IAMply - AWS IAM Management Module

A comprehensive IAM management module for AWDX with real-world DevSecOps use cases. Provides commands for IAM user, role, policy, and access management with security best practices and innovative automation features.

## 🚀 Features

### Standard IAM Management
- **User Management**: List, analyze, and manage IAM users with security insights
- **Role Management**: Analyze IAM roles with trust relationship assessment
- **Policy Management**: Review IAM policies with permission analysis
- **Group Management**: Manage IAM groups and member analysis

### Advanced Security & Compliance
- **Security Audit**: Comprehensive IAM security audit with risk assessment
- **Access Analysis**: Analyze effective permissions and access patterns
- **Compliance Checking**: Check IAM compliance with CIS, SOC2, and PCI standards
- **Smart Recommendations**: AI-powered recommendations and automation

### Data & Reporting
- **Data Export**: Export IAM data in JSON/CSV formats for analysis
- **Comprehensive Help**: Built-in help system with best practices

## 📋 Commands

### Basic IAM Management

#### List and Manage Users
```bash
# List all IAM users
awdx iam users

# Show detailed user information
awdx iam users --detailed

# Show only inactive users
awdx iam users --inactive
```

#### Analyze IAM Roles
```bash
# List all IAM roles
awdx iam roles

# Show detailed role information
awdx iam roles --detailed

# Show only unused roles
awdx iam roles --unused
```

#### Review IAM Policies
```bash
# List all IAM policies
awdx iam policies

# Show detailed policy information
awdx iam policies --detailed

# Filter by scope (All/Local/AWS)
awdx iam policies --scope Local
```

#### Manage IAM Groups
```bash
# List all IAM groups
awdx iam groups

# Show detailed group information
awdx iam groups --detailed
```

### Security & Compliance

#### Comprehensive Security Audit
```bash
# Run full security audit
awdx iam audit

# Export audit results to JSON
awdx iam audit --export audit_results.json

# Export audit results to CSV
awdx iam audit --export audit_results.csv
```

#### Analyze Access Patterns
```bash
# Analyze all entities
awdx iam access

# Analyze specific user/role
awdx iam access --entity myuser

# Analyze specific AWS service
awdx iam access --service s3
```

#### Check Compliance
```bash
# Check CIS compliance
awdx iam compliance --standard CIS

# Check SOC2 compliance
awdx iam compliance --standard SOC2

# Check PCI compliance
awdx iam compliance --standard PCI
```

#### Smart Recommendations
```bash
# Get smart recommendations
awdx iam smart

# Show what would be changed (dry run)
awdx iam smart --auto-fix --dry-run

# Apply safe fixes automatically
awdx iam smart --auto-fix --no-dry-run
```

### Data Export

#### Export IAM Data
```bash
# Export to JSON (default)
awdx iam export

# Export to CSV
awdx iam export --format csv

# Custom output filename
awdx iam export --output my_iam_data

# Export without policy details
awdx iam export --no-include-policies

# Export without permission analysis
awdx iam export --no-include-permissions
```

### Help & Documentation
```bash
# Show comprehensive help
awdx iam help
```

## 🔍 Real-World Use Cases

### 1. Security Compliance Audits
**Scenario**: Quarterly security audit for SOC2 compliance
```bash
# Run comprehensive audit
awdx iam audit --export quarterly_audit.json

# Check specific compliance standards
awdx iam compliance --standard SOC2

# Generate compliance report
awdx iam export --format csv --output compliance_report
```

### 2. Access Review and Cleanup
**Scenario**: Annual access review and cleanup
```bash
# Find unused entities
awdx iam users --inactive
awdx iam roles --unused

# Analyze access patterns
awdx iam access --entity specific_user

# Get smart recommendations for cleanup
awdx iam smart --auto-fix --dry-run
```

### 3. Policy Optimization
**Scenario**: Optimize overly permissive policies
```bash
# Review all policies
awdx iam policies --detailed

# Analyze specific policy permissions
awdx iam access --service ec2

# Get recommendations for policy improvements
awdx iam smart
```

### 4. Incident Response
**Scenario**: Security incident investigation
```bash
# Quick security audit
awdx iam audit

# Export current state for analysis
awdx iam export --format json --output incident_analysis

# Check for privilege escalation risks
awdx iam access
```

### 5. DevOps Automation
**Scenario**: Automated IAM management in CI/CD
```bash
# Pre-deployment security check
awdx iam audit --export pre_deploy_check.json

# Compliance validation
awdx iam compliance --standard CIS

# Post-deployment verification
awdx iam access --entity deployment_role
```

## 🛡️ Security Features

### Risk Assessment
- **Critical Issues**: Root account usage, excessive permissions
- **High Issues**: Missing MFA, wildcard permissions
- **Medium Issues**: Old access keys, unused credentials
- **Low Issues**: Unused entities, minor policy issues

### Compliance Standards
- **CIS AWS Foundations**: Industry-standard security benchmarks
- **SOC2**: Service Organization Control 2 compliance
- **PCI DSS**: Payment Card Industry compliance

### Smart Automation
- **Auto-fix Capabilities**: Safe automated remediation
- **Dry-run Mode**: Preview changes before applying
- **Risk-based Recommendations**: Prioritized by security impact

## 📊 Output Examples

### Security Audit Output
```
🔍 Starting comprehensive IAM security audit...
👤 Profile: default

🔍 Checking root account usage...
   ✅ Using IAM user/role

🔍 Checking MFA configuration...
   ❌ HIGH: 3 users without MFA
      - user1
      - user2
      - user3

🔍 Checking access key age...
   ⚠️ MEDIUM: 2 old access keys found
      - admin:AKIA... (450 days)
      - dev:AKIA... (380 days)

🔍 Audit Summary:
  🔴 Critical Issues: 0
  🟠 High Issues: 1
  🟡 Medium Issues: 1
  🟢 Low Issues: 0
```

### Access Analysis Output
```
🔑 Analyzing IAM access patterns...
👤 Profile: default

📊 Analyzing 15 entities...

👤 admin (user)
   ⚡ Total Permissions: 45
   🎯 Privileged: 12
   ❌ Wildcards: 3
      🎯❌ iam:*
      🎯❌ s3:*
      ec2:DescribeInstances

🎭 deployment-role (role)
   ⚡ Total Permissions: 28
   🎯 Privileged: 8
   ❌ Wildcards: 1
      🎯❌ ec2:*

📊 Access Analysis Summary:
  📊 Total Entities: 15
  ⚡ Total Permissions: 342
  🎯 Privileged Permissions: 67
  ❌ Wildcard Permissions: 12
```

## 💡 Best Practices

### Security Best Practices
- ✅ Use least privilege principle
- ✅ Enable MFA for all users
- ✅ Rotate access keys every 90 days
- ✅ Remove unused IAM entities
- ✅ Avoid wildcard permissions
- ✅ Use IAM Access Analyzer
- ✅ Monitor IAM changes
- ✅ Regular security audits

### Common Mistakes to Avoid
- ❌ Using root account for daily tasks
- ❌ Sharing access keys
- ❌ Overly permissive policies
- ❌ Long-lived access keys
- ❌ Not using MFA
- ❌ Ignoring unused entities

## 🔧 Advanced Features

### Automated Remediation
The `smart` command can automatically apply safe fixes:
- Remove unused users and roles
- Clean up orphaned policies
- Generate rotation schedules for access keys

### Compliance Automation
- Automated compliance checking against industry standards
- Export-ready compliance reports
- Integration with compliance frameworks

### Permission Analysis
- Deep permission analysis with risk scoring
- Service-specific permission reviews
- Privilege escalation detection

## 📈 Integration Examples

### CI/CD Pipeline Integration
```yaml
# Example GitHub Actions workflow
- name: IAM Security Check
  run: |
    awdx iam audit --export security_check.json
    awdx iam compliance --standard CIS
    
- name: Fail on Critical Issues
  run: |
    if grep -q "Critical Issues: [1-9]" security_check.json; then
      echo "Critical security issues found!"
      exit 1
    fi
```

### Monitoring and Alerting
```bash
# Daily security check script
#!/bin/bash
awdx iam audit --export daily_audit.json

# Check for new issues
if [ $(jq '.critical_issues | length' daily_audit.json) -gt 0 ]; then
    echo "Critical IAM issues detected!" | mail -s "IAM Security Alert" admin@company.com
fi
```

## 🎯 Use Cases by Role

### Security Engineers
- Regular security audits and compliance checks
- Incident response and investigation
- Policy optimization and risk assessment

### DevOps Engineers
- CI/CD pipeline security validation
- Automated IAM management
- Deployment role verification

### Compliance Officers
- Automated compliance reporting
- Audit trail generation
- Policy compliance validation

### System Administrators
- Daily IAM management tasks
- Access review and cleanup
- User lifecycle management

## 📚 Additional Resources

- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [CIS AWS Foundations Benchmark](https://www.cisecurity.org/benchmark/amazon_web_services/)
- [AWS IAM Access Analyzer](https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html)

---

**IAMply** - Making IAM management simple, secure, and smart! 🔐 