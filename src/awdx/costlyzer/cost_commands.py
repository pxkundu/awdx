import csv
import json
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import boto3
import typer
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound

from .. import AWDXErrorHandler

cost_app = typer.Typer(help="AWS cost analysis and optimization commands.")

# Emoji constants for consistent UI
COST_EMOJI = "💰"
ANALYSIS_EMOJI = "📊"
WARNING_EMOJI = "⚠️"
SUCCESS_EMOJI = "✅"
ERROR_EMOJI = "❌"
TIP_EMOJI = "💡"
SAVINGS_EMOJI = "💸"
TREND_EMOJI = "📈"
ALERT_EMOJI = "🚨"
INFO_EMOJI = "ℹ️"
DANGER_EMOJI = "❗"
BEST_PRACTICE_EMOJI = "✅"
AVOID_EMOJI = "🚫"
FORECAST_EMOJI = "🔮"


def get_cost_explorer_client(profile: Optional[str] = None):
    """
    Get AWS Cost Explorer client for the specified profile.

    Args:
        profile (Optional[str]): AWS profile name. If None, uses default profile.

    Returns:
        boto3.client: Cost Explorer client

    Raises:
        ProfileNotFound: If the specified profile doesn't exist
        NoCredentialsError: If no credentials are found
        ClientError: If there's an AWS API error
    """
    try:
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        return session.client("ce")
    except ProfileNotFound:
        AWDXErrorHandler.handle_aws_error(
            ProfileNotFound(f"Profile '{profile}' not found"), profile=profile
        )
        raise typer.BadParameter(f"Profile '{profile}' not found")
    except NoCredentialsError:
        AWDXErrorHandler.handle_aws_error(NoCredentialsError())
        raise typer.BadParameter(
            "No AWS credentials found. Please configure your AWS credentials."
        )
    except Exception as e:
        AWDXErrorHandler.handle_aws_error(e)
        raise typer.BadParameter(f"Error creating Cost Explorer client: {e}")


def format_cost(amount: str, unit: str) -> str:
    """
    Format cost amount with proper currency symbol and precision.

    Args:
        amount (str): Cost amount as string
        unit (str): Currency unit (USD, EUR, etc.)

    Returns:
        str: Formatted cost string
    """
    try:
        cost = float(amount)
        if unit == "USD":
            return f"${cost:.2f}"
        elif unit == "EUR":
            return f"€{cost:.2f}"
        else:
            return f"{cost:.2f} {unit}"
    except (ValueError, TypeError):
        return f"{amount} {unit}"


def get_date_range(days: int = 30) -> tuple:
    """
    Get start and end dates for cost analysis.

    Args:
        days (int): Number of days to look back

    Returns:
        tuple: (start_date, end_date) as strings in YYYY-MM-DD format
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")


@cost_app.command("summary", help="Get AWS cost summary for the current period 💰")
def get_cost_summary(
    days: int = typer.Option(30, "--days", "-d", help="Number of days to analyze"),
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    granularity: str = typer.Option(
        "MONTHLY", "--granularity", "-g", help="Cost granularity (DAILY/MONTHLY)"
    ),
):
    """
    Get a comprehensive cost summary for the specified time period.

    This command provides an overview of AWS spending including:
    - Total cost for the period
    - Cost breakdown by service
    - Cost trends and patterns
    - Cost optimization recommendations
    """
    try:
        ce_client = get_cost_explorer_client(profile)
        start_date, end_date = get_date_range(days)

        typer.echo(f"{ANALYSIS_EMOJI} Analyzing AWS costs for the last {days} days...")
        typer.echo(f"📅 Period: {start_date} to {end_date}")
        typer.echo(f"👤 Profile: {profile or 'default'}")
        typer.echo()

        # Get total cost
        total_cost_response = ce_client.get_cost_and_usage(
            TimePeriod={"Start": start_date, "End": end_date},
            Granularity=granularity,
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
        )

        # Display total cost
        total_cost = 0
        service_costs = []

        for result in total_cost_response["ResultsByTime"]:
            for group in result["Groups"]:
                service_name = group["Keys"][0]
                cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
                unit = group["Metrics"]["UnblendedCost"]["Unit"]
                total_cost += cost
                service_costs.append(
                    {"service": service_name, "cost": cost, "unit": unit}
                )

        # Sort services by cost (highest first)
        service_costs.sort(key=lambda x: x["cost"], reverse=True)

        # Display summary
        typer.echo(f"{COST_EMOJI} Total Cost: {format_cost(str(total_cost), 'USD')}")
        typer.echo()

        # Display top services
        typer.echo(f"{ANALYSIS_EMOJI} Top 10 Services by Cost:")
        for i, service_cost in enumerate(service_costs[:10], 1):
            formatted_cost = format_cost(
                str(service_cost["cost"]), service_cost["unit"]
            )
            typer.echo(f"  {i:2d}. {service_cost['service']:<25} {formatted_cost:>10}")

        # Cost optimization tips
        typer.echo()
        typer.echo(f"{TIP_EMOJI} Cost Optimization Tips:")
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Use Reserved Instances for predictable workloads"
        )
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Enable Cost Explorer for detailed cost analysis"
        )
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Set up billing alerts to monitor spending")
        typer.echo(f"  {AVOID_EMOJI} Avoid leaving unused resources running")

    except Exception as e:
        typer.echo(f"{DANGER_EMOJI} {ERROR_EMOJI} Error getting cost summary: {e}")
        raise typer.Exit(1)


@cost_app.command("trends", help="Analyze cost trends over time 📈")
def analyze_cost_trends(
    days: int = typer.Option(90, "--days", "-d", help="Number of days to analyze"),
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    service: Optional[str] = typer.Option(
        None, "--service", "-s", help="Specific service to analyze"
    ),
):
    """
    Analyze cost trends over time to identify patterns and anomalies.

    This command helps you understand:
    - Cost trends and patterns
    - Seasonal variations
    - Unexpected cost spikes
    - Growth patterns by service
    """
    try:
        ce_client = get_cost_explorer_client(profile)
        start_date, end_date = get_date_range(days)

        typer.echo(f"{TREND_EMOJI} Analyzing cost trends for the last {days} days...")
        typer.echo(f"📅 Period: {start_date} to {end_date}")
        if service:
            typer.echo(f"🔧 Service: {service}")
        typer.echo()

        # Build group by configuration
        group_by = [{"Type": "DIMENSION", "Key": "SERVICE"}]
        if service:
            # Filter by specific service
            filter_config = {"Dimensions": {"Key": "SERVICE", "Values": [service]}}
        else:
            filter_config = None

        # Get cost data with daily granularity
        # Only include Filter if filter_config is not None
        request_params = {
            "TimePeriod": {"Start": start_date, "End": end_date},
            "Granularity": "DAILY",
            "Metrics": ["UnblendedCost"],
            "GroupBy": group_by,
        }

        if filter_config is not None:
            request_params["Filter"] = filter_config

        response = ce_client.get_cost_and_usage(**request_params)

        # Analyze trends
        daily_costs = {}
        service_trends = {}

        for result in response["ResultsByTime"]:
            date = result["TimePeriod"]["Start"]
            total_daily_cost = 0

            for group in result["Groups"]:
                service_name = group["Keys"][0]
                cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
                total_daily_cost += cost

                if service_name not in service_trends:
                    service_trends[service_name] = []
                service_trends[service_name].append(cost)

            daily_costs[date] = total_daily_cost

        # Calculate trend statistics
        if daily_costs:
            costs_list = list(daily_costs.values())
            avg_cost = sum(costs_list) / len(costs_list)
            max_cost = max(costs_list)
            min_cost = min(costs_list)

            typer.echo(f"{ANALYSIS_EMOJI} Cost Trend Analysis:")
            typer.echo(f"  📊 Average daily cost: {format_cost(str(avg_cost), 'USD')}")
            typer.echo(f"  📈 Highest daily cost: {format_cost(str(max_cost), 'USD')}")
            typer.echo(f"  📉 Lowest daily cost: {format_cost(str(min_cost), 'USD')}")
            typer.echo(
                f"  📊 Cost variance: {format_cost(str(max_cost - min_cost), 'USD')}"
            )

            # Identify trends
            if len(costs_list) > 7:
                recent_avg = sum(costs_list[-7:]) / 7
                if recent_avg > avg_cost * 1.2:
                    typer.echo(f"  {ALERT_EMOJI} Recent costs are trending upward!")
                elif recent_avg < avg_cost * 0.8:
                    typer.echo(f"  {SUCCESS_EMOJI} Recent costs are trending downward!")
                else:
                    typer.echo(f"  {INFO_EMOJI} Costs are relatively stable")

        # Service-specific trends
        if not service and service_trends:
            typer.echo()
            typer.echo(f"{ANALYSIS_EMOJI} Service Trends:")
            for service_name, costs in sorted(
                service_trends.items(), key=lambda x: sum(x[1]), reverse=True
            )[:5]:
                avg_service_cost = sum(costs) / len(costs)
                typer.echo(
                    f"  {service_name:<25} Avg: {format_cost(str(avg_service_cost), 'USD')}"
                )

        typer.echo()
        typer.echo(f"{TIP_EMOJI} Trend Analysis Tips:")
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Monitor cost trends weekly to catch issues early"
        )
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Set up cost anomaly detection alerts")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Review services with increasing costs")

    except Exception as e:
        AWDXErrorHandler.handle_aws_error(e, context="cost trends analysis")
        typer.echo(f"{DANGER_EMOJI} {ERROR_EMOJI} Error analyzing cost trends: {e}")
        raise typer.Exit(1)


@cost_app.command("alerts", help="Set up cost monitoring alerts 🚨")
def setup_cost_alerts(
    threshold: float = typer.Option(
        100.0, "--threshold", "-t", help="Cost threshold in USD"
    ),
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    email: Optional[str] = typer.Option(None, "--email", "-e", help="Email for alerts"),
):
    """
    Set up cost monitoring alerts to stay informed about spending.

    This command helps you:
    - Set up billing alerts
    - Monitor cost thresholds
    - Get notified of cost anomalies
    - Track budget vs actual spending
    """
    try:
        # Get CloudWatch client for alarms
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        cw_client = session.client("cloudwatch")

        typer.echo(f"{ALERT_EMOJI} Setting up cost monitoring alerts...")
        typer.echo(f"💰 Threshold: ${threshold:.2f}")
        typer.echo(f"👤 Profile: {profile or 'default'}")
        typer.echo()

        # Note: This is a simplified implementation
        # In a real scenario, you would need to:
        # 1. Set up CloudWatch alarms for billing metrics
        # 2. Configure SNS topics for notifications
        # 3. Set up IAM permissions for billing access

        typer.echo(f"{INFO_EMOJI} Cost Alert Setup Instructions:")
        typer.echo()
        typer.echo("1. Enable Billing Alerts in AWS Console:")
        typer.echo("   - Go to AWS Billing Console")
        typer.echo("   - Navigate to 'Billing Preferences'")
        typer.echo("   - Enable 'Receive Billing Alerts'")
        typer.echo()
        typer.echo("2. Create CloudWatch Billing Alarm:")
        typer.echo("   - Go to CloudWatch Console")
        typer.echo("   - Create alarm for 'EstimatedCharges' metric")
        typer.echo(f"   - Set threshold to ${threshold}")
        typer.echo()
        typer.echo("3. Configure SNS Notification:")
        if email:
            typer.echo(f"   - Create SNS topic with email subscription: {email}")
        else:
            typer.echo("   - Create SNS topic with your email subscription")
        typer.echo("   - Attach SNS topic to the billing alarm")
        typer.echo()

        typer.echo(f"{TIP_EMOJI} Alert Configuration Tips:")
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Set multiple thresholds (50%, 80%, 100% of budget)"
        )
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Use different notification channels (email, SMS, Slack)"
        )
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Set up anomaly detection for unusual spending patterns"
        )
        typer.echo(
            f"  {AVOID_EMOJI} Don't set thresholds too low to avoid alert fatigue"
        )

    except Exception as e:
        typer.echo(f"{DANGER_EMOJI} {ERROR_EMOJI} Error setting up cost alerts: {e}")
        raise typer.Exit(1)


@cost_app.command("optimize", help="Get cost optimization recommendations 💸")
def get_optimization_recommendations(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    service: Optional[str] = typer.Option(
        None, "--service", "-s", help="Specific service to optimize"
    ),
):
    """
    Get personalized cost optimization recommendations.

    This command analyzes your AWS usage and provides:
    - Reserved Instance recommendations
    - Unused resource identification
    - Storage optimization suggestions
    - Service-specific cost savings
    """
    try:
        typer.echo(f"{SAVINGS_EMOJI} Analyzing cost optimization opportunities...")
        typer.echo(f"👤 Profile: {profile or 'default'}")
        if service:
            typer.echo(f"🔧 Service: {service}")
        typer.echo()

        # Get Cost Explorer client
        ce_client = get_cost_explorer_client(profile)

        # Get recent cost data for analysis
        start_date, end_date = get_date_range(30)

        response = ce_client.get_cost_and_usage(
            TimePeriod={"Start": start_date, "End": end_date},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
        )

        # Analyze services for optimization opportunities
        service_costs = {}
        total_cost = 0

        for result in response["ResultsByTime"]:
            for group in result["Groups"]:
                service_name = group["Keys"][0]
                cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
                service_costs[service_name] = cost
                total_cost += cost

        # Sort services by cost
        sorted_services = sorted(
            service_costs.items(), key=lambda x: x[1], reverse=True
        )

        typer.echo(f"{ANALYSIS_EMOJI} Cost Optimization Analysis:")
        typer.echo(f"💰 Total monthly cost: {format_cost(str(total_cost), 'USD')}")
        typer.echo()

        # Provide service-specific recommendations
        typer.echo(f"{TIP_EMOJI} Optimization Recommendations:")
        typer.echo()

        for service_name, cost in sorted_services[:10]:
            if (
                cost > 10
            ):  # Only show recommendations for services with significant cost
                typer.echo(f"🔧 {service_name} (${cost:.2f}):")

                if service_name == "Amazon Elastic Compute Cloud - Compute":
                    typer.echo(
                        f"  {BEST_PRACTICE_EMOJI} Consider Reserved Instances for predictable workloads"
                    )
                    typer.echo(
                        f"  {BEST_PRACTICE_EMOJI} Use Spot Instances for flexible workloads"
                    )
                    typer.echo(
                        f"  {BEST_PRACTICE_EMOJI} Right-size instances based on usage patterns"
                    )
                    typer.echo(
                        f"  {AVOID_EMOJI} Avoid leaving instances running when not needed"
                    )

                elif service_name == "Amazon Simple Storage Service":
                    typer.echo(
                        f"  {BEST_PRACTICE_EMOJI} Use S3 Intelligent Tiering for automatic cost optimization"
                    )
                    typer.echo(
                        f"  {BEST_PRACTICE_EMOJI} Move infrequently accessed data to Glacier"
                    )
                    typer.echo(
                        f"  {BEST_PRACTICE_EMOJI} Enable lifecycle policies for automatic cleanup"
                    )
                    typer.echo(f"  {AVOID_EMOJI} Avoid storing unnecessary data")

                elif service_name == "Amazon Relational Database Service":
                    typer.echo(
                        f"  {BEST_PRACTICE_EMOJI} Use Reserved Instances for production databases"
                    )
                    typer.echo(
                        f"  {BEST_PRACTICE_EMOJI} Consider Aurora Serverless for variable workloads"
                    )
                    typer.echo(f"  {BEST_PRACTICE_EMOJI} Right-size database instances")
                    typer.echo(f"  {AVOID_EMOJI} Don't over-provision storage")

                elif service_name == "AWS Lambda":
                    typer.echo(
                        f"  {BEST_PRACTICE_EMOJI} Optimize function memory allocation"
                    )
                    typer.echo(
                        f"  {BEST_PRACTICE_EMOJI} Use provisioned concurrency for predictable workloads"
                    )
                    typer.echo(
                        f"  {BEST_PRACTICE_EMOJI} Implement proper error handling to avoid retries"
                    )
                    typer.echo(f"  {AVOID_EMOJI} Avoid cold starts in critical paths")

                else:
                    typer.echo(
                        f"  {BEST_PRACTICE_EMOJI} Review usage patterns and optimize accordingly"
                    )
                    typer.echo(
                        f"  {BEST_PRACTICE_EMOJI} Consider alternative services if cost is high"
                    )
                    typer.echo(
                        f"  {BEST_PRACTICE_EMOJI} Implement proper resource tagging for cost allocation"
                    )

                typer.echo()

        # General recommendations
        typer.echo(f"{TIP_EMOJI} General Cost Optimization Tips:")
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Use AWS Cost Explorer regularly to monitor spending"
        )
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Implement proper resource tagging for cost allocation"
        )
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Set up billing alerts to avoid surprises")
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Use AWS Trusted Advisor for cost optimization"
        )
        typer.echo(f"  {AVOID_EMOJI} Avoid over-provisioning resources")
        typer.echo(f"  {AVOID_EMOJI} Don't leave unused resources running")

    except Exception as e:
        typer.echo(
            f"{DANGER_EMOJI} {ERROR_EMOJI} Error getting optimization recommendations: {e}"
        )
        raise typer.Exit(1)


@cost_app.command("export", help="Export cost data to file 📤")
def export_cost_data(
    days: int = typer.Option(30, "--days", "-d", help="Number of days to export"),
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    format: str = typer.Option(
        "csv", "--format", "-f", help="Export format (csv/json)"
    ),
    output: str = typer.Option(
        "cost_data", "--output", "-o", help="Output filename (without extension)"
    ),
):
    """
    Export cost data to CSV or JSON format for further analysis.

    This command allows you to:
    - Export cost data for external analysis
    - Create custom reports
    - Share cost data with stakeholders
    - Perform advanced analytics
    """
    try:
        ce_client = get_cost_explorer_client(profile)
        start_date, end_date = get_date_range(days)

        typer.echo(f"{INFO_EMOJI} Exporting cost data for the last {days} days...")
        typer.echo(f"📅 Period: {start_date} to {end_date}")
        typer.echo(f"📁 Format: {format.upper()}")
        typer.echo()

        # Get cost data
        response = ce_client.get_cost_and_usage(
            TimePeriod={"Start": start_date, "End": end_date},
            Granularity="DAILY",
            Metrics=["UnblendedCost"],
            GroupBy=[
                {"Type": "DIMENSION", "Key": "SERVICE"},
                {"Type": "DIMENSION", "Key": "REGION"},
            ],
        )

        # Prepare data for export
        export_data = []

        for result in response["ResultsByTime"]:
            date = result["TimePeriod"]["Start"]

            for group in result["Groups"]:
                service = group["Keys"][0]
                region = group["Keys"][1]
                cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
                unit = group["Metrics"]["UnblendedCost"]["Unit"]

                export_data.append(
                    {
                        "date": date,
                        "service": service,
                        "region": region,
                        "cost": cost,
                        "unit": unit,
                    }
                )

        # Export based on format
        if format.lower() == "csv":
            filename = f"{output}.csv"
            with open(filename, "w", newline="") as csvfile:
                fieldnames = ["date", "service", "region", "cost", "unit"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(export_data)

        elif format.lower() == "json":
            filename = f"{output}.json"
            with open(filename, "w") as jsonfile:
                json.dump(export_data, jsonfile, indent=2)

        else:
            raise typer.BadParameter(
                f"Unsupported format: {format}. Use 'csv' or 'json'"
            )

        typer.echo(f"{SUCCESS_EMOJI} Cost data exported to: {filename}")
        typer.echo(f"📊 Total records: {len(export_data)}")
        typer.echo()

        typer.echo(f"{TIP_EMOJI} Export Tips:")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Use CSV format for spreadsheet analysis")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Use JSON format for programmatic analysis")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Export data regularly for trend analysis")
        typer.echo(
            f"  {AVOID_EMOJI} Don't share exported data with sensitive cost information"
        )

    except Exception as e:
        typer.echo(f"{DANGER_EMOJI} {ERROR_EMOJI} Error exporting cost data: {e}")
        raise typer.Exit(1)


@cost_app.command("budget", help="Create and manage cost budgets 📋")
def manage_budgets(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    create: bool = typer.Option(False, "--create", "-c", help="Create a new budget"),
    list_budgets: bool = typer.Option(
        False, "--list", "-l", help="List existing budgets"
    ),
):
    """
    Create and manage AWS cost budgets.

    This command helps you:
    - Create monthly or annual budgets
    - Set up budget alerts
    - Track budget vs actual spending
    - Manage multiple budgets for different projects
    """
    try:
        # Get Budgets client
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        budgets_client = session.client("budgets")

        if list_budgets:
            typer.echo(f"{INFO_EMOJI} Listing existing budgets...")
            typer.echo()

            try:
                response = budgets_client.describe_budgets(
                    AccountId=session.client("sts").get_caller_identity()["Account"]
                )

                if response["Budgets"]:
                    for budget in response["Budgets"]:
                        typer.echo(f"📋 Budget: {budget['BudgetName']}")
                        typer.echo(
                            f"   💰 Amount: {budget['BudgetLimit']['Amount']} {budget['BudgetLimit']['Unit']}"
                        )
                        typer.echo(
                            f"   📅 Time Period: {budget['TimePeriod']['Start']} to {budget['TimePeriod']['End']}"
                        )
                        typer.echo(f"   🔧 Type: {budget['BudgetType']}")
                        typer.echo()
                else:
                    typer.echo(
                        f"{INFO_EMOJI} No budgets found. Create one with --create flag."
                    )

            except ClientError as e:
                if e.response["Error"]["Code"] == "AccessDeniedException":
                    typer.echo(
                        f"{WARNING_EMOJI} Access denied. You may need to enable AWS Budgets access."
                    )
                else:
                    raise e

        elif create:
            typer.echo(f"{INFO_EMOJI} Creating a new budget...")
            typer.echo()

            # Get budget details from user
            budget_name = typer.prompt("📋 Enter budget name")
            budget_amount = typer.prompt("💰 Enter budget amount (USD)")
            budget_type = typer.prompt("🔧 Enter budget type", default="COST")

            try:
                # Get account ID
                sts_client = session.client("sts")
                account_id = sts_client.get_caller_identity()["Account"]

                # Create budget
                budget_response = budgets_client.create_budget(
                    AccountId=account_id,
                    Budget={
                        "BudgetName": budget_name,
                        "BudgetLimit": {"Amount": budget_amount, "Unit": "USD"},
                        "BudgetType": budget_type,
                        "TimeUnit": "MONTHLY",
                        "TimePeriod": {
                            "Start": datetime.now().strftime("%Y-%m-%d"),
                            "End": (datetime.now() + timedelta(days=365)).strftime(
                                "%Y-%m-%d"
                            ),
                        },
                    },
                )

                typer.echo(
                    f"{SUCCESS_EMOJI} Budget '{budget_name}' created successfully!"
                )
                typer.echo(f"  💰 Amount: ${budget_amount}")
                typer.echo(f"  🔧 Type: {budget_type}")
                typer.echo(f"  📅 Time Unit: Monthly")
                typer.echo()

                # Create budget notification
                if typer.confirm("Would you like to set up budget alerts?"):
                    email = typer.prompt("Enter email for alerts")
                    threshold = typer.prompt(
                        "Enter alert threshold percentage", default="80"
                    )

                    try:
                        # Create SNS topic for notifications
                        sns_client = session.client("sns")
                        topic_name = (
                            f"budget-alerts-{budget_name.lower().replace(' ', '-')}"
                        )
                        topic_response = sns_client.create_topic(Name=topic_name)

                        # Subscribe email to topic
                        sns_client.subscribe(
                            TopicArn=topic_response["TopicArn"],
                            Protocol="email",
                            Endpoint=email,
                        )

                        # Create budget notification
                        budgets_client.create_notification(
                            AccountId=account_id,
                            BudgetName=budget_name,
                            Notification={
                                "ComparisonOperator": "GREATER_THAN",
                                "NotificationType": "ACTUAL",
                                "Threshold": float(threshold),
                                "ThresholdType": "PERCENTAGE",
                            },
                            Subscribers=[
                                {
                                    "SubscriptionType": "SNS",
                                    "Address": topic_response["TopicArn"],
                                }
                            ],
                        )

                        typer.echo(f"{SUCCESS_EMOJI} Budget alerts configured!")
                        typer.echo(f"  📧 Email: {email}")
                        typer.echo(f"  🚨 Threshold: {threshold}%")

                    except Exception as e:
                        typer.echo(f"{WARNING_EMOJI} Could not set up alerts: {e}")
                        typer.echo(
                            f"{TIP_EMOJI} You can set up alerts manually in the AWS Console"
                        )

            except ClientError as e:
                if e.response["Error"]["Code"] == "AccessDeniedException":
                    typer.echo(
                        f"{WARNING_EMOJI} Access denied. You may need to enable AWS Budgets access."
                    )
                    typer.echo(f"{INFO_EMOJI} Manual Budget Creation Instructions:")
                    typer.echo()
                    typer.echo("1. Go to AWS Budgets Console:")
                    typer.echo("   - Navigate to AWS Budgets service")
                    typer.echo("   - Click 'Create budget'")
                    typer.echo()
                    typer.echo("2. Configure Budget:")
                    typer.echo(f"   - Budget name: {budget_name}")
                    typer.echo(f"   - Budget amount: ${budget_amount}")
                    typer.echo(f"   - Budget type: {budget_type}")
                    typer.echo()
                    typer.echo("3. Set up Alerts:")
                    typer.echo(
                        "   - Configure alert thresholds (e.g., 80%, 100%, 120%)"
                    )
                    typer.echo("   - Set up email notifications")
                    typer.echo("   - Choose alert frequency")
                else:
                    raise e

        else:
            typer.echo(f"{INFO_EMOJI} Budget Management Options:")
            typer.echo(f"  Use --list to see existing budgets")
            typer.echo(f"  Use --create to create a new budget")
            typer.echo()
            typer.echo(f"{TIP_EMOJI} Budget Best Practices:")
            typer.echo(
                f"  {BEST_PRACTICE_EMOJI} Set up budgets for all major cost centers"
            )
            typer.echo(f"  {BEST_PRACTICE_EMOJI} Review and adjust budgets monthly")
            typer.echo(
                f"  {BEST_PRACTICE_EMOJI} Use budget alerts to prevent overspending"
            )

    except Exception as e:
        AWDXErrorHandler.handle_aws_error(e, context="budget management")
        typer.echo(f"{DANGER_EMOJI} {ERROR_EMOJI} Error managing budgets: {e}")
        raise typer.Exit(1)


@cost_app.command(
    "anomaly", help="Detect cost anomalies and unusual spending patterns 🔍"
)
def detect_cost_anomalies(
    days: int = typer.Option(30, "--days", "-d", help="Number of days to analyze"),
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    threshold: float = typer.Option(
        2.0, "--threshold", "-t", help="Anomaly threshold multiplier (default: 2.0x)"
    ),
):
    """
    Detect unusual spending patterns and cost anomalies.

    This command uses statistical analysis to identify:
    - Sudden cost spikes
    - Unusual service usage patterns
    - Potential billing errors
    - Resource misconfigurations
    """
    try:
        ce_client = get_cost_explorer_client(profile)
        start_date, end_date = get_date_range(days)

        typer.echo(f"🔍 Detecting cost anomalies for the last {days} days...")
        typer.echo(f"📅 Period: {start_date} to {end_date}")
        typer.echo(f"🎯 Threshold: {threshold}x average")
        typer.echo()

        # Get daily cost data
        response = ce_client.get_cost_and_usage(
            TimePeriod={"Start": start_date, "End": end_date},
            Granularity="DAILY",
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
        )

        # Analyze daily costs for anomalies
        daily_costs = {}
        service_costs = {}

        for result in response["ResultsByTime"]:
            date = result["TimePeriod"]["Start"]
            daily_total = 0

            for group in result["Groups"]:
                service_name = group["Keys"][0]
                cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
                daily_total += cost

                if service_name not in service_costs:
                    service_costs[service_name] = []
                service_costs[service_name].append(cost)

            daily_costs[date] = daily_total

        # Calculate statistics
        costs_list = list(daily_costs.values())
        avg_cost = sum(costs_list) / len(costs_list)
        std_dev = (
            sum((x - avg_cost) ** 2 for x in costs_list) / len(costs_list)
        ) ** 0.5

        typer.echo(f"{ANALYSIS_EMOJI} Statistical Analysis:")
        typer.echo(f"  📊 Average daily cost: {format_cost(str(avg_cost), 'USD')}")
        typer.echo(f"  📈 Standard deviation: {format_cost(str(std_dev), 'USD')}")
        typer.echo(
            f"  🎯 Anomaly threshold: {format_cost(str(avg_cost * threshold), 'USD')}"
        )
        typer.echo()

        # Detect anomalies
        anomalies = []
        for date, cost in daily_costs.items():
            if cost > avg_cost * threshold:
                anomalies.append(
                    {
                        "date": date,
                        "cost": cost,
                        "deviation": (cost - avg_cost) / avg_cost * 100,
                    }
                )

        if anomalies:
            typer.echo(f"{ALERT_EMOJI} Cost Anomalies Detected:")
            for anomaly in sorted(anomalies, key=lambda x: x["cost"], reverse=True):
                typer.echo(
                    f"  📅 {anomaly['date']}: {format_cost(str(anomaly['cost']), 'USD')} "
                    f"({anomaly['deviation']:+.1f}% above average)"
                )

            typer.echo()
            typer.echo(f"{TIP_EMOJI} Anomaly Investigation Tips:")
            typer.echo(
                f"  {BEST_PRACTICE_EMOJI} Check for new resources or services launched"
            )
            typer.echo(
                f"  {BEST_PRACTICE_EMOJI} Review recent deployments or configuration changes"
            )
            typer.echo(
                f"  {BEST_PRACTICE_EMOJI} Verify if the cost increase is expected"
            )
            typer.echo(f"  {AVOID_EMOJI} Don't ignore persistent anomalies")
        else:
            typer.echo(f"{SUCCESS_EMOJI} No significant anomalies detected!")
            typer.echo(f"{INFO_EMOJI} Your cost patterns appear normal")

        # Service-specific anomalies
        typer.echo()
        typer.echo(f"{ANALYSIS_EMOJI} Service Anomaly Analysis:")
        for service_name, costs in service_costs.items():
            if len(costs) > 7:  # Need enough data
                service_avg = sum(costs) / len(costs)
                service_max = max(costs)
                if service_max > service_avg * threshold:
                    typer.echo(
                        f"  🔧 {service_name}: Peak cost {format_cost(str(service_max), 'USD')} "
                        f"({service_max/service_avg:.1f}x average)"
                    )

    except Exception as e:
        AWDXErrorHandler.handle_aws_error(e, context="cost anomalies detection")
        typer.echo(f"{DANGER_EMOJI} {ERROR_EMOJI} Error detecting anomalies: {e}")
        raise typer.Exit(1)


@cost_app.command("forecast", help="Predict future costs based on historical data 🔮")
def forecast_costs(
    months: int = typer.Option(
        3, "--months", "-m", help="Number of months to forecast"
    ),
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    confidence: float = typer.Option(
        0.95, "--confidence", "-c", help="Confidence interval (0.8-0.99)"
    ),
):
    """
    Forecast future AWS costs using historical data analysis.

    This command provides:
    - Monthly cost predictions
    - Confidence intervals
    - Growth trend analysis
    - Budget planning insights
    """
    try:
        ce_client = get_cost_explorer_client(profile)

        # Get historical data (last 6 months for better forecasting)
        historical_days = 180
        start_date, end_date = get_date_range(historical_days)

        typer.echo(f"🔮 Forecasting costs for the next {months} months...")
        typer.echo(f"📊 Using {historical_days} days of historical data")
        typer.echo(f"🎯 Confidence level: {confidence*100:.0f}%")
        typer.echo()

        # Get monthly historical data
        response = ce_client.get_cost_and_usage(
            TimePeriod={"Start": start_date, "End": end_date},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
        )

        monthly_costs = []
        for result in response["ResultsByTime"]:
            cost = float(result["Total"]["UnblendedCost"]["Amount"])
            monthly_costs.append(cost)

        if len(monthly_costs) < 3:
            typer.echo(
                f"{WARNING_EMOJI} Insufficient historical data for accurate forecasting"
            )
            typer.echo(
                f"{TIP_EMOJI} Need at least 3 months of data for reliable predictions"
            )
            return

        # Simple linear regression for forecasting
        n = len(monthly_costs)
        x = list(range(n))
        y = monthly_costs

        # Calculate trend
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
        intercept = (sum_y - slope * sum_x) / n

        # Calculate R-squared for trend confidence
        y_mean = sum_y / n
        ss_tot = sum((y[i] - y_mean) ** 2 for i in range(n))
        ss_res = sum((y[i] - (slope * x[i] + intercept)) ** 2 for i in range(n))
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        typer.echo(f"{ANALYSIS_EMOJI} Historical Trend Analysis:")
        typer.echo(
            f"  📈 Trend direction: {'Upward' if slope > 0 else 'Downward' if slope < 0 else 'Stable'}"
        )
        typer.echo(f"  📊 Monthly change: {format_cost(str(abs(slope)), 'USD')}")
        typer.echo(f"  🎯 Trend confidence: {r_squared:.1%}")
        typer.echo()

        # Generate forecasts
        typer.echo(f"{FORECAST_EMOJI} Cost Forecasts:")
        current_month = len(monthly_costs)

        for i in range(1, months + 1):
            forecast_month = current_month + i
            base_forecast = slope * forecast_month + intercept

            # Simple confidence interval (assuming normal distribution)
            std_error = (ss_res / (n - 2)) ** 0.5 if n > 2 else 0
            confidence_interval = std_error * 1.96  # 95% confidence

            typer.echo(
                f"  📅 Month {i}: {format_cost(str(max(0, base_forecast)), 'USD')} "
                f"(±{format_cost(str(confidence_interval), 'USD')})"
            )

        # Growth analysis
        if slope > 0:
            growth_rate = (slope / (sum_y / n)) * 100
            typer.echo()
            typer.echo(f"{TREND_EMOJI} Growth Analysis:")
            typer.echo(f"  📈 Estimated monthly growth rate: {growth_rate:.1f}%")
            if growth_rate > 10:
                typer.echo(
                    f"  {ALERT_EMOJI} High growth rate detected - consider optimization"
                )
            elif growth_rate > 5:
                typer.echo(f"  {WARNING_EMOJI} Moderate growth - monitor closely")
            else:
                typer.echo(f"  {SUCCESS_EMOJI} Stable growth pattern")

        typer.echo()
        typer.echo(f"{TIP_EMOJI} Forecasting Tips:")
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Use forecasts for budget planning and resource allocation"
        )
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Consider seasonal patterns and business cycles"
        )
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Update forecasts regularly as new data becomes available"
        )
        typer.echo(
            f"  {AVOID_EMOJI} Don't rely solely on forecasts for critical decisions"
        )

    except Exception as e:
        typer.echo(f"{DANGER_EMOJI} {ERROR_EMOJI} Error forecasting costs: {e}")
        raise typer.Exit(1)


@cost_app.command(
    "compare", help="Compare costs across different time periods or profiles 📊"
)
def compare_costs(
    period1: str = typer.Option("30", "--period1", "-p1", help="First period in days"),
    period2: str = typer.Option("60", "--period2", "-p2", help="Second period in days"),
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    service: Optional[str] = typer.Option(
        None, "--service", "-s", help="Specific service to compare"
    ),
):
    """
    Compare AWS costs across different time periods or services.

    This command helps you:
    - Compare monthly/quarterly costs
    - Identify cost changes over time
    - Analyze service-specific trends
    - Track optimization effectiveness
    """
    try:
        ce_client = get_cost_explorer_client(profile)

        # Parse periods
        try:
            p1_days = int(period1)
            p2_days = int(period2)
        except ValueError:
            typer.echo(
                f"{ERROR_EMOJI} Invalid period format. Use number of days (e.g., 30, 90)"
            )
            raise typer.Exit(1)

        typer.echo(f"📊 Comparing costs across two periods...")
        typer.echo(f"📅 Period 1: Last {p1_days} days")
        typer.echo(f"📅 Period 2: Last {p2_days} days")
        if service:
            typer.echo(f"🔧 Service: {service}")
        typer.echo()

        # Get cost data for both periods
        def get_period_costs(days):
            start_date, end_date = get_date_range(days)
            response = ce_client.get_cost_and_usage(
                TimePeriod={"Start": start_date, "End": end_date},
                Granularity="MONTHLY",
                Metrics=["UnblendedCost"],
                GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
            )

            total_cost = 0
            service_costs = {}

            for result in response["ResultsByTime"]:
                for group in result["Groups"]:
                    service_name = group["Keys"][0]
                    cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
                    total_cost += cost
                    service_costs[service_name] = (
                        service_costs.get(service_name, 0) + cost
                    )

            return total_cost, service_costs

        cost1, services1 = get_period_costs(p1_days)
        cost2, services2 = get_period_costs(p2_days)

        # Calculate differences
        cost_diff = cost2 - cost1
        cost_change_pct = (cost_diff / cost1 * 100) if cost1 > 0 else 0

        typer.echo(f"{ANALYSIS_EMOJI} Overall Cost Comparison:")
        typer.echo(f"  📅 Period 1 ({p1_days} days): {format_cost(str(cost1), 'USD')}")
        typer.echo(f"  📅 Period 2 ({p2_days} days): {format_cost(str(cost2), 'USD')}")
        typer.echo(
            f"  📊 Difference: {format_cost(str(cost_diff), 'USD')} ({cost_change_pct:+.1f}%)"
        )

        # Trend interpretation
        if cost_change_pct > 20:
            typer.echo(f"  {ALERT_EMOJI} Significant cost increase detected!")
        elif cost_change_pct > 10:
            typer.echo(f"  {WARNING_EMOJI} Moderate cost increase")
        elif cost_change_pct < -10:
            typer.echo(f"  {SUCCESS_EMOJI} Cost reduction achieved!")
        else:
            typer.echo(f"  {INFO_EMOJI} Costs are relatively stable")

        typer.echo()

        # Service-specific comparison
        if not service:
            typer.echo(f"{ANALYSIS_EMOJI} Service Comparison:")
            all_services = set(services1.keys()) | set(services2.keys())

            for service_name in sorted(all_services):
                cost1_service = services1.get(service_name, 0)
                cost2_service = services2.get(service_name, 0)
                service_diff = cost2_service - cost1_service

                if cost1_service > 0:
                    service_change_pct = service_diff / cost1_service * 100
                    change_emoji = (
                        "📈"
                        if service_change_pct > 5
                        else "📉" if service_change_pct < -5 else "➡️"
                    )
                    typer.echo(
                        f"  {change_emoji} {service_name:<30} "
                        f"{format_cost(str(cost1_service), 'USD'):>10} → "
                        f"{format_cost(str(cost2_service), 'USD'):>10} "
                        f"({service_change_pct:+.1f}%)"
                    )

        # Insights and recommendations
        typer.echo()
        typer.echo(f"{TIP_EMOJI} Comparison Insights:")
        if cost_change_pct > 0:
            typer.echo(
                f"  {BEST_PRACTICE_EMOJI} Investigate services with the largest cost increases"
            )
            typer.echo(
                f"  {BEST_PRACTICE_EMOJI} Check for new resources or increased usage"
            )
            typer.echo(f"  {AVOID_EMOJI} Don't ignore persistent cost growth")
        else:
            typer.echo(
                f"  {SUCCESS_EMOJI} Good cost management - maintain current practices"
            )
            typer.echo(
                f"  {BEST_PRACTICE_EMOJI} Identify what caused the cost reduction"
            )
            typer.echo(
                f"  {BEST_PRACTICE_EMOJI} Apply successful strategies to other areas"
            )

    except Exception as e:
        typer.echo(f"{DANGER_EMOJI} {ERROR_EMOJI} Error comparing costs: {e}")
        raise typer.Exit(1)


@cost_app.command(
    "tags", help="Analyze costs by resource tags for better cost allocation 🏷️"
)
def analyze_cost_by_tags(
    days: int = typer.Option(30, "--days", "-d", help="Number of days to analyze"),
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    tag_key: Optional[str] = typer.Option(
        None, "--tag", "-t", help="Specific tag key to analyze"
    ),
):
    """
    Analyze AWS costs by resource tags for better cost allocation and accountability.

    This command helps you:
    - Track costs by project, environment, or team
    - Identify untagged resources
    - Improve cost allocation strategies
    - Enforce tagging policies
    """
    try:
        ce_client = get_cost_explorer_client(profile)
        start_date, end_date = get_date_range(days)

        typer.echo(f"🏷️ Analyzing costs by resource tags for the last {days} days...")
        typer.echo(f"📅 Period: {start_date} to {end_date}")
        if tag_key:
            typer.echo(f"🏷️ Tag key: {tag_key}")
        typer.echo()

        # Get cost data grouped by tags
        # AWS Cost Explorer only allows maximum 2 GroupBy values
        if tag_key:
            group_by = [{"Type": "TAG", "Key": tag_key}]
        else:
            # Limit to 2 most common tag keys
            group_by = [
                {"Type": "TAG", "Key": "Environment"},
                {"Type": "TAG", "Key": "Project"},
            ]

        response = ce_client.get_cost_and_usage(
            TimePeriod={"Start": start_date, "End": end_date},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            GroupBy=group_by,
        )

        # Analyze tagged vs untagged costs
        tagged_costs = {}
        untagged_cost = 0
        total_cost = 0

        for result in response["ResultsByTime"]:
            for group in result["Groups"]:
                tag_value = group["Keys"][0] if group["Keys"] else "Untagged"
                cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
                total_cost += cost

                if tag_value == "Untagged":
                    untagged_cost += cost
                else:
                    tagged_costs[tag_value] = tagged_costs.get(tag_value, 0) + cost

        # Display results
        typer.echo(f"{ANALYSIS_EMOJI} Cost Allocation Analysis:")
        typer.echo(f"💰 Total cost: {format_cost(str(total_cost), 'USD')}")
        typer.echo(
            f"🏷️ Tagged cost: {format_cost(str(total_cost - untagged_cost), 'USD')}"
        )
        typer.echo(f"❓ Untagged cost: {format_cost(str(untagged_cost), 'USD')}")

        if total_cost > 0:
            tagging_percentage = ((total_cost - untagged_cost) / total_cost) * 100
            typer.echo(f"📊 Tagging coverage: {tagging_percentage:.1f}%")

            if tagging_percentage < 50:
                typer.echo(
                    f"  {ALERT_EMOJI} Low tagging coverage - implement tagging policies!"
                )
            elif tagging_percentage < 80:
                typer.echo(
                    f"  {WARNING_EMOJI} Moderate tagging coverage - improve tagging"
                )
            else:
                typer.echo(
                    f"  {SUCCESS_EMOJI} Good tagging coverage - maintain standards"
                )

        typer.echo()

        # Show tagged costs breakdown
        if tagged_costs:
            typer.echo(f"{ANALYSIS_EMOJI} Cost Breakdown by Tags:")
            sorted_tags = sorted(tagged_costs.items(), key=lambda x: x[1], reverse=True)

            for tag_value, cost in sorted_tags[:10]:  # Top 10
                percentage = (cost / total_cost * 100) if total_cost > 0 else 0
                typer.echo(
                    f"  🏷️ {tag_value:<20} {format_cost(str(cost), 'USD'):>10} ({percentage:.1f}%)"
                )

        # Tagging recommendations
        typer.echo()
        typer.echo(f"{TIP_EMOJI} Tagging Best Practices:")
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Use consistent tag keys across all resources"
        )
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Implement automated tagging for new resources"
        )
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Regular audits to ensure tagging compliance"
        )
        typer.echo(f"  {AVOID_EMOJI} Don't use too many unique tag values")

        if untagged_cost > total_cost * 0.2:  # More than 20% untagged
            typer.echo()
            typer.echo(f"{ALERT_EMOJI} High untagged cost detected!")
            typer.echo(
                f"  {BEST_PRACTICE_EMOJI} Review and tag existing untagged resources"
            )
            typer.echo(
                f"  {BEST_PRACTICE_EMOJI} Implement tagging policies for new resources"
            )
            typer.echo(
                f"  {BEST_PRACTICE_EMOJI} Consider using AWS Config for tagging compliance"
            )

    except Exception as e:
        AWDXErrorHandler.handle_aws_error(e, context="cost tags analysis")
        typer.echo(f"{DANGER_EMOJI} {ERROR_EMOJI} Error analyzing costs by tags: {e}")
        raise typer.Exit(1)


@cost_app.command(
    "savings", help="Calculate potential savings from optimization recommendations 💰"
)
def calculate_savings(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    scenario: str = typer.Option(
        "conservative",
        "--scenario",
        "-s",
        help="Savings scenario (conservative/moderate/aggressive)",
    ),
):
    """
    Calculate potential cost savings from various optimization strategies.

    This command provides:
    - Reserved Instance savings estimates
    - Storage optimization savings
    - Resource right-sizing opportunities
    - Overall savings potential
    """
    try:
        ce_client = get_cost_explorer_client(profile)

        typer.echo(f"💰 Calculating potential savings with {scenario} scenario...")
        typer.echo(f"👤 Profile: {profile or 'default'}")
        typer.echo()

        # Get current cost data
        start_date, end_date = get_date_range(30)

        response = ce_client.get_cost_and_usage(
            TimePeriod={"Start": start_date, "End": end_date},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
        )

        # Calculate current costs by service
        service_costs = {}
        total_current_cost = 0

        for result in response["ResultsByTime"]:
            for group in result["Groups"]:
                service_name = group["Keys"][0]
                cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
                service_costs[service_name] = cost
                total_current_cost += cost

        # Define savings scenarios
        savings_scenarios = {
            "conservative": {
                "ec2_ri": 0.15,  # 15% savings from Reserved Instances
                "storage_optimization": 0.10,  # 10% storage savings
                "right_sizing": 0.05,  # 5% from right-sizing
                "unused_resources": 0.08,  # 8% from removing unused resources
            },
            "moderate": {
                "ec2_ri": 0.25,  # 25% savings from Reserved Instances
                "storage_optimization": 0.20,  # 20% storage savings
                "right_sizing": 0.10,  # 10% from right-sizing
                "unused_resources": 0.15,  # 15% from removing unused resources
            },
            "aggressive": {
                "ec2_ri": 0.35,  # 35% savings from Reserved Instances
                "storage_optimization": 0.30,  # 30% storage savings
                "right_sizing": 0.15,  # 15% from right-sizing
                "unused_resources": 0.25,  # 25% from removing unused resources
            },
        }

        scenario_rates = savings_scenarios.get(
            scenario, savings_scenarios["conservative"]
        )

        # Calculate potential savings by category
        savings_breakdown = {}
        total_potential_savings = 0

        for service_name, cost in service_costs.items():
            if service_name == "Amazon Elastic Compute Cloud - Compute":
                ri_savings = cost * scenario_rates["ec2_ri"]
                right_sizing_savings = cost * scenario_rates["right_sizing"]
                savings_breakdown["EC2 Reserved Instances"] = ri_savings
                savings_breakdown["EC2 Right-sizing"] = right_sizing_savings
                total_potential_savings += ri_savings + right_sizing_savings

            elif service_name == "Amazon Simple Storage Service":
                storage_savings = cost * scenario_rates["storage_optimization"]
                savings_breakdown["S3 Storage Optimization"] = storage_savings
                total_potential_savings += storage_savings

            elif service_name == "Amazon Relational Database Service":
                ri_savings = cost * scenario_rates["ec2_ri"]
                right_sizing_savings = cost * scenario_rates["right_sizing"]
                savings_breakdown["RDS Reserved Instances"] = ri_savings
                savings_breakdown["RDS Right-sizing"] = right_sizing_savings
                total_potential_savings += ri_savings + right_sizing_savings

        # Add general savings categories
        unused_savings = total_current_cost * scenario_rates["unused_resources"]
        savings_breakdown["Remove Unused Resources"] = unused_savings
        total_potential_savings += unused_savings

        # Display results
        typer.echo(
            f"{ANALYSIS_EMOJI} Current Monthly Cost: {format_cost(str(total_current_cost), 'USD')}"
        )
        typer.echo(
            f"{SAVINGS_EMOJI} Potential Monthly Savings: {format_cost(str(total_potential_savings), 'USD')}"
        )

        if total_current_cost > 0:
            savings_percentage = (total_potential_savings / total_current_cost) * 100
            typer.echo(f"📊 Potential savings: {savings_percentage:.1f}%")

        typer.echo()
        typer.echo(f"{ANALYSIS_EMOJI} Savings Breakdown:")
        for category, savings in sorted(
            savings_breakdown.items(), key=lambda x: x[1], reverse=True
        ):
            if savings > 0:
                percentage = (
                    (savings / total_current_cost * 100)
                    if total_current_cost > 0
                    else 0
                )
                typer.echo(
                    f"  💰 {category:<25} {format_cost(str(savings), 'USD'):>10} ({percentage:.1f}%)"
                )

        # Annual projections
        annual_savings = total_potential_savings * 12
        typer.echo()
        typer.echo(f"{FORECAST_EMOJI} Annual Projections:")
        typer.echo(
            f"  📅 Annual savings potential: {format_cost(str(annual_savings), 'USD')}"
        )
        typer.echo(
            f"  📈 ROI timeline: {format_cost(str(total_current_cost * 0.1), 'USD')} initial investment"
        )

        # Recommendations
        typer.echo()
        typer.echo(f"{TIP_EMOJI} Implementation Recommendations:")
        if total_potential_savings > total_current_cost * 0.1:  # More than 10% savings
            typer.echo(
                f"  {BEST_PRACTICE_EMOJI} High savings potential - prioritize implementation"
            )
            typer.echo(
                f"  {BEST_PRACTICE_EMOJI} Start with Reserved Instances for immediate savings"
            )
            typer.echo(f"  {BEST_PRACTICE_EMOJI} Implement automated resource cleanup")
        else:
            typer.echo(
                f"  {INFO_EMOJI} Moderate savings potential - focus on high-impact areas"
            )
            typer.echo(
                f"  {BEST_PRACTICE_EMOJI} Review and optimize largest cost centers first"
            )

        typer.echo(
            f"  {AVOID_EMOJI} Don't implement all changes at once - test gradually"
        )

    except Exception as e:
        typer.echo(f"{DANGER_EMOJI} {ERROR_EMOJI} Error calculating savings: {e}")
        raise typer.Exit(1)
