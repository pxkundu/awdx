# awdx

**awdx** (AWS DevOps X) is a next-generation, human-friendly CLI tool for AWS DevSecOps. It helps you manage, automate, and secure your AWS environment with simple, interactive commands and smart suggestions.

![AWDX Banner](https://raw.githubusercontent.com/pxkundu/awdx/development/assests/AWDX.png)

---

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Modules](#modules)
- [Future Plans](#future-plans)
- [Project Status](#project-status)

---

## Features
- **Profile Management:** Create, switch, and validate AWS profiles interactively
- **Cost Intelligence:** Advanced cost analysis with anomaly detection and forecasting
- **IAM Management:** Comprehensive IAM security audit and compliance checking
- **S3 Security:** Complete S3 bucket security assessment and compliance monitoring
- **Secret Management:** Automated secret discovery, rotation, and compliance
- **Security Assessment:** Comprehensive security posture and vulnerability scanning
- **Smart Suggestions:** Receive actionable best-practice tips after every action
- **Human-Friendly CLI:** Simple, memorable commands and interactive prompts
- **Future:** AI/NLP-powered natural language commands

---

## Requirements
- Python 3.8+
- [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [typer](https://typer.tiangolo.com/)

---

## Installation

### From Source
```bash
pip install .
```

### From PyPI
```bash
pip install awdx
```

📦 **Available on PyPI:** [awdx on PyPI](https://pypi.org/project/awdx/)

---

## Quick Start

Show help and available commands:
```bash
awdx --help
```

---

## Modules

### Profile Management
Manage AWS profiles with security best practices and validation.

![Profile Management Commands](https://raw.githubusercontent.com/pxkundu/awdx/development/assests/AWDX_PROFILE_HELP.png)

```bash
# List all profiles
awdx profile list
👤 Found 3 profiles:
🎯 👤 default (current)
👤 devops
👤 prod

# Switch profiles
awdx profile switch devops
✅ To switch profile, run:
  export AWS_PROFILE=devops

# Validate credentials
awdx profile validate devops
✅ Profile 'devops' is valid. Account: 123456789012, ARN: arn:aws:iam::123456789012:user/devops
```

📖 **Full Documentation:** [Profilyze Module README](https://github.com/pxkundu/awdx/blob/development/Profilyze/DESIGN.md)

### Cost Analysis
Monitor, analyze, and optimize AWS spending with intelligent insights.

![Cost Management Commands](https://raw.githubusercontent.com/pxkundu/awdx/development/assests/AWDX_COST_HELP.png)

```bash
# Get cost summary
awdx cost summary
💰 Total Cost: $1,234.56
📊 Top 10 Services by Cost:
   1. Amazon EC2                    $567.89
   2. Amazon S3                     $234.56
   3. Amazon RDS                    $123.45

# Detect anomalies
awdx cost anomaly --threshold 2.5
🔍 Detecting cost anomalies for the last 30 days...
📊 Average daily cost: $123.45
📈 Standard deviation: $45.67
✅ No significant anomalies detected!

# Forecast costs
awdx cost forecast --months 3
🔮 Forecasting costs for the next 3 months...
📈 Trend direction: Upward
📊 Monthly change: $45.67
🎯 Trend confidence: 85.2%
```

📖 **Full Documentation:** [Costlyzer Module README](https://github.com/pxkundu/awdx/tree/development/Costlyzer)

### IAM Management
Comprehensive IAM security audit, compliance checking, and smart automation.

![IAM Management Commands](https://raw.githubusercontent.com/pxkundu/awdx/development/assests/AWDX_IAM_HELP.png)

```bash
# Security audit
awdx iam audit
🔍 Starting comprehensive IAM security audit...
🔍 Checking root account usage...
   ✅ Using IAM user/role
🔍 Checking MFA configuration...
   ❌ HIGH: 3 users without MFA
🔍 Audit Summary:
  🔴 Critical Issues: 0
  🟠 High Issues: 1
  🟡 Medium Issues: 1

# Analyze access patterns
awdx iam access
🔑 Analyzing IAM access patterns...
👤 admin (user)
   ⚡ Total Permissions: 45
   🎯 Privileged: 12
   ❌ Wildcards: 3

# Smart recommendations
awdx iam smart --auto-fix --dry-run
🚀 Generating smart IAM recommendations...
1. 🔴 Remove unused users 🤖
2. 🟠 Rotate old access keys 👤
3. 🔴 Review wildcard permissions 👤
```

📖 **Full Documentation:** [IAMply Module README](https://github.com/pxkundu/awdx/tree/development/IAMply)

### S3 Security & Compliance
Complete S3 bucket security assessment, compliance monitoring, and automated remediation.

![S3 Security Commands](https://raw.githubusercontent.com/pxkundu/awdx/development/assests/AWDX_S3_HELP.png)

```bash
# Comprehensive S3 audit
awdx s3 audit
🪣 Starting comprehensive S3 security audit...
🔍 Checking bucket configurations...
   ✅ Encryption: Enabled
   ❌ HIGH: Public access detected
🔍 Audit Summary:
  🔴 Critical Issues: 0
  🟠 High Issues: 2
  🟡 Medium Issues: 3

# Scan for vulnerabilities
awdx s3 scan --type public
🔍 Scanning for public S3 buckets...
🚨 Found 2 publicly accessible buckets:
   - my-public-bucket (HIGH RISK)
   - test-bucket (MEDIUM RISK)

# Compliance assessment
awdx s3 compliance --framework sox
📋 Assessing SOX compliance for S3...
✅ Encryption controls: PASS
❌ Access logging: FAIL
✅ Versioning: PASS
```

📖 **Full Documentation:** [S3ntry Module README](https://github.com/pxkundu/awdx/tree/development/S3ntry)

### Secret Management
Automated secret discovery, rotation, compliance monitoring, and smart remediation.

![Secret Management Commands](https://raw.githubusercontent.com/pxkundu/awdx/development/assests/AWDX_SECRET_HELP.png)

```bash
# Discover all secrets
awdx secret discover
🔐 Discovering secrets across AWS services...
🔍 Found 15 secrets:
   - 8 in Secrets Manager
   - 5 in Parameter Store
   - 2 in IAM access keys
❌ HIGH: 3 secrets expired
⚠️ MEDIUM: 5 secrets expiring soon

# Rotate secrets
awdx secret rotate my-secret-id
🔄 Rotating secret: my-secret-id
✅ Secret rotated successfully
📅 Next rotation: 2024-02-15

# Monitor secret health
awdx secret monitor --days 30
📊 Monitoring secret health for last 30 days...
✅ Successful rotations: 12
❌ Failed rotations: 1
⚠️ Expiring soon: 3
```

📖 **Full Documentation:** [Secrex Module README](https://github.com/pxkundu/awdx/tree/development/Secrex)

### Security Assessment
Comprehensive security posture assessment, vulnerability scanning, and incident response.

![Security Assessment Commands](https://raw.githubusercontent.com/pxkundu/awdx/development/assests/AWDX_SECURITY_HELP.png)

```bash
# Security posture assessment
awdx security posture
🛡️ Starting comprehensive security posture assessment...
🔍 Network Security: 85/100
🔍 IAM Security: 92/100
🔍 Data Protection: 78/100
📊 Overall Security Score: 85/100

# Vulnerability scanning
awdx security vulnerabilities --service ec2
🚨 Scanning EC2 instances for vulnerabilities...
🔍 Found 5 security issues:
   - 2 open security groups (HIGH)
   - 1 unencrypted EBS volume (MEDIUM)
   - 2 outdated AMIs (LOW)

# Incident response
awdx security incident --type breach
🚨 Initiating incident response for security breach...
📋 Investigation checklist:
   - CloudTrail logs analysis
   - IAM access review
   - Resource access audit
   - Threat detection alerts
```

📖 **Full Documentation:** [SecuTide Module README](https://github.com/pxkundu/awdx/tree/development/SecuTide)

---

## Future Plans

### Upcoming Features
- **AI-Powered Insights:** Natural language queries and intelligent recommendations
- **Multi-Cloud Support:** Extend beyond AWS to Azure and GCP
- **Integration Hub:** Connect with popular DevOps tools and CI/CD pipelines
- **Real-time Monitoring:** Live cost and security monitoring with alerts

### Enterprise Features
- **Team Collaboration:** Multi-user support with role-based access
- **Audit Trails:** Comprehensive logging and compliance reporting
- **Custom Policies:** Define organization-specific security and cost policies
- **API Access:** RESTful API for integration with existing tools

---

## Project Status

Active development with comprehensive module coverage. The project follows a modular architecture allowing for easy extension and customization.

### Current Status
- ✅ **Profilyze Module:** Complete with full feature set
- ✅ **Costlyzer Module:** Complete with smart analytics
- ✅ **IAMply Module:** Complete with security audit and compliance
- ✅ **S3ntry Module:** Complete with security assessment and compliance
- ✅ **Secrex Module:** Complete with secret management and rotation
- ✅ **SecuTide Module:** Complete with security posture and incident response
- 🚧 **Core Infrastructure:** Stable and production-ready
- 📋 **Documentation:** Comprehensive guides and examples

### Contributing
We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for details on how to get started.

### Community
- 📖 **Documentation:** [GitHub Wiki](https://github.com/pxkundu/awdx/wiki)
- 🐛 **Issues:** [GitHub Issues](https://github.com/pxkundu/awdx/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/pxkundu/awdx/discussions)
- 📄 **License:** [MIT License](LICENSE)

---

## 👨‍💻 Author & Attribution

**AWDX** is created and maintained by **Partha Sarathi Kundu** (@pxkundu).

**Independence Notice**: AWDX is developed independently and is not affiliated with, endorsed by, or sponsored by any organization, university, or company.

### Copyright & License
- **Copyright**: © 2024 Partha Sarathi Kundu. All rights reserved.
- **License**: MIT License - see [LICENSE](LICENSE) for details
- **Trademark**: "AWDX" and "AWS DevOps X" are trademarks of Partha Sarathi Kundu

### Citation
If you use AWDX in academic research or commercial projects, please cite:

```
Kundu, P. S. (2024). AWDX: AWS DevOps X - Gen AI-powered AWS DevSecOps CLI tool. 
GitHub. https://github.com/pxkundu/awdx
```

For academic papers (BibTeX):
```bibtex
@software{awdx2024,
  author = {Kundu, Partha Sarathi},
  title = {AWDX: AWS DevOps X - Gen AI-powered AWS DevSecOps CLI tool},
  year = {2024},
  url = {https://github.com/pxkundu/awdx},
  note = {MIT License}
}
```

### Contact
- **Email**: inboxkundu@gmail.com
- **GitHub**: [@pxkundu](https://github.com/pxkundu)
- **Project**: [https://github.com/pxkundu/awdx](https://github.com/pxkundu/awdx)

### Contributors
See [AUTHORS.md](AUTHORS.md) for a complete list of contributors and their contributions. 