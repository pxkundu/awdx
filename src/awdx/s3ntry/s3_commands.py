import base64
import csv
import hashlib
import json
import os
import re
import secrets
import string
import urllib.parse
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import boto3
import typer
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound

s3_app = typer.Typer(help="AWS S3 security and compliance commands.")

# Emoji constants for consistent UI
S3_EMOJI = "🪣"
SECURITY_EMOJI = "🔒"
COMPLIANCE_EMOJI = "📋"
ENCRYPTION_EMOJI = "🔐"
ACCESS_EMOJI = "👤"
MONITORING_EMOJI = "📊"
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
VERSIONING_EMOJI = "📝"
LOGGING_EMOJI = "📋"
REPLICATION_EMOJI = "🔄"
LIFECYCLE_EMOJI = "⏳"
TAGGING_EMOJI = "🏷️"
POLICY_EMOJI = "📜"
PERMISSION_EMOJI = "🔑"
PUBLIC_EMOJI = "🌐"
PRIVATE_EMOJI = "🔒"


@dataclass
class S3Finding:
    """Data class for S3 security findings."""

    severity: str
    category: str
    title: str
    description: str
    impact: str
    recommendation: str
    bucket_name: str
    region: str
    priority: int
    resource_type: str = "S3 Bucket"
    last_modified: Optional[datetime] = None
    size_bytes: Optional[int] = None


@dataclass
class S3Compliance:
    """Data class for S3 compliance checks."""

    framework: str
    control: str
    status: str
    description: str
    impact: str
    recommendation: str
    bucket_name: str
    region: str


def get_aws_clients(profile: Optional[str] = None):
    """Get AWS clients for S3 security management."""
    try:
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        return {
            "s3": session.client("s3"),
            "s3control": session.client("s3control"),
            "iam": session.client("iam"),
            "cloudtrail": session.client("cloudtrail"),
            "config": session.client("config"),
            "securityhub": session.client("securityhub"),
            "guardduty": session.client("guardduty"),
            "sts": session.client("sts"),
            "cloudwatch": session.client("cloudwatch"),
            "lambda": session.client("lambda"),
            "events": session.client("events"),
        }
    except ProfileNotFound:
        raise typer.BadParameter(f"Profile '{profile}' not found")
    except NoCredentialsError:
        raise typer.BadParameter(
            "No AWS credentials found. Please configure your AWS credentials."
        )
    except Exception as e:
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


def format_size(size_bytes: int) -> str:
    """Format bytes to human readable size."""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.2f} {size_names[i]}"


def calculate_risk_score(findings: List[S3Finding]) -> int:
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


def is_public_bucket(bucket_name: str, s3_client) -> bool:
    """Check if bucket is publicly accessible."""
    try:
        # Check bucket ACL
        acl = s3_client.get_bucket_acl(Bucket=bucket_name)
        for grant in acl.get("Grants", []):
            grantee = grant.get("Grantee", {})
            if grantee.get("URI") == "http://acs.amazonaws.com/groups/global/AllUsers":
                return True

        # Check bucket policy
        try:
            policy = s3_client.get_bucket_policy(Bucket=bucket_name)
            policy_doc = json.loads(policy["Policy"])
            for statement in policy_doc.get("Statement", []):
                principal = statement.get("Principal", {})
                if principal == "*" or principal.get("AWS") == "*":
                    return True
        except ClientError:
            pass  # No bucket policy

        return False
    except ClientError:
        return False


def check_encryption(bucket_name: str, s3_client) -> Dict[str, Any]:
    """Check bucket encryption configuration."""
    try:
        encryption = s3_client.get_bucket_encryption(Bucket=bucket_name)
        return {
            "enabled": True,
            "algorithm": encryption["ServerSideEncryptionConfiguration"]["Rules"][0][
                "ApplyServerSideEncryptionByDefault"
            ]["SSEAlgorithm"],
            "kms_key": encryption["ServerSideEncryptionConfiguration"]["Rules"][0][
                "ApplyServerSideEncryptionByDefault"
            ].get("KMSMasterKeyID"),
        }
    except ClientError:
        return {"enabled": False}


def check_versioning(bucket_name: str, s3_client) -> Dict[str, Any]:
    """Check bucket versioning configuration."""
    try:
        versioning = s3_client.get_bucket_versioning(Bucket=bucket_name)
        return {
            "enabled": versioning.get("Status") == "Enabled",
            "mfa_delete": versioning.get("MFADelete") == "Enabled",
        }
    except ClientError:
        return {"enabled": False, "mfa_delete": False}


def check_logging(bucket_name: str, s3_client) -> Dict[str, Any]:
    """Check bucket logging configuration."""
    try:
        logging = s3_client.get_bucket_logging(Bucket=bucket_name)
        if "LoggingEnabled" in logging:
            return {
                "enabled": True,
                "target_bucket": logging["LoggingEnabled"]["TargetBucket"],
                "target_prefix": logging["LoggingEnabled"].get("TargetPrefix", ""),
            }
        return {"enabled": False}
    except ClientError:
        return {"enabled": False}


def check_lifecycle(bucket_name: str, s3_client) -> Dict[str, Any]:
    """Check bucket lifecycle configuration."""
    try:
        lifecycle = s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
        return {"enabled": True, "rules": len(lifecycle.get("Rules", []))}
    except ClientError:
        return {"enabled": False, "rules": 0}


def calculate_bucket_score(bucket_config: Dict[str, Any]) -> int:
    """Calculate security score for a bucket."""
    score = 0

    # Encryption
    if bucket_config.get("encryption", {}).get("enabled"):
        score += 20
    else:
        score -= 10

    # Versioning
    if bucket_config.get("versioning", {}).get("enabled"):
        score += 15
    else:
        score -= 5

    # Logging
    if bucket_config.get("logging", {}).get("enabled"):
        score += 15
    else:
        score -= 5

    # Public access
    if not bucket_config.get("public_access"):
        score += 20
    else:
        score -= 20

    # Lifecycle
    if bucket_config.get("lifecycle", {}).get("enabled"):
        score += 10
    else:
        score -= 2

    return score


@s3_app.command()
def audit(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    region: Optional[str] = typer.Option(
        None, "--region", "-r", help="AWS region to scan"
    ),
    bucket_name: Optional[str] = typer.Option(
        None, "--bucket", "-b", help="Specific bucket to audit"
    ),
    output_format: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    include_objects: bool = typer.Option(
        False, "--include-objects", help="Include object-level analysis"
    ),
    risk_threshold: str = typer.Option(
        "MEDIUM", "--risk-threshold", help="Minimum risk level to report"
    ),
):
    """Comprehensive S3 bucket security audit."""
    typer.echo(f"{AUDIT_EMOJI} Starting comprehensive S3 security audit...")

    try:
        clients = get_aws_clients(profile)
        s3_client = clients["s3"]
        regions = [region] if region else get_region_list(profile)
        findings = []

        # Get buckets to audit
        buckets_to_audit = []
        if bucket_name:
            buckets_to_audit.append(bucket_name)
        else:
            try:
                response = s3_client.list_buckets()
                buckets_to_audit = [bucket["Name"] for bucket in response["Buckets"]]
            except ClientError as e:
                typer.echo(f"{ERROR_EMOJI} Error listing buckets: {e}")
                return

        for bucket in buckets_to_audit:
            typer.echo(f"  {SCANNING_EMOJI} Auditing bucket: {bucket}")

            try:
                # Get bucket location
                location = s3_client.get_bucket_location(Bucket=bucket)
                bucket_region = location.get("LocationConstraint") or "us-east-1"

                # Skip if region specified and doesn't match
                if region and bucket_region != region:
                    continue

                bucket_config = {
                    "name": bucket,
                    "region": bucket_region,
                    "encryption": check_encryption(bucket, s3_client),
                    "versioning": check_versioning(bucket, s3_client),
                    "logging": check_logging(bucket, s3_client),
                    "lifecycle": check_lifecycle(bucket, s3_client),
                    "public_access": is_public_bucket(bucket, s3_client),
                }

                # Check for security issues

                # Public access check
                if bucket_config["public_access"]:
                    findings.append(
                        S3Finding(
                            severity="CRITICAL",
                            category="Public Access",
                            title=f"Public Bucket: {bucket}",
                            description=f"Bucket {bucket} is publicly accessible",
                            impact="Data exposure and potential unauthorized access",
                            recommendation="Remove public access and implement proper access controls",
                            bucket_name=bucket,
                            region=bucket_region,
                            priority=10,
                        )
                    )

                # Encryption check
                if not bucket_config["encryption"]["enabled"]:
                    findings.append(
                        S3Finding(
                            severity="HIGH",
                            category="Encryption",
                            title=f"Unencrypted Bucket: {bucket}",
                            description=f"Bucket {bucket} does not have encryption enabled",
                            impact="Data at rest is not protected",
                            recommendation="Enable server-side encryption for the bucket",
                            bucket_name=bucket,
                            region=bucket_region,
                            priority=7,
                        )
                    )

                # Versioning check
                if not bucket_config["versioning"]["enabled"]:
                    findings.append(
                        S3Finding(
                            severity="MEDIUM",
                            category="Versioning",
                            title=f"No Versioning: {bucket}",
                            description=f"Bucket {bucket} does not have versioning enabled",
                            impact="Data loss risk and compliance issues",
                            recommendation="Enable versioning for data protection",
                            bucket_name=bucket,
                            region=bucket_region,
                            priority=4,
                        )
                    )

                # Logging check
                if not bucket_config["logging"]["enabled"]:
                    findings.append(
                        S3Finding(
                            severity="MEDIUM",
                            category="Logging",
                            title=f"No Logging: {bucket}",
                            description=f"Bucket {bucket} does not have access logging enabled",
                            impact="No audit trail for bucket access",
                            recommendation="Enable access logging for compliance and security",
                            bucket_name=bucket,
                            region=bucket_region,
                            priority=4,
                        )
                    )

                # Lifecycle check
                if not bucket_config["lifecycle"]["enabled"]:
                    findings.append(
                        S3Finding(
                            severity="LOW",
                            category="Lifecycle",
                            title=f"No Lifecycle: {bucket}",
                            description=f"Bucket {bucket} does not have lifecycle policies",
                            impact="Potential cost overruns and data management issues",
                            recommendation="Implement lifecycle policies for cost optimization",
                            bucket_name=bucket,
                            region=bucket_region,
                            priority=1,
                        )
                    )

                # Object-level analysis if requested
                if include_objects:
                    try:
                        objects = s3_client.list_objects_v2(Bucket=bucket, MaxKeys=1000)
                        if "Contents" in objects:
                            total_size = sum(obj["Size"] for obj in objects["Contents"])
                            findings.append(
                                S3Finding(
                                    severity="INFO",
                                    category="Objects",
                                    title=f"Bucket Objects: {bucket}",
                                    description=f"Bucket contains {len(objects['Contents'])} objects ({format_size(total_size)})",
                                    impact="Information only",
                                    recommendation="Review object access patterns and permissions",
                                    bucket_name=bucket,
                                    region=bucket_region,
                                    priority=0,
                                    size_bytes=total_size,
                                )
                            )
                    except ClientError:
                        pass

            except ClientError as e:
                if e.response["Error"]["Code"] != "AccessDenied":
                    typer.echo(
                        f"    {WARNING_EMOJI} Error auditing bucket {bucket}: {e}"
                    )

        # Display results
        if findings:
            typer.echo(f"\n{AUDIT_EMOJI} S3 Security Audit Results:")
            typer.echo(f"  {ANALYSIS_EMOJI} Found {len(findings)} security issues")

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
                            "bucket_name": finding.bucket_name,
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
                        "Bucket",
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
                            finding.bucket_name,
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
                    typer.echo(f"    Bucket: {finding.bucket_name}")
                    typer.echo(f"    Region: {finding.region}")
                    typer.echo(f"    Priority Score: {finding.priority}")
        else:
            typer.echo(f"\n{SUCCESS_EMOJI} No security issues found!")

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
        typer.echo(f"\n{TIP_EMOJI} S3 Security Best Practices:")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Enable encryption for all buckets")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Block public access by default")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Enable versioning for data protection")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Configure access logging for audit trails")
        typer.echo(f"  {AVOID_EMOJI} Never use public read/write permissions")

    except Exception as e:
        typer.echo(f"{ERROR_EMOJI} Error during S3 audit: {e}")


@s3_app.command()
def scan(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    region: Optional[str] = typer.Option(
        None, "--region", "-r", help="AWS region to scan"
    ),
    bucket_name: Optional[str] = typer.Option(
        None, "--bucket", "-b", help="Specific bucket to scan"
    ),
    scan_type: str = typer.Option(
        "all",
        "--type",
        "-t",
        help="Scan type: all, public, encryption, versioning, logging",
    ),
    output_format: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    include_sensitive: bool = typer.Option(
        False,
        "--include-sensitive",
        help="Include potentially sensitive data detection",
    ),
):
    """Scan S3 buckets for specific security issues."""
    typer.echo(f"{SCANNING_EMOJI} Starting S3 security scan...")

    try:
        clients = get_aws_clients(profile)
        s3_client = clients["s3"]
        findings = []

        # Get buckets to scan
        buckets_to_scan = []
        if bucket_name:
            buckets_to_scan.append(bucket_name)
        else:
            try:
                response = s3_client.list_buckets()
                buckets_to_scan = [bucket["Name"] for bucket in response["Buckets"]]
            except ClientError as e:
                typer.echo(f"{ERROR_EMOJI} Error listing buckets: {e}")
                return

        for bucket in buckets_to_scan:
            typer.echo(f"  {SCANNING_EMOJI} Scanning bucket: {bucket}")

            try:
                # Get bucket location
                location = s3_client.get_bucket_location(Bucket=bucket)
                bucket_region = location.get("LocationConstraint") or "us-east-1"

                # Skip if region specified and doesn't match
                if region and bucket_region != region:
                    continue

                # Public access scan
                if scan_type in ["all", "public"]:
                    if is_public_bucket(bucket, s3_client):
                        findings.append(
                            S3Finding(
                                severity="CRITICAL",
                                category="Public Access",
                                title=f"Public Bucket Detected: {bucket}",
                                description=f"Bucket {bucket} allows public access",
                                impact="Critical security risk - data exposure",
                                recommendation="Immediately remove public access and review bucket policy",
                                bucket_name=bucket,
                                region=bucket_region,
                                priority=10,
                            )
                        )

                # Encryption scan
                if scan_type in ["all", "encryption"]:
                    encryption_config = check_encryption(bucket, s3_client)
                    if not encryption_config["enabled"]:
                        findings.append(
                            S3Finding(
                                severity="HIGH",
                                category="Encryption",
                                title=f"Unencrypted Bucket: {bucket}",
                                description=f"Bucket {bucket} lacks server-side encryption",
                                impact="Data at rest is not protected",
                                recommendation="Enable AES256 or KMS encryption",
                                bucket_name=bucket,
                                region=bucket_region,
                                priority=7,
                            )
                        )
                    elif encryption_config.get("algorithm") == "AES256":
                        findings.append(
                            S3Finding(
                                severity="MEDIUM",
                                category="Encryption",
                                title=f"Basic Encryption: {bucket}",
                                description=f"Bucket {bucket} uses basic AES256 encryption",
                                impact="Consider using KMS for better key management",
                                recommendation="Upgrade to KMS encryption for enhanced security",
                                bucket_name=bucket,
                                region=bucket_region,
                                priority=3,
                            )
                        )

                # Versioning scan
                if scan_type in ["all", "versioning"]:
                    versioning_config = check_versioning(bucket, s3_client)
                    if not versioning_config["enabled"]:
                        findings.append(
                            S3Finding(
                                severity="MEDIUM",
                                category="Versioning",
                                title=f"No Versioning: {bucket}",
                                description=f"Bucket {bucket} does not have versioning enabled",
                                impact="Data loss risk and compliance issues",
                                recommendation="Enable versioning for data protection",
                                bucket_name=bucket,
                                region=bucket_region,
                                priority=4,
                            )
                        )
                    elif not versioning_config["mfa_delete"]:
                        findings.append(
                            S3Finding(
                                severity="LOW",
                                category="Versioning",
                                title=f"No MFA Delete: {bucket}",
                                description=f"Bucket {bucket} versioning lacks MFA delete protection",
                                impact="Reduced protection against accidental deletion",
                                recommendation="Enable MFA delete for versioning",
                                bucket_name=bucket,
                                region=bucket_region,
                                priority=2,
                            )
                        )

                # Logging scan
                if scan_type in ["all", "logging"]:
                    logging_config = check_logging(bucket, s3_client)
                    if not logging_config["enabled"]:
                        findings.append(
                            S3Finding(
                                severity="MEDIUM",
                                category="Logging",
                                title=f"No Logging: {bucket}",
                                description=f"Bucket {bucket} does not have access logging enabled",
                                impact="No audit trail for compliance and security",
                                recommendation="Enable access logging to a separate bucket",
                                bucket_name=bucket,
                                region=bucket_region,
                                priority=4,
                            )
                        )

                # Sensitive data detection
                if include_sensitive and scan_type in ["all", "sensitive"]:
                    try:
                        objects = s3_client.list_objects_v2(Bucket=bucket, MaxKeys=100)
                        sensitive_patterns = [
                            r"password",
                            r"secret",
                            r"key",
                            r"token",
                            r"credential",
                            r"\.env",
                            r"config\.",
                            r"\.pem",
                            r"\.key",
                            r"\.crt",
                            r"backup",
                            r"dump",
                            r"export",
                            r"database",
                        ]

                        for obj in objects.get("Contents", []):
                            obj_key = obj["Key"].lower()
                            for pattern in sensitive_patterns:
                                if re.search(pattern, obj_key):
                                    findings.append(
                                        S3Finding(
                                            severity="HIGH",
                                            category="Sensitive Data",
                                            title=f"Potentially Sensitive Object: {obj['Key']}",
                                            description=f"Object in {bucket} may contain sensitive data",
                                            impact="Potential data exposure risk",
                                            recommendation="Review object permissions and consider encryption",
                                            bucket_name=bucket,
                                            region=bucket_region,
                                            priority=6,
                                        )
                                    )
                                    break
                    except ClientError:
                        pass

            except ClientError as e:
                if e.response["Error"]["Code"] != "AccessDenied":
                    typer.echo(
                        f"    {WARNING_EMOJI} Error scanning bucket {bucket}: {e}"
                    )

        # Display results
        if findings:
            typer.echo(f"\n{SCANNING_EMOJI} S3 Security Scan Results:")
            typer.echo(f"  {ANALYSIS_EMOJI} Found {len(findings)} security issues")

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
                            "bucket_name": finding.bucket_name,
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
                        "Bucket",
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
                            finding.bucket_name,
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
                    typer.echo(f"    Bucket: {finding.bucket_name}")
                    typer.echo(f"    Region: {finding.region}")
                    typer.echo(f"    Priority Score: {finding.priority}")
        else:
            typer.echo(f"\n{SUCCESS_EMOJI} No security issues found!")

        # Scan summary
        typer.echo(f"\n{SCANNING_EMOJI} Scan Summary:")
        typer.echo(f"  {ANALYSIS_EMOJI} Scanned {len(buckets_to_scan)} buckets")
        typer.echo(f"  {FINDINGS_EMOJI} Found {len(findings)} security issues")

        # Best practices
        typer.echo(f"\n{TIP_EMOJI} S3 Security Best Practices:")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Block all public access by default")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Enable encryption for all data")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Use KMS encryption for sensitive data")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Enable versioning for data protection")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Configure comprehensive logging")

    except Exception as e:
        typer.echo(f"{ERROR_EMOJI} Error during S3 scan: {e}")


@s3_app.command()
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
    """Check S3 compliance against various frameworks."""
    typer.echo(f"{COMPLIANCE_EMOJI} Checking S3 compliance...")

    try:
        clients = get_aws_clients(profile)
        s3_client = clients["s3"]

        compliance_checks = []

        # Get all buckets
        try:
            response = s3_client.list_buckets()
            buckets = [bucket["Name"] for bucket in response["Buckets"]]
        except ClientError as e:
            typer.echo(f"{ERROR_EMOJI} Error listing buckets: {e}")
            return

        for bucket in buckets:
            try:
                # Get bucket location
                location = s3_client.get_bucket_location(Bucket=bucket)
                bucket_region = location.get("LocationConstraint") or "us-east-1"

                # Skip if region specified and doesn't match
                if region and bucket_region != region:
                    continue

                # SOX Compliance Checks
                if framework in ["all", "sox"]:
                    typer.echo(
                        f"  {COMPLIANCE_EMOJI} Checking SOX compliance for {bucket}..."
                    )

                    # Check encryption
                    encryption_config = check_encryption(bucket, s3_client)
                    if not encryption_config["enabled"]:
                        compliance_checks.append(
                            S3Compliance(
                                framework="SOX",
                                control="SOX-404",
                                status="FAIL",
                                description=f"Bucket {bucket} lacks encryption",
                                impact="Non-compliance with SOX data protection requirements",
                                recommendation="Enable server-side encryption",
                                bucket_name=bucket,
                                region=bucket_region,
                            )
                        )

                    # Check access logging
                    logging_config = check_logging(bucket, s3_client)
                    if not logging_config["enabled"]:
                        compliance_checks.append(
                            S3Compliance(
                                framework="SOX",
                                control="SOX-404",
                                status="FAIL",
                                description=f"Bucket {bucket} lacks access logging",
                                impact="Non-compliance with SOX audit requirements",
                                recommendation="Enable access logging",
                                bucket_name=bucket,
                                region=bucket_region,
                            )
                        )

                # PCI DSS Compliance Checks
                if framework in ["all", "pci"]:
                    typer.echo(
                        f"  {COMPLIANCE_EMOJI} Checking PCI DSS compliance for {bucket}..."
                    )

                    # Check public access
                    if is_public_bucket(bucket, s3_client):
                        compliance_checks.append(
                            S3Compliance(
                                framework="PCI DSS",
                                control="PCI-3.4",
                                status="FAIL",
                                description=f"Bucket {bucket} allows public access",
                                impact="Non-compliance with PCI DSS data protection",
                                recommendation="Remove public access immediately",
                                bucket_name=bucket,
                                region=bucket_region,
                            )
                        )

                    # Check encryption
                    encryption_config = check_encryption(bucket, s3_client)
                    if not encryption_config["enabled"]:
                        compliance_checks.append(
                            S3Compliance(
                                framework="PCI DSS",
                                control="PCI-3.4",
                                status="FAIL",
                                description=f"Bucket {bucket} lacks encryption",
                                impact="Non-compliance with PCI DSS encryption requirements",
                                recommendation="Enable strong encryption",
                                bucket_name=bucket,
                                region=bucket_region,
                            )
                        )

                # HIPAA Compliance Checks
                if framework in ["all", "hipaa"]:
                    typer.echo(
                        f"  {COMPLIANCE_EMOJI} Checking HIPAA compliance for {bucket}..."
                    )

                    # Check encryption
                    encryption_config = check_encryption(bucket, s3_client)
                    if not encryption_config["enabled"]:
                        compliance_checks.append(
                            S3Compliance(
                                framework="HIPAA",
                                control="HIPAA-164.312(a)(2)(iv)",
                                status="FAIL",
                                description=f"Bucket {bucket} lacks encryption",
                                impact="Non-compliance with HIPAA encryption standards",
                                recommendation="Enable encryption for PHI data",
                                bucket_name=bucket,
                                region=bucket_region,
                            )
                        )

                    # Check access controls
                    compliance_checks.append(
                        S3Compliance(
                            framework="HIPAA",
                            control="HIPAA-164.312(a)(1)",
                            status="INFO",
                            description=f"Bucket {bucket} access controls should be reviewed",
                            impact="Required for HIPAA compliance",
                            recommendation="Implement least privilege access",
                            bucket_name=bucket,
                            region=bucket_region,
                        )
                    )

                # GDPR Compliance Checks
                if framework in ["all", "gdpr"]:
                    typer.echo(
                        f"  {COMPLIANCE_EMOJI} Checking GDPR compliance for {bucket}..."
                    )

                    # Check data protection
                    compliance_checks.append(
                        S3Compliance(
                            framework="GDPR",
                            control="GDPR-Article-32",
                            status="INFO",
                            description=f"Bucket {bucket} should have appropriate security measures",
                            impact="Required for GDPR compliance",
                            recommendation="Implement encryption and access controls",
                            bucket_name=bucket,
                            region=bucket_region,
                        )
                    )

                    # Check audit trails
                    logging_config = check_logging(bucket, s3_client)
                    if not logging_config["enabled"]:
                        compliance_checks.append(
                            S3Compliance(
                                framework="GDPR",
                                control="GDPR-Article-30",
                                status="FAIL",
                                description=f"Bucket {bucket} lacks access logging",
                                impact="Non-compliance with GDPR record keeping",
                                recommendation="Enable comprehensive logging",
                                bucket_name=bucket,
                                region=bucket_region,
                            )
                        )

            except ClientError as e:
                if e.response["Error"]["Code"] != "AccessDenied":
                    typer.echo(
                        f"    {WARNING_EMOJI} Error checking compliance for {bucket}: {e}"
                    )

        # Display compliance results
        if compliance_checks:
            typer.echo(f"\n{COMPLIANCE_EMOJI} Compliance Assessment Results:")

            if output_format == "json":
                results = []
                for check in compliance_checks:
                    results.append(
                        {
                            "framework": check.framework,
                            "control": check.control,
                            "status": check.status,
                            "description": check.description,
                            "impact": check.impact,
                            "recommendation": check.recommendation,
                            "bucket_name": check.bucket_name,
                            "region": check.region,
                        }
                    )
                typer.echo(json.dumps(results, indent=2))
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
                        "Bucket",
                        "Region",
                    ]
                )
                for check in compliance_checks:
                    writer.writerow(
                        [
                            check.framework,
                            check.control,
                            check.status,
                            check.description,
                            check.impact,
                            check.recommendation,
                            check.bucket_name,
                            check.region,
                        ]
                    )
            else:
                by_framework = defaultdict(list)
                for check in compliance_checks:
                    by_framework[check.framework].append(check)

                for framework_name, checks in by_framework.items():
                    typer.echo(f"\n  {COMPLIANCE_EMOJI} {framework_name} Compliance:")
                    fails = [c for c in checks if c.status == "FAIL"]
                    infos = [c for c in checks if c.status == "INFO"]

                    if fails:
                        typer.echo(f"    {ERROR_EMOJI} {len(fails)} Failures:")
                        for check in fails:
                            typer.echo(f"      {check.control}: {check.description}")
                            typer.echo(f"        Impact: {check.impact}")
                            typer.echo(
                                f"        Recommendation: {check.recommendation}"
                            )

                    if infos:
                        typer.echo(f"    {TIP_EMOJI} {len(infos)} Recommendations:")
                        for check in infos:
                            typer.echo(f"      {check.control}: {check.description}")
                            typer.echo(
                                f"        Recommendation: {check.recommendation}"
                            )
        else:
            typer.echo(f"\n{SUCCESS_EMOJI} All compliance checks passed!")

        # Compliance recommendations
        typer.echo(f"\n{TIP_EMOJI} Compliance Best Practices:")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Enable encryption for all buckets")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Block public access by default")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Enable access logging for audit trails")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Implement least privilege access")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Regular compliance audits and assessments")

    except Exception as e:
        typer.echo(f"{ERROR_EMOJI} Error during compliance check: {e}")


@s3_app.command()
def remediate(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
    bucket_name: Optional[str] = typer.Option(
        None, "--bucket", "-b", help="Specific bucket to remediate"
    ),
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
    """Automated remediation of S3 security issues."""
    typer.echo(f"{REMEDIATION_EMOJI} Starting automated S3 remediation...")

    try:
        clients = get_aws_clients(profile)
        s3_client = clients["s3"]

        if dry_run:
            typer.echo(f"  {ANALYSIS_EMOJI} Dry run mode - no changes will be made")

        remediation_actions = []

        # Get buckets to remediate
        buckets_to_remediate = []
        if bucket_name:
            buckets_to_remediate.append(bucket_name)
        else:
            try:
                response = s3_client.list_buckets()
                buckets_to_remediate = [
                    bucket["Name"] for bucket in response["Buckets"]
                ]
            except ClientError as e:
                typer.echo(f"{ERROR_EMOJI} Error listing buckets: {e}")
                return

        for bucket in buckets_to_remediate:
            typer.echo(f"  {SCANNING_EMOJI} Analyzing bucket: {bucket}")

            try:
                # Get bucket location
                location = s3_client.get_bucket_location(Bucket=bucket)
                bucket_region = location.get("LocationConstraint") or "us-east-1"

                # Skip if region specified and doesn't match
                if region and bucket_region != region:
                    continue

                actions = []

                # Check for public access
                if is_public_bucket(bucket, s3_client):
                    actions.append(
                        {
                            "action": "block_public_access",
                            "description": f"Block public access for {bucket}",
                            "risk": "CRITICAL",
                            "bucket": bucket,
                        }
                    )

                # Check for encryption
                encryption_config = check_encryption(bucket, s3_client)
                if not encryption_config["enabled"]:
                    actions.append(
                        {
                            "action": "enable_encryption",
                            "description": f"Enable encryption for {bucket}",
                            "risk": "HIGH",
                            "bucket": bucket,
                        }
                    )

                # Check for versioning
                versioning_config = check_versioning(bucket, s3_client)
                if not versioning_config["enabled"]:
                    actions.append(
                        {
                            "action": "enable_versioning",
                            "description": f"Enable versioning for {bucket}",
                            "risk": "MEDIUM",
                            "bucket": bucket,
                        }
                    )

                # Check for logging
                logging_config = check_logging(bucket, s3_client)
                if not logging_config["enabled"]:
                    actions.append(
                        {
                            "action": "enable_logging",
                            "description": f"Enable access logging for {bucket}",
                            "risk": "MEDIUM",
                            "bucket": bucket,
                        }
                    )

                remediation_actions.extend(actions)

            except ClientError as e:
                if e.response["Error"]["Code"] != "AccessDenied":
                    typer.echo(
                        f"    {WARNING_EMOJI} Error analyzing bucket {bucket}: {e}"
                    )

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

                if action["action"] == "block_public_access":
                    # Block public access
                    s3_client.put_public_access_block(
                        Bucket=action["bucket"],
                        PublicAccessBlockConfiguration={
                            "BlockPublicAcls": True,
                            "IgnorePublicAcls": True,
                            "BlockPublicPolicy": True,
                            "RestrictPublicBuckets": True,
                        },
                    )
                    typer.echo(
                        f"  {SUCCESS_EMOJI} Blocked public access for {action['bucket']}"
                    )
                    success_count += 1

                elif action["action"] == "enable_encryption":
                    # Enable encryption
                    s3_client.put_bucket_encryption(
                        Bucket=action["bucket"],
                        ServerSideEncryptionConfiguration={
                            "Rules": [
                                {
                                    "ApplyServerSideEncryptionByDefault": {
                                        "SSEAlgorithm": "AES256"
                                    }
                                }
                            ]
                        },
                    )
                    typer.echo(
                        f"  {SUCCESS_EMOJI} Enabled encryption for {action['bucket']}"
                    )
                    success_count += 1

                elif action["action"] == "enable_versioning":
                    # Enable versioning
                    s3_client.put_bucket_versioning(
                        Bucket=action["bucket"],
                        VersioningConfiguration={"Status": "Enabled"},
                    )
                    typer.echo(
                        f"  {SUCCESS_EMOJI} Enabled versioning for {action['bucket']}"
                    )
                    success_count += 1

                elif action["action"] == "enable_logging":
                    # Enable logging (requires a target bucket)
                    typer.echo(
                        f"  {WARNING_EMOJI} Manual intervention required for logging: {action['bucket']}"
                    )
                    typer.echo(f"    Please specify a target bucket for access logs")
                    error_count += 1

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
                f"  {BEST_PRACTICE_EMOJI} Verify that applications can still access the buckets"
            )
            typer.echo(f"  {BEST_PRACTICE_EMOJI} Monitor for any access issues")
            typer.echo(
                f"  {BEST_PRACTICE_EMOJI} Set up alerts for future security issues"
            )

    except Exception as e:
        typer.echo(f"{ERROR_EMOJI} Error during remediation: {e}")


@s3_app.command()
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
    """Get intelligent recommendations for S3 optimization."""
    typer.echo(f"{TIP_EMOJI} Generating intelligent S3 recommendations...")

    try:
        clients = get_aws_clients(profile)
        s3_client = clients["s3"]

        recommendations = []

        # Get all buckets
        try:
            response = s3_client.list_buckets()
            buckets = [bucket["Name"] for bucket in response["Buckets"]]
        except ClientError as e:
            typer.echo(f"{ERROR_EMOJI} Error listing buckets: {e}")
            return

        # Security recommendations
        if include_security:
            typer.echo(f"  {SECURITY_EMOJI} Analyzing security posture...")

            public_buckets = []
            unencrypted_buckets = []
            no_versioning_buckets = []
            no_logging_buckets = []

            for bucket in buckets:
                try:
                    # Get bucket location
                    location = s3_client.get_bucket_location(Bucket=bucket)
                    bucket_region = location.get("LocationConstraint") or "us-east-1"

                    # Skip if region specified and doesn't match
                    if region and bucket_region != region:
                        continue

                    # Check public access
                    if is_public_bucket(bucket, s3_client):
                        public_buckets.append(bucket)

                    # Check encryption
                    encryption_config = check_encryption(bucket, s3_client)
                    if not encryption_config["enabled"]:
                        unencrypted_buckets.append(bucket)

                    # Check versioning
                    versioning_config = check_versioning(bucket, s3_client)
                    if not versioning_config["enabled"]:
                        no_versioning_buckets.append(bucket)

                    # Check logging
                    logging_config = check_logging(bucket, s3_client)
                    if not logging_config["enabled"]:
                        no_logging_buckets.append(bucket)

                except ClientError:
                    continue

            # Generate recommendations
            if public_buckets:
                recommendations.append(
                    {
                        "category": "Security",
                        "priority": "CRITICAL",
                        "title": "Block Public Access",
                        "description": f"Found {len(public_buckets)} buckets with public access",
                        "impact": "Critical security risk - immediate data exposure",
                        "effort": "Low",
                        "cost": "None",
                        "action": "Block public access for all buckets immediately",
                    }
                )

            if unencrypted_buckets:
                recommendations.append(
                    {
                        "category": "Security",
                        "priority": "HIGH",
                        "title": "Enable Encryption",
                        "description": f"Found {len(unencrypted_buckets)} unencrypted buckets",
                        "impact": "Data at rest is not protected",
                        "effort": "Low",
                        "cost": "Minimal",
                        "action": "Enable server-side encryption for all buckets",
                    }
                )

            if no_versioning_buckets:
                recommendations.append(
                    {
                        "category": "Security",
                        "priority": "MEDIUM",
                        "title": "Enable Versioning",
                        "description": f"Found {len(no_versioning_buckets)} buckets without versioning",
                        "impact": "Data loss risk and compliance issues",
                        "effort": "Low",
                        "cost": "Storage costs for versions",
                        "action": "Enable versioning for data protection",
                    }
                )

            if no_logging_buckets:
                recommendations.append(
                    {
                        "category": "Security",
                        "priority": "MEDIUM",
                        "title": "Enable Access Logging",
                        "description": f"Found {len(no_logging_buckets)} buckets without logging",
                        "impact": "No audit trail for compliance and security",
                        "effort": "Medium",
                        "cost": "Storage costs for logs",
                        "action": "Enable access logging for audit trails",
                    }
                )

        # Cost optimization recommendations
        if include_cost:
            typer.echo(f"  {COST_EMOJI} Analyzing cost optimization opportunities...")

            recommendations.extend(
                [
                    {
                        "category": "Cost",
                        "priority": "MEDIUM",
                        "title": "Implement Lifecycle Policies",
                        "description": "Review and implement lifecycle policies for cost optimization",
                        "impact": "Potential cost savings through intelligent data management",
                        "effort": "Medium",
                        "cost": "Savings",
                        "action": "Implement lifecycle policies for data archival and deletion",
                    },
                    {
                        "category": "Cost",
                        "priority": "MEDIUM",
                        "title": "Review Storage Classes",
                        "description": "Analyze storage class usage for cost optimization",
                        "impact": "Potential cost savings through appropriate storage classes",
                        "effort": "Medium",
                        "cost": "Savings",
                        "action": "Use S3 Intelligent Tiering or lifecycle policies",
                    },
                    {
                        "category": "Cost",
                        "priority": "LOW",
                        "title": "Remove Unused Objects",
                        "description": "Identify and remove unused or orphaned objects",
                        "impact": "Direct cost savings through storage reduction",
                        "effort": "High",
                        "cost": "Savings",
                        "action": "Audit and clean up unused objects",
                    },
                ]
            )

        # Add general best practices
        recommendations.extend(
            [
                {
                    "category": "Best Practices",
                    "priority": "MEDIUM",
                    "title": "Implement Cross-Region Replication",
                    "description": "Set up cross-region replication for critical data",
                    "impact": "Improved disaster recovery and compliance",
                    "effort": "High",
                    "cost": "Replication costs",
                    "action": "Configure cross-region replication for critical buckets",
                },
                {
                    "category": "Best Practices",
                    "priority": "MEDIUM",
                    "title": "Enable Object Lock",
                    "description": "Enable object lock for compliance requirements",
                    "impact": "Enhanced data protection and compliance",
                    "effort": "Medium",
                    "cost": "Minimal",
                    "action": "Enable object lock for compliance buckets",
                },
                {
                    "category": "Best Practices",
                    "priority": "LOW",
                    "title": "Implement Tagging Strategy",
                    "description": "Implement comprehensive tagging for cost allocation",
                    "impact": "Better cost tracking and resource management",
                    "effort": "Medium",
                    "cost": "None",
                    "action": "Implement consistent tagging strategy",
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
        critical_priority = [r for r in recommendations if r["priority"] == "CRITICAL"]
        high_priority = [r for r in recommendations if r["priority"] == "HIGH"]
        medium_priority = [r for r in recommendations if r["priority"] == "MEDIUM"]

        if critical_priority:
            typer.echo(
                f"  {DANGER_EMOJI} {len(critical_priority)} critical items need immediate attention"
            )
        if high_priority:
            typer.echo(
                f"  {WARNING_EMOJI} {len(high_priority)} high-priority items for planning"
            )
        if medium_priority:
            typer.echo(
                f"  {TIP_EMOJI} {len(medium_priority)} medium-priority items for optimization"
            )

        typer.echo(f"\n{TIP_EMOJI} Implementation Strategy:")
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Address critical and high-priority items first"
        )
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Plan medium-priority items for next sprint"
        )
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Consider automation for repetitive tasks")

    except Exception as e:
        typer.echo(f"{ERROR_EMOJI} Error generating recommendations: {e}")


@s3_app.command()
def monitor(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
    days: int = typer.Option(30, "--days", "-d", help="Number of days to look back"),
    bucket_name: Optional[str] = typer.Option(
        None, "--bucket", "-b", help="Specific bucket to monitor"
    ),
    output_format: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
):
    """Monitor S3 bucket access patterns and security events."""
    typer.echo(f"{MONITORING_EMOJI} Monitoring S3 bucket access patterns...")

    try:
        clients = get_aws_clients(profile)
        s3_client = clients["s3"]
        cloudtrail_client = clients["cloudtrail"]

        # Get buckets to monitor
        buckets_to_monitor = []
        if bucket_name:
            buckets_to_monitor.append(bucket_name)
        else:
            try:
                response = s3_client.list_buckets()
                buckets_to_monitor = [bucket["Name"] for bucket in response["Buckets"]]
            except ClientError as e:
                typer.echo(f"{ERROR_EMOJI} Error listing buckets: {e}")
                return

        # Get CloudTrail events
        typer.echo(
            f"  {ANALYSIS_EMOJI} Analyzing access patterns (last {days} days)..."
        )

        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days)

            events = cloudtrail_client.lookup_events(
                StartTime=start_time,
                EndTime=end_time,
                LookupAttributes=[
                    {"AttributeKey": "EventName", "AttributeValue": "GetObject"},
                    {"AttributeKey": "EventName", "AttributeValue": "PutObject"},
                    {"AttributeKey": "EventName", "AttributeValue": "DeleteObject"},
                    {"AttributeKey": "EventName", "AttributeValue": "ListBucket"},
                ],
            )

            # Analyze access patterns
            access_by_bucket = defaultdict(lambda: defaultdict(int))
            access_by_user = defaultdict(lambda: defaultdict(int))

            for event in events["Events"]:
                event_data = json.loads(event.get("CloudTrailEvent", "{}"))
                request_params = event_data.get("requestParameters", {})

                bucket = request_params.get("bucketName") or request_params.get(
                    "bucket"
                )
                if bucket and bucket in buckets_to_monitor:
                    access_by_bucket[bucket][event["EventName"]] += 1

                    username = event.get("Username", "Unknown")
                    access_by_user[username][event["EventName"]] += 1

            # Display monitoring results
            typer.echo(f"\n{MONITORING_EMOJI} S3 Access Monitoring Results:")

            if output_format == "json":
                monitoring_data = {
                    "monitoring_period": f"Last {days} days",
                    "buckets_analyzed": len(buckets_to_monitor),
                    "access_by_bucket": dict(access_by_bucket),
                    "access_by_user": dict(access_by_user),
                }
                typer.echo(json.dumps(monitoring_data, indent=2, default=str))
            elif output_format == "csv":
                import csv
                import sys

                writer = csv.writer(sys.stdout)
                writer.writerow(["Bucket", "Event", "Count"])
                for bucket, events in access_by_bucket.items():
                    for event, count in events.items():
                        writer.writerow([bucket, event, count])
            else:
                # Bucket access summary
                typer.echo(f"  {ANALYSIS_EMOJI} Bucket Access Summary:")
                for bucket, events in access_by_bucket.items():
                    typer.echo(f"    {S3_EMOJI} {bucket}:")
                    total_access = sum(events.values())
                    typer.echo(f"      Total accesses: {total_access}")
                    for event, count in events.items():
                        typer.echo(f"      {event}: {count}")

                    if total_access > 1000:
                        typer.echo(
                            f"      {WARNING_EMOJI} High access frequency - review if necessary"
                        )

                # User access summary
                typer.echo(f"\n  {ACCESS_EMOJI} User Access Summary:")
                for user, events in access_by_user.items():
                    total_access = sum(events.values())
                    if total_access > 100:  # Only show high-access users
                        typer.echo(f"    {user}: {total_access} total accesses")
                        for event, count in events.items():
                            typer.echo(f"      {event}: {count}")

        except ClientError as e:
            if e.response["Error"]["Code"] == "AccessDenied":
                typer.echo(
                    f"  {WARNING_EMOJI} CloudTrail access denied - limited monitoring available"
                )
            else:
                typer.echo(f"  {WARNING_EMOJI} Error accessing CloudTrail: {e}")

        # Security monitoring recommendations
        typer.echo(f"\n{TIP_EMOJI} Monitoring Recommendations:")
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Set up CloudWatch alarms for unusual access patterns"
        )
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Monitor for unauthorized access attempts")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Review access patterns regularly")
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Implement automated alerts for security events"
        )

    except Exception as e:
        typer.echo(f"{ERROR_EMOJI} Error during monitoring: {e}")


@s3_app.command()
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
        True, "--include-metadata", help="Include bucket metadata"
    ),
    include_objects: bool = typer.Option(
        False, "--include-objects", help="Include object information"
    ),
):
    """Export S3 bucket data for analysis and reporting."""
    typer.echo(f"{EXPORT_EMOJI} Exporting S3 bucket data...")

    try:
        clients = get_aws_clients(profile)
        s3_client = clients["s3"]

        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "profile": profile or "default",
            "region": region or "all",
            "buckets": [],
            "summary": {},
        }

        # Get all buckets
        try:
            response = s3_client.list_buckets()
            buckets = [bucket["Name"] for bucket in response["Buckets"]]
        except ClientError as e:
            typer.echo(f"{ERROR_EMOJI} Error listing buckets: {e}")
            return

        for bucket in buckets:
            try:
                # Get bucket location
                location = s3_client.get_bucket_location(Bucket=bucket)
                bucket_region = location.get("LocationConstraint") or "us-east-1"

                # Skip if region specified and doesn't match
                if region and bucket_region != region:
                    continue

                bucket_data = {
                    "name": bucket,
                    "region": bucket_region,
                    "creation_date": response["Buckets"][0]["CreationDate"].isoformat(),
                }

                if include_metadata:
                    bucket_data.update(
                        {
                            "encryption": check_encryption(bucket, s3_client),
                            "versioning": check_versioning(bucket, s3_client),
                            "logging": check_logging(bucket, s3_client),
                            "lifecycle": check_lifecycle(bucket, s3_client),
                            "public_access": is_public_bucket(bucket, s3_client),
                        }
                    )

                if include_objects:
                    try:
                        objects = s3_client.list_objects_v2(Bucket=bucket, MaxKeys=1000)
                        if "Contents" in objects:
                            bucket_data["objects"] = {
                                "count": len(objects["Contents"]),
                                "total_size": sum(
                                    obj["Size"] for obj in objects["Contents"]
                                ),
                                "sample_objects": [
                                    obj["Key"] for obj in objects["Contents"][:10]
                                ],
                            }
                    except ClientError:
                        bucket_data["objects"] = {"error": "Access denied"}

                export_data["buckets"].append(bucket_data)

            except ClientError as e:
                if e.response["Error"]["Code"] != "AccessDenied":
                    typer.echo(
                        f"  {WARNING_EMOJI} Error processing bucket {bucket}: {e}"
                    )

        # Generate summary
        total_buckets = len(export_data["buckets"])
        public_buckets = len(
            [b for b in export_data["buckets"] if b.get("public_access", False)]
        )
        encrypted_buckets = len(
            [
                b
                for b in export_data["buckets"]
                if b.get("encryption", {}).get("enabled", False)
            ]
        )

        export_data["summary"] = {
            "total_buckets": total_buckets,
            "public_buckets": public_buckets,
            "encrypted_buckets": encrypted_buckets,
            "security_score": (
                (encrypted_buckets / total_buckets * 100) if total_buckets > 0 else 0
            ),
        }

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

            # Write buckets
            if export_data["buckets"]:
                fieldnames = list(export_data["buckets"][0].keys())
                writer.writerow(fieldnames)
                for bucket in export_data["buckets"]:
                    row = []
                    for field in fieldnames:
                        value = bucket.get(field, "")
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
            f"  {ANALYSIS_EMOJI} Total buckets: {export_data['summary']['total_buckets']}"
        )
        typer.echo(
            f"  {PUBLIC_EMOJI} Public buckets: {export_data['summary']['public_buckets']}"
        )
        typer.echo(
            f"  {ENCRYPTION_EMOJI} Encrypted buckets: {export_data['summary']['encrypted_buckets']}"
        )
        typer.echo(
            f"  {SECURITY_EMOJI} Security score: {export_data['summary']['security_score']:.1f}%"
        )

    except Exception as e:
        typer.echo(f"{ERROR_EMOJI} Error during export: {e}")


@s3_app.command()
def help():
    """Show detailed help for S3ntry commands."""
    typer.echo(f"{S3_EMOJI} S3ntry - AWS S3 Security and Compliance Module")
    typer.echo(f"\n{INNOVATION_EMOJI} Real-World DevSecOps Use Cases:")
    typer.echo(f"  {AUDIT_EMOJI} S3 Security Audit & Assessment")
    typer.echo(f"  {SCANNING_EMOJI} Targeted Security Scanning")
    typer.echo(f"  {COMPLIANCE_EMOJI} Multi-Framework Compliance Validation")
    typer.echo(f"  {REMEDIATION_EMOJI} Automated Security Remediation")
    typer.echo(f"  {TIP_EMOJI} Intelligent Optimization Recommendations")
    typer.echo(f"  {MONITORING_EMOJI} Access Pattern Monitoring")
    typer.echo(f"  {EXPORT_EMOJI} Data Export & Reporting")

    typer.echo(f"\n{INNOVATION_EMOJI} Advanced Features:")
    typer.echo(f"  {AUTOMATION_EMOJI} Smart automation with risk-based prioritization")
    typer.echo(f"  {DETECTION_EMOJI} Sensitive data detection and classification")
    typer.echo(
        f"  {INTEGRATION_EMOJI} Multi-service integration (S3, CloudTrail, Config)"
    )
    typer.echo(f"  {SCHEDULING_EMOJI} Intelligent lifecycle management recommendations")
    typer.echo(f"  {NOTIFICATION_EMOJI} Proactive security alerting")
    typer.echo(
        f"  {VALIDATION_EMOJI} Automated compliance validation across frameworks"
    )

    typer.echo(f"\n{TIP_EMOJI} Best Practices:")
    typer.echo(f"  {BEST_PRACTICE_EMOJI} Block public access by default")
    typer.echo(f"  {BEST_PRACTICE_EMOJI} Enable encryption for all data")
    typer.echo(f"  {BEST_PRACTICE_EMOJI} Use KMS encryption for sensitive data")
    typer.echo(f"  {BEST_PRACTICE_EMOJI} Enable versioning for data protection")
    typer.echo(f"  {AVOID_EMOJI} Never use public read/write permissions")
    typer.echo(
        f"  {BEST_PRACTICE_EMOJI} Configure comprehensive logging and monitoring"
    )

    typer.echo(f"\n{INNOVATION_EMOJI} Innovation Highlights:")
    typer.echo(f"  {RISK_EMOJI} Risk-based prioritization for remediation actions")
    typer.echo(
        f"  {ANALYSIS_EMOJI} Intelligent analysis of access patterns and security trends"
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

    typer.echo(f"\n{SECURITY_EMOJI} Security Focus:")
    typer.echo(f"  {S3_EMOJI} Comprehensive S3 bucket security assessment")
    typer.echo(f"  {ENCRYPTION_EMOJI} Encryption validation and enforcement")
    typer.echo(f"  {ACCESS_EMOJI} Access control analysis and remediation")
    typer.echo(f"  {COMPLIANCE_EMOJI} Automated compliance validation")
    typer.echo(f"  {REMEDIATION_EMOJI} Intelligent issue remediation")
    typer.echo(f"  {DETECTION_EMOJI} Sensitive data detection and protection")

    typer.echo(f"\n{INNOVATION_EMOJI} DevSecOps Integration:")
    typer.echo(f"  {AUTOMATION_EMOJI} CI/CD pipeline integration for S3 security")
    typer.echo(f"  {MONITORING_EMOJI} Integration with monitoring and alerting systems")
    typer.echo(f"  {COMPLIANCE_EMOJI} Automated compliance reporting for audits")
    typer.echo(
        f"  {INTEGRATION_EMOJI} Integration with security tools and SIEM systems"
    )
    typer.echo(f"  {EXPORT_EMOJI} Data export for custom reporting and analysis")
    typer.echo(
        f"  {SCHEDULING_EMOJI} Intelligent lifecycle management based on usage patterns"
    )

    typer.echo(
        f"\n{SUCCESS_EMOJI} Ready to secure your S3 buckets with intelligent automation!"
    )


if __name__ == "__main__":
    s3_app()
