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
- **Security Audits:** Scan for misconfigurations, exposed secrets, and risky permissions
- **Resource Checks:** Instantly check S3 buckets, security groups, IAM users, and more
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

![Profile Management Commands](https://raw.githubusercontent.com/pxkundu/awdx/
development/assests/AWDX_PROFILE_HELP.png)

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

---

## Future Plans

### Upcoming Modules
- **Secrex:** Secret management and rotation automation
- **S3ntry:** S3 bucket security and compliance checks
- **SecuTide:** Security posture assessment and remediation
- **IAMply:** IAM policy analysis and optimization

### Advanced Features
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

Early development with active community contributions. The project follows a modular architecture allowing for easy extension and customization.

### Current Status
- ✅ **Profilyze Module:** Complete with full feature set
- ✅ **Costlyzer Module:** Complete with smart analytics
- 🚧 **Core Infrastructure:** Stable and production-ready
- 📋 **Documentation:** Comprehensive guides and examples

### Contributing
We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for details on how to get started.

### Community
- 📖 **Documentation:** [GitHub Wiki](https://github.com/pxkundu/awdx/wiki)
- 🐛 **Issues:** [GitHub Issues](https://github.com/pxkundu/awdx/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/pxkundu/awdx/discussions)
- 📄 **License:** [MIT License](LICENSE) 