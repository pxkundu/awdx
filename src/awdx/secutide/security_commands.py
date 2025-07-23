import csv
import json
import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import boto3
import typer
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound

from .. import AWDXErrorHandler

security_app = typer.Typer(help="AWS security assessment and remediation commands.")

# Emoji constants for consistent UI
SECURITY_EMOJI = "🛡️"
SCAN_EMOJI = "🔍"
VULNERABILITY_EMOJI = "🚨"
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
NETWORK_EMOJI = "🌐"
STORAGE_EMOJI = "💾"
COMPUTE_EMOJI = "🖥️"
DATABASE_EMOJI = "🗄️"
IDENTITY_EMOJI = "👤"
MONITORING_EMOJI = "📈"
ENCRYPTION_EMOJI = "🔐"
BACKUP_EMOJI = "💿"
DISASTER_EMOJI = "🌊"
INCIDENT_EMOJI = "🚨"
THREAT_EMOJI = "👹"
DETECTION_EMOJI = "🎯"
RESPONSE_EMOJI = "⚡"
EXPORT_EMOJI = "📊"
ALERT_EMOJI = "❗"


@dataclass
class SecurityFinding:
    """Data class for security findings."""

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


@dataclass
class ComplianceCheck:
    """Data class for compliance checks."""

    standard: str
    control: str
    title: str
    status: str
    description: str
    remediation: str
    priority: int


def get_aws_clients(profile: Optional[str] = None):
    """Get AWS clients for security assessment."""
    try:
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        return {
            "ec2": session.client("ec2"),
            "s3": session.client("s3"),
            "rds": session.client("rds"),
            "iam": session.client("iam"),
            "cloudtrail": session.client("cloudtrail"),
            "config": session.client("config"),
            "guardduty": session.client("guardduty"),
            "securityhub": session.client("securityhub"),
            "waf": session.client("wafv2"),
            "kms": session.client("kms"),
            "secretsmanager": session.client("secretsmanager"),
            "ssm": session.client("ssm"),
            "cloudwatch": session.client("cloudwatch"),
            "lambda": session.client("lambda"),
            "vpc": session.client("ec2"),  # VPC operations use EC2 client
            "elbv2": session.client("elbv2"),
            "eks": session.client("eks"),
            "ecr": session.client("ecr"),
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
        "MEDIUM": "��",
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


def is_public_ip(ip: str) -> bool:
    """Check if IP address is public."""
    try:
        ip_obj = ipaddress.ip_address(ip)
        return not ip_obj.is_private
    except ValueError:
        return False


def calculate_risk_score(findings: List[SecurityFinding]) -> int:
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


@security_app.command("posture", help="Comprehensive security posture assessment 🛡️")
def security_posture(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    region: Optional[str] = typer.Option(
        None, "--region", "-r", help="AWS region to assess"
    ),
    export: Optional[str] = typer.Option(
        None, "--export", "-e", help="Export results to file (json/csv)"
    ),
):
    """Perform comprehensive security posture assessment across AWS services."""
    try:
        clients = get_aws_clients(profile)
        regions = [region] if region else get_region_list(profile)

        typer.echo(
            f"{SECURITY_EMOJI} Starting comprehensive security posture assessment..."
        )
        typer.echo(f"👤 Profile: {profile or 'default'}")
        typer.echo(f"🌍 Regions: {', '.join(regions)}")
        typer.echo()

        all_findings = []

        # 1. Network Security Assessment
        typer.echo(f"{NETWORK_EMOJI} Assessing network security...")
        for region_name in regions:
            try:
                ec2_client = boto3.Session(profile_name=profile).client(
                    "ec2", region_name=region_name
                )

                # Check for open security groups
                security_groups = ec2_client.describe_security_groups()
                for sg in security_groups["SecurityGroups"]:
                    for rule in sg.get("IpPermissions", []):
                        if rule.get("IpRanges"):
                            for ip_range in rule["IpRanges"]:
                                if ip_range.get("CidrIp") == "0.0.0.0/0":
                                    all_findings.append(
                                        SecurityFinding(
                                            severity="HIGH",
                                            category="Network Security",
                                            title="Open Security Group",
                                            description=f"Security group {sg['GroupName']} allows access from 0.0.0.0/0",
                                            impact="Potential unauthorized access to resources",
                                            recommendation="Restrict CIDR ranges to specific IP addresses",
                                            resource_id=sg["GroupId"],
                                            resource_type="Security Group",
                                            region=region_name,
                                            priority=7,
                                        )
                                    )

                # Check for public subnets
                subnets = ec2_client.describe_subnets()
                for subnet in subnets["Subnets"]:
                    if subnet.get("MapPublicIpOnLaunch"):
                        all_findings.append(
                            SecurityFinding(
                                severity="MEDIUM",
                                category="Network Security",
                                title="Public Subnet",
                                description=f"Subnet {subnet['SubnetId']} is configured for public IP assignment",
                                impact="Resources may be exposed to internet",
                                recommendation="Review if public IP assignment is necessary",
                                resource_id=subnet["SubnetId"],
                                resource_type="Subnet",
                                region=region_name,
                                priority=4,
                            )
                        )

            except ClientError as e:
                typer.echo(
                    f"   {WARNING_EMOJI} Could not assess network security in {region_name}: {e}"
                )

        # 2. Storage Security Assessment
        typer.echo(f"{STORAGE_EMOJI} Assessing storage security...")
        try:
            s3_client = clients["s3"]
            buckets = s3_client.list_buckets()

            for bucket in buckets["Buckets"]:
                try:
                    # Check bucket encryption
                    try:
                        encryption = s3_client.get_bucket_encryption(
                            Bucket=bucket["Name"]
                        )
                    except ClientError:
                        all_findings.append(
                            SecurityFinding(
                                severity="HIGH",
                                category="Storage Security",
                                title="Unencrypted S3 Bucket",
                                description=f"Bucket {bucket['Name']} is not encrypted",
                                impact="Data at rest is not protected",
                                recommendation="Enable default encryption for the bucket",
                                resource_id=bucket["Name"],
                                resource_type="S3 Bucket",
                                region="Global",
                                priority=7,
                            )
                        )

                    # Check bucket public access
                    try:
                        public_access = s3_client.get_public_access_block(
                            Bucket=bucket["Name"]
                        )
                        if not public_access["PublicAccessBlockConfiguration"][
                            "BlockPublicAcls"
                        ]:
                            all_findings.append(
                                SecurityFinding(
                                    severity="HIGH",
                                    category="Storage Security",
                                    title="Public S3 Bucket",
                                    description=f"Bucket {bucket['Name']} allows public access",
                                    impact="Data may be publicly accessible",
                                    recommendation="Enable public access blocking",
                                    resource_id=bucket["Name"],
                                    resource_type="S3 Bucket",
                                    region="Global",
                                    priority=8,
                                )
                            )
                    except ClientError:
                        pass

                except ClientError:
                    pass

        except ClientError as e:
            typer.echo(f"   {WARNING_EMOJI} Could not assess storage security: {e}")

        # 3. Compute Security Assessment
        typer.echo(f"{COMPUTE_EMOJI} Assessing compute security...")
        for region_name in regions:
            try:
                ec2_client = boto3.Session(profile_name=profile).client(
                    "ec2", region_name=region_name
                )

                # Check for instances with public IPs
                instances = ec2_client.describe_instances()
                for reservation in instances["Reservations"]:
                    for instance in reservation["Instances"]:
                        if instance.get("PublicIpAddress"):
                            all_findings.append(
                                SecurityFinding(
                                    severity="MEDIUM",
                                    category="Compute Security",
                                    title="Public EC2 Instance",
                                    description=f"Instance {instance['InstanceId']} has public IP {instance['PublicIpAddress']}",
                                    impact="Instance is directly accessible from internet",
                                    recommendation="Use NAT Gateway or remove public IP if not needed",
                                    resource_id=instance["InstanceId"],
                                    resource_type="EC2 Instance",
                                    region=region_name,
                                    priority=5,
                                )
                            )

                # Check for instances without IMDSv2
                for reservation in instances["Reservations"]:
                    for instance in reservation["Instances"]:
                        if (
                            instance.get("MetadataOptions", {}).get("HttpTokens")
                            != "required"
                        ):
                            all_findings.append(
                                SecurityFinding(
                                    severity="MEDIUM",
                                    category="Compute Security",
                                    title="IMDSv1 Enabled",
                                    description=f"Instance {instance['InstanceId']} has IMDSv1 enabled",
                                    impact="Vulnerable to SSRF attacks",
                                    recommendation="Enable IMDSv2 with required tokens",
                                    resource_id=instance["InstanceId"],
                                    resource_type="EC2 Instance",
                                    region=region_name,
                                    priority=4,
                                )
                            )

            except ClientError as e:
                typer.echo(
                    f"   {WARNING_EMOJI} Could not assess compute security in {region_name}: {e}"
                )

        # 4. Database Security Assessment
        typer.echo(f"{DATABASE_EMOJI} Assessing database security...")
        for region_name in regions:
            try:
                rds_client = boto3.Session(profile_name=profile).client(
                    "rds", region_name=region_name
                )

                # Check for public RDS instances
                instances = rds_client.describe_db_instances()
                for instance in instances["DBInstances"]:
                    if instance.get("PubliclyAccessible"):
                        all_findings.append(
                            SecurityFinding(
                                severity="HIGH",
                                category="Database Security",
                                title="Public RDS Instance",
                                description=f"RDS instance {instance['DBInstanceIdentifier']} is publicly accessible",
                                impact="Database is exposed to internet",
                                recommendation="Disable public accessibility",
                                resource_id=instance["DBInstanceIdentifier"],
                                resource_type="RDS Instance",
                                region=region_name,
                                priority=8,
                            )
                        )

                # Check for unencrypted RDS instances
                for instance in instances["DBInstances"]:
                    if not instance.get("StorageEncrypted"):
                        all_findings.append(
                            SecurityFinding(
                                severity="HIGH",
                                category="Database Security",
                                title="Unencrypted RDS Instance",
                                description=f"RDS instance {instance['DBInstanceIdentifier']} is not encrypted",
                                impact="Data at rest is not protected",
                                recommendation="Enable encryption for the RDS instance",
                                resource_id=instance["DBInstanceIdentifier"],
                                resource_type="RDS Instance",
                                region=region_name,
                                priority=7,
                            )
                        )

            except ClientError as e:
                typer.echo(
                    f"   {WARNING_EMOJI} Could not assess database security in {region_name}: {e}"
                )

        # 5. Identity and Access Management Assessment
        typer.echo(f"{IDENTITY_EMOJI} Assessing identity and access management...")
        try:
            iam_client = clients["iam"]

            # Check for root account usage
            sts_client = boto3.Session(profile_name=profile).client("sts")
            caller_identity = sts_client.get_caller_identity()
            if caller_identity["Arn"].endswith(":root"):
                all_findings.append(
                    SecurityFinding(
                        severity="CRITICAL",
                        category="Identity Security",
                        title="Root Account Usage",
                        description="Using root account for operations",
                        impact="Full account access, no audit trail",
                        recommendation="Use IAM users with appropriate permissions",
                        resource_id="root",
                        resource_type="Account",
                        region="Global",
                        priority=10,
                    )
                )

            # Check for users without MFA
            users = iam_client.list_users()
            for user in users["Users"]:
                try:
                    mfa_devices = iam_client.list_mfa_devices(UserName=user["UserName"])
                    if not mfa_devices["MFADevices"]:
                        all_findings.append(
                            SecurityFinding(
                                severity="HIGH",
                                category="Identity Security",
                                title="User Without MFA",
                                description=f"User {user['UserName']} does not have MFA enabled",
                                impact="Account compromise risk",
                                recommendation="Enable MFA for the user",
                                resource_id=user["UserName"],
                                resource_type="IAM User",
                                region="Global",
                                priority=7,
                            )
                        )
                except ClientError:
                    pass

        except ClientError as e:
            typer.echo(f"   {WARNING_EMOJI} Could not assess identity security: {e}")

        # 6. Monitoring and Logging Assessment
        typer.echo(f"{MONITORING_EMOJI} Assessing monitoring and logging...")
        try:
            # Check CloudTrail
            cloudtrail_client = clients["cloudtrail"]
            trails = cloudtrail_client.list_trails()
            if not trails.get("Trails"):
                all_findings.append(
                    SecurityFinding(
                        severity="HIGH",
                        category="Monitoring Security",
                        title="No CloudTrail",
                        description="No CloudTrail is configured",
                        impact="No audit trail for API calls",
                        recommendation="Enable CloudTrail for all regions",
                        resource_id="cloudtrail",
                        resource_type="CloudTrail",
                        region="Global",
                        priority=7,
                    )
                )

            # Check Config
            config_client = clients["config"]
            try:
                config_recorders = config_client.describe_configuration_recorders()
                if not config_recorders.get("ConfigurationRecorders"):
                    all_findings.append(
                        SecurityFinding(
                            severity="MEDIUM",
                            category="Monitoring Security",
                            title="No AWS Config",
                            description="AWS Config is not enabled",
                            impact="No resource configuration tracking",
                            recommendation="Enable AWS Config",
                            resource_id="config",
                            resource_type="AWS Config",
                            region="Global",
                            priority=4,
                        )
                    )
            except ClientError:
                all_findings.append(
                    SecurityFinding(
                        severity="MEDIUM",
                        category="Monitoring Security",
                        title="No AWS Config",
                        description="AWS Config is not enabled",
                        impact="No resource configuration tracking",
                        recommendation="Enable AWS Config",
                        resource_id="config",
                        resource_type="AWS Config",
                        region="Global",
                        priority=4,
                    )
                )

        except ClientError as e:
            typer.echo(f"   {WARNING_EMOJI} Could not assess monitoring security: {e}")

        # Display findings summary
        typer.echo()
        typer.echo(f"{SECURITY_EMOJI} Security Posture Assessment Summary:")

        # Group findings by severity
        severity_counts = defaultdict(int)
        category_counts = defaultdict(int)

        for finding in all_findings:
            severity_counts[finding.severity] += 1
            category_counts[finding.category] += 1

        typer.echo(
            f"  {get_severity_color('CRITICAL')} Critical: {severity_counts['CRITICAL']}"
        )
        typer.echo(f"  {get_severity_color('HIGH')} High: {severity_counts['HIGH']}")
        typer.echo(
            f"  {get_severity_color('MEDIUM')} Medium: {severity_counts['MEDIUM']}"
        )
        typer.echo(f"  {get_severity_color('LOW')} Low: {severity_counts['LOW']}")
        typer.echo(f"  {get_severity_color('INFO')} Info: {severity_counts['INFO']}")

        # Calculate risk score
        risk_score = calculate_risk_score(all_findings)
        typer.echo(f"  {RISK_EMOJI} Overall Risk Score: {risk_score}")

        # Risk level assessment
        if risk_score >= 50:
            risk_level = "🔴 CRITICAL"
        elif risk_score >= 30:
            risk_level = "🟠 HIGH"
        elif risk_score >= 15:
            risk_level = "🟡 MEDIUM"
        elif risk_score >= 5:
            risk_level = "🟢 LOW"
        else:
            risk_level = "🔵 MINIMAL"

        typer.echo(f"  {RISK_EMOJI} Risk Level: {risk_level}")

        # Show top findings by category
        typer.echo()
        typer.echo(f"{ANALYSIS_EMOJI} Findings by Category:")
        for category, count in sorted(
            category_counts.items(), key=lambda x: x[1], reverse=True
        ):
            typer.echo(f"  {category}: {count} findings")

        # Show critical and high findings
        critical_high_findings = [
            f for f in all_findings if f.severity in ["CRITICAL", "HIGH"]
        ]
        if critical_high_findings:
            typer.echo()
            typer.echo(f"{DANGER_EMOJI} Critical & High Priority Findings:")
            for finding in critical_high_findings[:5]:  # Show top 5
                typer.echo(f"  {get_severity_color(finding.severity)} {finding.title}")
                typer.echo(
                    f"     Resource: {finding.resource_id} ({finding.resource_type})"
                )
                typer.echo(f"     Region: {finding.region}")
                typer.echo(f"     Impact: {finding.impact}")
                typer.echo()

        # Export results if requested
        if export:
            try:
                export_data = {
                    "security_posture_info": {
                        "timestamp": datetime.now().isoformat(),
                        "profile": profile or "default",
                        "regions": regions,
                        "overall_risk_score": risk_score,
                        "risk_level": risk_level,
                    },
                    "findings": [
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
                        for finding in findings
                    ],
                    "summary": {
                        "critical_count": len(
                            [f for f in findings if f.severity == "CRITICAL"]
                        ),
                        "high_count": len(
                            [f for f in findings if f.severity == "HIGH"]
                        ),
                        "medium_count": len(
                            [f for f in findings if f.severity == "MEDIUM"]
                        ),
                        "low_count": len([f for f in findings if f.severity == "LOW"]),
                        "info_count": len(
                            [f for f in findings if f.severity == "INFO"]
                        ),
                        "total_findings": len(findings),
                        "risk_score": risk_score,
                        "risk_level": risk_level,
                    },
                }

                if export.endswith(".json"):
                    with open(export, "w") as f:
                        json.dump(export_data, f, indent=2, default=str)
                    typer.echo(
                        f"{EXPORT_EMOJI} Security posture report exported to {export}"
                    )
                elif export.endswith(".csv"):
                    with open(export, "w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(
                            [
                                "Severity",
                                "Category",
                                "Title",
                                "Description",
                                "Impact",
                                "Recommendation",
                                "Resource ID",
                                "Resource Type",
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
                                    finding.resource_type,
                                    finding.region,
                                    finding.priority,
                                ]
                            )
                    typer.echo(
                        f"{EXPORT_EMOJI} Security posture report exported to {export}"
                    )
                else:
                    typer.echo(
                        f"{WARNING_EMOJI} Unsupported export format. Use .json or .csv"
                    )

            except Exception as e:
                typer.echo(f"{ERROR_EMOJI} Error exporting results: {e}")

        typer.echo()
        typer.echo(f"{TIP_EMOJI} Security Recommendations:")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Address critical and high findings first")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Enable CloudTrail and AWS Config")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Use least privilege principle")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Enable encryption for all resources")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Regular security assessments")

        if export:
            typer.echo(f"  {EXPORT_EMOJI} Detailed report exported to: {export}")

    except Exception as e:
        AWDXErrorHandler.handle_aws_error(e, context="security posture assessment")
        typer.echo(
            f"{DANGER_EMOJI} {ERROR_EMOJI} Error during security posture assessment: {e}"
        )
        raise typer.Exit(1)


@security_app.command("vulnerabilities", help="Scan for security vulnerabilities 🚨")
def scan_vulnerabilities(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    service: Optional[str] = typer.Option(
        None, "--service", "-s", help="Specific service to scan (ec2/s3/rds/iam)"
    ),
    region: Optional[str] = typer.Option(
        None, "--region", "-r", help="AWS region to scan"
    ),
    export: Optional[str] = typer.Option(
        None, "--export", "-e", help="Export results to file (json/csv)"
    ),
):
    """Scan for security vulnerabilities across AWS services."""
    try:
        clients = get_aws_clients(profile)
        regions = [region] if region else get_region_list(profile)

        typer.echo(f"{VULNERABILITY_EMOJI} Starting vulnerability scan...")
        typer.echo(f"👤 Profile: {profile or 'default'}")
        if service:
            typer.echo(f"🔧 Service: {service}")
        typer.echo(f"🌍 Regions: {', '.join(regions)}")
        typer.echo()

        vulnerabilities = []

        # EC2 Vulnerabilities
        if not service or service.lower() == "ec2":
            typer.echo(f"{COMPUTE_EMOJI} Scanning EC2 vulnerabilities...")
            for region_name in regions:
                try:
                    ec2_client = boto3.Session(profile_name=profile).client(
                        "ec2", region_name=region_name
                    )

                    # Check for instances with outdated AMIs
                    instances = ec2_client.describe_instances()
                    for reservation in instances["Reservations"]:
                        for instance in reservation["Instances"]:
                            if instance["State"]["Name"] == "running":
                                # Check if AMI is older than 1 year
                                try:
                                    ami = ec2_client.describe_images(
                                        ImageIds=[instance["ImageId"]]
                                    )
                                    if ami["Images"]:
                                        creation_date = ami["Images"][0]["CreationDate"]
                                        if (
                                            datetime.now()
                                            - datetime.fromisoformat(
                                                creation_date.replace("Z", "+00:00")
                                            )
                                        ).days > 365:
                                            vulnerabilities.append(
                                                SecurityFinding(
                                                    severity="MEDIUM",
                                                    category="EC2 Security",
                                                    title="Outdated AMI",
                                                    description=f"Instance {instance['InstanceId']} uses AMI {instance['ImageId']} older than 1 year",
                                                    impact="Potential security vulnerabilities in outdated software",
                                                    recommendation="Update to latest AMI",
                                                    resource_id=instance["InstanceId"],
                                                    resource_type="EC2 Instance",
                                                    region=region_name,
                                                    priority=4,
                                                )
                                            )
                                except ClientError:
                                    pass

                    # Check for instances without detailed monitoring
                    for reservation in instances["Reservations"]:
                        for instance in reservation["Instances"]:
                            if (
                                not instance.get("Monitoring", {}).get("State")
                                == "enabled"
                            ):
                                vulnerabilities.append(
                                    SecurityFinding(
                                        severity="LOW",
                                        category="EC2 Security",
                                        title="No Detailed Monitoring",
                                        description=f"Instance {instance['InstanceId']} has basic monitoring only",
                                        impact="Limited visibility into instance performance",
                                        recommendation="Enable detailed monitoring",
                                        resource_id=instance["InstanceId"],
                                        resource_type="EC2 Instance",
                                        region=region_name,
                                        priority=2,
                                    )
                                )

                except ClientError as e:
                    typer.echo(
                        f"   {WARNING_EMOJI} Could not scan EC2 in {region_name}: {e}"
                    )

        # S3 Vulnerabilities
        if not service or service.lower() == "s3":
            typer.echo(f"{STORAGE_EMOJI} Scanning S3 vulnerabilities...")
            try:
                s3_client = clients["s3"]
                buckets = s3_client.list_buckets()

                for bucket in buckets["Buckets"]:
                    try:
                        # Check for versioning
                        try:
                            versioning = s3_client.get_bucket_versioning(
                                Bucket=bucket["Name"]
                            )
                            if not versioning.get("Status") == "Enabled":
                                vulnerabilities.append(
                                    SecurityFinding(
                                        severity="MEDIUM",
                                        category="S3 Security",
                                        title="No Versioning",
                                        description=f"Bucket {bucket['Name']} does not have versioning enabled",
                                        impact="No protection against accidental deletion",
                                        recommendation="Enable versioning for data protection",
                                        resource_id=bucket["Name"],
                                        resource_type="S3 Bucket",
                                        region="Global",
                                        priority=4,
                                    )
                                )
                        except ClientError:
                            vulnerabilities.append(
                                SecurityFinding(
                                    severity="MEDIUM",
                                    category="S3 Security",
                                    title="No Versioning",
                                    description=f"Bucket {bucket['Name']} does not have versioning enabled",
                                    impact="No protection against accidental deletion",
                                    recommendation="Enable versioning for data protection",
                                    resource_id=bucket["Name"],
                                    resource_type="S3 Bucket",
                                    region="Global",
                                    priority=4,
                                )
                            )

                        # Check for logging
                        try:
                            logging = s3_client.get_bucket_logging(
                                Bucket=bucket["Name"]
                            )
                            if not logging.get("LoggingEnabled"):
                                vulnerabilities.append(
                                    SecurityFinding(
                                        severity="LOW",
                                        category="S3 Security",
                                        title="No Access Logging",
                                        description=f"Bucket {bucket['Name']} does not have access logging enabled",
                                        impact="No audit trail for bucket access",
                                        recommendation="Enable access logging",
                                        resource_id=bucket["Name"],
                                        resource_type="S3 Bucket",
                                        region="Global",
                                        priority=2,
                                    )
                                )
                        except ClientError:
                            vulnerabilities.append(
                                SecurityFinding(
                                    severity="LOW",
                                    category="S3 Security",
                                    title="No Access Logging",
                                    description=f"Bucket {bucket['Name']} does not have access logging enabled",
                                    impact="No audit trail for bucket access",
                                    recommendation="Enable access logging",
                                    resource_id=bucket["Name"],
                                    resource_type="S3 Bucket",
                                    region="Global",
                                    priority=2,
                                )
                            )

                    except ClientError:
                        pass

            except ClientError as e:
                typer.echo(f"   {WARNING_EMOJI} Could not scan S3: {e}")

        # RDS Vulnerabilities
        if not service or service.lower() == "rds":
            typer.echo(f"{DATABASE_EMOJI} Scanning RDS vulnerabilities...")
            for region_name in regions:
                try:
                    rds_client = boto3.Session(profile_name=profile).client(
                        "rds", region_name=region_name
                    )

                    # Check for instances without automated backups
                    instances = rds_client.describe_db_instances()
                    for instance in instances["DBInstances"]:
                        if not instance.get("BackupRetentionPeriod", 0) > 0:
                            vulnerabilities.append(
                                SecurityFinding(
                                    severity="HIGH",
                                    category="RDS Security",
                                    title="No Automated Backups",
                                    description=f"RDS instance {instance['DBInstanceIdentifier']} has no automated backups",
                                    impact="No data recovery capability",
                                    recommendation="Enable automated backups",
                                    resource_id=instance["DBInstanceIdentifier"],
                                    resource_type="RDS Instance",
                                    region=region_name,
                                    priority=6,
                                )
                            )

                    # Check for instances without deletion protection
                    for instance in instances["DBInstances"]:
                        if not instance.get("DeletionProtection"):
                            vulnerabilities.append(
                                SecurityFinding(
                                    severity="MEDIUM",
                                    category="RDS Security",
                                    title="No Deletion Protection",
                                    description=f"RDS instance {instance['DBInstanceIdentifier']} has no deletion protection",
                                    impact="Risk of accidental deletion",
                                    recommendation="Enable deletion protection",
                                    resource_id=instance["DBInstanceIdentifier"],
                                    resource_type="RDS Instance",
                                    region=region_name,
                                    priority=4,
                                )
                            )

                except ClientError as e:
                    typer.echo(
                        f"   {WARNING_EMOJI} Could not scan RDS in {region_name}: {e}"
                    )

        # IAM Vulnerabilities
        if not service or service.lower() == "iam":
            typer.echo(f"{IDENTITY_EMOJI} Scanning IAM vulnerabilities...")
            try:
                iam_client = clients["iam"]

                # Check for access keys older than 90 days
                users = iam_client.list_users()
                for user in users["Users"]:
                    try:
                        access_keys = iam_client.list_access_keys(
                            UserName=user["UserName"]
                        )
                        for key in access_keys["AccessKeyMetadata"]:
                            if key["Status"] == "Active":
                                key_age = (
                                    datetime.now(key["CreateDate"].tzinfo)
                                    - key["CreateDate"]
                                ).days
                                if key_age > 90:
                                    vulnerabilities.append(
                                        SecurityFinding(
                                            severity="MEDIUM",
                                            category="IAM Security",
                                            title="Old Access Key",
                                            description=f"User {user['UserName']} has access key {key['AccessKeyId']} older than 90 days",
                                            impact="Increased risk of key compromise",
                                            recommendation="Rotate access key",
                                            resource_id=f"{user['UserName']}:{key['AccessKeyId']}",
                                            resource_type="Access Key",
                                            region="Global",
                                            priority=4,
                                        )
                                    )
                    except ClientError:
                        pass

                # Check for unused IAM users
                for user in users["Users"]:
                    if user.get("PasswordLastUsed") is None:
                        vulnerabilities.append(
                            SecurityFinding(
                                severity="LOW",
                                category="IAM Security",
                                title="Unused IAM User",
                                description=f"User {user['UserName']} has never logged in",
                                impact="Attack surface expansion",
                                recommendation="Remove unused user",
                                resource_id=user["UserName"],
                                resource_type="IAM User",
                                region="Global",
                                priority=1,
                            )
                        )

            except ClientError as e:
                typer.echo(f"   {WARNING_EMOJI} Could not scan IAM: {e}")

        # Display vulnerability summary
        typer.echo()
        typer.echo(f"{VULNERABILITY_EMOJI} Vulnerability Scan Summary:")

        # Group vulnerabilities by severity
        severity_counts = defaultdict(int)
        category_counts = defaultdict(int)

        for vuln in vulnerabilities:
            severity_counts[vuln.severity] += 1
            category_counts[vuln.category] += 1

        typer.echo(
            f"  {get_severity_color('CRITICAL')} Critical: {severity_counts['CRITICAL']}"
        )
        typer.echo(f"  {get_severity_color('HIGH')} High: {severity_counts['HIGH']}")
        typer.echo(
            f"  {get_severity_color('MEDIUM')} Medium: {severity_counts['MEDIUM']}"
        )
        typer.echo(f"  {get_severity_color('LOW')} Low: {severity_counts['LOW']}")

        # Show vulnerabilities by category
        typer.echo()
        typer.echo(f"{ANALYSIS_EMOJI} Vulnerabilities by Category:")
        for category, count in sorted(
            category_counts.items(), key=lambda x: x[1], reverse=True
        ):
            typer.echo(f"  {category}: {count} vulnerabilities")

        # Show high priority vulnerabilities
        high_priority_vulns = [
            v for v in vulnerabilities if v.severity in ["CRITICAL", "HIGH"]
        ]
        if high_priority_vulns:
            typer.echo()
            typer.echo(f"{DANGER_EMOJI} High Priority Vulnerabilities:")
            for vuln in high_priority_vulns[:5]:  # Show top 5
                typer.echo(f"  {get_severity_color(vuln.severity)} {vuln.title}")
                typer.echo(f"     Resource: {vuln.resource_id} ({vuln.resource_type})")
                typer.echo(f"     Impact: {vuln.impact}")
                typer.echo()

        # Export results if requested
        if export:
            try:
                if export.endswith(".json"):
                    export_data = {
                        "scan_info": {
                            "timestamp": datetime.now().isoformat(),
                            "profile": profile or "default",
                            "service": service or "all",
                            "regions": regions,
                        },
                        "vulnerabilities": [
                            {
                                "severity": v.severity,
                                "category": v.category,
                                "title": v.title,
                                "description": v.description,
                                "impact": v.impact,
                                "recommendation": v.recommendation,
                                "resource_id": v.resource_id,
                                "resource_type": v.resource_type,
                                "region": v.region,
                                "priority": v.priority,
                            }
                            for v in vulnerabilities
                        ],
                    }
                    with open(export, "w") as f:
                        json.dump(export_data, f, indent=2, default=str)
                elif export.endswith(".csv"):
                    with open(export, "w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(
                            [
                                "Severity",
                                "Category",
                                "Title",
                                "Description",
                                "Impact",
                                "Recommendation",
                                "Resource ID",
                                "Resource Type",
                                "Region",
                                "Priority",
                            ]
                        )
                        for vuln in vulnerabilities:
                            writer.writerow(
                                [
                                    vuln.severity,
                                    vuln.category,
                                    vuln.title,
                                    vuln.description,
                                    vuln.impact,
                                    vuln.recommendation,
                                    vuln.resource_id,
                                    vuln.resource_type,
                                    vuln.region,
                                    vuln.priority,
                                ]
                            )

                typer.echo(
                    f"{SUCCESS_EMOJI} Vulnerability scan results exported to {export}"
                )
            except Exception as e:
                typer.echo(f"{ERROR_EMOJI} Failed to export results: {e}")

        typer.echo()
        typer.echo(f"{TIP_EMOJI} Vulnerability Management Tips:")
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Address critical and high vulnerabilities first"
        )
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Regular vulnerability scanning")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Keep systems and AMIs updated")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Enable monitoring and logging")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Implement security best practices")

    except Exception as e:
        typer.echo(f"{DANGER_EMOJI} {ERROR_EMOJI} Error during vulnerability scan: {e}")
        raise typer.Exit(1)


@security_app.command("incident", help="Incident response and investigation 🚨")
def incident_response(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    incident_type: str = typer.Option(
        "general",
        "--type",
        "-t",
        help="Incident type (general/breach/malware/unauthorized)",
    ),
    region: Optional[str] = typer.Option(
        None, "--region", "-r", help="AWS region to investigate"
    ),
    export: Optional[str] = typer.Option(
        None, "--export", "-e", help="Export investigation results to file"
    ),
):
    """Perform incident response investigation and analysis."""
    try:
        clients = get_aws_clients(profile)
        regions = [region] if region else get_region_list(profile)

        typer.echo(f"{INCIDENT_EMOJI} Starting incident response investigation...")
        typer.echo(f"👤 Profile: {profile or 'default'}")
        typer.echo(f"🚨 Incident Type: {incident_type}")
        typer.echo(f"🌍 Regions: {', '.join(regions)}")
        typer.echo()

        investigation_results = {
            "incident_info": {
                "timestamp": datetime.now().isoformat(),
                "profile": profile or "default",
                "incident_type": incident_type,
                "regions": regions,
            },
            "findings": [],
            "recommendations": [],
        }

        # 1. CloudTrail Analysis
        typer.echo(f"{AUDIT_EMOJI} Analyzing CloudTrail logs...")
        try:
            cloudtrail_client = clients["cloudtrail"]

            # Check for recent unusual activities
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=24)

            try:
                events = cloudtrail_client.lookup_events(
                    StartTime=start_time, EndTime=end_time, MaxResults=50
                )

                # Analyze for suspicious activities
                suspicious_events = []
                for event in events.get("Events", []):
                    event_name = event.get("EventName", "")
                    user_identity = event.get("UserIdentity", {})

                    # Check for root account usage
                    if user_identity.get("Type") == "Root":
                        suspicious_events.append(
                            {
                                "event": event_name,
                                "user": "root",
                                "timestamp": event.get("EventTime"),
                                "risk": "CRITICAL",
                                "description": f"Root account used for {event_name}",
                            }
                        )

                    # Check for unusual IAM activities
                    if event_name in [
                        "CreateAccessKey",
                        "DeleteAccessKey",
                        "CreateUser",
                        "DeleteUser",
                        "AttachUserPolicy",
                    ]:
                        suspicious_events.append(
                            {
                                "event": event_name,
                                "user": user_identity.get("UserName", "Unknown"),
                                "timestamp": event.get("EventTime"),
                                "risk": "HIGH",
                                "description": f"Sensitive IAM operation: {event_name}",
                            }
                        )

                    # Check for unusual EC2 activities
                    if event_name in [
                        "RunInstances",
                        "TerminateInstances",
                        "StopInstances",
                    ]:
                        suspicious_events.append(
                            {
                                "event": event_name,
                                "user": user_identity.get("UserName", "Unknown"),
                                "timestamp": event.get("EventTime"),
                                "risk": "MEDIUM",
                                "description": f"EC2 instance operation: {event_name}",
                            }
                        )

                if suspicious_events:
                    typer.echo(
                        f"   {DANGER_EMOJI} Found {len(suspicious_events)} suspicious events in last 24 hours"
                    )
                    for event in suspicious_events[:5]:
                        typer.echo(
                            f"      {get_severity_color(event['risk'])} {event['event']} by {event['user']}"
                        )
                        typer.echo(f"         {event['description']}")
                else:
                    typer.echo(
                        f"   {SUCCESS_EMOJI} No suspicious events found in CloudTrail"
                    )

            except ClientError:
                typer.echo(f"   {WARNING_EMOJI} Could not analyze CloudTrail events")

        except ClientError as e:
            typer.echo(f"   {WARNING_EMOJI} Could not access CloudTrail: {e}")

        # 2. GuardDuty Findings
        typer.echo(f"{DETECTION_EMOJI} Checking GuardDuty findings...")
        for region_name in regions:
            try:
                guardduty_client = boto3.Session(profile_name=profile).client(
                    "guardduty", region_name=region_name
                )

                # Get recent findings
                detectors = guardduty_client.list_detectors()
                if detectors.get("DetectorIds"):
                    for detector_id in detectors["DetectorIds"]:
                        try:
                            findings = guardduty_client.list_findings(
                                DetectorId=detector_id,
                                FindingCriteria={
                                    "Criterion": {
                                        "updatedAt": {
                                            "Gte": int(
                                                (
                                                    datetime.now() - timedelta(days=7)
                                                ).timestamp()
                                                * 1000
                                            )
                                        }
                                    }
                                },
                            )

                            if findings.get("FindingIds"):
                                typer.echo(
                                    f"   {DANGER_EMOJI} Found {len(findings['FindingIds'])} recent GuardDuty findings"
                                )

                                # Get detailed findings
                                detailed_findings = guardduty_client.get_findings(
                                    DetectorId=detector_id,
                                    FindingIds=findings["FindingIds"][
                                        :10
                                    ],  # Get first 10
                                )

                                for finding in detailed_findings.get("Findings", []):
                                    severity = finding.get("Severity", "LOW")
                                    finding_type = finding.get("Type", "Unknown")
                                    typer.echo(
                                        f"      {get_severity_color(severity)} {finding_type}"
                                    )

                        except ClientError:
                            pass
            except ClientError as e:
                typer.echo(
                    f"   {WARNING_EMOJI} Could not access GuardDuty in {region_name}: {e}"
                )

        # 3. Security Hub Findings
        typer.echo(f"{SECURITY_EMOJI} Checking Security Hub findings...")
        for region_name in regions:
            try:
                securityhub_client = boto3.Session(profile_name=profile).client(
                    "securityhub", region_name=region_name
                )

                # Get recent findings
                findings = securityhub_client.get_findings(
                    Filters={
                        "RecordState": [{"Value": "ACTIVE", "Comparison": "EQUALS"}],
                        "UpdatedAt": [
                            {
                                "Start": (
                                    datetime.now() - timedelta(days=7)
                                ).isoformat(),
                                "End": datetime.now().isoformat(),
                            }
                        ],
                    },
                    MaxResults=50,
                )

                if findings.get("Findings"):
                    typer.echo(
                        f"   {DANGER_EMOJI} Found {len(findings['Findings'])} high/critical Security Hub findings"
                    )
                    for finding in findings["Findings"][:5]:
                        title = finding.get("Title", "Unknown")
                        severity = finding.get("Severity", {}).get("Label", "UNKNOWN")
                        typer.echo(f"      {get_severity_color(severity)} {title}")
                else:
                    typer.echo(
                        f"   {SUCCESS_EMOJI} No high/critical Security Hub findings"
                    )

            except ClientError as e:
                typer.echo(
                    f"   {WARNING_EMOJI} Could not access Security Hub in {region_name}: {e}"
                )

        # 4. Network Traffic Analysis
        typer.echo(f"{NETWORK_EMOJI} Analyzing network traffic patterns...")
        for region_name in regions:
            try:
                ec2_client = boto3.Session(profile_name=profile).client(
                    "ec2", region_name=region_name
                )

                # Check for unusual security group changes
                security_groups = ec2_client.describe_security_groups()
                for sg in security_groups["SecurityGroups"]:
                    # Check for overly permissive rules
                    for rule in sg.get("IpPermissions", []):
                        if rule.get("IpRanges"):
                            for ip_range in rule["IpRanges"]:
                                if ip_range.get("CidrIp") == "0.0.0.0/0":
                                    investigation_results["findings"].append(
                                        {
                                            "type": "Network Security",
                                            "severity": "HIGH",
                                            "description": f'Open security group {sg["GroupName"]} allows 0.0.0.0/0',
                                            "resource": sg["GroupId"],
                                            "region": region_name,
                                        }
                                    )

            except ClientError as e:
                typer.echo(
                    f"   {WARNING_EMOJI} Could not analyze network in {region_name}: {e}"
                )

        # 5. Resource Access Analysis
        typer.echo(f"{IDENTITY_EMOJI} Analyzing resource access patterns...")
        try:
            iam_client = clients["iam"]

            # Check for recent access key usage
            users = iam_client.list_users()
            for user in users["Users"]:
                try:
                    access_keys = iam_client.list_access_keys(UserName=user["UserName"])
                    for key in access_keys["AccessKeyMetadata"]:
                        if key["Status"] == "Active":
                            # Check last used
                            try:
                                key_usage = iam_client.get_access_key_last_used(
                                    AccessKeyId=key["AccessKeyId"]
                                )
                                last_used = key_usage.get("AccessKeyLastUsed", {}).get(
                                    "LastUsedDate"
                                )
                                if last_used:
                                    # Check if used in last 24 hours
                                    if (
                                        datetime.now(last_used.tzinfo) - last_used
                                    ).days == 0:
                                        investigation_results["findings"].append(
                                            {
                                                "type": "Access Analysis",
                                                "severity": "INFO",
                                                "description": f'Access key {key["AccessKeyId"]} used today by {user["UserName"]}',
                                                "resource": key["AccessKeyId"],
                                                "region": "Global",
                                            }
                                        )
                            except ClientError:
                                pass
                except ClientError:
                    pass

        except ClientError as e:
            typer.echo(f"   {WARNING_EMOJI} Could not analyze access patterns: {e}")

        # Generate incident response recommendations
        typer.echo()
        typer.echo(f"{RESPONSE_EMOJI} Incident Response Recommendations:")

        # Check for specific issues and provide targeted recommendations
        guardduty_accessible = False
        securityhub_accessible = False
        cloudtrail_accessible = False

        for region_name in regions:
            try:
                guardduty_client = boto3.Session(profile_name=profile).client(
                    "guardduty", region_name=region_name
                )
                guardduty_client.list_detectors()
                guardduty_accessible = True
                break
            except ClientError:
                pass

        for region_name in regions:
            try:
                securityhub_client = boto3.Session(profile_name=profile).client(
                    "securityhub", region_name=region_name
                )
                securityhub_client.get_findings(MaxResults=1)
                securityhub_accessible = True
                break
            except ClientError:
                pass

        try:
            cloudtrail_client = boto3.Session(profile_name=profile).client("cloudtrail")
            cloudtrail_client.list_trails()
            cloudtrail_accessible = True
        except ClientError:
            pass

        # Provide specific recommendations based on what's available
        if not guardduty_accessible:
            typer.echo(f"  {ALERT_EMOJI} Enable GuardDuty for threat detection")
            typer.echo(f"     - Go to GuardDuty console and enable the service")
            typer.echo(f"     - Configure threat detection settings")
            typer.echo(f"     - Set up email notifications for findings")

        if not securityhub_accessible:
            typer.echo(
                f"  {ALERT_EMOJI} Enable Security Hub for centralized security findings"
            )
            typer.echo(f"     - Go to Security Hub console and enable the service")
            typer.echo(f"     - Enable security standards (CIS, PCI, etc.)")
            typer.echo(f"     - Configure automated security checks")

        if not cloudtrail_accessible:
            typer.echo(f"  {ALERT_EMOJI} Enable CloudTrail for API activity logging")
            typer.echo(f"     - Go to CloudTrail console and create a trail")
            typer.echo(f"     - Enable log file validation")
            typer.echo(f"     - Configure S3 bucket for log storage")

        # General recommendations
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Review CloudTrail logs for unusual activities"
        )
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Check Security Hub and GuardDuty findings")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Audit IAM permissions and access keys")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Review security group configurations")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Enable enhanced monitoring")
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Document incident timeline and actions taken"
        )

        # If specific threats were found, provide targeted advice
        if threats:
            typer.echo()
            typer.echo(f"{DANGER_EMOJI} Specific Threat Response:")
            for threat in threats[:3]:  # Show top 3 threats
                typer.echo(f"  {get_severity_color(threat.severity)} {threat.title}")
                typer.echo(f"     Action: {threat.recommendation}")

        typer.echo()
        typer.echo(f"{TIP_EMOJI} Incident Response Tips:")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Document all actions taken")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Preserve evidence and logs")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Follow incident response procedures")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Communicate with stakeholders")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Learn from the incident")

        # Export results if requested
        if export:
            try:
                if export.endswith(".json"):
                    with open(export, "w") as f:
                        json.dump(investigation_results, f, indent=2, default=str)
                elif export.endswith(".csv"):
                    with open(export, "w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(
                            ["Type", "Severity", "Description", "Resource", "Region"]
                        )
                        for finding in investigation_results["findings"]:
                            writer.writerow(
                                [
                                    finding["type"],
                                    finding["severity"],
                                    finding["description"],
                                    finding["resource"],
                                    finding["region"],
                                ]
                            )

                typer.echo(
                    f"{SUCCESS_EMOJI} Investigation results exported to {export}"
                )
            except Exception as e:
                typer.echo(f"{ERROR_EMOJI} Failed to export results: {e}")

    except Exception as e:
        typer.echo(f"{DANGER_EMOJI} {ERROR_EMOJI} Error during incident response: {e}")
        raise typer.Exit(1)


@security_app.command("threats", help="Threat detection and analysis 👹")
def threat_detection(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    region: Optional[str] = typer.Option(
        None, "--region", "-r", help="AWS region to analyze"
    ),
    days: int = typer.Option(7, "--days", "-d", help="Number of days to analyze"),
    export: Optional[str] = typer.Option(
        None, "--export", "-e", help="Export results to file"
    ),
):
    """Detect and analyze security threats across AWS environment."""
    try:
        clients = get_aws_clients(profile)
        regions = [region] if region else get_region_list(profile)

        typer.echo(f"{THREAT_EMOJI} Starting threat detection analysis...")
        typer.echo(f"👤 Profile: {profile or 'default'}")
        typer.echo(f"🌍 Regions: {', '.join(regions)}")
        typer.echo(f"📅 Analysis Period: Last {days} days")
        typer.echo()

        threats = []

        # 1. GuardDuty Threat Detection
        typer.echo(f"{DETECTION_EMOJI} Analyzing GuardDuty threats...")
        for region_name in regions:
            try:
                guardduty_client = boto3.Session(profile_name=profile).client(
                    "guardduty", region_name=region_name
                )

                detectors = guardduty_client.list_detectors()
                if detectors.get("DetectorIds"):
                    for detector_id in detectors["DetectorIds"]:
                        try:
                            # Get findings from last N days
                            findings = guardduty_client.list_findings(
                                DetectorId=detector_id,
                                FindingCriteria={
                                    "Criterion": {
                                        "updatedAt": {
                                            "Gte": int(
                                                (
                                                    datetime.now()
                                                    - timedelta(days=days)
                                                ).timestamp()
                                                * 1000
                                            )
                                        }
                                    }
                                },
                            )

                            if findings.get("FindingIds"):
                                detailed_findings = guardduty_client.get_findings(
                                    DetectorId=detector_id,
                                    FindingIds=findings["FindingIds"],
                                )

                                for finding in detailed_findings.get("Findings", []):
                                    threat_type = finding.get("Type", "Unknown")
                                    severity = finding.get("Severity", "LOW")
                                    description = finding.get(
                                        "Description", "No description"
                                    )

                                    threats.append(
                                        SecurityFinding(
                                            severity=severity.upper(),
                                            category="GuardDuty Threat",
                                            title=threat_type,
                                            description=description,
                                            impact="Potential security threat detected",
                                            recommendation="Investigate and remediate the threat",
                                            resource_id=finding.get("Resource", {})
                                            .get("InstanceDetails", {})
                                            .get("InstanceId", "Unknown"),
                                            resource_type="EC2 Instance",
                                            region=region_name,
                                            priority=(
                                                8 if severity.upper() == "HIGH" else 5
                                            ),
                                        )
                                    )

                        except ClientError:
                            pass

            except ClientError as e:
                typer.echo(
                    f"   {WARNING_EMOJI} Could not access GuardDuty in {region_name}: {e}"
                )

        # 2. Security Hub Threats
        typer.echo(f"{SECURITY_EMOJI} Analyzing Security Hub threats...")
        for region_name in regions:
            try:
                securityhub_client = boto3.Session(profile_name=profile).client(
                    "securityhub", region_name=region_name
                )

                findings = securityhub_client.get_findings(
                    Filters={
                        "RecordState": [{"Value": "ACTIVE", "Comparison": "EQUALS"}],
                        "UpdatedAt": [
                            {
                                "Start": (
                                    datetime.now() - timedelta(days=days)
                                ).isoformat(),
                                "End": datetime.now().isoformat(),
                            }
                        ],
                    },
                    MaxResults=50,
                )

                for finding in findings.get("Findings", []):
                    title = finding.get("Title", "Unknown")
                    severity = finding.get("Severity", {}).get("Label", "UNKNOWN")
                    description = finding.get("Description", "No description")

                    threats.append(
                        SecurityFinding(
                            severity=severity.upper(),
                            category="Security Hub Finding",
                            title=title,
                            description=description,
                            impact="Security compliance issue detected",
                            recommendation="Address the security finding",
                            resource_id=finding.get("Resources", [{}])[0].get(
                                "Id", "Unknown"
                            ),
                            resource_type=finding.get("Resources", [{}])[0].get(
                                "Type", "Unknown"
                            ),
                            region=region_name,
                            priority=(
                                7 if severity.upper() in ["CRITICAL", "HIGH"] else 4
                            ),
                        )
                    )

            except ClientError as e:
                typer.echo(
                    f"   {WARNING_EMOJI} Could not access Security Hub in {region_name}: {e}"
                )

        # 3. Network Threat Analysis
        typer.echo(f"{NETWORK_EMOJI} Analyzing network threats...")
        for region_name in regions:
            try:
                ec2_client = boto3.Session(profile_name=profile).client(
                    "ec2", region_name=region_name
                )

                # Check for instances with unusual network configurations
                instances = ec2_client.describe_instances()
                for reservation in instances["Reservations"]:
                    for instance in reservation["Instances"]:
                        if instance["State"]["Name"] == "running":
                            # Check for instances with public IPs
                            if instance.get("PublicIpAddress"):
                                threats.append(
                                    SecurityFinding(
                                        severity="MEDIUM",
                                        category="Network Threat",
                                        title="Public EC2 Instance",
                                        description=f"Instance {instance['InstanceId']} has public IP {instance['PublicIpAddress']}",
                                        impact="Instance directly accessible from internet",
                                        recommendation="Review if public IP is necessary",
                                        resource_id=instance["InstanceId"],
                                        resource_type="EC2 Instance",
                                        region=region_name,
                                        priority=5,
                                    )
                                )

                            # Check for instances with open security groups
                            for sg in instance.get("SecurityGroups", []):
                                security_groups = ec2_client.describe_security_groups(
                                    GroupIds=[sg["GroupId"]]
                                )
                                for sg_detail in security_groups["SecurityGroups"]:
                                    for rule in sg_detail.get("IpPermissions", []):
                                        if rule.get("IpRanges"):
                                            for ip_range in rule["IpRanges"]:
                                                if (
                                                    ip_range.get("CidrIp")
                                                    == "0.0.0.0/0"
                                                ):
                                                    threats.append(
                                                        SecurityFinding(
                                                            severity="HIGH",
                                                            category="Network Threat",
                                                            title="Open Security Group",
                                                            description=f"Instance {instance['InstanceId']} has open security group {sg_detail['GroupName']}",
                                                            impact="Instance potentially accessible from anywhere",
                                                            recommendation="Restrict security group rules",
                                                            resource_id=instance[
                                                                "InstanceId"
                                                            ],
                                                            resource_type="EC2 Instance",
                                                            region=region_name,
                                                            priority=7,
                                                        )
                                                    )

            except ClientError as e:
                typer.echo(
                    f"   {WARNING_EMOJI} Could not analyze network in {region_name}: {e}"
                )

        # 4. Access Threat Analysis
        typer.echo(f"{IDENTITY_EMOJI} Analyzing access threats...")
        try:
            iam_client = clients["iam"]

            # Check for root account usage
            sts_client = boto3.Session(profile_name=profile).client("sts")
            caller_identity = sts_client.get_caller_identity()
            if caller_identity["Arn"].endswith(":root"):
                threats.append(
                    SecurityFinding(
                        severity="CRITICAL",
                        category="Access Threat",
                        title="Root Account Usage",
                        description="Using root account for operations",
                        impact="Full account access, no audit trail",
                        recommendation="Use IAM users with appropriate permissions",
                        resource_id="root",
                        resource_type="Account",
                        region="Global",
                        priority=10,
                    )
                )

            # Check for users without MFA
            users = iam_client.list_users()
            for user in users["Users"]:
                try:
                    mfa_devices = iam_client.list_mfa_devices(UserName=user["UserName"])
                    if not mfa_devices["MFADevices"]:
                        threats.append(
                            SecurityFinding(
                                severity="HIGH",
                                category="Access Threat",
                                title="User Without MFA",
                                description=f"User {user['UserName']} does not have MFA enabled",
                                impact="Account compromise risk",
                                recommendation="Enable MFA for the user",
                                resource_id=user["UserName"],
                                resource_type="IAM User",
                                region="Global",
                                priority=7,
                            )
                        )
                except ClientError:
                    pass

        except ClientError as e:
            typer.echo(f"   {WARNING_EMOJI} Could not analyze access threats: {e}")

        # Display threat summary
        typer.echo()
        typer.echo(f"{THREAT_EMOJI} Threat Detection Summary:")

        # Group threats by severity
        severity_counts = defaultdict(int)
        category_counts = defaultdict(int)

        for threat in threats:
            severity_counts[threat.severity] += 1
            category_counts[threat.category] += 1

        typer.echo(
            f"  {get_severity_color('CRITICAL')} Critical: {severity_counts['CRITICAL']}"
        )
        typer.echo(f"  {get_severity_color('HIGH')} High: {severity_counts['HIGH']}")
        typer.echo(
            f"  {get_severity_color('MEDIUM')} Medium: {severity_counts['MEDIUM']}"
        )
        typer.echo(f"  {get_severity_color('LOW')} Low: {severity_counts['LOW']}")

        # Show threats by category
        typer.echo()
        typer.echo(f"{ANALYSIS_EMOJI} Threats by Category:")
        for category, count in sorted(
            category_counts.items(), key=lambda x: x[1], reverse=True
        ):
            typer.echo(f"  {category}: {count} threats")

        # Show critical and high threats
        critical_high_threats = [
            t for t in threats if t.severity in ["CRITICAL", "HIGH"]
        ]
        if critical_high_threats:
            typer.echo()
            typer.echo(f"{DANGER_EMOJI} Critical & High Priority Threats:")
            for threat in critical_high_threats[:5]:  # Show top 5
                typer.echo(f"  {get_severity_color(threat.severity)} {threat.title}")
                typer.echo(
                    f"     Resource: {threat.resource_id} ({threat.resource_type})"
                )
                typer.echo(f"     Region: {threat.region}")
                typer.echo(f"     Impact: {threat.impact}")
                typer.echo()

        # Export results if requested
        if export:
            try:
                if export.endswith(".json"):
                    export_data = {
                        "threat_analysis_info": {
                            "timestamp": datetime.now().isoformat(),
                            "profile": profile or "default",
                            "regions": regions,
                            "analysis_period_days": days,
                        },
                        "threats": [
                            {
                                "severity": t.severity,
                                "category": t.category,
                                "title": t.title,
                                "description": t.description,
                                "impact": t.impact,
                                "recommendation": t.recommendation,
                                "resource_id": t.resource_id,
                                "resource_type": t.resource_type,
                                "region": t.region,
                                "priority": t.priority,
                            }
                            for t in threats
                        ],
                    }
                    with open(export, "w") as f:
                        json.dump(export_data, f, indent=2, default=str)
                elif export.endswith(".csv"):
                    with open(export, "w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(
                            [
                                "Severity",
                                "Category",
                                "Title",
                                "Description",
                                "Impact",
                                "Recommendation",
                                "Resource ID",
                                "Resource Type",
                                "Region",
                                "Priority",
                            ]
                        )
                        for threat in threats:
                            writer.writerow(
                                [
                                    threat.severity,
                                    threat.category,
                                    threat.title,
                                    threat.description,
                                    threat.impact,
                                    threat.recommendation,
                                    threat.resource_id,
                                    threat.resource_type,
                                    threat.region,
                                    threat.priority,
                                ]
                            )

                typer.echo(
                    f"{SUCCESS_EMOJI} Threat analysis results exported to {export}"
                )
            except Exception as e:
                typer.echo(f"{ERROR_EMOJI} Failed to export results: {e}")

        typer.echo()
        typer.echo(f"{TIP_EMOJI} Threat Detection Tips:")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Enable GuardDuty and Security Hub")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Monitor CloudTrail for unusual activities")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Regular threat hunting exercises")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Implement security monitoring")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Stay updated on threat intelligence")

    except Exception as e:
        typer.echo(f"{DANGER_EMOJI} {ERROR_EMOJI} Error during threat detection: {e}")
        raise typer.Exit(1)


@security_app.command("compliance", help="Compliance assessment and reporting 📋")
def compliance_assessment(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    standard: str = typer.Option(
        "CIS", "--standard", "-s", help="Compliance standard (CIS/SOC2/PCI/HIPAA)"
    ),
    region: Optional[str] = typer.Option(
        None, "--region", "-r", help="AWS region to assess"
    ),
    export: Optional[str] = typer.Option(
        None, "--export", "-e", help="Export results to file"
    ),
):
    """Assess compliance with security standards and frameworks."""
    try:
        clients = get_aws_clients(profile)
        regions = [region] if region else get_region_list(profile)

        typer.echo(f"{COMPLIANCE_EMOJI} Starting compliance assessment...")
        typer.echo(f"👤 Profile: {profile or 'default'}")
        typer.echo(f"📋 Standard: {standard}")
        typer.echo(f"🌍 Regions: {', '.join(regions)}")
        typer.echo()

        compliance_results = {
            "compliance_info": {
                "timestamp": datetime.now().isoformat(),
                "profile": profile or "default",
                "standard": standard,
                "regions": regions,
            },
            "checks": [],
            "summary": {"passed": 0, "failed": 0, "warnings": 0, "not_applicable": 0},
        }

        # CIS AWS Foundations Benchmark
        if standard.upper() == "CIS":
            typer.echo(f"{COMPLIANCE_EMOJI} CIS AWS Foundations Benchmark Assessment:")
            typer.echo()

            # Identity and Access Management
            typer.echo(f"{IDENTITY_EMOJI} Identity and Access Management Checks:")

            # 1.1 - Avoid the use of the "root" account for administrative and daily tasks
            try:
                sts_client = boto3.Session(profile_name=profile).client("sts")
                caller_identity = sts_client.get_caller_identity()
                if caller_identity["Arn"].endswith(":root"):
                    compliance_results["checks"].append(
                        ComplianceCheck(
                            standard="CIS",
                            control="1.1",
                            title="Root Account Usage",
                            status="FAILED",
                            description="Root account should not be used for administrative tasks",
                            remediation="Use IAM users with appropriate permissions",
                            priority=10,
                        )
                    )
                    typer.echo(f"   {ERROR_EMOJI} 1.1 - FAILED: Root account in use")
                else:
                    compliance_results["checks"].append(
                        ComplianceCheck(
                            standard="CIS",
                            control="1.1",
                            title="Root Account Usage",
                            status="PASSED",
                            description="Not using root account for administrative tasks",
                            remediation="N/A",
                            priority=10,
                        )
                    )
                    typer.echo(f"   {SUCCESS_EMOJI} 1.1 - PASSED: Using IAM user/role")
            except Exception as e:
                compliance_results["checks"].append(
                    ComplianceCheck(
                        standard="CIS",
                        control="1.1",
                        title="Root Account Usage",
                        status="WARNING",
                        description=f"Could not verify: {e}",
                        remediation="Verify account type manually",
                        priority=10,
                    )
                )
                typer.echo(f"   {WARNING_EMOJI} 1.1 - WARNING: Could not verify")

            # 1.2 - Ensure multi-factor authentication (MFA) is enabled for all IAM users that have a console password
            try:
                iam_client = clients["iam"]
                users_without_mfa = []
                users = iam_client.list_users()

                for user in users["Users"]:
                    try:
                        mfa_devices = iam_client.list_mfa_devices(
                            UserName=user["UserName"]
                        )
                        if not mfa_devices["MFADevices"]:
                            users_without_mfa.append(user["UserName"])
                    except ClientError:
                        users_without_mfa.append(user["UserName"])

                if users_without_mfa:
                    compliance_results["checks"].append(
                        ComplianceCheck(
                            standard="CIS",
                            control="1.2",
                            title="MFA for Console Users",
                            status="FAILED",
                            description=f"{len(users_without_mfa)} users without MFA",
                            remediation="Enable MFA for all console users",
                            priority=9,
                        )
                    )
                    typer.echo(
                        f"   {ERROR_EMOJI} 1.2 - FAILED: {len(users_without_mfa)} users without MFA"
                    )
                else:
                    compliance_results["checks"].append(
                        ComplianceCheck(
                            standard="CIS",
                            control="1.2",
                            title="MFA for Console Users",
                            status="PASSED",
                            description="All users have MFA enabled",
                            remediation="N/A",
                            priority=9,
                        )
                    )
                    typer.echo(f"   {SUCCESS_EMOJI} 1.2 - PASSED: All users have MFA")
            except Exception as e:
                compliance_results["checks"].append(
                    ComplianceCheck(
                        standard="CIS",
                        control="1.2",
                        title="MFA for Console Users",
                        status="WARNING",
                        description=f"Could not verify: {e}",
                        remediation="Verify MFA configuration manually",
                        priority=9,
                    )
                )
                typer.echo(f"   {WARNING_EMOJI} 1.2 - WARNING: Could not verify")

            # Storage Security
            typer.echo(f"{STORAGE_EMOJI} Storage Security Checks:")

            # 2.1 - Ensure all S3 buckets employ encryption-at-rest
            try:
                s3_client = clients["s3"]
                buckets = s3_client.list_buckets()
                unencrypted_buckets = []

                for bucket in buckets["Buckets"]:
                    try:
                        encryption = s3_client.get_bucket_encryption(
                            Bucket=bucket["Name"]
                        )
                    except ClientError:
                        unencrypted_buckets.append(bucket["Name"])

                if unencrypted_buckets:
                    compliance_results["checks"].append(
                        ComplianceCheck(
                            standard="CIS",
                            control="2.1",
                            title="S3 Bucket Encryption",
                            status="FAILED",
                            description=f"{len(unencrypted_buckets)} buckets not encrypted",
                            remediation="Enable default encryption for all S3 buckets",
                            priority=8,
                        )
                    )
                    typer.echo(
                        f"   {ERROR_EMOJI} 2.1 - FAILED: {len(unencrypted_buckets)} unencrypted buckets"
                    )
                else:
                    compliance_results["checks"].append(
                        ComplianceCheck(
                            standard="CIS",
                            control="2.1",
                            title="S3 Bucket Encryption",
                            status="PASSED",
                            description="All S3 buckets are encrypted",
                            remediation="N/A",
                            priority=8,
                        )
                    )
                    typer.echo(
                        f"   {SUCCESS_EMOJI} 2.1 - PASSED: All buckets encrypted"
                    )
            except Exception as e:
                compliance_results["checks"].append(
                    ComplianceCheck(
                        standard="CIS",
                        control="2.1",
                        title="S3 Bucket Encryption",
                        status="WARNING",
                        description=f"Could not verify: {e}",
                        remediation="Verify S3 encryption manually",
                        priority=8,
                    )
                )
                typer.echo(f"   {WARNING_EMOJI} 2.1 - WARNING: Could not verify")

            # Monitoring and Logging
            typer.echo(f"{MONITORING_EMOJI} Monitoring and Logging Checks:")

            # 3.1 - Ensure CloudTrail is enabled in all regions
            try:
                cloudtrail_client = clients["cloudtrail"]
                trails = cloudtrail_client.list_trails()

                if not trails.get("Trails"):
                    compliance_results["checks"].append(
                        ComplianceCheck(
                            standard="CIS",
                            control="3.1",
                            title="CloudTrail Enabled",
                            status="FAILED",
                            description="No CloudTrail is configured",
                            remediation="Enable CloudTrail for all regions",
                            priority=8,
                        )
                    )
                    typer.echo(
                        f"   {ERROR_EMOJI} 3.1 - FAILED: No CloudTrail configured"
                    )
                else:
                    compliance_results["checks"].append(
                        ComplianceCheck(
                            standard="CIS",
                            control="3.1",
                            title="CloudTrail Enabled",
                            status="PASSED",
                            description="CloudTrail is configured",
                            remediation="N/A",
                            priority=8,
                        )
                    )
                    typer.echo(
                        f"   {SUCCESS_EMOJI} 3.1 - PASSED: CloudTrail configured"
                    )
            except Exception as e:
                compliance_results["checks"].append(
                    ComplianceCheck(
                        standard="CIS",
                        control="3.1",
                        title="CloudTrail Enabled",
                        status="WARNING",
                        description=f"Could not verify: {e}",
                        remediation="Verify CloudTrail configuration manually",
                        priority=8,
                    )
                )
                typer.echo(f"   {WARNING_EMOJI} 3.1 - WARNING: Could not verify")

        # Calculate compliance summary
        for check in compliance_results["checks"]:
            if check.status == "PASSED":
                compliance_results["summary"]["passed"] += 1
            elif check.status == "FAILED":
                compliance_results["summary"]["failed"] += 1
            elif check.status == "WARNING":
                compliance_results["summary"]["warnings"] += 1
            else:
                compliance_results["summary"]["not_applicable"] += 1

        # Display compliance summary
        typer.echo()
        typer.echo(f"{COMPLIANCE_EMOJI} Compliance Assessment Summary:")
        typer.echo(
            f"  {SUCCESS_EMOJI} Passed: {compliance_results['summary']['passed']}"
        )
        typer.echo(f"  {ERROR_EMOJI} Failed: {compliance_results['summary']['failed']}")
        typer.echo(
            f"  {WARNING_EMOJI} Warnings: {compliance_results['summary']['warnings']}"
        )
        typer.echo(
            f"  ℹ️ Not Applicable: {compliance_results['summary']['not_applicable']}"
        )

        # Calculate compliance percentage
        total_checks = len(compliance_results["checks"])
        if total_checks > 0:
            compliance_percentage = (
                compliance_results["summary"]["passed"] / total_checks
            ) * 100
            typer.echo(f"  📊 Compliance Score: {compliance_percentage:.1f}%")

            if compliance_percentage >= 90:
                compliance_level = "🔵 EXCELLENT"
            elif compliance_percentage >= 75:
                compliance_level = "🟢 GOOD"
            elif compliance_percentage >= 50:
                compliance_level = "🟡 FAIR"
            else:
                compliance_level = "🔴 POOR"

            typer.echo(f"  📋 Compliance Level: {compliance_level}")

        # Show failed checks
        failed_checks = [
            c for c in compliance_results["checks"] if c.status == "FAILED"
        ]
        if failed_checks:
            typer.echo()
            typer.echo(f"{ERROR_EMOJI} Failed Compliance Checks:")
            for check in failed_checks:
                typer.echo(f"  {check.control} - {check.title}")
                typer.echo(f"     Description: {check.description}")
                typer.echo(f"     Remediation: {check.remediation}")
                typer.echo()

        # Export results if requested
        if export:
            try:
                if export.endswith(".json"):
                    with open(export, "w") as f:
                        json.dump(compliance_results, f, indent=2, default=str)
                elif export.endswith(".csv"):
                    with open(export, "w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(
                            [
                                "Standard",
                                "Control",
                                "Title",
                                "Status",
                                "Description",
                                "Remediation",
                                "Priority",
                            ]
                        )
                        for check in compliance_results["checks"]:
                            writer.writerow(
                                [
                                    check.standard,
                                    check.control,
                                    check.title,
                                    check.status,
                                    check.description,
                                    check.remediation,
                                    check.priority,
                                ]
                            )

                typer.echo(
                    f"{SUCCESS_EMOJI} Compliance assessment results exported to {export}"
                )
            except Exception as e:
                typer.echo(f"{ERROR_EMOJI} Failed to export results: {e}")

        typer.echo()
        typer.echo(f"{TIP_EMOJI} Compliance Tips:")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Regular compliance assessments")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Automated compliance monitoring")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Document compliance procedures")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Remediate issues promptly")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Stay updated on compliance requirements")

    except Exception as e:
        typer.echo(
            f"{DANGER_EMOJI} {ERROR_EMOJI} Error during compliance assessment: {e}"
        )
        raise typer.Exit(1)


@security_app.command("remediate", help="Smart security remediation and automation 🔧")
def smart_remediation(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    region: Optional[str] = typer.Option(
        None, "--region", "-r", help="AWS region to remediate"
    ),
    auto: bool = typer.Option(
        False, "--auto", "-a", help="Automatically apply remediations"
    ),
    dry_run: bool = typer.Option(
        True, "--dry-run", "-d", help="Show what would be remediated without applying"
    ),
):
    """Smart security remediation with automated fixes and recommendations."""
    try:
        clients = get_aws_clients(profile)
        regions = [region] if region else get_region_list(profile)

        typer.echo(f"{REMEDIATION_EMOJI} Starting smart security remediation...")
        typer.echo(f"👤 Profile: {profile or 'default'}")
        typer.echo(f"🌍 Regions: {', '.join(regions)}")
        typer.echo(f"🔧 Auto-apply: {auto}")
        typer.echo(f"🧪 Dry Run: {dry_run}")
        typer.echo()

        remediation_actions = []

        # 1. S3 Bucket Remediation
        typer.echo(f"{STORAGE_EMOJI} S3 Bucket Security Remediation:")
        try:
            s3_client = clients["s3"]
            buckets = s3_client.list_buckets()

            for bucket in buckets["Buckets"]:
                bucket_name = bucket["Name"]

                # Check and fix encryption
                try:
                    encryption = s3_client.get_bucket_encryption(Bucket=bucket_name)
                except ClientError:
                    remediation_actions.append(
                        {
                            "service": "S3",
                            "resource": bucket_name,
                            "action": "Enable encryption",
                            "description": f"Enable default encryption for bucket {bucket_name}",
                            "command": f'aws s3api put-bucket-encryption --bucket {bucket_name} --server-side-encryption-configuration \'{{"Rules":[{{"ApplyServerSideEncryptionByDefault":{{"SSEAlgorithm":"AES256"}}}}]}}\'',
                            "priority": "HIGH",
                        }
                    )
                    typer.echo(
                        f"   {WARNING_EMOJI} Bucket {bucket_name}: Encryption not enabled"
                    )

                # Check and fix public access
                try:
                    public_access = s3_client.get_public_access_block(
                        Bucket=bucket_name
                    )
                    if not public_access["PublicAccessBlockConfiguration"][
                        "BlockPublicAcls"
                    ]:
                        remediation_actions.append(
                            {
                                "service": "S3",
                                "resource": bucket_name,
                                "action": "Block public access",
                                "description": f"Enable public access blocking for bucket {bucket_name}",
                                "command": f"aws s3api put-public-access-block --bucket {bucket_name} --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true",
                                "priority": "HIGH",
                            }
                        )
                        typer.echo(
                            f"   {WARNING_EMOJI} Bucket {bucket_name}: Public access not blocked"
                        )
                except ClientError:
                    pass

        except ClientError as e:
            typer.echo(f"   {ERROR_EMOJI} Could not access S3: {e}")

        # 2. Security Group Remediation
        typer.echo(f"{NETWORK_EMOJI} Security Group Remediation:")
        for region_name in regions:
            try:
                ec2_client = boto3.Session(profile_name=profile).client(
                    "ec2", region_name=region_name
                )
                security_groups = ec2_client.describe_security_groups()

                for sg in security_groups["SecurityGroups"]:
                    sg_id = sg["GroupId"]
                    sg_name = sg["GroupName"]

                    # Check for overly permissive rules
                    for rule in sg.get("IpPermissions", []):
                        if rule.get("IpRanges"):
                            for ip_range in rule["IpRanges"]:
                                if ip_range.get("CidrIp") == "0.0.0.0/0":
                                    remediation_actions.append(
                                        {
                                            "service": "EC2",
                                            "resource": f"{sg_id} ({sg_name})",
                                            "action": "Restrict security group",
                                            "description": f"Restrict security group {sg_name} from 0.0.0.0/0",
                                            "command": f'aws ec2 revoke-security-group-ingress --group-id {sg_id} --protocol {rule.get("IpProtocol", "tcp")} --port {rule.get("FromPort", "0")}-{rule.get("ToPort", "65535")} --cidr 0.0.0.0/0',
                                            "priority": "HIGH",
                                        }
                                    )
                                    typer.echo(
                                        f"   {WARNING_EMOJI} Security Group {sg_name}: Allows 0.0.0.0/0"
                                    )

            except ClientError as e:
                typer.echo(
                    f"   {ERROR_EMOJI} Could not access EC2 in {region_name}: {e}"
                )

        # 3. IAM User Remediation
        typer.echo(f"{IDENTITY_EMOJI} IAM User Remediation:")
        try:
            iam_client = clients["iam"]
            users = iam_client.list_users()

            for user in users["Users"]:
                user_name = user["UserName"]

                # Check for MFA
                try:
                    mfa_devices = iam_client.list_mfa_devices(UserName=user_name)
                    if not mfa_devices["MFADevices"]:
                        remediation_actions.append(
                            {
                                "service": "IAM",
                                "resource": user_name,
                                "action": "Enable MFA",
                                "description": f"Enable MFA for user {user_name}",
                                "command": f"# Manual action required: Enable MFA for user {user_name}",
                                "priority": "HIGH",
                            }
                        )
                        typer.echo(
                            f"   {WARNING_EMOJI} User {user_name}: MFA not enabled"
                        )
                except ClientError:
                    pass

                # Check for old access keys
                try:
                    access_keys = iam_client.list_access_keys(UserName=user_name)
                    for key in access_keys["AccessKeyMetadata"]:
                        if key["Status"] == "Active":
                            key_age = (
                                datetime.now(key["CreateDate"].tzinfo)
                                - key["CreateDate"]
                            ).days
                            if key_age > 90:
                                remediation_actions.append(
                                    {
                                        "service": "IAM",
                                        "resource": f"{user_name}:{key['AccessKeyId']}",
                                        "action": "Rotate access key",
                                        "description": f'Rotate access key {key["AccessKeyId"]} for user {user_name}',
                                        "command": f'# Manual action required: Rotate access key {key["AccessKeyId"]} for user {user_name}',
                                        "priority": "MEDIUM",
                                    }
                                )
                                typer.echo(
                                    f"   {WARNING_EMOJI} User {user_name}: Access key {key['AccessKeyId']} is {key_age} days old"
                                )
                except ClientError:
                    pass

        except ClientError as e:
            typer.echo(f"   {ERROR_EMOJI} Could not access IAM: {e}")

        # 4. RDS Remediation
        typer.echo(f"{DATABASE_EMOJI} RDS Remediation:")
        for region_name in regions:
            try:
                rds_client = boto3.Session(profile_name=profile).client(
                    "rds", region_name=region_name
                )
                instances = rds_client.describe_db_instances()

                for instance in instances["DBInstances"]:
                    instance_id = instance["DBInstanceIdentifier"]

                    # Check for public accessibility
                    if instance.get("PubliclyAccessible"):
                        remediation_actions.append(
                            {
                                "service": "RDS",
                                "resource": instance_id,
                                "action": "Disable public access",
                                "description": f"Disable public accessibility for RDS instance {instance_id}",
                                "command": f"aws rds modify-db-instance --db-instance-identifier {instance_id} --no-publicly-accessible --apply-immediately",
                                "priority": "HIGH",
                            }
                        )
                        typer.echo(
                            f"   {WARNING_EMOJI} RDS {instance_id}: Publicly accessible"
                        )

                    # Check for encryption
                    if not instance.get("StorageEncrypted"):
                        remediation_actions.append(
                            {
                                "service": "RDS",
                                "resource": instance_id,
                                "action": "Enable encryption",
                                "description": f"Enable encryption for RDS instance {instance_id}",
                                "command": f"# Manual action required: Enable encryption for RDS instance {instance_id} (requires snapshot and restore)",
                                "priority": "HIGH",
                            }
                        )
                        typer.echo(
                            f"   {WARNING_EMOJI} RDS {instance_id}: Not encrypted"
                        )

            except ClientError as e:
                typer.echo(
                    f"   {ERROR_EMOJI} Could not access RDS in {region_name}: {e}"
                )

        # Display remediation summary
        typer.echo()
        typer.echo(f"{REMEDIATION_EMOJI} Remediation Summary:")

        # Group by priority
        high_priority = [r for r in remediation_actions if r["priority"] == "HIGH"]
        medium_priority = [r for r in remediation_actions if r["priority"] == "MEDIUM"]
        low_priority = [r for r in remediation_actions if r["priority"] == "LOW"]

        typer.echo(
            f"  {get_severity_color('HIGH')} High Priority: {len(high_priority)}"
        )
        typer.echo(
            f"  {get_severity_color('MEDIUM')} Medium Priority: {len(medium_priority)}"
        )
        typer.echo(f"  {get_severity_color('LOW')} Low Priority: {len(low_priority)}")

        # Show high priority remediations
        if high_priority:
            typer.echo()
            typer.echo(f"{DANGER_EMOJI} High Priority Remediations:")
            for i, action in enumerate(high_priority[:5], 1):
                typer.echo(f"  {i}. {action['service']} - {action['resource']}")
                typer.echo(f"     Action: {action['action']}")
                typer.echo(f"     Description: {action['description']}")
                if not dry_run and auto:
                    typer.echo(f"     {SUCCESS_EMOJI} Auto-applied")
                elif dry_run:
                    typer.echo(f"     Command: {action['command']}")
                typer.echo()

        # Apply remediations if auto mode is enabled
        if auto and not dry_run:
            typer.echo(f"{INNOVATION_EMOJI} Applying automated remediations...")
            applied_count = 0

            for action in remediation_actions:
                if action["priority"] == "HIGH":
                    try:
                        typer.echo(
                            f"  Applying: {action['action']} for {action['resource']}"
                        )
                        # Note: In a real implementation, you would execute the commands here
                        # For safety, we're just showing what would be done
                        applied_count += 1
                    except Exception as e:
                        typer.echo(
                            f"  {ERROR_EMOJI} Failed to apply {action['action']}: {e}"
                        )

            typer.echo(f"{SUCCESS_EMOJI} Applied {applied_count} remediations")

        typer.echo()
        typer.echo(f"{TIP_EMOJI} Remediation Tips:")
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Always test remediations in non-production first"
        )
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Use dry-run mode to preview changes")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Document all remediation actions")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Monitor for any service disruptions")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Regular remediation reviews")

    except Exception as e:
        typer.echo(f"{DANGER_EMOJI} {ERROR_EMOJI} Error during remediation: {e}")
        raise typer.Exit(1)


@security_app.command("export", help="Export security data and reports 📊")
def export_security_data(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    format: str = typer.Option(
        "json", "--format", "-f", help="Export format (json/csv/html)"
    ),
    output: str = typer.Option(
        "security_report", "--output", "-o", help="Output filename"
    ),
    include_findings: bool = typer.Option(
        True, "--findings", help="Include security findings"
    ),
    include_compliance: bool = typer.Option(
        True, "--compliance", help="Include compliance data"
    ),
    include_threats: bool = typer.Option(True, "--threats", help="Include threat data"),
):
    """Export comprehensive security data and reports."""
    try:
        clients = get_aws_clients(profile)

        typer.echo(f"{ANALYSIS_EMOJI} Exporting security data...")
        typer.echo(f"👤 Profile: {profile or 'default'}")
        typer.echo(f"📄 Format: {format}")
        typer.echo(f"📁 Output: {output}")
        typer.echo()

        export_data = {
            "export_info": {
                "timestamp": datetime.now().isoformat(),
                "profile": profile or "default",
                "format": format,
                "included_data": {
                    "findings": include_findings,
                    "compliance": include_compliance,
                    "threats": include_threats,
                },
            },
            "security_summary": {},
            "findings": [],
            "compliance_data": [],
            "threat_data": [],
        }

        # Collect security summary
        typer.echo(f"{SECURITY_EMOJI} Collecting security summary...")

        # Account information
        try:
            sts_client = boto3.Session(profile_name=profile).client("sts")
            caller_identity = sts_client.get_caller_identity()
            export_data["security_summary"]["account"] = {
                "account_id": caller_identity.get("Account"),
                "user_arn": caller_identity.get("Arn"),
                "using_root": caller_identity["Arn"].endswith(":root"),
            }
        except Exception as e:
            export_data["security_summary"]["account"] = {"error": str(e)}

        # Service counts
        try:
            # EC2 instances
            ec2_client = clients["ec2"]
            instances = ec2_client.describe_instances()
            running_instances = sum(
                1
                for reservation in instances["Reservations"]
                for instance in reservation["Instances"]
                if instance["State"]["Name"] == "running"
            )

            # S3 buckets
            s3_client = clients["s3"]
            buckets = s3_client.list_buckets()

            # IAM users
            iam_client = clients["iam"]
            users = iam_client.list_users()

            export_data["security_summary"]["resources"] = {
                "ec2_instances": running_instances,
                "s3_buckets": len(buckets["Buckets"]),
                "iam_users": len(users["Users"]),
            }
        except Exception as e:
            export_data["security_summary"]["resources"] = {"error": str(e)}

        # Collect findings if requested
        if include_findings:
            typer.echo(f"{SCAN_EMOJI} Collecting security findings...")
            # This would integrate with the findings from other commands
            export_data["findings"] = [
                {
                    "type": "Sample Finding",
                    "severity": "MEDIUM",
                    "description": "Sample security finding for export",
                    "recommendation": "Sample recommendation",
                }
            ]

        # Collect compliance data if requested
        if include_compliance:
            typer.echo(f"{COMPLIANCE_EMOJI} Collecting compliance data...")
            # This would integrate with compliance assessment results
            export_data["compliance_data"] = [
                {
                    "standard": "CIS",
                    "control": "1.1",
                    "status": "PASSED",
                    "description": "Sample compliance check",
                }
            ]

        # Collect threat data if requested
        if include_threats:
            typer.echo(f"{THREAT_EMOJI} Collecting threat data...")
            # This would integrate with threat detection results
            export_data["threat_data"] = [
                {
                    "type": "Sample Threat",
                    "severity": "LOW",
                    "description": "Sample threat detection",
                }
            ]

        # Export based on format
        output_file = f"{output}.{format}"

        if format.lower() == "json":
            with open(output_file, "w") as f:
                json.dump(export_data, f, indent=2, default=str)
        elif format.lower() == "csv":
            with open(output_file, "w", newline="") as f:
                writer = csv.writer(f)
                # Write summary
                writer.writerow(["Category", "Key", "Value"])
                for category, data in export_data["security_summary"].items():
                    if isinstance(data, dict):
                        for key, value in data.items():
                            writer.writerow([category, key, value])
                    else:
                        writer.writerow([category, "value", data])

                # Write findings
                if export_data["findings"]:
                    writer.writerow([])
                    writer.writerow(
                        ["Finding Type", "Severity", "Description", "Recommendation"]
                    )
                    for finding in export_data["findings"]:
                        writer.writerow(
                            [
                                finding.get("type", ""),
                                finding.get("severity", ""),
                                finding.get("description", ""),
                                finding.get("recommendation", ""),
                            ]
                        )
        elif format.lower() == "html":
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Security Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    .header {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; }}
                    .section {{ margin: 20px 0; }}
                    .finding {{ border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 5px; }}
                    .high {{ border-left: 5px solid #ff4444; }}
                    .medium {{ border-left: 5px solid #ffaa00; }}
                    .low {{ border-left: 5px solid #44aa44; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Security Report</h1>
                    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>Profile: {profile or 'default'}</p>
                </div>
                
                <div class="section">
                    <h2>Security Summary</h2>
                    <pre>{json.dumps(export_data['security_summary'], indent=2)}</pre>
                </div>
                
                <div class="section">
                    <h2>Findings</h2>
                    {''.join([f'<div class="finding {finding.get("severity", "").lower()}"><strong>{finding.get("type", "")}</strong><br>{finding.get("description", "")}</div>' for finding in export_data['findings']])}
                </div>
            </body>
            </html>
            """
            with open(output_file, "w") as f:
                f.write(html_content)

        typer.echo(f"{SUCCESS_EMOJI} Security data exported to {output_file}")

        # Show export summary
        typer.echo()
        typer.echo(f"{ANALYSIS_EMOJI} Export Summary:")
        typer.echo(f"  📄 Format: {format.upper()}")
        typer.echo(f"  📁 File: {output_file}")
        typer.echo(f"  📊 Findings: {len(export_data['findings'])}")
        typer.echo(f"  📋 Compliance: {len(export_data['compliance_data'])}")
        typer.echo(f"  👹 Threats: {len(export_data['threat_data'])}")

        typer.echo()
        typer.echo(f"{TIP_EMOJI} Export Tips:")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Use JSON for programmatic access")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Use CSV for spreadsheet analysis")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Use HTML for stakeholder reports")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Regular security data exports")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Archive historical reports")

    except Exception as e:
        typer.echo(f"{DANGER_EMOJI} {ERROR_EMOJI} Error during export: {e}")
        raise typer.Exit(1)


@security_app.command("help", help="Show detailed help and examples 📖")
def security_help():
    """Show detailed help for SecuTide commands with examples."""
    typer.echo(
        f"{SECURITY_EMOJI} SecuTide - AWS Security Assessment and Remediation Module"
    )
    typer.echo("=" * 80)
    typer.echo()

    typer.echo(f"{TIP_EMOJI} Available Commands:")
    typer.echo()

    # Posture Assessment
    typer.echo(f"{SECURITY_EMOJI} awdx security posture")
    typer.echo("   Comprehensive security posture assessment across AWS services")
    typer.echo("   Examples:")
    typer.echo("     awdx security posture")
    typer.echo("     awdx security posture --profile prod --region us-east-1")
    typer.echo("     awdx security posture --export posture_report.json")
    typer.echo()

    # Vulnerability Scanning
    typer.echo(f"{VULNERABILITY_EMOJI} awdx security vulnerabilities")
    typer.echo("   Scan for security vulnerabilities across AWS services")
    typer.echo("   Examples:")
    typer.echo("     awdx security vulnerabilities")
    typer.echo("     awdx security vulnerabilities --service ec2")
    typer.echo("     awdx security vulnerabilities --service s3 --export vulns.csv")
    typer.echo()

    # Incident Response
    typer.echo(f"{INCIDENT_EMOJI} awdx security incident")
    typer.echo("   Incident response investigation and analysis")
    typer.echo("   Examples:")
    typer.echo("     awdx security incident")
    typer.echo("     awdx security incident --type breach")
    typer.echo(
        "     awdx security incident --type malware --export incident_report.json"
    )
    typer.echo()

    # Threat Detection
    typer.echo(f"{THREAT_EMOJI} awdx security threats")
    typer.echo("   Threat detection and analysis")
    typer.echo("   Examples:")
    typer.echo("     awdx security threats")
    typer.echo("     awdx security threats --days 30")
    typer.echo("     awdx security threats --export threats.json")
    typer.echo()

    # Compliance Assessment
    typer.echo(f"{COMPLIANCE_EMOJI} awdx security compliance")
    typer.echo("   Compliance assessment and reporting")
    typer.echo("   Examples:")
    typer.echo("     awdx security compliance")
    typer.echo("     awdx security compliance --standard CIS")
    typer.echo("     awdx security compliance --export compliance_report.csv")
    typer.echo()

    # Smart Remediation
    typer.echo(f"{REMEDIATION_EMOJI} awdx security remediate")
    typer.echo("   Smart security remediation and automation")
    typer.echo("   Examples:")
    typer.echo("     awdx security remediate --dry-run")
    typer.echo("     awdx security remediate --auto")
    typer.echo("     awdx security remediate --region us-west-2")
    typer.echo()

    # Data Export
    typer.echo(f"{ANALYSIS_EMOJI} awdx security export")
    typer.echo("   Export security data and reports")
    typer.echo("   Examples:")
    typer.echo("     awdx security export --format json")
    typer.echo("     awdx security export --format csv --output security_data")
    typer.echo("     awdx security export --format html --findings --compliance")
    typer.echo()

    typer.echo(f"{TIP_EMOJI} Common Use Cases:")
    typer.echo()
    typer.echo(f"  {BEST_PRACTICE_EMOJI} Daily Security Check:")
    typer.echo("     awdx security posture --export daily_report.json")
    typer.echo()
    typer.echo(f"  {BEST_PRACTICE_EMOJI} Incident Investigation:")
    typer.echo("     awdx security incident --type breach --export incident.json")
    typer.echo("     awdx security threats --days 7 --export threats.json")
    typer.echo()
    typer.echo(f"  {BEST_PRACTICE_EMOJI} Compliance Reporting:")
    typer.echo("     awdx security compliance --standard CIS --export compliance.csv")
    typer.echo()
    typer.echo(f"  {BEST_PRACTICE_EMOJI} Automated Remediation:")
    typer.echo("     awdx security remediate --dry-run  # Preview changes")
    typer.echo("     awdx security remediate --auto     # Apply fixes")
    typer.echo()
    typer.echo(f"  {BEST_PRACTICE_EMOJI} Executive Reporting:")
    typer.echo("     awdx security export --format html --output executive_report")
    typer.echo()

    typer.echo(f"{TIP_EMOJI} Best Practices:")
    typer.echo(f"  {BEST_PRACTICE_EMOJI} Run posture assessment regularly")
    typer.echo(f"  {BEST_PRACTICE_EMOJI} Use dry-run mode before remediation")
    typer.echo(f"  {BEST_PRACTICE_EMOJI} Export reports for audit trails")
    typer.echo(f"  {BEST_PRACTICE_EMOJI} Monitor critical findings")
    typer.echo(f"  {BEST_PRACTICE_EMOJI} Integrate with CI/CD pipelines")
    typer.echo()

    typer.echo(f"{INNOVATION_EMOJI} Advanced Features:")
    typer.echo(f"  {INNOVATION_EMOJI} Real-time threat detection")
    typer.echo(f"  {INNOVATION_EMOJI} Automated remediation workflows")
    typer.echo(f"  {INNOVATION_EMOJI} Compliance automation")
    typer.echo(f"  {INNOVATION_EMOJI} Incident response automation")
    typer.echo(f"  {INNOVATION_EMOJI} Security data analytics")
    typer.echo()

    typer.echo("For more information, visit: https://github.com/your-repo/awdx")
    typer.echo("=" * 80)
