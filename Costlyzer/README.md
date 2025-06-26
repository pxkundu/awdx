# Costlyzer Module

The Costlyzer module provides comprehensive AWS cost analysis and optimization capabilities for the AWDX CLI tool. It helps you monitor, analyze, and optimize your AWS spending through easy-to-use commands with intelligent insights and smart recommendations.

## Features

### 💰 Cost Summary
Get a comprehensive overview of your AWS spending including:
- Total cost for specified time periods
- Cost breakdown by service
- Top spending services
- Cost optimization recommendations

### 📈 Cost Trends Analysis
Analyze cost patterns and trends over time:
- Daily, weekly, and monthly cost trends
- Seasonal variations and patterns
- Cost spike identification
- Growth pattern analysis by service

### 🚨 Cost Alerts
Set up monitoring and alerting for cost management:
- Billing threshold alerts
- Cost anomaly detection
- Budget vs actual spending tracking
- Multi-channel notifications

### 💸 Cost Optimization
Get personalized recommendations for cost savings:
- Reserved Instance recommendations
- Unused resource identification
- Storage optimization suggestions
- Service-specific cost savings tips

### 📤 Data Export
Export cost data for external analysis:
- CSV and JSON export formats
- Customizable time periods
- Service and region breakdowns
- External reporting capabilities

### 📋 Budget Management
Create and manage AWS cost budgets:
- Monthly and annual budget creation
- Budget alert configuration
- Multi-project budget tracking
- Budget vs actual comparison

### 🔍 **Smart Anomaly Detection**
Detect unusual spending patterns and cost anomalies:
- Statistical analysis of cost patterns
- Automatic anomaly detection with configurable thresholds
- Service-specific anomaly identification
- Investigation recommendations for detected anomalies

### 🔮 **Cost Forecasting**
Predict future costs using advanced analytics:
- Linear regression-based cost predictions
- Confidence intervals and trend analysis
- Growth rate calculations
- Budget planning insights

### 📊 **Cost Comparison**
Compare costs across different time periods:
- Side-by-side cost analysis
- Percentage change calculations
- Service-specific comparisons
- Trend interpretation and insights

### 🏷️ **Tag-Based Cost Analysis**
Analyze costs by resource tags for better allocation:
- Cost allocation by project, environment, or team
- Tagging coverage analysis
- Untagged resource identification
- Tagging policy recommendations

### 💰 **Savings Calculator**
Calculate potential savings from optimization strategies:
- Multiple savings scenarios (conservative/moderate/aggressive)
- Service-specific savings estimates
- Annual projections and ROI analysis
- Implementation recommendations

## Commands

### `awdx cost summary`
Get a comprehensive cost summary for the current period.

```bash
# Basic cost summary for last 30 days
awdx cost summary

# Custom time period
awdx cost summary --days 90

# Use specific AWS profile
awdx cost summary --profile production

# Different granularity
awdx cost summary --granularity DAILY
```

### `awdx cost trends`
Analyze cost trends over time to identify patterns.

```bash
# Analyze trends for last 90 days
awdx cost trends --days 90

# Analyze specific service trends
awdx cost trends --service "Amazon EC2"

# Use specific profile
awdx cost trends --profile development
```

### `awdx cost alerts`
Set up cost monitoring alerts.

```bash
# Set up basic cost alert
awdx cost alerts --threshold 1000

# Set up alert with email notification
awdx cost alerts --threshold 500 --email user@example.com

# Use specific profile
awdx cost alerts --profile production
```

### `awdx cost optimize`
Get cost optimization recommendations.

```bash
# Get general optimization recommendations
awdx cost optimize

# Get service-specific recommendations
awdx cost optimize --service "Amazon S3"

# Use specific profile
awdx cost optimize --profile development
```

### `awdx cost export`
Export cost data to CSV or JSON format.

```bash
# Export last 30 days to CSV
awdx cost export --format csv --output monthly_costs

# Export last 90 days to JSON
awdx cost export --days 90 --format json --output quarterly_costs

# Use specific profile
awdx cost export --profile production
```

### `awdx cost budget`
Create and manage AWS cost budgets.

```bash
# List existing budgets
awdx cost budget --list

# Create new budget
awdx cost budget --create

# Use specific profile
awdx cost budget --profile production
```

### `awdx cost anomaly` 🔍
Detect cost anomalies and unusual spending patterns.

```bash
# Detect anomalies for last 30 days
awdx cost anomaly

# Custom analysis period
awdx cost anomaly --days 60

# Adjust anomaly threshold (2.5x average)
awdx cost anomaly --threshold 2.5

# Use specific profile
awdx cost anomaly --profile production
```

### `awdx cost forecast` 🔮
Predict future costs based on historical data.

```bash
# Forecast next 3 months
awdx cost forecast

# Forecast next 6 months
awdx cost forecast --months 6

# Adjust confidence level
awdx cost forecast --confidence 0.90

# Use specific profile
awdx cost forecast --profile production
```

### `awdx cost compare` 📊
Compare costs across different time periods.

```bash
# Compare last 30 vs 60 days
awdx cost compare

# Custom period comparison
awdx cost compare --period1 30 --period2 90

# Compare specific service
awdx cost compare --service "Amazon EC2"

# Use specific profile
awdx cost compare --profile production
```

### `awdx cost tags` 🏷️
Analyze costs by resource tags for better allocation.

```bash
# Analyze costs by common tags
awdx cost tags

# Analyze specific tag key
awdx cost tags --tag "Environment"

# Custom analysis period
awdx cost tags --days 60

# Use specific profile
awdx cost tags --profile production
```

### `awdx cost savings` 💰
Calculate potential savings from optimization strategies.

```bash
# Calculate savings with conservative scenario
awdx cost savings

# Use moderate savings scenario
awdx cost savings --scenario moderate

# Use aggressive savings scenario
awdx cost savings --scenario aggressive

# Use specific profile
awdx cost savings --profile production
```

## Smart Features

### 🔍 **Intelligent Anomaly Detection**
- **Statistical Analysis**: Uses standard deviation and mean calculations
- **Configurable Thresholds**: Adjust sensitivity for different environments
- **Service-Specific Detection**: Identifies anomalies per service
- **Investigation Guidance**: Provides specific steps to investigate anomalies

### 🔮 **Advanced Cost Forecasting**
- **Linear Regression**: Uses historical data for trend analysis
- **Confidence Intervals**: Provides uncertainty ranges for predictions
- **Growth Rate Analysis**: Calculates and interprets growth patterns
- **Trend Confidence**: R-squared analysis for prediction reliability

### 📊 **Smart Cost Comparison**
- **Percentage Analysis**: Automatic calculation of cost changes
- **Trend Interpretation**: Intelligent interpretation of cost changes
- **Service Breakdown**: Detailed comparison by service
- **Insight Generation**: Context-aware recommendations

### 🏷️ **Tag Intelligence**
- **Coverage Analysis**: Calculates tagging coverage percentage
- **Untagged Resource Detection**: Identifies resources without tags
- **Policy Recommendations**: Suggests tagging improvements
- **Cost Allocation Insights**: Helps with chargeback and showback

### 💰 **Savings Intelligence**
- **Multiple Scenarios**: Conservative, moderate, and aggressive estimates
- **Service-Specific Calculations**: Different savings rates per service
- **Annual Projections**: Long-term savings potential
- **ROI Analysis**: Implementation cost vs. savings analysis

## Prerequisites

### AWS Permissions
The Costlyzer module requires the following AWS permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ce:GetCostAndUsage",
                "ce:GetDimensionValues",
                "ce:GetReservationUtilization",
                "ce:GetReservationCoverage",
                "budgets:DescribeBudgets",
                "budgets:DescribeBudget",
                "budgets:DescribeBudgetActionsForAccount",
                "budgets:DescribeBudgetActionsForBudget",
                "cloudwatch:DescribeAlarms",
                "cloudwatch:PutMetricAlarm",
                "sns:CreateTopic",
                "sns:Subscribe",
                "sns:Publish"
            ],
            "Resource": "*"
        }
    ]
}
```

### Required Python Packages
- `boto3` - AWS SDK for Python
- `typer` - CLI framework
- `botocore` - Low-level AWS service access

## Configuration

### AWS Credentials
Ensure your AWS credentials are properly configured:

```bash
# Configure AWS credentials
aws configure

# Or use a specific profile
aws configure --profile production
```

### Cost Explorer Access
Enable AWS Cost Explorer in your AWS account:
1. Go to AWS Cost Explorer console
2. Enable Cost Explorer if not already enabled
3. Wait for data to become available (may take up to 24 hours)

### Budgets Access
Enable AWS Budgets access:
1. Go to AWS Budgets console
2. Enable Budgets if not already enabled
3. Configure billing alerts

## Best Practices

### Cost Monitoring
- Set up regular cost reviews (weekly/monthly)
- Use cost alerts to prevent overspending
- Monitor cost trends for anomalies
- Review unused resources regularly

### Optimization
- Use Reserved Instances for predictable workloads
- Implement proper resource tagging
- Enable S3 Intelligent Tiering
- Right-size EC2 instances and RDS databases

### Budget Management
- Set realistic budgets based on historical data
- Create separate budgets for different projects
- Set up multiple alert thresholds
- Review and adjust budgets regularly

### Data Export
- Export cost data regularly for analysis
- Use appropriate formats for your use case
- Secure exported data containing sensitive information
- Archive historical cost data

### Anomaly Detection
- Set appropriate thresholds for your environment
- Investigate anomalies promptly
- Document expected cost increases
- Use anomaly detection for proactive cost management

### Forecasting
- Use forecasts for budget planning
- Consider seasonal patterns
- Update forecasts regularly
- Don't rely solely on forecasts for critical decisions

### Tag Management
- Use consistent tag keys across resources
- Implement automated tagging
- Regular tagging audits
- Avoid too many unique tag values

## Troubleshooting

### Common Issues

**"No AWS credentials found"**
```bash
# Configure AWS credentials
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

**"Access denied" errors**
- Ensure your AWS user/role has the required permissions
- Check if Cost Explorer and Budgets are enabled
- Verify you're using the correct AWS profile

**"No cost data available"**
- Cost Explorer data may take up to 24 hours to appear
- Ensure you have active AWS resources
- Check if you're in the correct AWS account/region

**"Profile not found"**
```bash
# List available profiles
awdx profile list

# Switch to correct profile
export AWS_PROFILE=your_profile_name
```

**"Insufficient data for forecasting"**
- Need at least 3 months of historical data
- Ensure Cost Explorer is enabled
- Check if you have consistent cost data

### Getting Help

```bash
# Get help for cost commands
awdx cost --help

# Get help for specific command
awdx cost summary --help

# List all available cost commands
awdx cost --help
```

## Examples

### Daily Cost Monitoring
```bash
# Check today's costs
awdx cost summary --days 1

# Monitor cost trends
awdx cost trends --days 7

# Detect anomalies
awdx cost anomaly --days 7
```

### Monthly Cost Review
```bash
# Get monthly summary
awdx cost summary --days 30

# Export monthly data
awdx cost export --days 30 --format csv --output monthly_report

# Get optimization recommendations
awdx cost optimize

# Calculate potential savings
awdx cost savings --scenario moderate
```

### Budget Setup
```bash
# Create budget for new project
awdx cost budget --create

# Set up alerts
awdx cost alerts --threshold 1000 --email team@company.com

# Forecast costs for budget planning
awdx cost forecast --months 6
```

### Cost Analysis
```bash
# Analyze EC2 costs
awdx cost trends --service "Amazon EC2" --days 90

# Compare costs across periods
awdx cost compare --period1 30 --period2 90

# Analyze costs by tags
awdx cost tags --tag "Environment"

# Export detailed cost data
awdx cost export --days 90 --format json --output detailed_analysis
```

### Advanced Analytics
```bash
# Detect cost anomalies
awdx cost anomaly --threshold 2.5 --days 60

# Forecast future costs
awdx cost forecast --months 12 --confidence 0.95

# Compare different time periods
awdx cost compare --period1 30 --period2 180

# Analyze tagging coverage
awdx cost tags --days 30
```

## Contributing

To contribute to the Costlyzer module:

1. Follow the project's coding standards
2. Add comprehensive tests for new features
3. Update documentation for any changes
4. Ensure proper error handling
5. Follow AWS best practices for cost management

## License

This module is part of the AWDX project and follows the same license terms. 