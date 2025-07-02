# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **IAMply Module**: Comprehensive AWS IAM management and security analysis
  - **Basic IAM Management**: User, role, policy, and group management with security insights
  - **Security Audit**: Comprehensive IAM security audit with risk assessment and export capabilities
  - **Access Analysis**: Effective permission analysis and access pattern identification
  - **Compliance Checking**: CIS, SOC2, and PCI compliance validation
  - **Smart Recommendations**: AI-powered recommendations with automated remediation
  - **Data Export**: JSON/CSV export for external analysis and reporting
  - **Real-world DevSecOps Use Cases**: Incident response, CI/CD integration, compliance automation
  - **Risk Assessment**: Critical, high, medium, and low risk categorization
  - **Automated Remediation**: Safe auto-fix capabilities with dry-run mode
  - **Permission Analysis**: Deep permission analysis with privilege escalation detection
- **Costlyzer Module**: Comprehensive AWS cost analysis and optimization capabilities
  - Cost summary and breakdown by service
  - Cost trends analysis with pattern identification
  - Cost monitoring alerts and budget management
  - Cost optimization recommendations with service-specific tips
  - Data export functionality (CSV/JSON) for external analysis
  - Budget creation and management tools
  - **Smart Anomaly Detection**: Statistical analysis to detect unusual spending patterns
  - **Cost Forecasting**: Linear regression-based predictions with confidence intervals
  - **Cost Comparison**: Side-by-side analysis across different time periods
  - **Tag-Based Analysis**: Cost allocation analysis by resource tags
  - **Savings Calculator**: ROI analysis with multiple scenarios (conservative/moderate/aggressive)
- Comprehensive community standards and contribution guidelines
- GitHub issue templates for bug reports, feature requests, and documentation
- Enhanced pull request template with approval requirements
- Code of Conduct following Contributor Covenant v2.0
- Security policy and vulnerability reporting guidelines
- Development workflow script for proper branching strategy
- Detailed code commenting standards and examples
- GitFlow-inspired branching strategy documentation
- Pre-commit check automation
- Conventional commit message validation

### Changed
- Updated contributing guide to start from development branch
- Enhanced PR approval process with minimum maintainer approval requirement
- Improved code documentation standards with comprehensive docstrings
- Updated release workflow to follow proper branching strategy
- Enhanced testing guidelines with commented examples
- Updated documentation structure and standards
- Enhanced main README with Costlyzer module documentation and examples
- **Simplified root README**: Cleaned up and made more concise, focusing on high-level use cases
- **Improved PyPI metadata**: Added keywords, classifiers, and GitHub repository links
- **Modular documentation**: Moved detailed command documentation to module-specific READMEs

## [0.0.4] - 2025-06-25

### Added
- Profile management commands (`awdx profile list`, `awdx profile current`, etc.)
- Interactive profile switching and validation
- Security posture analysis for AWS profiles
- Best practice suggestions for profile management
- GitHub Actions workflow for image hosting
- Manual publishing script for PyPI

### Changed
- Updated README with visual elements and GitHub-hosted images
- Improved project structure with modular design
- Enhanced documentation with examples and usage guides

### Fixed
- Resolved virtual environment setup issues
- Fixed package building and distribution process

## [0.0.3] - 2025-06-24

### Added
- Initial PyPI package release
- Basic CLI structure with Typer framework
- AWS profile management foundation
- Project documentation and setup scripts

### Changed
- Updated project configuration for PyPI distribution
- Improved development environment setup

## [0.0.2] - 2025-06-23

### Added
- Initial project structure
- Basic CLI interface
- Development environment setup

## [0.0.1] - 2025-06-22

### Added
- Project initialization
- Basic repository structure
- License and initial documentation

---

## Types of Changes

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** in case of vulnerabilities

## Contributing to Changelog

When contributing to this project, please update the changelog by adding an entry under the `[Unreleased]` section. Use the appropriate type of change and provide a clear description of what was added, changed, or fixed.

### Example Entry

```markdown
### Added
- New feature description

### Changed
- Description of changes to existing functionality

### Fixed
- Description of bug fixes
```

## Links

- [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
- [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
- [Contributing Guidelines](CONTRIBUTING.md) 