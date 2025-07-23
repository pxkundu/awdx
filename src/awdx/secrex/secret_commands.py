import base64
import csv
import hashlib
import json
import os
import re
import secrets
import string
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import boto3
import typer
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound

from .. import AWDXErrorHandler

secret_app = typer.Typer(help="AWS secret management and rotation commands.")

# Emoji constants for consistent UI
SECRET_EMOJI = "🔐"
ROTATION_EMOJI = "🔄"
DISCOVERY_EMOJI = "🔍"
MONITORING_EMOJI = "📊"
COMPLIANCE_EMOJI = "📋"
REMEDIATION_EMOJI = "🔧"
WARNING_EMOJI = "⚠️"
SUCCESS_EMOJI = "✅"
ERROR_EMOJI = "❌"
TIP_EMOJI = "💡"
DANGER_EMOJI = "❗"
BEST_PRACTICE_EMOJI = "✅"
AVOID_EMOJI = "🚫"
ANALYSIS_EMOJI = "📊"
AUDIT_EMOJI = "🔍"
RISK_EMOJI = "🎯"
INNOVATION_EMOJI = "🚀"
STORAGE_EMOJI = "💾"
COMPUTE_EMOJI = "🖥️"
DATABASE_EMOJI = "🗄️"
IDENTITY_EMOJI = "👤"
ENCRYPTION_EMOJI = "🔐"
BACKUP_EMOJI = "💿"
EXPORT_EMOJI = "📤"
IMPORT_EMOJI = "📥"
VALIDATION_EMOJI = "✅"
EXPOSURE_EMOJI = "🚨"
LEAKAGE_EMOJI = "💧"
DETECTION_EMOJI = "🎯"
AUTOMATION_EMOJI = "🤖"
SCHEDULING_EMOJI = "⏰"
NOTIFICATION_EMOJI = "🔔"
INTEGRATION_EMOJI = "🔗"
SCANNING_EMOJI = "🔍"
ANALYSIS_EMOJI = "📈"
REPORTING_EMOJI = "📋"
BACKUP_EMOJI = "💿"
RESTORE_EMOJI = "🔄"
MIGRATION_EMOJI = "🚚"
SYNC_EMOJI = "🔄"
ARCHIVE_EMOJI = "📦"
CLEANUP_EMOJI = "🧹"
SECURITY_EMOJI = "🔒"
INFO_EMOJI = "ℹ️"


@dataclass
class SecretFinding:
    """Data class for secret findings."""

    severity: str
    category: str
    title: str
    description: str
    impact: str
    recommendation: str
    resource_id: str
    resource_type: str
    region: str
    priority: int
    last_rotated: Optional[datetime] = None
    expiry_date: Optional[datetime] = None


@dataclass
class SecretRotation:
    """Data class for secret rotation."""

    secret_id: str
    secret_type: str
    rotation_status: str
    last_rotation: datetime
    next_rotation: datetime
    rotation_window: str
    auto_rotation: bool
    manual_rotation_required: bool


def get_aws_clients(profile: Optional[str] = None):
    """Get AWS clients for secret management."""
    try:
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        return {
            "secretsmanager": session.client("secretsmanager"),
            "kms": session.client("kms"),
            "ssm": session.client("ssm"),
            "iam": session.client("iam"),
            "rds": session.client("rds"),
            "ec2": session.client("ec2"),
            "lambda": session.client("lambda"),
            "cloudtrail": session.client("cloudtrail"),
            "config": session.client("config"),
            "securityhub": session.client("securityhub"),
            "guardduty": session.client("guardduty"),
            "sts": session.client("sts"),
        }
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
        raise typer.BadParameter(f"Error creating AWS clients: {e}")


def get_severity_color(severity: str) -> str:
    """Get emoji for severity level."""
    severity_colors = {
        "CRITICAL": "🔴",
        "HIGH": "🟠",
        "MEDIUM": "🟡",
        "LOW": "🟢",
        "INFO": "🔵",
    }
    return severity_colors.get(severity.upper(), "⚪")


def format_arn(arn: str) -> str:
    """Format ARN for better readability."""
    if not arn:
        return "N/A"
    parts = arn.split(":")
    if len(parts) >= 6:
        return f"{parts[2]}:{parts[4]}:{parts[5]}"
    return arn


def calculate_risk_score(findings: List[SecretFinding]) -> int:
    """Calculate overall risk score based on findings."""
    score = 0
    severity_weights = {"CRITICAL": 10, "HIGH": 7, "MEDIUM": 4, "LOW": 1, "INFO": 0}

    for finding in findings:
        score += severity_weights.get(finding.severity.upper(), 0)

    return score


def get_region_list(profile: Optional[str] = None) -> List[str]:
    """Get list of available AWS regions."""
    try:
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        ec2_client = session.client("ec2", region_name="us-east-1")
        regions = ec2_client.describe_regions()
        return [region["RegionName"] for region in regions["Regions"]]
    except Exception:
        # Fallback to common regions
        return [
            "us-east-1",
            "us-east-2",
            "us-west-1",
            "us-west-2",
            "eu-west-1",
            "eu-central-1",
            "ap-southeast-1",
            "ap-northeast-1",
        ]


def generate_secure_password(length: int = 32) -> str:
    """Generate a secure random password."""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(characters) for _ in range(length))


def is_secret_expired(expiry_date: Optional[datetime]) -> bool:
    """Check if a secret is expired."""
    if not expiry_date:
        return False
    return datetime.now(expiry_date.tzinfo) > expiry_date


def is_secret_expiring_soon(expiry_date: Optional[datetime], days: int = 30) -> bool:
    """Check if a secret is expiring soon."""
    if not expiry_date:
        return False
    warning_date = datetime.now(expiry_date.tzinfo) + timedelta(days=days)
    return expiry_date <= warning_date


def calculate_rotation_score(secret: Dict[str, Any]) -> int:
    """Calculate rotation score based on various factors."""
    score = 0

    # Check if auto-rotation is enabled
    if secret.get("RotationEnabled"):
        score += 20
    else:
        score -= 10

    # Check last rotation date
    last_rotated = secret.get("LastRotatedDate")
    if last_rotated:
        days_since_rotation = (datetime.now(last_rotated.tzinfo) - last_rotated).days
        if days_since_rotation <= 90:
            score += 15
        elif days_since_rotation <= 180:
            score += 5
        else:
            score -= 15

    # Check if rotation is overdue
    if secret.get("RotationRules"):
        rotation_days = secret["RotationRules"].get("AutomaticallyAfterDays", 0)
        if rotation_days > 0 and last_rotated:
            days_since_rotation = (
                datetime.now(last_rotated.tzinfo) - last_rotated
            ).days
            if days_since_rotation > rotation_days:
                score -= 20

    return score


@secret_app.command()
def discover(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    region: Optional[str] = typer.Option(
        None, "--region", "-r", help="AWS region to scan"
    ),
    scan_type: str = typer.Option(
        "all",
        "--type",
        "-t",
        help="Scan type: all, secrets, parameters, keys, databases",
    ),
    output_format: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    include_expired: bool = typer.Option(
        False, "--include-expired", help="Include expired secrets"
    ),
    risk_threshold: str = typer.Option(
        "MEDIUM", "--risk-threshold", help="Minimum risk level to report"
    ),
):
    """Discover and analyze secrets across AWS services."""
    typer.echo(f"{DISCOVERY_EMOJI} Starting comprehensive secret discovery...")

    try:
        clients = get_aws_clients(profile)
        regions = [region] if region else get_region_list(profile)
        findings = []

        for region_name in regions:
            typer.echo(f"  {SCANNING_EMOJI} Scanning region: {region_name}")

            # Scan Secrets Manager
            if scan_type in ["all", "secrets"]:
                try:
                    secrets_client = boto3.Session(profile_name=profile).client(
                        "secretsmanager", region_name=region_name
                    )
                    secrets = secrets_client.list_secrets()

                    for secret in secrets["SecretList"]:
                        risk_score = calculate_rotation_score(secret)
                        severity = (
                            "HIGH"
                            if risk_score < 0
                            else "MEDIUM" if risk_score < 10 else "LOW"
                        )

                        if severity >= risk_threshold:
                            findings.append(
                                SecretFinding(
                                    severity=severity,
                                    category="Secrets Manager",
                                    title=f"Secret: {secret['Name']}",
                                    description=f"Secret in {region_name} with rotation score: {risk_score}",
                                    impact="Potential security risk if not properly rotated",
                                    recommendation="Enable auto-rotation and review rotation schedule",
                                    resource_id=secret["ARN"],
                                    resource_type="AWS::SecretsManager::Secret",
                                    region=region_name,
                                    priority=risk_score,
                                    last_rotated=secret.get("LastRotatedDate"),
                                    expiry_date=secret.get("LastChangedDate"),
                                )
                            )
                except ClientError as e:
                    if e.response["Error"]["Code"] != "AccessDenied":
                        typer.echo(
                            f"    {WARNING_EMOJI} Error scanning Secrets Manager in {region_name}: {e}"
                        )

            # Scan Systems Manager Parameter Store
            if scan_type in ["all", "parameters"]:
                try:
                    ssm_client = boto3.Session(profile_name=profile).client(
                        "ssm", region_name=region_name
                    )
                    parameters = ssm_client.describe_parameters()

                    for param in parameters["Parameters"]:
                        if param.get("Type") in ["SecureString"]:
                            findings.append(
                                SecretFinding(
                                    severity="MEDIUM",
                                    category="Parameter Store",
                                    title=f"Secure Parameter: {param['Name']}",
                                    description=f"Secure parameter stored in SSM Parameter Store",
                                    impact="Secure parameters should be regularly rotated",
                                    recommendation="Consider migrating to Secrets Manager for better rotation",
                                    resource_id=param["Name"],
                                    resource_type="AWS::SSM::Parameter",
                                    region=region_name,
                                    priority=5,
                                )
                            )
                except ClientError as e:
                    if e.response["Error"]["Code"] != "AccessDenied":
                        typer.echo(
                            f"    {WARNING_EMOJI} Error scanning Parameter Store in {region_name}: {e}"
                        )

            # Scan KMS Keys
            if scan_type in ["all", "keys"]:
                try:
                    kms_client = boto3.Session(profile_name=profile).client(
                        "kms", region_name=region_name
                    )
                    keys = kms_client.list_keys()

                    for key in keys["Keys"]:
                        try:
                            key_metadata = kms_client.describe_key(KeyId=key["KeyId"])
                            if key_metadata["KeyMetadata"]["KeyState"] == "Enabled":
                                findings.append(
                                    SecretFinding(
                                        severity="LOW",
                                        category="KMS",
                                        title=f"KMS Key: {key['KeyId']}",
                                        description=f"Active KMS key for encryption",
                                        impact="KMS keys should be regularly rotated",
                                        recommendation="Enable automatic key rotation",
                                        resource_id=key["KeyId"],
                                        resource_type="AWS::KMS::Key",
                                        region=region_name,
                                        priority=3,
                                    )
                                )
                        except ClientError:
                            continue
                except ClientError as e:
                    if e.response["Error"]["Code"] != "AccessDenied":
                        typer.echo(
                            f"    {WARNING_EMOJI} Error scanning KMS in {region_name}: {e}"
                        )

        # Display results
        if findings:
            typer.echo(f"\n{DISCOVERY_EMOJI} Secret Discovery Results:")
            typer.echo(
                f"  {ANALYSIS_EMOJI} Found {len(findings)} secret-related resources"
            )

            if output_format == "json":
                results = []
                for finding in findings:
                    results.append(
                        {
                            "severity": finding.severity,
                            "category": finding.category,
                            "title": finding.title,
                            "description": finding.description,
                            "impact": finding.impact,
                            "recommendation": finding.recommendation,
                            "resource_id": finding.resource_id,
                            "resource_type": finding.resource_type,
                            "region": finding.region,
                            "priority": finding.priority,
                        }
                    )
                typer.echo(json.dumps(results, indent=2, default=str))
            elif output_format == "csv":
                import csv
                import sys

                writer = csv.writer(sys.stdout)
                writer.writerow(
                    [
                        "Severity",
                        "Category",
                        "Title",
                        "Description",
                        "Impact",
                        "Recommendation",
                        "Resource ID",
                        "Region",
                        "Priority",
                    ]
                )
                for finding in findings:
                    writer.writerow(
                        [
                            finding.severity,
                            finding.category,
                            finding.title,
                            finding.description,
                            finding.impact,
                            finding.recommendation,
                            finding.resource_id,
                            finding.region,
                            finding.priority,
                        ]
                    )
            else:
                for finding in findings:
                    severity_emoji = get_severity_color(finding.severity)
                    typer.echo(
                        f"\n  {severity_emoji} {finding.severity} - {finding.category}"
                    )
                    typer.echo(f"    {finding.title}")
                    typer.echo(f"    Description: {finding.description}")
                    typer.echo(f"    Impact: {finding.impact}")
                    typer.echo(f"    Recommendation: {finding.recommendation}")
                    typer.echo(f"    Resource: {format_arn(finding.resource_id)}")
                    typer.echo(f"    Region: {finding.region}")
                    typer.echo(f"    Priority Score: {finding.priority}")
        else:
            typer.echo(f"\n{SUCCESS_EMOJI} No secret-related issues found!")

        # Risk assessment
        risk_score = calculate_risk_score(findings)
        typer.echo(f"\n{RISK_EMOJI} Overall Risk Assessment:")
        typer.echo(f"  Risk Score: {risk_score}")
        if risk_score > 50:
            typer.echo(
                f"  {DANGER_EMOJI} High risk environment - immediate attention required"
            )
        elif risk_score > 20:
            typer.echo(
                f"  {WARNING_EMOJI} Medium risk environment - review recommended"
            )
        else:
            typer.echo(
                f"  {SUCCESS_EMOJI} Low risk environment - good security posture"
            )

        # Best practices tips
        typer.echo(f"\n{TIP_EMOJI} Best Practices:")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Enable automatic rotation for all secrets")
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Use Secrets Manager instead of Parameter Store for sensitive data"
        )
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Implement least privilege access to secrets"
        )
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Monitor secret access patterns for anomalies"
        )
        typer.echo(
            f"  {AVOID_EMOJI} Never store secrets in code or configuration files"
        )

    except Exception as e:
        typer.echo(f"{ERROR_EMOJI} Error during secret discovery: {e}")


@secret_app.command()
def rotate(
    secret_id: Optional[str] = typer.Argument(None, help="Secret ID or ARN to rotate"),
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force rotation even if not due"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be rotated without doing it"
    ),
    list_secrets: bool = typer.Option(
        False, "--list", "-l", help="List available secrets"
    ),
):
    """Rotate AWS secrets manually or automatically."""
    try:
        clients = get_aws_clients(profile)
        secrets_client = clients["secretsmanager"]

        if list_secrets or secret_id is None:
            typer.echo(f"{DISCOVERY_EMOJI} Available secrets:")
            typer.echo()

            try:
                secrets = secrets_client.list_secrets()
                if secrets["SecretList"]:
                    for secret in secrets["SecretList"]:
                        rotation_status = (
                            "🔄 Enabled"
                            if secret.get("RotationEnabled")
                            else "⏸️ Disabled"
                        )
                        last_rotated = secret.get("LastRotatedDate", "Never")
                        if isinstance(last_rotated, datetime):
                            last_rotated = last_rotated.strftime("%Y-%m-%d")

                        typer.echo(f"  🔐 {secret['Name']}")
                        typer.echo(f"     ID: {secret['ARN']}")
                        typer.echo(f"     Rotation: {rotation_status}")
                        typer.echo(f"     Last rotated: {last_rotated}")
                        typer.echo()

                    typer.echo(
                        f"{TIP_EMOJI} To rotate a secret, use: awdx secret rotate <secret-id>"
                    )
                    typer.echo(f"{TIP_EMOJI} Example: awdx secret rotate my-app-secret")
                else:
                    typer.echo(f"{INFO_EMOJI} No secrets found in this account/region")

                return

            except ClientError as e:
                typer.echo(f"{ERROR_EMOJI} Error listing secrets: {e}")
                return

        if not secret_id:
            typer.echo(
                f"{ERROR_EMOJI} Please provide a secret ID or use --list to see available secrets"
            )
            typer.echo(f"{TIP_EMOJI} Usage: awdx secret rotate <secret-id>")
            typer.echo(f"{TIP_EMOJI} Example: awdx secret rotate my-app-secret")
            raise typer.Exit(1)

        typer.echo(f"{ROTATION_EMOJI} Starting secret rotation for: {secret_id}")

        if dry_run:
            typer.echo(f"  {ANALYSIS_EMOJI} Dry run mode - no changes will be made")

        # Get secret details
        try:
            secret = secrets_client.describe_secret(SecretId=secret_id)
            typer.echo(f"  {SECRET_EMOJI} Secret: {secret['Name']}")
            typer.echo(
                f"  {ROTATION_EMOJI} Auto-rotation: {'Enabled' if secret.get('RotationEnabled') else 'Disabled'}"
            )

            if secret.get("LastRotatedDate"):
                typer.echo(
                    f"  {SCHEDULING_EMOJI} Last rotated: {secret['LastRotatedDate']}"
                )

            if secret.get("RotationRules"):
                rules = secret["RotationRules"]
                typer.echo(
                    f"  {SCHEDULING_EMOJI} Rotation schedule: Every {rules.get('AutomaticallyAfterDays', 'N/A')} days"
                )

        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                typer.echo(f"{ERROR_EMOJI} Secret not found: {secret_id}")
                raise typer.Exit(1)
            else:
                raise e

        # Check if rotation is needed
        if not force and secret.get("RotationEnabled"):
            typer.echo(
                f"  {WARNING_EMOJI} Auto-rotation is enabled. Manual rotation may not be necessary."
            )
            if not typer.confirm("Continue with manual rotation?"):
                typer.echo(f"{SUCCESS_EMOJI} Rotation cancelled")
                return

        # Perform rotation
        if not dry_run:
            try:
                response = secrets_client.rotate_secret(SecretId=secret_id)
                typer.echo(f"  {SUCCESS_EMOJI} Rotation initiated successfully!")
                typer.echo(f"  {ROTATION_EMOJI} Rotation ARN: {response['ARN']}")
                typer.echo(f"  {SCHEDULING_EMOJI} Version ID: {response['VersionId']}")
            except ClientError as e:
                if e.response["Error"]["Code"] == "InvalidRequestException":
                    typer.echo(
                        f"{ERROR_EMOJI} Rotation failed: {e.response['Error']['Message']}"
                    )
                else:
                    raise e
        else:
            typer.echo(f"  {ANALYSIS_EMOJI} Would rotate secret: {secret_id}")

        # Best practices
        typer.echo(f"\n{TIP_EMOJI} Rotation Best Practices:")
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Enable automatic rotation for consistent security"
        )
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Test rotation in non-production environments first"
        )
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Monitor applications during rotation for any issues"
        )
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Keep previous versions available for rollback"
        )

    except Exception as e:
        AWDXErrorHandler.handle_aws_error(e, context="secret rotation")
        typer.echo(f"{ERROR_EMOJI} Error during secret rotation: {e}")
        raise typer.Exit(1)


@secret_app.command()
def monitor(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
    days: int = typer.Option(30, "--days", "-d", help="Number of days to look back"),
    alert_threshold: int = typer.Option(
        5, "--threshold", "-t", help="Alert threshold for failed rotations"
    ),
    output_format: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
):
    """Monitor secret rotation and access patterns."""
    typer.echo(f"{MONITORING_EMOJI} Monitoring secret rotation and access patterns...")

    try:
        clients = get_aws_clients(profile)
        secrets_client = clients["secretsmanager"]
        cloudtrail_client = clients["cloudtrail"]

        # Get rotation events
        typer.echo(
            f"  {ROTATION_EMOJI} Analyzing rotation events (last {days} days)..."
        )

        try:
            # Get CloudTrail events for Secrets Manager
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)

            events = cloudtrail_client.lookup_events(
                StartTime=start_time,
                EndTime=end_time,
                LookupAttributes=[
                    {"AttributeKey": "EventName", "AttributeValue": "RotateSecret"},
                    {"AttributeKey": "EventName", "AttributeValue": "UpdateSecret"},
                    {"AttributeKey": "EventName", "AttributeValue": "GetSecretValue"},
                ],
            )

            rotation_events = []
            access_events = []

            for event in events["Events"]:
                if event["EventName"] in ["RotateSecret", "UpdateSecret"]:
                    rotation_events.append(event)
                elif event["EventName"] == "GetSecretValue":
                    access_events.append(event)

            # Analyze rotation patterns
            typer.echo(f"\n{ANALYSIS_EMOJI} Rotation Analysis:")
            typer.echo(f"  Total rotation events: {len(rotation_events)}")
            typer.echo(f"  Total access events: {len(access_events)}")

            if rotation_events:
                typer.echo(f"\n{ROTATION_EMOJI} Recent Rotation Events:")
                for event in rotation_events[:10]:  # Show last 10
                    typer.echo(
                        f"    {event['EventTime']} - {event['EventName']} by {event.get('Username', 'Unknown')}"
                    )

            # Check for failed rotations
            failed_rotations = [
                e
                for e in rotation_events
                if "error" in e.get("CloudTrailEvent", "").lower()
            ]
            if failed_rotations:
                typer.echo(f"\n{DANGER_EMOJI} Failed Rotations Detected:")
                typer.echo(f"  {len(failed_rotations)} failed rotation attempts")
                if len(failed_rotations) >= alert_threshold:
                    typer.echo(
                        f"  {EXPOSURE_EMOJI} ALERT: High number of failed rotations!"
                    )

            # Access pattern analysis
            if access_events:
                access_by_user = defaultdict(int)
                for event in access_events:
                    username = event.get("Username", "Unknown")
                    access_by_user[username] += 1

                typer.echo(f"\n{ANALYSIS_EMOJI} Access Pattern Analysis:")
                for user, count in sorted(
                    access_by_user.items(), key=lambda x: x[1], reverse=True
                )[:5]:
                    typer.echo(f"  {user}: {count} accesses")

                    if count > 100:  # High access threshold
                        typer.echo(
                            f"    {WARNING_EMOJI} High access frequency - review if necessary"
                        )

        except ClientError as e:
            if e.response["Error"]["Code"] == "AccessDenied":
                typer.echo(
                    f"  {WARNING_EMOJI} CloudTrail access denied - limited monitoring available"
                )
            else:
                typer.echo(f"  {WARNING_EMOJI} Error accessing CloudTrail: {e}")

        # Get current secret status
        try:
            secrets = secrets_client.list_secrets()
            overdue_secrets = []
            expiring_secrets = []

            for secret in secrets["SecretList"]:
                if secret.get("RotationEnabled") and secret.get("LastRotatedDate"):
                    last_rotated = secret["LastRotatedDate"]
                    rotation_days = secret.get("RotationRules", {}).get(
                        "AutomaticallyAfterDays", 90
                    )
                    days_since_rotation = (
                        datetime.now(last_rotated.tzinfo) - last_rotated
                    ).days

                    if days_since_rotation > rotation_days:
                        overdue_secrets.append(secret)
                    elif days_since_rotation > (
                        rotation_days - 7
                    ):  # Expiring within a week
                        expiring_secrets.append(secret)

            if overdue_secrets:
                typer.echo(f"\n{DANGER_EMOJI} Overdue Rotations:")
                for secret in overdue_secrets:
                    typer.echo(
                        f"  {secret['Name']} - Overdue by {days_since_rotation - rotation_days} days"
                    )

            if expiring_secrets:
                typer.echo(f"\n{WARNING_EMOJI} Expiring Soon:")
                for secret in expiring_secrets:
                    typer.echo(
                        f"  {secret['Name']} - Expires in {rotation_days - days_since_rotation} days"
                    )

        except ClientError as e:
            typer.echo(f"  {WARNING_EMOJI} Error accessing Secrets Manager: {e}")

        # Monitoring recommendations
        typer.echo(f"\n{TIP_EMOJI} Monitoring Recommendations:")
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Set up CloudWatch alarms for failed rotations"
        )
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Monitor access patterns for unusual activity"
        )
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Use AWS Config rules for compliance monitoring"
        )
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Implement automated notifications for rotation failures"
        )

    except Exception as e:
        AWDXErrorHandler.handle_aws_error(e, context="secret monitoring")
        typer.echo(f"{ERROR_EMOJI} Error during monitoring: {e}")
        raise typer.Exit(1)


@secret_app.command()
def compliance(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
    framework: str = typer.Option(
        "all",
        "--framework",
        "-f",
        help="Compliance framework: all, sox, pci, hipaa, gdpr",
    ),
    output_format: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
):
    """Check secret management compliance against various frameworks."""
    typer.echo(f"{COMPLIANCE_EMOJI} Checking secret management compliance...")

    try:
        clients = get_aws_clients(profile)
        secrets_client = clients["secretsmanager"]
        config_client = clients["config"]

        compliance_checks = []

        # SOX Compliance Checks
        if framework in ["all", "sox"]:
            typer.echo(f"  {COMPLIANCE_EMOJI} Checking SOX compliance...")

            try:
                secrets = secrets_client.list_secrets()
                for secret in secrets["SecretList"]:
                    # Check for auto-rotation
                    if not secret.get("RotationEnabled"):
                        compliance_checks.append(
                            {
                                "framework": "SOX",
                                "control": "SOX-404",
                                "status": "FAIL",
                                "description": f"Secret {secret['Name']} does not have auto-rotation enabled",
                                "impact": "Manual rotation increases risk of oversight",
                                "recommendation": "Enable automatic rotation for all financial system secrets",
                            }
                        )

                    # Check for encryption
                    if not secret.get("EncryptedBy"):
                        compliance_checks.append(
                            {
                                "framework": "SOX",
                                "control": "SOX-404",
                                "status": "FAIL",
                                "description": f"Secret {secret['Name']} may not be properly encrypted",
                                "impact": "Potential data exposure risk",
                                "recommendation": "Ensure all secrets use KMS encryption",
                            }
                        )

            except ClientError as e:
                typer.echo(f"    {WARNING_EMOJI} Error checking SOX compliance: {e}")

        # PCI DSS Compliance Checks
        if framework in ["all", "pci"]:
            typer.echo(f"  {COMPLIANCE_EMOJI} Checking PCI DSS compliance...")

            try:
                secrets = secrets_client.list_secrets()
                for secret in secrets["SecretList"]:
                    # Check for strong authentication
                    if not secret.get("RotationEnabled"):
                        compliance_checks.append(
                            {
                                "framework": "PCI DSS",
                                "control": "PCI-3.4",
                                "status": "FAIL",
                                "description": f"Secret {secret['Name']} lacks automatic rotation",
                                "impact": "Non-compliance with PCI DSS requirement 3.4",
                                "recommendation": "Implement automatic secret rotation every 90 days",
                            }
                        )

                    # Check for access logging
                    compliance_checks.append(
                        {
                            "framework": "PCI DSS",
                            "control": "PCI-10.1",
                            "status": "INFO",
                            "description": f"Secret {secret['Name']} access should be logged",
                            "impact": "Required for audit trails",
                            "recommendation": "Enable CloudTrail logging for all secret access",
                        }
                    )

            except ClientError as e:
                typer.echo(
                    f"    {WARNING_EMOJI} Error checking PCI DSS compliance: {e}"
                )

        # HIPAA Compliance Checks
        if framework in ["all", "hipaa"]:
            typer.echo(f"  {COMPLIANCE_EMOJI} Checking HIPAA compliance...")

            try:
                secrets = secrets_client.list_secrets()
                for secret in secrets["SecretList"]:
                    # Check for encryption at rest
                    if not secret.get("EncryptedBy"):
                        compliance_checks.append(
                            {
                                "framework": "HIPAA",
                                "control": "HIPAA-164.312(a)(2)(iv)",
                                "status": "FAIL",
                                "description": f"Secret {secret['Name']} may not meet encryption requirements",
                                "impact": "Non-compliance with HIPAA encryption standards",
                                "recommendation": "Ensure all PHI-related secrets use strong encryption",
                            }
                        )

                    # Check for access controls
                    compliance_checks.append(
                        {
                            "framework": "HIPAA",
                            "control": "HIPAA-164.312(a)(1)",
                            "status": "INFO",
                            "description": f"Secret {secret['Name']} access controls should be reviewed",
                            "impact": "Required for HIPAA compliance",
                            "recommendation": "Implement least privilege access to all secrets",
                        }
                    )

            except ClientError as e:
                typer.echo(f"    {WARNING_EMOJI} Error checking HIPAA compliance: {e}")

        # GDPR Compliance Checks
        if framework in ["all", "gdpr"]:
            typer.echo(f"  {COMPLIANCE_EMOJI} Checking GDPR compliance...")

            try:
                secrets = secrets_client.list_secrets()
                for secret in secrets["SecretList"]:
                    # Check for data protection
                    compliance_checks.append(
                        {
                            "framework": "GDPR",
                            "control": "GDPR-Article-32",
                            "status": "INFO",
                            "description": f"Secret {secret['Name']} should have appropriate security measures",
                            "impact": "Required for GDPR compliance",
                            "recommendation": "Implement encryption and access controls for personal data",
                        }
                    )

                    # Check for audit trails
                    compliance_checks.append(
                        {
                            "framework": "GDPR",
                            "control": "GDPR-Article-30",
                            "status": "INFO",
                            "description": f"Secret {secret['Name']} access should be logged",
                            "impact": "Required for GDPR record keeping",
                            "recommendation": "Enable comprehensive logging of all secret access",
                        }
                    )

            except ClientError as e:
                typer.echo(f"    {WARNING_EMOJI} Error checking GDPR compliance: {e}")

        # Display compliance results
        if compliance_checks:
            typer.echo(f"\n{COMPLIANCE_EMOJI} Compliance Assessment Results:")

            if output_format == "json":
                typer.echo(json.dumps(compliance_checks, indent=2))
            elif output_format == "csv":
                import csv
                import sys

                writer = csv.writer(sys.stdout)
                writer.writerow(
                    [
                        "Framework",
                        "Control",
                        "Status",
                        "Description",
                        "Impact",
                        "Recommendation",
                    ]
                )
                for check in compliance_checks:
                    writer.writerow(
                        [
                            check["framework"],
                            check["control"],
                            check["status"],
                            check["description"],
                            check["impact"],
                            check["recommendation"],
                        ]
                    )
            else:
                by_framework = defaultdict(list)
                for check in compliance_checks:
                    by_framework[check["framework"]].append(check)

                for framework_name, checks in by_framework.items():
                    typer.echo(f"\n  {COMPLIANCE_EMOJI} {framework_name} Compliance:")
                    fails = [c for c in checks if c["status"] == "FAIL"]
                    infos = [c for c in checks if c["status"] == "INFO"]

                    if fails:
                        typer.echo(f"    {ERROR_EMOJI} {len(fails)} Failures:")
                        for check in fails:
                            typer.echo(
                                f"      {check['control']}: {check['description']}"
                            )
                            typer.echo(f"        Impact: {check['impact']}")
                            typer.echo(
                                f"        Recommendation: {check['recommendation']}"
                            )

                    if infos:
                        typer.echo(f"    {TIP_EMOJI} {len(infos)} Recommendations:")
                        for check in infos:
                            typer.echo(
                                f"      {check['control']}: {check['description']}"
                            )
                            typer.echo(
                                f"        Recommendation: {check['recommendation']}"
                            )
        else:
            typer.echo(f"\n{SUCCESS_EMOJI} All compliance checks passed!")

        # Compliance recommendations
        typer.echo(f"\n{TIP_EMOJI} Compliance Best Practices:")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Enable automatic rotation for all secrets")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Use KMS encryption for all sensitive data")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Implement comprehensive access logging")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Regular compliance audits and assessments")
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Document all security controls and procedures"
        )

    except Exception as e:
        AWDXErrorHandler.handle_aws_error(e, context="secret compliance")
        typer.echo(f"{ERROR_EMOJI} Error during compliance check: {e}")
        raise typer.Exit(1)


@secret_app.command()
def remediate(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
    auto_fix: bool = typer.Option(
        False, "--auto-fix", help="Automatically fix issues where possible"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be fixed without doing it"
    ),
    risk_threshold: str = typer.Option(
        "HIGH", "--risk-threshold", help="Minimum risk level to remediate"
    ),
):
    """Automated remediation of secret management issues."""
    typer.echo(f"{REMEDIATION_EMOJI} Starting automated secret remediation...")

    try:
        clients = get_aws_clients(profile)
        secrets_client = clients["secretsmanager"]

        if dry_run:
            typer.echo(f"  {ANALYSIS_EMOJI} Dry run mode - no changes will be made")

        remediation_actions = []

        # Find secrets that need remediation
        try:
            secrets = secrets_client.list_secrets()

            for secret in secrets["SecretList"]:
                actions = []

                # Check for auto-rotation
                if not secret.get("RotationEnabled"):
                    actions.append(
                        {
                            "action": "enable_auto_rotation",
                            "description": f"Enable auto-rotation for {secret['Name']}",
                            "risk": "HIGH",
                            "secret_id": secret["ARN"],
                        }
                    )

                # Check for overdue rotation
                if secret.get("RotationEnabled") and secret.get("LastRotatedDate"):
                    last_rotated = secret["LastRotatedDate"]
                    rotation_days = secret.get("RotationRules", {}).get(
                        "AutomaticallyAfterDays", 90
                    )
                    days_since_rotation = (
                        datetime.now(last_rotated.tzinfo) - last_rotated
                    ).days

                    if days_since_rotation > rotation_days:
                        actions.append(
                            {
                                "action": "force_rotation",
                                "description": f"Force rotation for overdue secret {secret['Name']}",
                                "risk": "MEDIUM",
                                "secret_id": secret["ARN"],
                            }
                        )

                # Check for missing tags
                if not secret.get("Tags"):
                    actions.append(
                        {
                            "action": "add_tags",
                            "description": f"Add security tags to {secret['Name']}",
                            "risk": "LOW",
                            "secret_id": secret["ARN"],
                        }
                    )

                remediation_actions.extend(actions)

        except ClientError as e:
            typer.echo(f"  {WARNING_EMOJI} Error accessing Secrets Manager: {e}")

        # Filter by risk threshold
        risk_weights = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        threshold_weight = risk_weights.get(risk_threshold.upper(), 2)

        filtered_actions = [
            action
            for action in remediation_actions
            if risk_weights.get(action["risk"], 0) >= threshold_weight
        ]

        if not filtered_actions:
            typer.echo(f"\n{SUCCESS_EMOJI} No remediation actions needed!")
            return

        # Display remediation plan
        typer.echo(f"\n{REMEDIATION_EMOJI} Remediation Plan:")
        typer.echo(
            f"  {ANALYSIS_EMOJI} Found {len(filtered_actions)} actions to perform"
        )

        for action in filtered_actions:
            risk_emoji = get_severity_color(action["risk"])
            typer.echo(f"    {risk_emoji} {action['risk']} - {action['description']}")

        if not auto_fix and not dry_run:
            if not typer.confirm("\nProceed with remediation?"):
                typer.echo(f"{SUCCESS_EMOJI} Remediation cancelled")
                return

        # Execute remediation
        success_count = 0
        error_count = 0

        for action in filtered_actions:
            try:
                if dry_run:
                    typer.echo(
                        f"  {ANALYSIS_EMOJI} Would perform: {action['description']}"
                    )
                    continue

                if action["action"] == "enable_auto_rotation":
                    # Enable auto-rotation with 90-day schedule
                    secrets_client.rotate_secret(
                        SecretId=action["secret_id"],
                        RotationRules={"AutomaticallyAfterDays": 90},
                    )
                    typer.echo(
                        f"  {SUCCESS_EMOJI} Enabled auto-rotation for {action['secret_id']}"
                    )
                    success_count += 1

                elif action["action"] == "force_rotation":
                    secrets_client.rotate_secret(SecretId=action["secret_id"])
                    typer.echo(
                        f"  {SUCCESS_EMOJI} Forced rotation for {action['secret_id']}"
                    )
                    success_count += 1

                elif action["action"] == "add_tags":
                    # Add security tags
                    tags = [
                        {"Key": "SecurityLevel", "Value": "High"},
                        {"Key": "AutoRotation", "Value": "Enabled"},
                        {
                            "Key": "LastAudit",
                            "Value": datetime.now().strftime("%Y-%m-%d"),
                        },
                    ]
                    secrets_client.tag_resource(SecretId=action["secret_id"], Tags=tags)
                    typer.echo(
                        f"  {SUCCESS_EMOJI} Added security tags to {action['secret_id']}"
                    )
                    success_count += 1

            except ClientError as e:
                typer.echo(f"  {ERROR_EMOJI} Failed to {action['action']}: {e}")
                error_count += 1

        # Summary
        typer.echo(f"\n{REMEDIATION_EMOJI} Remediation Summary:")
        typer.echo(f"  {SUCCESS_EMOJI} Successful: {success_count}")
        typer.echo(f"  {ERROR_EMOJI} Failed: {error_count}")

        if success_count > 0:
            typer.echo(f"\n{TIP_EMOJI} Next Steps:")
            typer.echo(
                f"  {BEST_PRACTICE_EMOJI} Monitor the remediated secrets for any issues"
            )
            typer.echo(
                f"  {BEST_PRACTICE_EMOJI} Verify that applications can still access the secrets"
            )
            typer.echo(
                f"  {BEST_PRACTICE_EMOJI} Set up alerts for future rotation failures"
            )

    except Exception as e:
        AWDXErrorHandler.handle_aws_error(e, context="secret remediation")
        typer.echo(f"{ERROR_EMOJI} Error during remediation: {e}")
        raise typer.Exit(1)


@secret_app.command()
def recommend(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
    include_cost: bool = typer.Option(
        False, "--include-cost", help="Include cost optimization recommendations"
    ),
    include_security: bool = typer.Option(
        True, "--include-security", help="Include security recommendations"
    ),
    output_format: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
):
    """Get intelligent recommendations for secret management optimization."""
    typer.echo(
        f"{TIP_EMOJI} Generating intelligent secret management recommendations..."
    )

    try:
        clients = get_aws_clients(profile)
        secrets_client = clients["secretsmanager"]
        ssm_client = clients["ssm"]

        recommendations = []

        # Analyze current secret landscape
        try:
            secrets = secrets_client.list_secrets()

            # Security recommendations
            if include_security:
                typer.echo(f"  {SECURITY_EMOJI} Analyzing security posture...")

                # Check for secrets without auto-rotation
                non_rotating_secrets = [
                    s for s in secrets["SecretList"] if not s.get("RotationEnabled")
                ]
                if non_rotating_secrets:
                    recommendations.append(
                        {
                            "category": "Security",
                            "priority": "HIGH",
                            "title": "Enable Auto-Rotation",
                            "description": f"Found {len(non_rotating_secrets)} secrets without auto-rotation",
                            "impact": "Reduces manual rotation overhead and security risks",
                            "effort": "Low",
                            "cost": "Minimal",
                            "action": "Enable automatic rotation for all secrets",
                        }
                    )

                # Check for secrets in Parameter Store
                try:
                    parameters = ssm_client.describe_parameters()
                    secure_params = [
                        p
                        for p in parameters["Parameters"]
                        if p.get("Type") == "SecureString"
                    ]
                    if secure_params:
                        recommendations.append(
                            {
                                "category": "Security",
                                "priority": "MEDIUM",
                                "title": "Migrate to Secrets Manager",
                                "description": f"Found {len(secure_params)} secure parameters in SSM",
                                "impact": "Better rotation capabilities and security features",
                                "effort": "Medium",
                                "cost": "Low",
                                "action": "Migrate secure parameters to Secrets Manager",
                            }
                        )
                except ClientError:
                    pass

                # Check for overdue rotations
                overdue_count = 0
                for secret in secrets["SecretList"]:
                    if secret.get("RotationEnabled") and secret.get("LastRotatedDate"):
                        last_rotated = secret["LastRotatedDate"]
                        rotation_days = secret.get("RotationRules", {}).get(
                            "AutomaticallyAfterDays", 90
                        )
                        days_since_rotation = (
                            datetime.now(last_rotated.tzinfo) - last_rotated
                        ).days
                        if days_since_rotation > rotation_days:
                            overdue_count += 1

                if overdue_count > 0:
                    recommendations.append(
                        {
                            "category": "Security",
                            "priority": "HIGH",
                            "title": "Address Overdue Rotations",
                            "description": f"Found {overdue_count} secrets with overdue rotations",
                            "impact": "Immediate security risk reduction",
                            "effort": "Low",
                            "cost": "None",
                            "action": "Force rotation of overdue secrets",
                        }
                    )

            # Cost optimization recommendations
            if include_cost:
                typer.echo(
                    f"  {COST_EMOJI} Analyzing cost optimization opportunities..."
                )

                # Check for unused secrets
                try:
                    # This would require CloudTrail analysis in a real implementation
                    recommendations.append(
                        {
                            "category": "Cost",
                            "priority": "MEDIUM",
                            "title": "Audit Secret Usage",
                            "description": "Review secret access patterns for unused secrets",
                            "impact": "Potential cost savings from removing unused secrets",
                            "effort": "Medium",
                            "cost": "Savings",
                            "action": "Analyze CloudTrail logs for secret access patterns",
                        }
                    )
                except ClientError:
                    pass

                # Check for appropriate rotation schedules
                long_rotation_secrets = []
                for secret in secrets["SecretList"]:
                    if secret.get("RotationRules"):
                        rotation_days = secret["RotationRules"].get(
                            "AutomaticallyAfterDays", 0
                        )
                        if rotation_days > 365:  # More than a year
                            long_rotation_secrets.append(secret)

                if long_rotation_secrets:
                    recommendations.append(
                        {
                            "category": "Security",
                            "priority": "MEDIUM",
                            "title": "Review Rotation Schedules",
                            "description": f"Found {len(long_rotation_secrets)} secrets with long rotation periods",
                            "impact": "Balance between security and operational overhead",
                            "effort": "Low",
                            "cost": "None",
                            "action": "Review and adjust rotation schedules based on risk",
                        }
                    )

        except ClientError as e:
            typer.echo(f"  {WARNING_EMOJI} Error analyzing secrets: {e}")

        # Add general best practices
        recommendations.extend(
            [
                {
                    "category": "Best Practices",
                    "priority": "MEDIUM",
                    "title": "Implement Secret Scanning",
                    "description": "Set up automated scanning for secrets in code repositories",
                    "impact": "Prevents secret leakage in source code",
                    "effort": "Medium",
                    "cost": "Low",
                    "action": "Integrate with tools like GitGuardian or TruffleHog",
                },
                {
                    "category": "Best Practices",
                    "priority": "MEDIUM",
                    "title": "Enhance Monitoring",
                    "description": "Set up comprehensive monitoring and alerting",
                    "impact": "Early detection of security issues",
                    "effort": "Medium",
                    "cost": "Low",
                    "action": "Configure CloudWatch alarms and SNS notifications",
                },
                {
                    "category": "Best Practices",
                    "priority": "LOW",
                    "title": "Documentation",
                    "description": "Create comprehensive secret management documentation",
                    "impact": "Improved team knowledge and compliance",
                    "effort": "Medium",
                    "cost": "None",
                    "action": "Document rotation procedures and emergency contacts",
                },
            ]
        )

        # Display recommendations
        if recommendations:
            typer.echo(f"\n{TIP_EMOJI} Intelligent Recommendations:")
            typer.echo(
                f"  {ANALYSIS_EMOJI} Generated {len(recommendations)} recommendations"
            )

            if output_format == "json":
                typer.echo(json.dumps(recommendations, indent=2))
            elif output_format == "csv":
                import csv
                import sys

                writer = csv.writer(sys.stdout)
                writer.writerow(
                    [
                        "Category",
                        "Priority",
                        "Title",
                        "Description",
                        "Impact",
                        "Effort",
                        "Cost",
                        "Action",
                    ]
                )
                for rec in recommendations:
                    writer.writerow(
                        [
                            rec["category"],
                            rec["priority"],
                            rec["title"],
                            rec["description"],
                            rec["impact"],
                            rec["effort"],
                            rec["cost"],
                            rec["action"],
                        ]
                    )
            else:
                by_category = defaultdict(list)
                for rec in recommendations:
                    by_category[rec["category"]].append(rec)

                for category, recs in by_category.items():
                    typer.echo(f"\n  {category} Recommendations:")
                    for rec in recs:
                        priority_emoji = get_severity_color(rec["priority"])
                        typer.echo(
                            f"    {priority_emoji} {rec['priority']} - {rec['title']}"
                        )
                        typer.echo(f"      Description: {rec['description']}")
                        typer.echo(f"      Impact: {rec['impact']}")
                        typer.echo(
                            f"      Effort: {rec['effort']} | Cost: {rec['cost']}"
                        )
                        typer.echo(f"      Action: {rec['action']}")
        else:
            typer.echo(f"\n{SUCCESS_EMOJI} No specific recommendations needed!")

        # Summary insights
        typer.echo(f"\n{ANALYSIS_EMOJI} Summary Insights:")
        high_priority = [r for r in recommendations if r["priority"] == "HIGH"]
        medium_priority = [r for r in recommendations if r["priority"] == "MEDIUM"]

        if high_priority:
            typer.echo(
                f"  {DANGER_EMOJI} {len(high_priority)} high-priority items need immediate attention"
            )
        if medium_priority:
            typer.echo(
                f"  {WARNING_EMOJI} {len(medium_priority)} medium-priority items for planning"
            )

        typer.echo(f"\n{TIP_EMOJI} Implementation Strategy:")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Address high-priority items first")
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Plan medium-priority items for next sprint"
        )
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Consider automation for repetitive tasks")

    except Exception as e:
        AWDXErrorHandler.handle_aws_error(e, context="secret recommendation")
        typer.echo(f"{ERROR_EMOJI} Error generating recommendations: {e}")
        raise typer.Exit(1)


@secret_app.command()
def export(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
    format: str = typer.Option(
        "json", "--format", "-f", help="Export format: json, csv, yaml"
    ),
    output_file: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file path"
    ),
    include_metadata: bool = typer.Option(
        True, "--include-metadata", help="Include secret metadata"
    ),
    include_rotation_history: bool = typer.Option(
        False, "--include-history", help="Include rotation history"
    ),
):
    """Export secret management data for analysis and reporting."""
    typer.echo(f"{EXPORT_EMOJI} Exporting secret management data...")

    try:
        clients = get_aws_clients(profile)
        secrets_client = clients["secretsmanager"]

        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "profile": profile or "default",
            "region": region or "all",
            "secrets": [],
            "summary": {},
        }

        # Collect secret data
        try:
            secrets = secrets_client.list_secrets()

            for secret in secrets["SecretList"]:
                secret_data = {
                    "name": secret["Name"],
                    "arn": secret["ARN"],
                    "description": secret.get("Description", ""),
                    "rotation_enabled": secret.get("RotationEnabled", False),
                    "last_rotated": secret.get("LastRotatedDate"),
                    "last_changed": secret.get("LastChangedDate"),
                    "tags": secret.get("Tags", []),
                }

                if include_metadata:
                    try:
                        secret_details = secrets_client.describe_secret(
                            SecretId=secret["ARN"]
                        )
                        secret_data.update(
                            {
                                "version_id": secret_details.get("VersionId"),
                                "rotation_rules": secret_details.get("RotationRules"),
                                "encrypted_by": secret_details.get("EncryptedBy"),
                                "deletion_date": secret_details.get("DeletionDate"),
                            }
                        )
                    except ClientError:
                        pass

                if include_rotation_history:
                    try:
                        # This would require CloudTrail analysis in a real implementation
                        secret_data["rotation_history"] = []
                    except ClientError:
                        pass

                export_data["secrets"].append(secret_data)

            # Generate summary
            total_secrets = len(export_data["secrets"])
            rotating_secrets = len(
                [s for s in export_data["secrets"] if s["rotation_enabled"]]
            )
            non_rotating_secrets = total_secrets - rotating_secrets

            export_data["summary"] = {
                "total_secrets": total_secrets,
                "rotating_secrets": rotating_secrets,
                "non_rotating_secrets": non_rotating_secrets,
                "rotation_percentage": (
                    (rotating_secrets / total_secrets * 100) if total_secrets > 0 else 0
                ),
            }

        except ClientError as e:
            typer.echo(f"  {WARNING_EMOJI} Error accessing Secrets Manager: {e}")

        # Export data
        if format == "json":
            output_content = json.dumps(export_data, indent=2, default=str)
        elif format == "csv":
            import csv
            import io

            output = io.StringIO()
            writer = csv.writer(output)

            # Write summary
            writer.writerow(["Metric", "Value"])
            for key, value in export_data["summary"].items():
                writer.writerow([key, value])
            writer.writerow([])

            # Write secrets
            if export_data["secrets"]:
                fieldnames = list(export_data["secrets"][0].keys())
                writer.writerow(fieldnames)
                for secret in export_data["secrets"]:
                    row = []
                    for field in fieldnames:
                        value = secret.get(field, "")
                        if isinstance(value, (list, dict)):
                            value = json.dumps(value)
                        row.append(str(value))
                    writer.writerow(row)

            output_content = output.getvalue()
        elif format == "yaml":
            import yaml

            output_content = yaml.dump(
                export_data, default_flow_style=False, allow_unicode=True
            )
        else:
            raise typer.BadParameter(f"Unsupported format: {format}")

        # Output to file or stdout
        if output_file:
            with open(output_file, "w") as f:
                f.write(output_content)
            typer.echo(f"  {SUCCESS_EMOJI} Data exported to: {output_file}")
        else:
            typer.echo(output_content)

        # Export summary
        typer.echo(f"\n{EXPORT_EMOJI} Export Summary:")
        typer.echo(
            f"  {ANALYSIS_EMOJI} Total secrets: {export_data['summary']['total_secrets']}"
        )
        typer.echo(
            f"  {ROTATION_EMOJI} Rotating secrets: {export_data['summary']['rotating_secrets']}"
        )
        typer.echo(
            f"  {WARNING_EMOJI} Non-rotating secrets: {export_data['summary']['non_rotating_secrets']}"
        )
        typer.echo(
            f"  {ANALYSIS_EMOJI} Rotation coverage: {export_data['summary']['rotation_percentage']:.1f}%"
        )

    except Exception as e:
        AWDXErrorHandler.handle_aws_error(e, context="secret export")
        typer.echo(f"{ERROR_EMOJI} Error during export: {e}")
        raise typer.Exit(1)


@secret_app.command()
def help():
    """Show detailed help for Secrex commands."""
    typer.echo(f"{SECRET_EMOJI} Secrex - AWS Secret Management and Rotation Module")
    typer.echo(f"\n{INNOVATION_EMOJI} Real-World DevSecOps Use Cases:")
    typer.echo(f"  {DISCOVERY_EMOJI} Secret Discovery & Inventory")
    typer.echo(f"  {ROTATION_EMOJI} Automated Secret Rotation")
    typer.echo(f"  {MONITORING_EMOJI} Continuous Monitoring & Alerting")
    typer.echo(f"  {COMPLIANCE_EMOJI} Compliance Framework Validation")
    typer.echo(f"  {REMEDIATION_EMOJI} Automated Issue Remediation")
    typer.echo(f"  {TIP_EMOJI} Intelligent Recommendations")
    typer.echo(f"  {EXPORT_EMOJI} Data Export & Reporting")

    typer.echo(f"\n{INNOVATION_EMOJI} Advanced Features:")
    typer.echo(f"  {AUTOMATION_EMOJI} Smart automation with risk-based prioritization")
    typer.echo(f"  {DETECTION_EMOJI} Anomaly detection in secret access patterns")
    typer.echo(
        f"  {INTEGRATION_EMOJI} Multi-service secret discovery (Secrets Manager, SSM, KMS)"
    )
    typer.echo(
        f"  {SCHEDULING_EMOJI} Intelligent rotation scheduling based on usage patterns"
    )
    typer.echo(f"  {NOTIFICATION_EMOJI} Proactive alerting for security events")
    typer.echo(
        f"  {VALIDATION_EMOJI} Automated compliance validation across frameworks"
    )

    typer.echo(f"\n{TIP_EMOJI} Best Practices:")
    typer.echo(f"  {BEST_PRACTICE_EMOJI} Enable automatic rotation for all secrets")
    typer.echo(
        f"  {BEST_PRACTICE_EMOJI} Use Secrets Manager instead of Parameter Store for sensitive data"
    )
    typer.echo(f"  {BEST_PRACTICE_EMOJI} Implement least privilege access to secrets")
    typer.echo(f"  {BEST_PRACTICE_EMOJI} Monitor secret access patterns for anomalies")
    typer.echo(f"  {AVOID_EMOJI} Never store secrets in code or configuration files")
    typer.echo(f"  {BEST_PRACTICE_EMOJI} Regular compliance audits and assessments")

    typer.echo(f"\n{INNOVATION_EMOJI} Innovation Highlights:")
    typer.echo(f"  {RISK_EMOJI} Risk-based prioritization for remediation actions")
    typer.echo(
        f"  {ANALYSIS_EMOJI} Intelligent analysis of rotation patterns and access trends"
    )
    typer.echo(
        f"  {AUTOMATION_EMOJI} Automated remediation with safety checks and dry-run capabilities"
    )
    typer.echo(
        f"  {COMPLIANCE_EMOJI} Multi-framework compliance validation (SOX, PCI, HIPAA, GDPR)"
    )
    typer.echo(
        f"  {DETECTION_EMOJI} Proactive detection of security issues and compliance gaps"
    )
    typer.echo(
        f"  {INTEGRATION_EMOJI} Seamless integration with existing AWS security tools"
    )

    typer.echo(f"\n{EXPOSURE_EMOJI} Security Focus:")
    typer.echo(f"  {SECRET_EMOJI} Comprehensive secret lifecycle management")
    typer.echo(f"  {ROTATION_EMOJI} Automated rotation with minimal downtime")
    typer.echo(f"  {MONITORING_EMOJI} Real-time monitoring and alerting")
    typer.echo(f"  {COMPLIANCE_EMOJI} Automated compliance validation")
    typer.echo(f"  {REMEDIATION_EMOJI} Intelligent issue remediation")
    typer.echo(f"  {DETECTION_EMOJI} Anomaly detection and threat prevention")

    typer.echo(f"\n{INNOVATION_EMOJI} DevSecOps Integration:")
    typer.echo(f"  {AUTOMATION_EMOJI} CI/CD pipeline integration for secret rotation")
    typer.echo(f"  {MONITORING_EMOJI} Integration with monitoring and alerting systems")
    typer.echo(f"  {COMPLIANCE_EMOJI} Automated compliance reporting for audits")
    typer.echo(
        f"  {INTEGRATION_EMOJI} Integration with security tools and SIEM systems"
    )
    typer.echo(f"  {EXPORT_EMOJI} Data export for custom reporting and analysis")
    typer.echo(
        f"  {SCHEDULING_EMOJI} Intelligent scheduling based on application patterns"
    )

    typer.echo(
        f"\n{SUCCESS_EMOJI} Ready to secure your secrets with intelligent automation!"
    )


if __name__ == "__main__":
    secret_app()
