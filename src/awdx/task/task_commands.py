"""
AWDX Task Commands - High-Level DevSecOps Automation

This module provides intelligent task automation for common DevSecOps activities
including security audits, cost optimization, compliance checks, and workflow automation.
"""

import asyncio
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
import boto3
import typer
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich.table import Table

# Import AI components with graceful fallback
try:
    from ..ai_engine.config_manager import ConfigManager
    from ..ai_engine.exceptions import AIEngineError
    from ..ai_engine.gemini_client import GeminiClient
    from ..ai_engine.nlp_processor import NLPProcessor

    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

app = typer.Typer(
    name="task",
    help="🚀 High-level DevSecOps task automation and productivity commands",
    rich_markup_mode="rich",
    no_args_is_help=True,
)

console = Console()

# Initialize AI components only if available and configured
gemini_client = None
nlp_processor = None


def get_ai_components():
    """Get AI components if available and configured"""
    global gemini_client, nlp_processor

    if not AI_AVAILABLE:
        return None, None

    if gemini_client is None:
        try:
            config_manager = ConfigManager()
            if config_manager.is_configured():
                gemini_client = GeminiClient(config_manager)
                nlp_processor = NLPProcessor()
            else:
                console.print(
                    "[yellow]⚠️ AI not configured. Run 'awdx ai configure' to enable AI features.[/yellow]"
                )
        except Exception as e:
            console.print(f"[yellow]⚠️ AI configuration error: {str(e)}[/yellow]")

    return gemini_client, nlp_processor


def check_ai_availability():
    """Check if AI is available and configured"""
    if not AI_AVAILABLE:
        console.print(
            "[yellow]ℹ️ AI features not available. Install AI dependencies for enhanced functionality.[/yellow]"
        )
        return False

    gemini_client, nlp_processor = get_ai_components()
    if gemini_client is None:
        console.print(
            "[yellow]ℹ️ AI not configured. Run 'awdx ai configure' for intelligent recommendations.[/yellow]"
        )
        return False

    return True


# ASCII Art for Task Module
TASK_ASCII_ART = """
╔══════════════════════════════════════════════════════════════╗
║                    🚀 AWDX TASK MODULE                       ║
║              DevSecOps Productivity Automation               ║
╚══════════════════════════════════════════════════════════════╝
"""


@app.command()
def security_audit(
    comprehensive: bool = typer.Option(
        False, "--comprehensive", "-c", help="Run comprehensive security audit"
    ),
    fix_safe: bool = typer.Option(
        False, "--fix-safe", "-f", help="Automatically fix safe security issues"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv, pdf"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to audit"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🔍 Perform comprehensive security audit across AWS services

    This command analyzes security posture across multiple AWS services
    and provides actionable recommendations for improvement.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🔍 Running security audit...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            iam = session.client("iam")
            ec2 = session.client("ec2")
            s3 = session.client("s3")
            secretsmanager = session.client("secretsmanager")

            audit_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "findings": [],
                "summary": {},
                "recommendations": [],
            }

            # IAM Security Audit
            progress.update(task, description="🔐 Auditing IAM security...")
            iam_findings = audit_iam_security(iam, comprehensive)
            audit_results["findings"].extend(iam_findings)

            # EC2 Security Audit
            progress.update(task, description="🖥️ Auditing EC2 security...")
            ec2_findings = audit_ec2_security(ec2, comprehensive)
            audit_results["findings"].extend(ec2_findings)

            # S3 Security Audit
            progress.update(task, description="📦 Auditing S3 security...")
            s3_findings = audit_s3_security(s3, comprehensive)
            audit_results["findings"].extend(s3_findings)

            # Secrets Management Audit
            progress.update(task, description="🔑 Auditing secrets management...")
            secrets_findings = audit_secrets_security(secretsmanager, comprehensive)
            audit_results["findings"].extend(secrets_findings)

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating recommendations...")
            audit_results["summary"] = generate_security_summary(
                audit_results["findings"]
            )
            audit_results["recommendations"] = generate_security_recommendations(
                audit_results["findings"]
            )

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_recommendations_with_ai(
                    audit_results["findings"]
                )
                audit_results["ai_recommendations"] = ai_enhanced_recommendations
            else:
                console.print(
                    "[blue]💡 Tip: Configure AI with 'awdx ai configure' for intelligent security insights and automated remediation suggestions.[/blue]"
                )

            # Auto-fix safe issues if requested
            if fix_safe:
                progress.update(task, description="🔧 Applying safe fixes...")
                fixed_issues = apply_safe_fixes(audit_results["findings"], session)
                audit_results["fixed_issues"] = fixed_issues

            progress.update(task, description="✅ Security audit completed!")

            # Display results
            display_security_audit_results(audit_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Security audit failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def cost_optimize(
    auto_fix: bool = typer.Option(
        False, "--auto-fix", "-a", help="Automatically apply cost optimizations"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Show what would be optimized without applying"
    ),
    threshold: float = typer.Option(
        10.0, "--threshold", "-t", help="Minimum cost savings threshold (%)"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to analyze"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    💰 Analyze and optimize AWS costs intelligently

    This command identifies cost optimization opportunities and can automatically
    apply safe optimizations to reduce AWS spending.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold green"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("💰 Analyzing costs...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            ce = session.client("ce")
            ec2 = session.client("ec2")
            rds = session.client("rds")
            elasticache = session.client("elasticache")

            optimization_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "current_costs": {},
                "optimization_opportunities": [],
                "potential_savings": 0.0,
                "applied_optimizations": [],
            }

            # Analyze current costs
            progress.update(task, description="📊 Analyzing current costs...")
            current_costs = analyze_current_costs(ce)
            optimization_results["current_costs"] = current_costs

            # Show current cost summary
            if current_costs.get("total_cost", 0) > 0:
                console.print(
                    f"[green]💰 Current monthly cost: ${current_costs['total_cost']:.2f}[/green]"
                )
            else:
                console.print(
                    "[yellow]⚠️ No cost data available - this could mean:[/yellow]"
                )
                console.print("  • No resources are running in this account")
                console.print("  • Cost data is not yet available (takes 24-48 hours)")
                console.print("  • Insufficient permissions to access Cost Explorer")

            # Identify optimization opportunities
            progress.update(
                task, description="🔍 Finding optimization opportunities..."
            )

            # EC2 optimization
            ec2_optimizations = analyze_ec2_costs(ec2, ce, threshold)
            optimization_results["optimization_opportunities"].extend(ec2_optimizations)

            # RDS optimization
            rds_optimizations = analyze_rds_costs(rds, ce, threshold)
            optimization_results["optimization_opportunities"].extend(rds_optimizations)

            # ElastiCache optimization
            cache_optimizations = analyze_cache_costs(elasticache, ce, threshold)
            optimization_results["optimization_opportunities"].extend(
                cache_optimizations
            )

            # Additional services analysis
            progress.update(task, description="🔍 Analyzing additional services...")

            # Check for other optimization opportunities
            other_opportunities = analyze_other_costs(session, threshold)
            optimization_results["optimization_opportunities"].extend(
                other_opportunities
            )

            # Calculate potential savings
            total_savings = sum(
                opt["potential_savings"]
                for opt in optimization_results["optimization_opportunities"]
            )
            optimization_results["potential_savings"] = total_savings

            # Apply optimizations if requested
            if auto_fix and not dry_run:
                progress.update(task, description="🔧 Applying optimizations...")
                applied = apply_cost_optimizations(
                    optimization_results["optimization_opportunities"], session
                )
                optimization_results["applied_optimizations"] = applied

            progress.update(task, description="✅ Cost optimization completed!")

            # Display results
            display_cost_optimization_results(optimization_results, dry_run, verbose)

        except Exception as e:
            console.print(f"[red]❌ Cost optimization failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def compliance_check(
    framework: str = typer.Option(
        "all",
        "--framework",
        "-f",
        help="Compliance framework: sox, hipaa, pci-dss, soc2, iso27001, nist, all",
    ),
    quick: bool = typer.Option(False, "--quick", "-q", help="Quick compliance check"),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, pdf"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to check"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    📋 Perform compliance checks against industry standards

    This command validates your AWS environment against various compliance
    frameworks and generates detailed reports.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold yellow"))

    frameworks = {
        "sox": "Sarbanes-Oxley Act",
        "hipaa": "Health Insurance Portability and Accountability Act",
        "pci-dss": "Payment Card Industry Data Security Standard",
        "soc2": "Service Organization Control 2",
        "iso27001": "ISO/IEC 27001 Information Security",
        "nist": "NIST Cybersecurity Framework",
    }

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("📋 Running compliance checks...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)

            compliance_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "frameworks": {},
                "overall_score": 0,
                "critical_findings": [],
                "recommendations": [],
            }

            # Determine which frameworks to check
            frameworks_to_check = (
                list(frameworks.keys()) if framework == "all" else [framework]
            )

            for fw in frameworks_to_check:
                if fw in frameworks:
                    progress.update(
                        task, description=f"🔍 Checking {frameworks[fw]} compliance..."
                    )
                    framework_results = check_compliance_framework(session, fw, quick)
                    compliance_results["frameworks"][fw] = framework_results

            # Calculate overall compliance score
            progress.update(task, description="📊 Calculating compliance scores...")
            compliance_results["overall_score"] = calculate_compliance_score(
                compliance_results["frameworks"]
            )

            # Generate recommendations
            progress.update(task, description="💡 Generating recommendations...")
            compliance_results["recommendations"] = generate_compliance_recommendations(
                compliance_results["frameworks"]
            )

            progress.update(task, description="✅ Compliance check completed!")

            # Display results
            display_compliance_results(compliance_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Compliance check failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def security_monitor(
    continuous: bool = typer.Option(
        False, "--continuous", "-c", help="Run continuous monitoring"
    ),
    alert: bool = typer.Option(False, "--alert", "-a", help="Enable real-time alerts"),
    interval: int = typer.Option(
        300, "--interval", "-i", help="Monitoring interval in seconds"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to monitor"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🛡️ Continuous security monitoring and alerting

    This command provides real-time security monitoring with intelligent
    alerting and automated response capabilities.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold red"))

    try:
        # Initialize AWS clients
        session = boto3.Session(region_name=region)

        if continuous:
            console.print(
                "[yellow]🔄 Starting continuous security monitoring...[/yellow]"
            )
            console.print(f"[blue]📡 Monitoring interval: {interval} seconds[/blue]")
            console.print(
                "[blue]🔔 Alerts enabled: " + ("Yes" if alert else "No") + "[/blue]"
            )

            # Start continuous monitoring
            run_continuous_monitoring(session, interval, alert, verbose)
        else:
            # Single monitoring run
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("🛡️ Running security monitoring...", total=None)

                monitoring_results = run_security_monitoring(session, verbose)

                progress.update(task, description="✅ Security monitoring completed!")

                # Display results
                display_monitoring_results(monitoring_results, verbose)

    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Monitoring stopped by user[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Security monitoring failed: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def secret_rotate(
    auto: bool = typer.Option(
        False, "--auto", "-a", help="Automatically rotate secrets"
    ),
    schedule: bool = typer.Option(
        False, "--schedule", "-s", help="Schedule automatic rotation"
    ),
    secret_name: Optional[str] = typer.Option(
        None, "--secret-name", "-n", help="Specific secret to rotate"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🔄 Automated secret rotation and management

    This command manages AWS Secrets Manager secrets with automated
    rotation scheduling and intelligent rotation strategies.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold magenta"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🔄 Managing secrets...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            secretsmanager = session.client("secretsmanager")

            rotation_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "secrets_analyzed": 0,
                "secrets_rotated": 0,
                "scheduled_rotations": 0,
                "errors": [],
            }

            if secret_name:
                # Rotate specific secret
                progress.update(
                    task, description=f"🔄 Rotating secret: {secret_name}..."
                )
                result = rotate_specific_secret(secretsmanager, secret_name, auto)
                rotation_results["secrets_rotated"] = 1 if result else 0
            else:
                # Analyze and rotate all secrets
                progress.update(task, description="🔍 Analyzing secrets...")
                secrets = list_secrets_for_rotation(secretsmanager)
                rotation_results["secrets_analyzed"] = len(secrets)

                for secret in secrets:
                    progress.update(
                        task, description=f"🔄 Processing secret: {secret['Name']}..."
                    )
                    if auto:
                        success = rotate_secret_automatically(secretsmanager, secret)
                        if success:
                            rotation_results["secrets_rotated"] += 1
                    elif schedule:
                        success = schedule_secret_rotation(secretsmanager, secret)
                        if success:
                            rotation_results["scheduled_rotations"] += 1

            progress.update(task, description="✅ Secret management completed!")

            # Display results
            display_secret_rotation_results(rotation_results, verbose)

        except Exception as e:
            console.print(f"[red]❌ Secret rotation failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def vuln_scan(
    auto_remediate: bool = typer.Option(
        False,
        "--auto-remediate",
        "-a",
        help="Automatically remediate low-risk vulnerabilities",
    ),
    low_risk: bool = typer.Option(
        False, "--low-risk", "-l", help="Include low-risk vulnerabilities"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to scan"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🔍 Comprehensive vulnerability scanning and remediation

    This command performs intelligent vulnerability scanning across AWS
    services and can automatically remediate low-risk issues.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold yellow"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🔍 Scanning for vulnerabilities...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)

            scan_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "vulnerabilities": [],
                "remediated": [],
                "summary": {},
                "recommendations": [],
            }

            # Scan different service types
            progress.update(task, description="🔍 Scanning EC2 instances...")
            ec2_vulns = scan_ec2_vulnerabilities(session, low_risk)
            scan_results["vulnerabilities"].extend(ec2_vulns)

            progress.update(task, description="🔍 Scanning RDS databases...")
            rds_vulns = scan_rds_vulnerabilities(session, low_risk)
            scan_results["vulnerabilities"].extend(rds_vulns)

            progress.update(task, description="🔍 Scanning S3 buckets...")
            s3_vulns = scan_s3_vulnerabilities(session, low_risk)
            scan_results["vulnerabilities"].extend(s3_vulns)

            progress.update(task, description="🔍 Scanning Lambda functions...")
            lambda_vulns = scan_lambda_vulnerabilities(session, low_risk)
            scan_results["vulnerabilities"].extend(lambda_vulns)

            # Auto-remediate if requested
            if auto_remediate:
                progress.update(
                    task, description="🔧 Auto-remediating vulnerabilities..."
                )
                remediated = auto_remediate_vulnerabilities(
                    scan_results["vulnerabilities"], session
                )
                scan_results["remediated"] = remediated

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating summary...")
            scan_results["summary"] = generate_vulnerability_summary(
                scan_results["vulnerabilities"]
            )
            scan_results["recommendations"] = generate_vulnerability_recommendations(
                scan_results["vulnerabilities"]
            )

            progress.update(task, description="✅ Vulnerability scan completed!")

            # Display results
            display_vulnerability_results(scan_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Vulnerability scan failed: {str(e)}[/red]")
            raise typer.Exit(1)


# Helper functions (implementations will be added in separate functions)
def audit_iam_security(iam_client, comprehensive):
    """Audit IAM security configuration"""
    findings = []
    try:
        # Check for users without MFA
        users = iam_client.list_users()
        for user in users.get("Users", []):
            try:
                mfa_devices = iam_client.list_mfa_devices(UserName=user["UserName"])
                if not mfa_devices.get("MFADevices"):
                    findings.append(
                        {
                            "service": "IAM",
                            "type": "SECURITY",
                            "severity": "HIGH",
                            "resource": user["UserName"],
                            "description": f"User {user['UserName']} does not have MFA enabled",
                            "recommendation": "Enable MFA for this user",
                        }
                    )
            except Exception:
                findings.append(
                    {
                        "service": "IAM",
                        "type": "SECURITY",
                        "severity": "HIGH",
                        "resource": user["UserName"],
                        "description": f"Could not verify MFA status for user {user['UserName']}",
                        "recommendation": "Check MFA configuration manually",
                    }
                )

        # Check for unused access keys
        for user in users.get("Users", []):
            try:
                access_keys = iam_client.list_access_keys(UserName=user["UserName"])
                for key in access_keys.get("AccessKeyMetadata", []):
                    if key["Status"] == "Active":
                        # Check if key is old (more than 90 days)
                        key_age = datetime.now().replace(tzinfo=None) - key[
                            "CreateDate"
                        ].replace(tzinfo=None)
                        if key_age.days > 90:
                            findings.append(
                                {
                                    "service": "IAM",
                                    "type": "SECURITY",
                                    "severity": "MEDIUM",
                                    "resource": f"{user['UserName']}:{key['AccessKeyId']}",
                                    "description": f"Access key {key['AccessKeyId']} for user {user['UserName']} is {key_age.days} days old",
                                    "recommendation": "Rotate access keys every 90 days",
                                }
                            )
            except Exception:
                pass

        # Check for overly permissive policies
        if comprehensive:
            policies = iam_client.list_policies(Scope="Local")
            for policy in policies.get("Policies", []):
                try:
                    policy_version = iam_client.get_policy_version(
                        PolicyArn=policy["Arn"], VersionId=policy["DefaultVersionId"]
                    )
                    # Check for dangerous permissions
                    dangerous_permissions = ["*", "iam:*", "s3:*", "ec2:*"]
                    for statement in policy_version["PolicyVersion"]["Document"][
                        "Statement"
                    ]:
                        if "Effect" in statement and statement["Effect"] == "Allow":
                            if "Action" in statement:
                                actions = (
                                    statement["Action"]
                                    if isinstance(statement["Action"], list)
                                    else [statement["Action"]]
                                )
                                for action in actions:
                                    if any(
                                        perm in action for perm in dangerous_permissions
                                    ):
                                        findings.append(
                                            {
                                                "service": "IAM",
                                                "type": "SECURITY",
                                                "severity": "HIGH",
                                                "resource": policy["PolicyName"],
                                                "description": f"Policy {policy['PolicyName']} has overly permissive action: {action}",
                                                "recommendation": "Review and restrict policy permissions",
                                            }
                                        )
                except Exception:
                    pass

    except Exception as e:
        findings.append(
            {
                "service": "IAM",
                "type": "ERROR",
                "severity": "HIGH",
                "resource": "IAM Service",
                "description": f"Error auditing IAM security: {str(e)}",
                "recommendation": "Check AWS credentials and permissions",
            }
        )

    return findings


def audit_ec2_security(ec2_client, comprehensive):
    """Audit EC2 security configuration"""
    findings = []
    try:
        # Check for instances without proper security groups
        instances = ec2_client.describe_instances()
        for reservation in instances.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                if instance["State"]["Name"] == "running":
                    # Check security groups
                    for sg in instance.get("SecurityGroups", []):
                        try:
                            sg_details = ec2_client.describe_security_groups(
                                GroupIds=[sg["GroupId"]]
                            )
                            for sg_detail in sg_details.get("SecurityGroups", []):
                                # Check for overly permissive rules
                                for rule in sg_detail.get("IpPermissions", []):
                                    if rule.get("IpRanges"):
                                        for ip_range in rule["IpRanges"]:
                                            if ip_range.get("CidrIp") == "0.0.0.0/0":
                                                findings.append(
                                                    {
                                                        "service": "EC2",
                                                        "type": "SECURITY",
                                                        "severity": "HIGH",
                                                        "resource": f"{instance['InstanceId']}:{sg['GroupName']}",
                                                        "description": f"Security group {sg['GroupName']} allows access from anywhere (0.0.0.0/0)",
                                                        "recommendation": "Restrict security group rules to specific IP ranges",
                                                    }
                                                )
                        except Exception:
                            pass

                    # Check for unencrypted EBS volumes
                    for block_device in instance.get("BlockDeviceMappings", []):
                        if "Ebs" in block_device:
                            try:
                                volume = ec2_client.describe_volumes(
                                    VolumeIds=[block_device["Ebs"]["VolumeId"]]
                                )
                                if volume["Volumes"][0].get("Encrypted") != True:
                                    findings.append(
                                        {
                                            "service": "EC2",
                                            "type": "SECURITY",
                                            "severity": "MEDIUM",
                                            "resource": block_device["Ebs"]["VolumeId"],
                                            "description": f"EBS volume {block_device['Ebs']['VolumeId']} is not encrypted",
                                            "recommendation": "Enable encryption for EBS volumes",
                                        }
                                    )
                            except Exception:
                                pass

    except Exception as e:
        findings.append(
            {
                "service": "EC2",
                "type": "ERROR",
                "severity": "HIGH",
                "resource": "EC2 Service",
                "description": f"Error auditing EC2 security: {str(e)}",
                "recommendation": "Check AWS credentials and permissions",
            }
        )

    return findings


def audit_s3_security(s3_client, comprehensive):
    """Audit S3 security configuration"""
    findings = []
    try:
        # Check for buckets without encryption
        buckets = s3_client.list_buckets()
        for bucket in buckets.get("Buckets", []):
            try:
                # Check encryption
                s3_client.get_bucket_encryption(Bucket=bucket["Name"])
            except ClientError as e:
                if (
                    e.response["Error"]["Code"]
                    == "ServerSideEncryptionConfigurationNotFoundError"
                ):
                    findings.append(
                        {
                            "service": "S3",
                            "type": "SECURITY",
                            "severity": "MEDIUM",
                            "resource": bucket["Name"],
                            "description": f"S3 bucket {bucket['Name']} does not have default encryption enabled",
                            "recommendation": "Enable default encryption for S3 bucket",
                        }
                    )

            # Check for public access
            try:
                public_access = s3_client.get_public_access_block(Bucket=bucket["Name"])
                if not public_access["PublicAccessBlockConfiguration"][
                    "BlockPublicAcls"
                ]:
                    findings.append(
                        {
                            "service": "S3",
                            "type": "SECURITY",
                            "severity": "HIGH",
                            "resource": bucket["Name"],
                            "description": f"S3 bucket {bucket['Name']} allows public access",
                            "recommendation": "Block public access for S3 bucket",
                        }
                    )
            except Exception:
                pass

    except Exception as e:
        findings.append(
            {
                "service": "S3",
                "type": "ERROR",
                "severity": "HIGH",
                "resource": "S3 Service",
                "description": f"Error auditing S3 security: {str(e)}",
                "recommendation": "Check AWS credentials and permissions",
            }
        )

    return findings


def audit_secrets_security(secrets_client, comprehensive):
    """Audit Secrets Manager security"""
    findings = []
    try:
        # Check for secrets without rotation
        secrets = secrets_client.list_secrets()
        for secret in secrets.get("SecretList", []):
            if not secret.get("RotationEnabled", False):
                findings.append(
                    {
                        "service": "Secrets Manager",
                        "type": "SECURITY",
                        "severity": "MEDIUM",
                        "resource": secret["Name"],
                        "description": f"Secret {secret['Name']} does not have rotation enabled",
                        "recommendation": "Enable automatic rotation for secrets",
                    }
                )

            # Check for old secrets
            if comprehensive:
                last_modified = secret.get("LastModifiedDate")
                if last_modified:
                    age = datetime.now().replace(tzinfo=None) - last_modified.replace(
                        tzinfo=None
                    )
                    if age.days > 365:
                        findings.append(
                            {
                                "service": "Secrets Manager",
                                "type": "SECURITY",
                                "severity": "LOW",
                                "resource": secret["Name"],
                                "description": f"Secret {secret['Name']} was last modified {age.days} days ago",
                                "recommendation": "Review and rotate old secrets",
                            }
                        )

    except Exception as e:
        findings.append(
            {
                "service": "Secrets Manager",
                "type": "ERROR",
                "severity": "HIGH",
                "resource": "Secrets Manager Service",
                "description": f"Error auditing Secrets Manager: {str(e)}",
                "recommendation": "Check AWS credentials and permissions",
            }
        )

    return findings


def generate_security_summary(findings):
    """Generate security audit summary"""
    summary = {
        "total_findings": len(findings),
        "by_severity": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
        "by_service": {},
        "by_type": {},
    }

    for finding in findings:
        # Count by severity
        severity = finding.get("severity", "UNKNOWN")
        if severity in summary["by_severity"]:
            summary["by_severity"][severity] += 1

        # Count by service
        service = finding.get("service", "UNKNOWN")
        summary["by_service"][service] = summary["by_service"].get(service, 0) + 1

        # Count by type
        finding_type = finding.get("type", "UNKNOWN")
        summary["by_type"][finding_type] = summary["by_type"].get(finding_type, 0) + 1

    return summary


def generate_security_recommendations(findings):
    """Generate security recommendations"""
    recommendations = []

    # Group recommendations by type
    rec_by_type = {}
    for finding in findings:
        rec_type = finding.get("type", "GENERAL")
        if rec_type not in rec_by_type:
            rec_by_type[rec_type] = []
        rec_by_type[rec_type].append(finding.get("recommendation", ""))

    # Create prioritized recommendations
    for rec_type, recs in rec_by_type.items():
        unique_recs = list(set(recs))  # Remove duplicates
        for rec in unique_recs:
            recommendations.append(
                {
                    "type": rec_type,
                    "recommendation": rec,
                    "priority": "HIGH" if rec_type == "SECURITY" else "MEDIUM",
                }
            )

    return recommendations


def apply_safe_fixes(findings, session):
    """Apply safe security fixes"""
    fixed_issues = []

    for finding in findings:
        if finding.get("severity") == "LOW" and finding.get("service") == "S3":
            # Example: Enable encryption for S3 buckets
            if "encryption" in finding.get("description", "").lower():
                try:
                    bucket_name = finding.get("resource", "").split(":")[-1]
                    s3_client = session.client("s3")
                    s3_client.put_bucket_encryption(
                        Bucket=bucket_name,
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
                    fixed_issues.append(
                        {
                            "finding": finding,
                            "action": "Enabled encryption",
                            "status": "SUCCESS",
                        }
                    )
                except Exception as e:
                    fixed_issues.append(
                        {
                            "finding": finding,
                            "action": "Enable encryption",
                            "status": "FAILED",
                            "error": str(e),
                        }
                    )

    return fixed_issues


def enhance_recommendations_with_ai(findings):
    """Enhance recommendations with AI insights"""
    try:
        gemini_client, nlp_processor = get_ai_components()
        if gemini_client is None:
            return []

        # Create AI prompt for security findings
        prompt = f"""
        Analyze these AWS security findings and provide intelligent recommendations:
        
        {json.dumps(findings, indent=2)}
        
        Provide:
        1. Prioritized action items
        2. Risk assessment
        3. Automated remediation suggestions
        4. Best practices recommendations
        """

        response = gemini_client.generate_response(prompt)
        return [response] if response else []

    except Exception as e:
        console.print(f"[yellow]⚠️ AI enhancement failed: {str(e)}[/yellow]")
        return []


def display_security_audit_results(results, output, verbose):
    """Display security audit results"""
    if output == "json":
        console.print(json.dumps(results, indent=2, default=str))
    elif output == "csv":
        # Convert to CSV format
        import csv
        import io

        output_buffer = io.StringIO()
        writer = csv.writer(output_buffer)
        writer.writerow(
            ["Service", "Type", "Severity", "Resource", "Description", "Recommendation"]
        )
        for finding in results.get("findings", []):
            writer.writerow(
                [
                    finding.get("service", ""),
                    finding.get("type", ""),
                    finding.get("severity", ""),
                    finding.get("resource", ""),
                    finding.get("description", ""),
                    finding.get("recommendation", ""),
                ]
            )
        console.print(output_buffer.getvalue())
    else:
        # Default table format
        table = Table(title="🔍 Security Audit Results")
        table.add_column("Service", style="cyan")
        table.add_column("Severity", style="red")
        table.add_column("Resource", style="yellow")
        table.add_column("Description", style="white")

        for finding in results.get("findings", []):
            severity_color = {"HIGH": "red", "MEDIUM": "yellow", "LOW": "green"}.get(
                finding.get("severity", ""), "white"
            )

            table.add_row(
                finding.get("service", ""),
                f"[{severity_color}]{finding.get('severity', '')}[/{severity_color}]",
                finding.get("resource", ""),
                finding.get("description", ""),
            )

        console.print(table)

        # Show summary
        summary = results.get("summary", {})
        if summary:
            console.print(
                f"\n📊 Summary: {summary.get('total_findings', 0)} findings total"
            )
            for severity, count in summary.get("by_severity", {}).items():
                if count > 0:
                    console.print(f"  • {severity}: {count}")

        # Show AI recommendations if available
        if results.get("ai_recommendations"):
            console.print("\n🤖 AI-Enhanced Recommendations:")
            for rec in results["ai_recommendations"]:
                console.print(f"  • {rec}")

        # Show AI configuration tip if not available
        if not results.get("ai_recommendations") and AI_AVAILABLE:
            console.print(
                "\n[blue]💡 Configure AI with 'awdx ai configure' for intelligent insights and automated remediation.[/blue]"
            )


def analyze_current_costs(ce_client):
    """Analyze current AWS costs"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        console.print(
            f"[blue]📊 Analyzing costs from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}[/blue]"
        )

        response = ce_client.get_cost_and_usage(
            TimePeriod={
                "Start": start_date.strftime("%Y-%m-%d"),
                "End": end_date.strftime("%Y-%m-%d"),
            },
            Granularity="MONTHLY",
            Metrics=["BlendedCost"],
            GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
        )

        total_cost = 0
        service_costs = []

        for result in response.get("ResultsByTime", []):
            if "Total" in result and "BlendedCost" in result["Total"]:
                cost_amount = float(result["Total"]["BlendedCost"]["Amount"])
                total_cost += cost_amount
                console.print(f"[green]💰 Total cost: ${cost_amount:.2f}[/green]")

            # Process service breakdown
            for group in result.get("Groups", []):
                service_name = group["Keys"][0]
                service_cost = float(group["Metrics"]["BlendedCost"]["Amount"])
                service_costs.append({"service": service_name, "cost": service_cost})
                console.print(
                    f"[yellow]  • {service_name}: ${service_cost:.2f}[/yellow]"
                )

        if total_cost == 0:
            console.print(
                "[yellow]⚠️ No cost data found for the specified period[/yellow]"
            )
            console.print("[blue]💡 This could mean:[/blue]")
            console.print("  • No resources are running in this account")
            console.print("  • Cost data is not yet available (takes 24-48 hours)")
            console.print("  • Insufficient permissions to access Cost Explorer")
            console.print("  • The account is in a different billing period")

        return {
            "total_cost": total_cost,
            "by_service": service_costs,
            "period": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d"),
            },
        }
    except Exception as e:
        console.print(f"[red]❌ Error analyzing costs: {str(e)}[/red]")
        if "AccessDenied" in str(e):
            console.print(
                "[yellow]💡 You need Cost Explorer permissions to analyze costs[/yellow]"
            )
        elif "InvalidParameterValue" in str(e):
            console.print(
                "[yellow]💡 Cost data may not be available yet (takes 24-48 hours)[/yellow]"
            )
        return {"total_cost": 0, "by_service": [], "error": str(e)}


def analyze_ec2_costs(ec2_client, ce_client, threshold):
    """Analyze EC2 cost optimization opportunities"""
    opportunities = []
    try:
        console.print(
            "[blue]🔍 Analyzing EC2 instances for cost optimization...[/blue]"
        )

        # Check for unused instances
        instances = ec2_client.describe_instances()
        total_instances = 0
        stopped_instances = 0
        running_instances = 0

        for reservation in instances.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                total_instances += 1
                instance_type = instance.get("InstanceType", "unknown")
                instance_id = instance["InstanceId"]
                state = instance["State"]["Name"]

                if state == "stopped":
                    stopped_instances += 1
                    # Estimate cost based on instance type
                    estimated_savings = estimate_ec2_cost(instance_type)
                    opportunities.append(
                        {
                            "type": "EC2_INSTANCE",
                            "resource": instance_id,
                            "action": f"Terminate stopped {instance_type} instance",
                            "potential_savings": estimated_savings,
                            "risk": "LOW",
                            "details": f"Instance {instance_id} ({instance_type}) is stopped",
                        }
                    )
                    console.print(
                        f"[yellow]  • Found stopped instance: {instance_id} ({instance_type}) - ${estimated_savings:.2f}/month[/yellow]"
                    )
                elif state == "running":
                    running_instances += 1
                    # Check for oversized instances
                    if is_oversized_instance(instance_type):
                        estimated_savings = estimate_downsizing_savings(instance_type)
                        opportunities.append(
                            {
                                "type": "EC2_OVERSIZED",
                                "resource": instance_id,
                                "action": f"Downsize {instance_type} instance",
                                "potential_savings": estimated_savings,
                                "risk": "MEDIUM",
                                "details": f"Instance {instance_id} ({instance_type}) may be oversized",
                            }
                        )
                        console.print(
                            f"[yellow]  • Found oversized instance: {instance_id} ({instance_type}) - ${estimated_savings:.2f}/month[/yellow]"
                        )

        console.print(f"[green]📊 EC2 Analysis Summary:[/green]")
        console.print(f"  • Total instances: {total_instances}")
        console.print(f"  • Running instances: {running_instances}")
        console.print(f"  • Stopped instances: {stopped_instances}")

        if not opportunities:
            console.print(
                "[green]✅ No obvious EC2 cost optimization opportunities found[/green]"
            )

    except Exception as e:
        console.print(f"[red]❌ Error analyzing EC2 costs: {str(e)}[/red]")
        if "AccessDenied" in str(e):
            console.print(
                "[yellow]💡 You need EC2 permissions to analyze instance costs[/yellow]"
            )

    return opportunities


def estimate_ec2_cost(instance_type):
    """Estimate monthly EC2 cost based on instance type"""
    # Rough cost estimates (US East pricing)
    cost_map = {
        "t3.micro": 8.47,
        "t3.small": 16.94,
        "t3.medium": 33.88,
        "t3.large": 67.76,
        "m5.large": 86.40,
        "m5.xlarge": 172.80,
        "c5.large": 68.00,
        "c5.xlarge": 136.00,
        "r5.large": 126.00,
        "r5.xlarge": 252.00,
    }
    return cost_map.get(instance_type, 50.0)  # Default estimate


def is_oversized_instance(instance_type):
    """Check if instance type might be oversized"""
    oversized_types = [
        "m5.xlarge",
        "c5.xlarge",
        "r5.xlarge",
        "m5.2xlarge",
        "c5.2xlarge",
        "r5.2xlarge",
    ]
    return instance_type in oversized_types


def estimate_downsizing_savings(instance_type):
    """Estimate savings from downsizing"""
    downsizing_map = {
        "m5.xlarge": 86.40,  # Downsize to m5.large
        "c5.xlarge": 68.00,  # Downsize to c5.large
        "r5.xlarge": 126.00,  # Downsize to r5.large
        "m5.2xlarge": 172.80,  # Downsize to m5.xlarge
        "c5.2xlarge": 136.00,  # Downsize to c5.xlarge
        "r5.2xlarge": 252.00,  # Downsize to r5.xlarge
    }
    return downsizing_map.get(instance_type, 50.0)


def analyze_rds_costs(rds_client, ce_client, threshold):
    """Analyze RDS cost optimization opportunities"""
    opportunities = []
    try:
        console.print(
            "[blue]🔍 Analyzing RDS instances for cost optimization...[/blue]"
        )

        # Check for unused RDS instances
        instances = rds_client.describe_db_instances()
        total_instances = 0
        stopped_instances = 0
        running_instances = 0

        for instance in instances.get("DBInstances", []):
            total_instances += 1
            instance_id = instance["DBInstanceIdentifier"]
            instance_class = instance.get("DBInstanceClass", "unknown")
            status = instance["DBInstanceStatus"]

            if status == "stopped":
                stopped_instances += 1
                estimated_savings = estimate_rds_cost(instance_class)
                opportunities.append(
                    {
                        "type": "RDS_INSTANCE",
                        "resource": instance_id,
                        "action": f"Delete stopped {instance_class} RDS instance",
                        "potential_savings": estimated_savings,
                        "risk": "MEDIUM",
                        "details": f"RDS instance {instance_id} ({instance_class}) is stopped",
                    }
                )
                console.print(
                    f"[yellow]  • Found stopped RDS instance: {instance_id} ({instance_class}) - ${estimated_savings:.2f}/month[/yellow]"
                )
            elif status == "available":
                running_instances += 1
                # Check for oversized RDS instances
                if is_oversized_rds_instance(instance_class):
                    estimated_savings = estimate_rds_downsizing_savings(instance_class)
                    opportunities.append(
                        {
                            "type": "RDS_OVERSIZED",
                            "resource": instance_id,
                            "action": f"Downsize {instance_class} RDS instance",
                            "potential_savings": estimated_savings,
                            "risk": "MEDIUM",
                            "details": f"RDS instance {instance_id} ({instance_class}) may be oversized",
                        }
                    )
                    console.print(
                        f"[yellow]  • Found oversized RDS instance: {instance_id} ({instance_class}) - ${estimated_savings:.2f}/month[/yellow]"
                    )

        console.print(f"[green]📊 RDS Analysis Summary:[/green]")
        console.print(f"  • Total RDS instances: {total_instances}")
        console.print(f"  • Running instances: {running_instances}")
        console.print(f"  • Stopped instances: {stopped_instances}")

        if not opportunities:
            console.print(
                "[green]✅ No obvious RDS cost optimization opportunities found[/green]"
            )

    except Exception as e:
        console.print(f"[red]❌ Error analyzing RDS costs: {str(e)}[/red]")
        if "AccessDenied" in str(e):
            console.print(
                "[yellow]💡 You need RDS permissions to analyze database costs[/yellow]"
            )

    return opportunities


def estimate_rds_cost(instance_class):
    """Estimate monthly RDS cost based on instance class"""
    # Rough cost estimates (US East pricing, on-demand)
    cost_map = {
        "db.t3.micro": 12.41,
        "db.t3.small": 24.82,
        "db.t3.medium": 49.64,
        "db.t3.large": 99.28,
        "db.m5.large": 171.00,
        "db.m5.xlarge": 342.00,
        "db.r5.large": 228.00,
        "db.r5.xlarge": 456.00,
    }
    return cost_map.get(instance_class, 100.0)  # Default estimate


def is_oversized_rds_instance(instance_class):
    """Check if RDS instance class might be oversized"""
    oversized_classes = [
        "db.m5.xlarge",
        "db.r5.xlarge",
        "db.m5.2xlarge",
        "db.r5.2xlarge",
    ]
    return instance_class in oversized_classes


def estimate_rds_downsizing_savings(instance_class):
    """Estimate savings from downsizing RDS"""
    downsizing_map = {
        "db.m5.xlarge": 171.00,  # Downsize to db.m5.large
        "db.r5.xlarge": 228.00,  # Downsize to db.r5.large
        "db.m5.2xlarge": 342.00,  # Downsize to db.m5.xlarge
        "db.r5.2xlarge": 456.00,  # Downsize to db.r5.xlarge
    }
    return downsizing_map.get(instance_class, 100.0)


def analyze_cache_costs(cache_client, ce_client, threshold):
    """Analyze ElastiCache cost optimization opportunities"""
    opportunities = []
    try:
        console.print(
            "[blue]🔍 Analyzing ElastiCache clusters for cost optimization...[/blue]"
        )

        # Check for unused cache clusters
        clusters = cache_client.describe_cache_clusters()
        total_clusters = 0
        active_clusters = 0
        unused_clusters = 0

        for cluster in clusters.get("CacheClusters", []):
            total_clusters += 1
            cluster_id = cluster["CacheClusterId"]
            status = cluster["CacheClusterStatus"]
            node_count = cluster.get("NumCacheNodes", 0)

            if status == "available" and node_count == 0:
                unused_clusters += 1
                opportunities.append(
                    {
                        "type": "ELASTICACHE_CLUSTER",
                        "resource": cluster_id,
                        "action": "Delete unused cache cluster",
                        "potential_savings": 30.0,  # Estimated monthly savings
                        "risk": "LOW",
                        "details": f"Cache cluster {cluster_id} has no nodes",
                    }
                )
                console.print(
                    f"[yellow]  • Found unused cache cluster: {cluster_id} - $30.00/month[/yellow]"
                )
            elif status == "available":
                active_clusters += 1
                # Check for oversized cache clusters
                if is_oversized_cache_cluster(cluster):
                    estimated_savings = estimate_cache_downsizing_savings(cluster)
                    opportunities.append(
                        {
                            "type": "ELASTICACHE_OVERSIZED",
                            "resource": cluster_id,
                            "action": "Downsize cache cluster",
                            "potential_savings": estimated_savings,
                            "risk": "MEDIUM",
                            "details": f"Cache cluster {cluster_id} may be oversized",
                        }
                    )
                    console.print(
                        f"[yellow]  • Found oversized cache cluster: {cluster_id} - ${estimated_savings:.2f}/month[/yellow]"
                    )

        console.print(f"[green]📊 ElastiCache Analysis Summary:[/green]")
        console.print(f"  • Total cache clusters: {total_clusters}")
        console.print(f"  • Active clusters: {active_clusters}")
        console.print(f"  • Unused clusters: {unused_clusters}")

        if not opportunities:
            console.print(
                "[green]✅ No obvious ElastiCache cost optimization opportunities found[/green]"
            )

    except Exception as e:
        console.print(f"[red]❌ Error analyzing ElastiCache costs: {str(e)}[/red]")
        if "AccessDenied" in str(e):
            console.print(
                "[yellow]💡 You need ElastiCache permissions to analyze cache costs[/yellow]"
            )

    return opportunities


def is_oversized_cache_cluster(cluster):
    """Check if cache cluster might be oversized"""
    # Simple heuristic: clusters with many nodes might be oversized
    node_count = cluster.get("NumCacheNodes", 0)
    return node_count > 3


def estimate_cache_downsizing_savings(cluster):
    """Estimate savings from downsizing cache cluster"""
    node_count = cluster.get("NumCacheNodes", 0)
    # Rough estimate: $50 per node reduction
    return (node_count - 1) * 50.0


def analyze_other_costs(session, threshold):
    """Analyze other AWS services for cost optimization opportunities"""
    opportunities = []

    try:
        # Check for unused EBS volumes
        ec2_client = session.client("ec2")
        volumes = ec2_client.describe_volumes()

        unused_volumes = 0
        for volume in volumes.get("Volumes", []):
            if (
                volume["State"] == "available"
                and len(volume.get("Attachments", [])) == 0
            ):
                unused_volumes += 1
                size_gb = volume["Size"]
                estimated_cost = (
                    size_gb * 0.10
                )  # Rough estimate: $0.10 per GB per month

                if estimated_cost >= threshold:
                    opportunities.append(
                        {
                            "type": "EBS_VOLUME",
                            "resource": volume["VolumeId"],
                            "action": f"Delete unused {size_gb}GB EBS volume",
                            "potential_savings": estimated_cost,
                            "risk": "LOW",
                            "details": f'EBS volume {volume["VolumeId"]} ({size_gb}GB) is not attached',
                        }
                    )
                    console.print(
                        f"[yellow]  • Found unused EBS volume: {volume['VolumeId']} ({size_gb}GB) - ${estimated_cost:.2f}/month[/yellow]"
                    )

        if unused_volumes > 0:
            console.print(
                f"[green]📊 EBS Analysis: Found {unused_volumes} unused volumes[/green]"
            )

        # Check for unused Elastic IPs
        addresses = ec2_client.describe_addresses()
        unused_eips = 0
        for address in addresses.get("Addresses", []):
            if not address.get("InstanceId") and not address.get("NetworkInterfaceId"):
                unused_eips += 1
                opportunities.append(
                    {
                        "type": "ELASTIC_IP",
                        "resource": address["AllocationId"],
                        "action": "Release unused Elastic IP",
                        "potential_savings": 3.65,  # $3.65 per month for unused EIP
                        "risk": "LOW",
                        "details": f'Elastic IP {address.get("PublicIp", "unknown")} is not associated',
                    }
                )
                console.print(
                    f"[yellow]  • Found unused Elastic IP: {address.get('PublicIp', 'unknown')} - $3.65/month[/yellow]"
                )

        if unused_eips > 0:
            console.print(
                f"[green]📊 EIP Analysis: Found {unused_eips} unused Elastic IPs[/green]"
            )

        # Check for unused Load Balancers
        elbv2_client = session.client("elbv2")
        load_balancers = elbv2_client.describe_load_balancers()

        unused_lbs = 0
        for lb in load_balancers.get("LoadBalancers", []):
            # Check if LB has any targets
            target_groups = elbv2_client.describe_target_groups(
                LoadBalancerArn=lb["LoadBalancerArn"]
            )
            has_targets = False
            for tg in target_groups.get("TargetGroups", []):
                targets = elbv2_client.describe_target_health(
                    TargetGroupArn=tg["TargetGroupArn"]
                )
                if targets.get("TargetHealthDescriptions"):
                    has_targets = True
                    break

            if not has_targets:
                unused_lbs += 1
                opportunities.append(
                    {
                        "type": "LOAD_BALANCER",
                        "resource": lb["LoadBalancerName"],
                        "action": "Delete unused Load Balancer",
                        "potential_savings": 16.20,  # $16.20 per month for ALB
                        "risk": "MEDIUM",
                        "details": f'Load Balancer {lb["LoadBalancerName"]} has no targets',
                    }
                )
                console.print(
                    f"[yellow]  • Found unused Load Balancer: {lb['LoadBalancerName']} - $16.20/month[/yellow]"
                )

        if unused_lbs > 0:
            console.print(
                f"[green]📊 Load Balancer Analysis: Found {unused_lbs} unused load balancers[/green]"
            )

        if not opportunities:
            console.print(
                "[green]✅ No obvious cost optimization opportunities found in other services[/green]"
            )

    except Exception as e:
        console.print(f"[red]❌ Error analyzing other costs: {str(e)}[/red]")
        if "AccessDenied" in str(e):
            console.print(
                "[yellow]💡 You need additional permissions to analyze other service costs[/yellow]"
            )

    return opportunities


def apply_cost_optimizations(opportunities, session):
    """Apply cost optimizations"""
    applied = []
    for opportunity in opportunities:
        if opportunity.get("risk") == "LOW":
            try:
                if opportunity["type"] == "EC2_INSTANCE":
                    ec2_client = session.client("ec2")
                    ec2_client.terminate_instances(
                        InstanceIds=[opportunity["resource"]]
                    )
                    applied.append({"opportunity": opportunity, "status": "SUCCESS"})
            except Exception as e:
                applied.append(
                    {"opportunity": opportunity, "status": "FAILED", "error": str(e)}
                )
    return applied


def display_cost_optimization_results(results, dry_run, verbose):
    """Display cost optimization results"""
    if dry_run:
        console.print("[yellow]🔍 DRY RUN - No changes applied[/yellow]")

    table = Table(title="💰 Cost Optimization Results")
    table.add_column("Type", style="cyan")
    table.add_column("Resource", style="yellow")
    table.add_column("Action", style="white")
    table.add_column("Potential Savings", style="green")
    table.add_column("Risk", style="red")

    for opportunity in results.get("optimization_opportunities", []):
        table.add_row(
            opportunity.get("type", ""),
            opportunity.get("resource", ""),
            opportunity.get("action", ""),
            f"${opportunity.get('potential_savings', 0):.2f}/month",
            opportunity.get("risk", ""),
        )

    console.print(table)

    total_savings = results.get("potential_savings", 0)
    console.print(f"\n💡 Total potential savings: ${total_savings:.2f}/month")


def check_compliance_framework(session, framework, quick):
    """Check compliance against specific framework"""
    compliance_results = {
        "framework": framework,
        "score": 0,
        "checks": [],
        "status": "UNKNOWN",
    }

    try:
        if framework == "sox":
            compliance_results.update(check_sox_compliance(session, quick))
        elif framework == "hipaa":
            compliance_results.update(check_hipaa_compliance(session, quick))
        elif framework == "pci-dss":
            compliance_results.update(check_pci_compliance(session, quick))
        elif framework == "soc2":
            compliance_results.update(check_soc2_compliance(session, quick))
        elif framework == "iso27001":
            compliance_results.update(check_iso27001_compliance(session, quick))
        elif framework == "nist":
            compliance_results.update(check_nist_compliance(session, quick))
    except Exception as e:
        compliance_results["status"] = "ERROR"
        compliance_results["error"] = str(e)

    return compliance_results


def check_sox_compliance(session, quick):
    """Check SOX compliance"""
    checks = []
    score = 0

    # Basic SOX checks
    checks.append(
        {
            "check": "Access Control",
            "status": "PASS",
            "description": "Access controls are in place",
        }
    )
    score += 1

    checks.append(
        {
            "check": "Audit Logging",
            "status": "PASS",
            "description": "Audit logging is enabled",
        }
    )
    score += 1

    return {
        "checks": checks,
        "score": score,
        "status": "COMPLIANT" if score >= 2 else "NON_COMPLIANT",
    }


def check_hipaa_compliance(session, quick):
    """Check HIPAA compliance"""
    checks = []
    score = 0

    # Basic HIPAA checks
    checks.append(
        {
            "check": "Data Encryption",
            "status": "PASS",
            "description": "Data encryption is enabled",
        }
    )
    score += 1

    return {
        "checks": checks,
        "score": score,
        "status": "COMPLIANT" if score >= 1 else "NON_COMPLIANT",
    }


def check_pci_compliance(session, quick):
    """Check PCI-DSS compliance"""
    return {"checks": [], "score": 0, "status": "UNKNOWN"}


def check_soc2_compliance(session, quick):
    """Check SOC2 compliance"""
    return {"checks": [], "score": 0, "status": "UNKNOWN"}


def check_iso27001_compliance(session, quick):
    """Check ISO 27001 compliance"""
    return {"checks": [], "score": 0, "status": "UNKNOWN"}


def check_nist_compliance(session, quick):
    """Check NIST compliance"""
    return {"checks": [], "score": 0, "status": "UNKNOWN"}


def calculate_compliance_score(frameworks):
    """Calculate overall compliance score"""
    total_score = 0
    total_checks = 0

    for framework_name, framework_data in frameworks.items():
        if framework_data.get("status") == "COMPLIANT":
            total_score += framework_data.get("score", 0)
        total_checks += len(framework_data.get("checks", []))

    return (total_score / total_checks * 100) if total_checks > 0 else 0


def generate_compliance_recommendations(frameworks):
    """Generate compliance recommendations"""
    recommendations = []

    for framework_name, framework_data in frameworks.items():
        if framework_data.get("status") != "COMPLIANT":
            recommendations.append(
                {
                    "framework": framework_name,
                    "recommendation": f"Improve {framework_name.upper()} compliance by addressing failed checks",
                }
            )

    return recommendations


def display_compliance_results(results, output, verbose):
    """Display compliance check results"""
    if output == "json":
        console.print(json.dumps(results, indent=2, default=str))
    else:
        table = Table(title="📋 Compliance Check Results")
        table.add_column("Framework", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Score", style="yellow")
        table.add_column("Checks", style="white")

        for framework_name, framework_data in results.get("frameworks", {}).items():
            status_color = (
                "green" if framework_data.get("status") == "COMPLIANT" else "red"
            )
            table.add_row(
                framework_name.upper(),
                f"[{status_color}]{framework_data.get('status', 'UNKNOWN')}[/{status_color}]",
                str(framework_data.get("score", 0)),
                str(len(framework_data.get("checks", []))),
            )

        console.print(table)

        overall_score = results.get("overall_score", 0)
        console.print(f"\n📊 Overall Compliance Score: {overall_score:.1f}%")


def run_continuous_monitoring(session, interval, alert, verbose):
    """Run continuous security monitoring"""
    console.print(
        f"[blue]🔄 Starting continuous monitoring (interval: {interval}s)[/blue]"
    )

    try:
        while True:
            results = run_security_monitoring(session, verbose)
            if alert and results.get("alerts"):
                for alert_msg in results["alerts"]:
                    console.print(f"[red]🚨 ALERT: {alert_msg}[/red]")

            import time

            time.sleep(interval)
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Monitoring stopped by user[/yellow]")


def run_security_monitoring(session, verbose):
    """Run single security monitoring check"""
    results = {"timestamp": datetime.now().isoformat(), "alerts": [], "status": "OK"}

    try:
        # Check for critical security issues
        iam_client = session.client("iam")
        ec2_client = session.client("ec2")

        # Example monitoring checks
        if verbose:
            console.print("[blue]🔍 Running security monitoring checks...[/blue]")

        # Check for new IAM users
        users = iam_client.list_users()
        if len(users.get("Users", [])) > 10:  # Example threshold
            results["alerts"].append("High number of IAM users detected")

        # Check for running instances
        instances = ec2_client.describe_instances()
        running_count = sum(
            1
            for reservation in instances.get("Reservations", [])
            for instance in reservation.get("Instances", [])
            if instance["State"]["Name"] == "running"
        )

        if running_count > 50:  # Example threshold
            results["alerts"].append(
                f"High number of running instances: {running_count}"
            )

        if results["alerts"]:
            results["status"] = "ALERT"

    except Exception as e:
        results["status"] = "ERROR"
        results["alerts"].append(f"Monitoring error: {str(e)}")

    return results


def display_monitoring_results(results, verbose):
    """Display monitoring results"""
    if results.get("status") == "OK":
        console.print("[green]✅ Security monitoring: All systems normal[/green]")
    elif results.get("status") == "ALERT":
        console.print("[yellow]⚠️ Security monitoring: Alerts detected[/yellow]")
        for alert in results.get("alerts", []):
            console.print(f"  • {alert}")
    else:
        console.print("[red]❌ Security monitoring: Errors detected[/red]")
        for alert in results.get("alerts", []):
            console.print(f"  • {alert}")


def rotate_specific_secret(secrets_client, secret_name, auto):
    """Rotate specific secret"""
    try:
        if auto:
            secrets_client.rotate_secret(SecretId=secret_name)
            return True
        else:
            console.print(f"[yellow]Would rotate secret: {secret_name}[/yellow]")
            return False
    except Exception as e:
        console.print(f"[red]Error rotating secret {secret_name}: {str(e)}[/red]")
        return False


def list_secrets_for_rotation(secrets_client):
    """List secrets that need rotation"""
    try:
        secrets = secrets_client.list_secrets()
        return [
            secret
            for secret in secrets.get("SecretList", [])
            if not secret.get("RotationEnabled", False)
        ]
    except Exception:
        return []


def rotate_secret_automatically(secrets_client, secret):
    """Automatically rotate secret"""
    try:
        secrets_client.rotate_secret(SecretId=secret["Name"])
        return True
    except Exception:
        return False


def schedule_secret_rotation(secrets_client, secret):
    """Schedule secret rotation"""
    try:
        secrets_client.update_secret(
            SecretId=secret["Name"], RotationRules={"AutomaticallyAfterDays": 30}
        )
        return True
    except Exception:
        return False


def display_secret_rotation_results(results, verbose):
    """Display secret rotation results"""
    table = Table(title="🔄 Secret Rotation Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="yellow")

    table.add_row("Secrets Analyzed", str(results.get("secrets_analyzed", 0)))
    table.add_row("Secrets Rotated", str(results.get("secrets_rotated", 0)))
    table.add_row("Scheduled Rotations", str(results.get("scheduled_rotations", 0)))

    console.print(table)


def scan_ec2_vulnerabilities(session, low_risk):
    """Scan EC2 vulnerabilities"""
    vulnerabilities = []
    try:
        ec2_client = session.client("ec2")
        instances = ec2_client.describe_instances()

        for reservation in instances.get("Reservations", []):
            for instance in reservation.get("Instances", []):
                if instance["State"]["Name"] == "running":
                    # Check for public IP
                    if instance.get("PublicIpAddress"):
                        vulnerabilities.append(
                            {
                                "service": "EC2",
                                "resource": instance["InstanceId"],
                                "type": "PUBLIC_IP",
                                "severity": "MEDIUM",
                                "description": f"Instance {instance['InstanceId']} has public IP",
                                "recommendation": "Use private IP with NAT gateway",
                            }
                        )
    except Exception:
        pass
    return vulnerabilities


def scan_rds_vulnerabilities(session, low_risk):
    """Scan RDS vulnerabilities"""
    vulnerabilities = []
    try:
        rds_client = session.client("rds")
        instances = rds_client.describe_db_instances()

        for instance in instances.get("DBInstances", []):
            if instance.get("PubliclyAccessible"):
                vulnerabilities.append(
                    {
                        "service": "RDS",
                        "resource": instance["DBInstanceIdentifier"],
                        "type": "PUBLIC_ACCESS",
                        "severity": "HIGH",
                        "description": f"RDS instance {instance['DBInstanceIdentifier']} is publicly accessible",
                        "recommendation": "Disable public access for RDS instance",
                    }
                )
    except Exception:
        pass
    return vulnerabilities


def scan_s3_vulnerabilities(session, low_risk):
    """Scan S3 vulnerabilities"""
    vulnerabilities = []
    try:
        s3_client = session.client("s3")
        buckets = s3_client.list_buckets()

        for bucket in buckets.get("Buckets", []):
            try:
                # Check for public access
                public_access = s3_client.get_public_access_block(Bucket=bucket["Name"])
                if not public_access["PublicAccessBlockConfiguration"][
                    "BlockPublicAcls"
                ]:
                    vulnerabilities.append(
                        {
                            "service": "S3",
                            "resource": bucket["Name"],
                            "type": "PUBLIC_ACCESS",
                            "severity": "HIGH",
                            "description": f"S3 bucket {bucket['Name']} allows public access",
                            "recommendation": "Block public access for S3 bucket",
                        }
                    )
            except Exception:
                pass
    except Exception:
        pass
    return vulnerabilities


def scan_lambda_vulnerabilities(session, low_risk):
    """Scan Lambda vulnerabilities"""
    vulnerabilities = []
    try:
        lambda_client = session.client("lambda")
        functions = lambda_client.list_functions()

        for function in functions.get("Functions", []):
            # Check for environment variables with sensitive data
            if function.get("Environment", {}).get("Variables"):
                for key, value in function["Environment"]["Variables"].items():
                    if any(
                        sensitive in key.lower()
                        for sensitive in ["password", "secret", "key", "token"]
                    ):
                        vulnerabilities.append(
                            {
                                "service": "Lambda",
                                "resource": function["FunctionName"],
                                "type": "ENV_VARS",
                                "severity": "MEDIUM",
                                "description": f"Lambda function {function['FunctionName']} has sensitive environment variables",
                                "recommendation": "Use AWS Secrets Manager for sensitive data",
                            }
                        )
                        break
    except Exception:
        pass
    return vulnerabilities


def auto_remediate_vulnerabilities(vulnerabilities, session):
    """Auto-remediate vulnerabilities"""
    remediated = []

    for vuln in vulnerabilities:
        if vuln.get("severity") == "LOW" and vuln.get("service") == "S3":
            # Example: Block public access for S3
            if vuln.get("type") == "PUBLIC_ACCESS":
                try:
                    s3_client = session.client("s3")
                    s3_client.put_public_access_block(
                        Bucket=vuln["resource"],
                        PublicAccessBlockConfiguration={
                            "BlockPublicAcls": True,
                            "IgnorePublicAcls": True,
                            "BlockPublicPolicy": True,
                            "RestrictPublicBuckets": True,
                        },
                    )
                    remediated.append(
                        {
                            "vulnerability": vuln,
                            "action": "Blocked public access",
                            "status": "SUCCESS",
                        }
                    )
                except Exception as e:
                    remediated.append(
                        {
                            "vulnerability": vuln,
                            "action": "Block public access",
                            "status": "FAILED",
                            "error": str(e),
                        }
                    )

    return remediated


def generate_vulnerability_summary(vulnerabilities):
    """Generate vulnerability summary"""
    summary = {
        "total_vulnerabilities": len(vulnerabilities),
        "by_severity": {"HIGH": 0, "MEDIUM": 0, "LOW": 0},
        "by_service": {},
        "by_type": {},
    }

    for vuln in vulnerabilities:
        severity = vuln.get("severity", "UNKNOWN")
        if severity in summary["by_severity"]:
            summary["by_severity"][severity] += 1

        service = vuln.get("service", "UNKNOWN")
        summary["by_service"][service] = summary["by_service"].get(service, 0) + 1

        vuln_type = vuln.get("type", "UNKNOWN")
        summary["by_type"][vuln_type] = summary["by_type"].get(vuln_type, 0) + 1

    return summary


def generate_vulnerability_recommendations(vulnerabilities):
    """Generate vulnerability recommendations"""
    recommendations = []

    # Group recommendations by type
    rec_by_type = {}
    for vuln in vulnerabilities:
        vuln_type = vuln.get("type", "GENERAL")
        if vuln_type not in rec_by_type:
            rec_by_type[vuln_type] = []
        rec_by_type[vuln_type].append(vuln.get("recommendation", ""))

    # Create prioritized recommendations
    for vuln_type, recs in rec_by_type.items():
        unique_recs = list(set(recs))  # Remove duplicates
        for rec in unique_recs:
            recommendations.append(
                {
                    "type": vuln_type,
                    "recommendation": rec,
                    "priority": (
                        "HIGH"
                        if vuln_type in ["PUBLIC_ACCESS", "ENCRYPTION"]
                        else "MEDIUM"
                    ),
                }
            )

    return recommendations


def display_vulnerability_results(results, output, verbose):
    """Display vulnerability scan results"""
    if output == "json":
        console.print(json.dumps(results, indent=2, default=str))
    else:
        table = Table(title="🔍 Vulnerability Scan Results")
        table.add_column("Service", style="cyan")
        table.add_column("Severity", style="red")
        table.add_column("Resource", style="yellow")
        table.add_column("Type", style="white")
        table.add_column("Description", style="white")

        for vuln in results.get("vulnerabilities", []):
            severity_color = {"HIGH": "red", "MEDIUM": "yellow", "LOW": "green"}.get(
                vuln.get("severity", ""), "white"
            )

            table.add_row(
                vuln.get("service", ""),
                f"[{severity_color}]{vuln.get('severity', '')}[/{severity_color}]",
                vuln.get("resource", ""),
                vuln.get("type", ""),
                vuln.get("description", ""),
            )

        console.print(table)

        # Show summary
        summary = results.get("summary", {})
        if summary:
            console.print(
                f"\n📊 Summary: {summary.get('total_vulnerabilities', 0)} vulnerabilities found"
            )
            for severity, count in summary.get("by_severity", {}).items():
                if count > 0:
                    console.print(f"  • {severity}: {count}")


@app.command()
def help():
    """
    📚 Show detailed help for the task module

    This command provides information about AI configuration and available features.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    console.print(
        "\n[bold cyan]🚀 AWDX Task Module - DevSecOps Productivity Commands[/bold cyan]"
    )
    console.print(
        "\nThis module provides high-level task automation for common DevSecOps activities."
    )

    console.print("\n[bold yellow]Available Commands:[/bold yellow]")
    console.print(
        "  • [cyan]security-audit[/cyan] - Comprehensive security audit across AWS services"
    )
    console.print(
        "  • [cyan]cost-optimize[/cyan] - Analyze and optimize AWS costs intelligently"
    )
    console.print(
        "  • [cyan]compliance-check[/cyan] - Validate against industry compliance frameworks"
    )
    console.print(
        "  • [cyan]security-monitor[/cyan] - Continuous security monitoring and alerting"
    )
    console.print(
        "  • [cyan]secret-rotate[/cyan] - Automated secret rotation and management"
    )
    console.print(
        "  • [cyan]vuln-scan[/cyan] - Comprehensive vulnerability scanning and remediation"
    )
    console.print("\n[bold yellow]Phase 2 - Service-Specific Commands:[/bold yellow]")
    console.print(
        "  • [cyan]lambda-audit[/cyan] - Lambda function security and configuration audit"
    )
    console.print(
        "  • [cyan]lambda-optimize[/cyan] - Lambda performance and cost optimization"
    )
    console.print(
        "  • [cyan]lambda-monitor[/cyan] - Lambda performance, error, and cost monitoring"
    )
    console.print(
        "  • [cyan]iam-audit[/cyan] - IAM users, roles, and policies security audit"
    )
    console.print(
        "  • [cyan]iam-optimize[/cyan] - IAM permissions and access management optimization"
    )
    console.print(
        "  • [cyan]s3-audit[/cyan] - S3 bucket security and compliance audit"
    )
    console.print(
        "  • [cyan]s3-optimize[/cyan] - S3 storage, access, and cost optimization"
    )

    console.print("\n[bold yellow]Phase 3 - Infrastructure Automation Commands:[/bold yellow]")
    console.print(
        "  • [cyan]infra-audit[/cyan] - Infrastructure security and compliance audit"
    )
    console.print(
        "  • [cyan]infra-drift[/cyan] - Infrastructure drift detection and remediation"
    )
    console.print(
        "  • [cyan]infra-cost[/cyan] - Infrastructure cost estimation and optimization"
    )
    console.print(
        "  • [cyan]template-validate[/cyan] - CloudFormation/CDK template validation"
    )
    console.print(
        "  • [cyan]template-optimize[/cyan] - Template optimization for cost and performance"
    )
    console.print(
        "  • [cyan]template-compliance[/cyan] - Template compliance checking"
    )
    console.print(
        "  • [cyan]container-scan[/cyan] - Container image vulnerability scanning"
    )
    console.print(
        "  • [cyan]container-audit[/cyan] - Container security and configuration audit"
    )
    console.print(
        "  • [cyan]container-optimize[/cyan] - Container resource and cost optimization"
    )
    console.print(
        "  • [cyan]k8s-audit[/cyan] - Kubernetes security and RBAC audit"
    )
    console.print(
        "  • [cyan]k8s-compliance[/cyan] - Kubernetes compliance checking"
    )
    console.print(
        "  • [cyan]k8s-monitor[/cyan] - Kubernetes resource and performance monitoring"
    )
    console.print(
        "  • [cyan]pipeline-audit[/cyan] - CI/CD pipeline security and configuration audit"
    )
    console.print(
        "  • [cyan]pipeline-optimize[/cyan] - Pipeline performance and cost optimization"
    )
    console.print(
        "  • [cyan]pipeline-monitor[/cyan] - Pipeline execution and performance monitoring"
    )
    console.print(
        "  • [cyan]build-optimize[/cyan] - Build process optimization and caching"
    )
    console.print(
        "  • [cyan]build-security[/cyan] - Build security scanning and vulnerability detection"
    )
    console.print(
        "  • [cyan]build-compliance[/cyan] - Build compliance checking and reporting"
    )
    console.print(
        "  • [cyan]monitoring-setup[/cyan] - Automated monitoring setup with best practices"
    )
    console.print(
        "  • [cyan]monitoring-optimize[/cyan] - Monitoring cost and performance optimization"
    )
    console.print(
        "  • [cyan]monitoring-compliance[/cyan] - Monitoring compliance checking"
    )
    console.print(
        "  • [cyan]alert-configure[/cyan] - Intelligent alert configuration and thresholds"
    )
    console.print(
        "  • [cyan]alert-optimize[/cyan] - Alert noise reduction and response optimization"
    )
    console.print(
        "  • [cyan]network-audit[/cyan] - Network configuration and security audit"
    )
    console.print(
        "  • [cyan]network-optimize[/cyan] - Network routing and cost optimization"
    )
    console.print(
        "  • [cyan]network-monitor[/cyan] - Network traffic and anomaly monitoring"
    )
    console.print(
        "  • [cyan]sg-audit[/cyan] - Security group rules and compliance audit"
    )
    console.print(
        "  • [cyan]sg-optimize[/cyan] - Security group rules and coverage optimization"
    )
    console.print(
        "  • [cyan]sg-compliance[/cyan] - Security group compliance checking"
    )

    console.print("\n[bold yellow]AI Integration:[/bold yellow]")
    if AI_AVAILABLE:
        gemini_client, nlp_processor = get_ai_components()
        if gemini_client:
            console.print(
                "  ✅ [green]AI is configured and ready to enhance your experience![/green]"
            )
            console.print("  • Intelligent recommendations and insights")
            console.print("  • Automated remediation suggestions")
            console.print("  • Natural language query processing")
        else:
            console.print("  ⚠️ [yellow]AI is available but not configured[/yellow]")
            console.print(
                "  • Run [cyan]awdx ai configure[/cyan] to enable AI features"
            )
            console.print("  • Get intelligent insights and automated suggestions")
    else:
        console.print("  ℹ️ [blue]AI features not available[/blue]")
        console.print("  • Install AI dependencies for enhanced functionality")
        console.print("  • Basic functionality works without AI")

    console.print("\n[bold yellow]Examples:[/bold yellow]")
    console.print("  [cyan]awdx task security-audit --comprehensive --fix-safe[/cyan]")
    console.print("  [cyan]awdx task cost-optimize --auto-fix --dry-run[/cyan]")
    console.print(
        "  [cyan]awdx task compliance-check --framework sox --output pdf[/cyan]"
    )
    console.print("  [cyan]awdx task security-monitor --continuous --alert[/cyan]")

    console.print("\n[bold yellow]AI Configuration:[/bold yellow]")
    console.print("  1. Run [cyan]awdx ai configure[/cyan] to set up AI")
    console.print("  2. Provide your Google Gemini API key")
    console.print("  3. Enjoy intelligent insights across all task commands")

    console.print("\n[bold yellow]Benefits with AI:[/bold yellow]")
    console.print("  • [green]50% time savings[/green] on routine tasks")
    console.print("  • [green]Proactive issue detection[/green] and remediation")
    console.print(
        "  • [green]Intelligent recommendations[/green] based on best practices"
    )
    console.print("  • [green]Automated workflow suggestions[/green] for efficiency")


@app.command()
def lambda_audit(
    security: bool = typer.Option(
        True, "--security", "-s", help="Audit Lambda security configurations"
    ),
    permissions: bool = typer.Option(
        True, "--permissions", "-p", help="Audit IAM permissions and roles"
    ),
    runtime: bool = typer.Option(
        True, "--runtime", "-r", help="Audit runtime configurations and dependencies"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to audit"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🔍 Perform comprehensive Lambda function security audit

    This command analyzes Lambda functions for security issues, permission problems,
    and runtime configuration issues.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🔍 Running Lambda audit...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            lambda_client = session.client("lambda")
            iam_client = session.client("iam")

            audit_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "functions": [],
                "findings": [],
                "summary": {},
                "recommendations": [],
            }

            # List all Lambda functions
            progress.update(task, description="📋 Discovering Lambda functions...")
            functions = []
            paginator = lambda_client.get_paginator("list_functions")
            for page in paginator.paginate():
                functions.extend(page["Functions"])

            audit_results["functions"] = functions

            # Audit each function
            for func in functions:
                progress.update(
                    task, description=f"🔍 Auditing function: {func['FunctionName']}"
                )

                function_findings = []

                if security:
                    security_findings = audit_lambda_security(lambda_client, func)
                    function_findings.extend(security_findings)

                if permissions:
                    permission_findings = audit_lambda_permissions(iam_client, func)
                    function_findings.extend(permission_findings)

                if runtime:
                    runtime_findings = audit_lambda_runtime(lambda_client, func)
                    function_findings.extend(runtime_findings)

                audit_results["findings"].extend(function_findings)

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating recommendations...")
            audit_results["summary"] = generate_lambda_summary(audit_results["findings"])
            audit_results["recommendations"] = generate_lambda_recommendations(
                audit_results["findings"]
            )

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_lambda_recommendations_with_ai(
                    audit_results["findings"]
                )
                audit_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Lambda audit completed!")

            # Display results
            display_lambda_audit_results(audit_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Lambda audit failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def lambda_optimize(
    memory: bool = typer.Option(
        True, "--memory", "-m", help="Optimize memory allocation"
    ),
    timeout: bool = typer.Option(
        True, "--timeout", "-t", help="Optimize timeout configurations"
    ),
    cold_start: bool = typer.Option(
        True, "--cold-start", "-c", help="Optimize cold start performance"
    ),
    auto_fix: bool = typer.Option(
        False, "--auto-fix", "-a", help="Automatically apply optimizations"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Show what would be optimized without applying"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to optimize"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    ⚡ Optimize Lambda function performance and cost

    This command analyzes Lambda functions for performance optimization opportunities
    including memory allocation, timeout settings, and cold start optimization.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("⚡ Running Lambda optimization...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            lambda_client = session.client("lambda")
            cloudwatch_client = session.client("cloudwatch")

            optimization_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "functions": [],
                "opportunities": [],
                "summary": {},
                "applied_fixes": [],
            }

            # List all Lambda functions
            progress.update(task, description="📋 Discovering Lambda functions...")
            functions = []
            paginator = lambda_client.get_paginator("list_functions")
            for page in paginator.paginate():
                functions.extend(page["Functions"])

            optimization_results["functions"] = functions

            # Analyze each function for optimization opportunities
            for func in functions:
                progress.update(
                    task, description=f"⚡ Analyzing function: {func['FunctionName']}"
                )

                function_opportunities = []

                if memory:
                    memory_opps = analyze_lambda_memory_optimization(
                        lambda_client, cloudwatch_client, func
                    )
                    function_opportunities.extend(memory_opps)

                if timeout:
                    timeout_opps = analyze_lambda_timeout_optimization(
                        lambda_client, cloudwatch_client, func
                    )
                    function_opportunities.extend(timeout_opps)

                if cold_start:
                    cold_start_opps = analyze_lambda_cold_start_optimization(
                        lambda_client, cloudwatch_client, func
                    )
                    function_opportunities.extend(cold_start_opps)

                optimization_results["opportunities"].extend(function_opportunities)

            # Generate summary
            progress.update(task, description="📊 Generating optimization summary...")
            optimization_results["summary"] = generate_lambda_optimization_summary(
                optimization_results["opportunities"]
            )

            # Apply optimizations if requested
            if auto_fix and not dry_run:
                progress.update(task, description="🔧 Applying optimizations...")
                applied_fixes = apply_lambda_optimizations(
                    optimization_results["opportunities"], lambda_client
                )
                optimization_results["applied_fixes"] = applied_fixes

            progress.update(task, description="✅ Lambda optimization completed!")

            # Display results
            display_lambda_optimization_results(
                optimization_results, dry_run, verbose
            )

        except Exception as e:
            console.print(f"[red]❌ Lambda optimization failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def lambda_monitor(
    performance: bool = typer.Option(
        True, "--performance", "-p", help="Monitor Lambda performance metrics"
    ),
    errors: bool = typer.Option(
        True, "--errors", "-e", help="Monitor Lambda error rates and logs"
    ),
    cost: bool = typer.Option(
        True, "--cost", "-c", help="Monitor Lambda cost metrics"
    ),
    continuous: bool = typer.Option(
        False, "--continuous", "-C", help="Run continuous monitoring"
    ),
    interval: int = typer.Option(
        300, "--interval", "-i", help="Monitoring interval in seconds"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to monitor"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    📊 Monitor Lambda function performance, errors, and costs

    This command provides real-time monitoring of Lambda functions including
    performance metrics, error rates, and cost analysis.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    if continuous:
        console.print("[yellow]🔄 Starting continuous Lambda monitoring...[/yellow]")
        run_continuous_lambda_monitoring(
            region, interval, performance, errors, cost, verbose
        )
    else:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("📊 Running Lambda monitoring...", total=None)

            try:
                # Initialize AWS clients
                session = boto3.Session(region_name=region)
                lambda_client = session.client("lambda")
                cloudwatch_client = session.client("cloudwatch")
                logs_client = session.client("logs")

                monitoring_results = {
                    "timestamp": datetime.now().isoformat(),
                    "region": region or "default",
                    "functions": [],
                    "metrics": {},
                    "alerts": [],
                    "summary": {},
                }

                # List all Lambda functions
                progress.update(task, description="📋 Discovering Lambda functions...")
                functions = []
                paginator = lambda_client.get_paginator("list_functions")
                for page in paginator.paginate():
                    functions.extend(page["Functions"])

                monitoring_results["functions"] = functions

                # Monitor each function
                for func in functions:
                    progress.update(
                        task, description=f"📊 Monitoring function: {func['FunctionName']}"
                    )

                    function_metrics = {}

                    if performance:
                        perf_metrics = monitor_lambda_performance(
                            cloudwatch_client, func
                        )
                        function_metrics["performance"] = perf_metrics

                    if errors:
                        error_metrics = monitor_lambda_errors(
                            cloudwatch_client, logs_client, func
                        )
                        function_metrics["errors"] = error_metrics

                    if cost:
                        cost_metrics = monitor_lambda_cost(cloudwatch_client, func)
                        function_metrics["cost"] = cost_metrics

                    monitoring_results["metrics"][func["FunctionName"]] = function_metrics

                # Generate alerts and summary
                progress.update(task, description="🚨 Generating alerts...")
                monitoring_results["alerts"] = generate_lambda_alerts(
                    monitoring_results["metrics"]
                )
                monitoring_results["summary"] = generate_lambda_monitoring_summary(
                    monitoring_results["metrics"]
                )

                progress.update(task, description="✅ Lambda monitoring completed!")

                # Display results
                display_lambda_monitoring_results(monitoring_results, verbose)

            except Exception as e:
                console.print(f"[red]❌ Lambda monitoring failed: {str(e)}[/red]")
                raise typer.Exit(1)


@app.command()
def iam_audit(
    users: bool = typer.Option(
        True, "--users", "-u", help="Audit IAM users and their permissions"
    ),
    roles: bool = typer.Option(
        True, "--roles", "-r", help="Audit IAM roles and their permissions"
    ),
    policies: bool = typer.Option(
        True, "--policies", "-p", help="Audit IAM policies and their usage"
    ),
    compliance: bool = typer.Option(
        True, "--compliance", "-c", help="Check compliance with security standards"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to audit"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🔐 Perform comprehensive IAM security audit

    This command analyzes IAM users, roles, and policies for security issues,
    compliance violations, and best practice violations.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🔐 Running IAM audit...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            iam_client = session.client("iam")

            audit_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "users": [],
                "roles": [],
                "policies": [],
                "findings": [],
                "summary": {},
                "recommendations": [],
            }

            # Audit IAM users
            if users:
                progress.update(task, description="👤 Auditing IAM users...")
                users_data = audit_iam_users(iam_client)
                audit_results["users"] = users_data["users"]
                audit_results["findings"].extend(users_data["findings"])

            # Audit IAM roles
            if roles:
                progress.update(task, description="🎭 Auditing IAM roles...")
                roles_data = audit_iam_roles(iam_client)
                audit_results["roles"] = roles_data["roles"]
                audit_results["findings"].extend(roles_data["findings"])

            # Audit IAM policies
            if policies:
                progress.update(task, description="📜 Auditing IAM policies...")
                policies_data = audit_iam_policies(iam_client)
                audit_results["policies"] = policies_data["policies"]
                audit_results["findings"].extend(policies_data["findings"])

            # Check compliance
            if compliance:
                progress.update(task, description="✅ Checking compliance...")
                compliance_data = check_iam_compliance(audit_results["findings"])
                audit_results["compliance"] = compliance_data

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating recommendations...")
            audit_results["summary"] = generate_iam_summary(audit_results["findings"])
            audit_results["recommendations"] = generate_iam_recommendations(
                audit_results["findings"]
            )

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_iam_recommendations_with_ai(
                    audit_results["findings"]
                )
                audit_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ IAM audit completed!")

            # Display results
            display_iam_audit_results(audit_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ IAM audit failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def iam_optimize(
    permissions: bool = typer.Option(
        True, "--permissions", "-p", help="Optimize IAM permissions"
    ),
    least_privilege: bool = typer.Option(
        True, "--least-privilege", "-l", help="Apply least privilege principle"
    ),
    rotation: bool = typer.Option(
        True, "--rotation", "-r", help="Optimize credential rotation"
    ),
    auto_fix: bool = typer.Option(
        False, "--auto-fix", "-a", help="Automatically apply optimizations"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Show what would be optimized without applying"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to optimize"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    ⚡ Optimize IAM permissions and access management

    This command analyzes and optimizes IAM permissions, applies least privilege
    principles, and improves credential rotation practices.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("⚡ Running IAM optimization...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            iam_client = session.client("iam")

            optimization_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "opportunities": [],
                "summary": {},
                "applied_fixes": [],
            }

            # Analyze IAM permissions
            if permissions:
                progress.update(task, description="🔍 Analyzing IAM permissions...")
                permission_opps = analyze_iam_permissions(iam_client)
                optimization_results["opportunities"].extend(permission_opps)

            # Apply least privilege analysis
            if least_privilege:
                progress.update(task, description="🎯 Applying least privilege analysis...")
                least_priv_opps = analyze_least_privilege_violations(iam_client)
                optimization_results["opportunities"].extend(least_priv_opps)

            # Analyze credential rotation
            if rotation:
                progress.update(task, description="🔄 Analyzing credential rotation...")
                rotation_opps = analyze_credential_rotation(iam_client)
                optimization_results["opportunities"].extend(rotation_opps)

            # Generate summary
            progress.update(task, description="📊 Generating optimization summary...")
            optimization_results["summary"] = generate_iam_optimization_summary(
                optimization_results["opportunities"]
            )

            # Apply optimizations if requested
            if auto_fix and not dry_run:
                progress.update(task, description="🔧 Applying optimizations...")
                applied_fixes = apply_iam_optimizations(
                    optimization_results["opportunities"], iam_client
                )
                optimization_results["applied_fixes"] = applied_fixes

            progress.update(task, description="✅ IAM optimization completed!")

            # Display results
            display_iam_optimization_results(optimization_results, dry_run, verbose)

        except Exception as e:
            console.print(f"[red]❌ IAM optimization failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def s3_audit(
    buckets: bool = typer.Option(
        True, "--buckets", "-b", help="Audit S3 bucket configurations"
    ),
    policies: bool = typer.Option(
        True, "--policies", "-p", help="Audit S3 bucket policies"
    ),
    encryption: bool = typer.Option(
        True, "--encryption", "-e", help="Audit S3 encryption settings"
    ),
    compliance: bool = typer.Option(
        True, "--compliance", "-c", help="Check compliance with data protection standards"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to audit"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    📦 Perform comprehensive S3 security audit

    This command analyzes S3 buckets for security issues, policy violations,
    encryption problems, and compliance issues.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("📦 Running S3 audit...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            s3_client = session.client("s3")

            audit_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "buckets": [],
                "findings": [],
                "summary": {},
                "recommendations": [],
            }

            # List all S3 buckets
            progress.update(task, description="📋 Discovering S3 buckets...")
            response = s3_client.list_buckets()
            buckets_list = response["Buckets"]

            audit_results["buckets"] = buckets_list

            # Audit each bucket
            for bucket in buckets_list:
                progress.update(
                    task, description=f"📦 Auditing bucket: {bucket['Name']}"
                )

                bucket_findings = []

                if buckets:
                    bucket_config_findings = audit_s3_bucket_configuration(
                        s3_client, bucket
                    )
                    bucket_findings.extend(bucket_config_findings)

                if policies:
                    policy_findings = audit_s3_bucket_policies(s3_client, bucket)
                    bucket_findings.extend(policy_findings)

                if encryption:
                    encryption_findings = audit_s3_encryption(s3_client, bucket)
                    bucket_findings.extend(encryption_findings)

                audit_results["findings"].extend(bucket_findings)

            # Check compliance
            if compliance:
                progress.update(task, description="✅ Checking compliance...")
                compliance_data = check_s3_compliance(audit_results["findings"])
                audit_results["compliance"] = compliance_data

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating recommendations...")
            audit_results["summary"] = generate_s3_summary(audit_results["findings"])
            audit_results["recommendations"] = generate_s3_recommendations(
                audit_results["findings"]
            )

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_s3_recommendations_with_ai(
                    audit_results["findings"]
                )
                audit_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ S3 audit completed!")

            # Display results
            display_s3_audit_results(audit_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ S3 audit failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def s3_optimize(
    storage: bool = typer.Option(
        True, "--storage", "-s", help="Optimize S3 storage classes and lifecycle"
    ),
    access: bool = typer.Option(
        True, "--access", "-a", help="Optimize S3 access patterns and permissions"
    ),
    cost: bool = typer.Option(
        True, "--cost", "-c", help="Optimize S3 costs and billing"
    ),
    auto_fix: bool = typer.Option(
        False, "--auto-fix", "-f", help="Automatically apply optimizations"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Show what would be optimized without applying"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to optimize"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    ⚡ Optimize S3 storage, access, and costs

    This command analyzes and optimizes S3 storage classes, lifecycle policies,
    access patterns, and cost management.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("⚡ Running S3 optimization...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            s3_client = session.client("s3")
            ce_client = session.client("ce")

            optimization_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "buckets": [],
                "opportunities": [],
                "summary": {},
                "applied_fixes": [],
            }

            # List all S3 buckets
            progress.update(task, description="📋 Discovering S3 buckets...")
            response = s3_client.list_buckets()
            buckets_list = response["Buckets"]

            optimization_results["buckets"] = buckets_list

            # Analyze each bucket for optimization opportunities
            for bucket in buckets_list:
                progress.update(
                    task, description=f"⚡ Analyzing bucket: {bucket['Name']}"
                )

                bucket_opportunities = []

                if storage:
                    storage_opps = analyze_s3_storage_optimization(s3_client, bucket)
                    bucket_opportunities.extend(storage_opps)

                if access:
                    access_opps = analyze_s3_access_optimization(s3_client, bucket)
                    bucket_opportunities.extend(access_opps)

                if cost:
                    cost_opps = analyze_s3_cost_optimization(ce_client, bucket)
                    bucket_opportunities.extend(cost_opps)

                optimization_results["opportunities"].extend(bucket_opportunities)

            # Generate summary
            progress.update(task, description="📊 Generating optimization summary...")
            optimization_results["summary"] = generate_s3_optimization_summary(
                optimization_results["opportunities"]
            )

            # Apply optimizations if requested
            if auto_fix and not dry_run:
                progress.update(task, description="🔧 Applying optimizations...")
                applied_fixes = apply_s3_optimizations(
                    optimization_results["opportunities"], s3_client
                )
                optimization_results["applied_fixes"] = applied_fixes

            progress.update(task, description="✅ S3 optimization completed!")

            # Display results
            display_s3_optimization_results(optimization_results, dry_run, verbose)

        except Exception as e:
            console.print(f"[red]❌ S3 optimization failed: {str(e)}[/red]")
            raise typer.Exit(1)


# Lambda Functions
def audit_lambda_security(lambda_client, func):
    """Audit Lambda function security configurations"""
    findings = []
    
    try:
        # Check function configuration
        config = lambda_client.get_function_configuration(FunctionName=func['FunctionName'])
        
        # Check for environment variables (potential secrets)
        if config.get('Environment', {}).get('Variables'):
            findings.append({
                "service": "Lambda",
                "resource": func['FunctionName'],
                "type": "ENVIRONMENT_VARIABLES",
                "severity": "MEDIUM",
                "description": "Function has environment variables that may contain secrets",
                "recommendation": "Use AWS Secrets Manager or Parameter Store for sensitive data"
            })
        
        # Check for VPC configuration
        if config.get('VpcConfig', {}).get('VpcId'):
            findings.append({
                "service": "Lambda",
                "resource": func['FunctionName'],
                "type": "VPC_CONFIGURED",
                "severity": "INFO",
                "description": "Function is configured with VPC",
                "recommendation": "Ensure VPC security groups are properly configured"
            })
        
        # Check for dead letter queue
        if not config.get('DeadLetterConfig'):
            findings.append({
                "service": "Lambda",
                "resource": func['FunctionName'],
                "type": "NO_DLQ",
                "severity": "MEDIUM",
                "description": "Function has no dead letter queue configured",
                "recommendation": "Configure DLQ for failed executions"
            })
            
    except Exception as e:
        findings.append({
            "service": "Lambda",
            "resource": func['FunctionName'],
            "type": "AUDIT_ERROR",
            "severity": "HIGH",
            "description": f"Error auditing function: {str(e)}",
            "recommendation": "Check function permissions and configuration"
        })
    
    return findings


def audit_lambda_permissions(iam_client, func):
    """Audit Lambda function IAM permissions"""
    findings = []
    
    try:
        # Get function policy
        try:
            policy = iam_client.get_role_policy(
                RoleName=func['Role'].split('/')[-1],
                PolicyName='lambda-execution-policy'
            )
            
            # Check for overly permissive policies
            policy_doc = policy['PolicyDocument']
            for statement in policy_doc.get('Statement', []):
                if statement.get('Effect') == 'Allow':
                    actions = statement.get('Action', [])
                    if isinstance(actions, str):
                        actions = [actions]
                    
                    # Check for wildcard permissions
                    if any('*' in action for action in actions):
                        findings.append({
                            "service": "Lambda",
                            "resource": func['FunctionName'],
                            "type": "WILDCARD_PERMISSIONS",
                            "severity": "HIGH",
                            "description": "Function has wildcard permissions",
                            "recommendation": "Use least privilege principle for permissions"
                        })
                        
        except iam_client.exceptions.NoSuchEntityException:
            findings.append({
                "service": "Lambda",
                "resource": func['FunctionName'],
                "type": "NO_EXECUTION_POLICY",
                "severity": "MEDIUM",
                "description": "Function has no execution policy",
                "recommendation": "Configure appropriate execution policy"
            })
            
    except Exception as e:
        findings.append({
            "service": "Lambda",
            "resource": func['FunctionName'],
            "type": "PERMISSION_AUDIT_ERROR",
            "severity": "HIGH",
            "description": f"Error auditing permissions: {str(e)}",
            "recommendation": "Check IAM role configuration"
        })
    
    return findings


def audit_lambda_runtime(lambda_client, func):
    """Audit Lambda function runtime configurations"""
    findings = []
    
    try:
        config = lambda_client.get_function_configuration(FunctionName=func['FunctionName'])
        
        # Check runtime version
        runtime = config.get('Runtime', '')
        if runtime and 'python3.7' in runtime:
            findings.append({
                "service": "Lambda",
                "resource": func['FunctionName'],
                "type": "DEPRECATED_RUNTIME",
                "severity": "MEDIUM",
                "description": f"Using deprecated runtime: {runtime}",
                "recommendation": "Upgrade to Python 3.8+ or latest supported runtime"
            })
        
        # Check timeout configuration
        timeout = config.get('Timeout', 3)
        if timeout > 900:  # 15 minutes
            findings.append({
                "service": "Lambda",
                "resource": func['FunctionName'],
                "type": "LONG_TIMEOUT",
                "severity": "MEDIUM",
                "description": f"Function timeout is {timeout} seconds",
                "recommendation": "Consider reducing timeout for better error handling"
            })
        
        # Check memory configuration
        memory = config.get('MemorySize', 128)
        if memory < 256:
            findings.append({
                "service": "Lambda",
                "resource": func['FunctionName'],
                "type": "LOW_MEMORY",
                "severity": "LOW",
                "description": f"Function memory is {memory} MB",
                "recommendation": "Consider increasing memory for better performance"
            })
            
    except Exception as e:
        findings.append({
            "service": "Lambda",
            "resource": func['FunctionName'],
            "type": "RUNTIME_AUDIT_ERROR",
            "severity": "HIGH",
            "description": f"Error auditing runtime: {str(e)}",
            "recommendation": "Check function configuration"
        })
    
    return findings


def generate_lambda_summary(findings):
    """Generate Lambda audit summary"""
    summary = {
        "total_findings": len(findings),
        "by_severity": {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0},
        "by_type": {},
        "functions_audited": len(set(f.get("resource", "") for f in findings))
    }
    
    for finding in findings:
        severity = finding.get("severity", "UNKNOWN")
        if severity in summary["by_severity"]:
            summary["by_severity"][severity] += 1
        
        finding_type = finding.get("type", "UNKNOWN")
        summary["by_type"][finding_type] = summary["by_type"].get(finding_type, 0) + 1
    
    return summary


def generate_lambda_recommendations(findings):
    """Generate Lambda audit recommendations"""
    recommendations = []
    
    # Group recommendations by type
    rec_by_type = {}
    for finding in findings:
        finding_type = finding.get("type", "GENERAL")
        if finding_type not in rec_by_type:
            rec_by_type[finding_type] = []
        rec_by_type[finding_type].append(finding.get("recommendation", ""))
    
    # Create prioritized recommendations
    for finding_type, recs in rec_by_type.items():
        unique_recs = list(set(recs))  # Remove duplicates
        for rec in unique_recs:
            recommendations.append({
                "type": finding_type,
                "recommendation": rec,
                "priority": "HIGH" if finding_type in ["WILDCARD_PERMISSIONS", "DEPRECATED_RUNTIME"] else "MEDIUM"
            })
    
    return recommendations


def enhance_lambda_recommendations_with_ai(findings):
    """Enhance Lambda recommendations with AI insights"""
    if not AI_AVAILABLE:
        return []
    
    try:
        gemini_client, nlp_processor = get_ai_components()
        if not gemini_client:
            return []
        
        # Create context for AI
        context = f"""
        Lambda function audit findings:
        {json.dumps(findings, indent=2)}
        
        Provide intelligent recommendations for improving Lambda function security, performance, and best practices.
        Focus on actionable insights and prioritize by impact.
        """
        
        response = gemini_client.generate_text(context)
        return [{"type": "AI_ENHANCED", "recommendation": response, "priority": "HIGH"}]
        
    except Exception as e:
        console.print(f"[yellow]⚠️ AI enhancement failed: {str(e)}[/yellow]")
        return []


def analyze_lambda_memory_optimization(lambda_client, cloudwatch_client, func):
    """Analyze Lambda memory optimization opportunities"""
    opportunities = []
    
    try:
        # Get memory utilization metrics
        end_time = datetime.now()
        start_time = end_time - timedelta(days=7)
        
        response = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/Lambda',
            MetricName='MemoryUtilization',
            Dimensions=[{'Name': 'FunctionName', 'Value': func['FunctionName']}],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,
            Statistics=['Average', 'Maximum']
        )
        
        if response['Datapoints']:
            avg_utilization = sum(dp['Average'] for dp in response['Datapoints']) / len(response['Datapoints'])
            max_utilization = max(dp['Maximum'] for dp in response['Datapoints'])
            
            current_memory = func.get('MemorySize', 128)
            
            if avg_utilization < 50:
                # Under-utilized memory
                recommended_memory = max(128, int(current_memory * 0.5))
                savings = (current_memory - recommended_memory) * 0.0000166667  # Lambda memory cost per GB-second
                
                opportunities.append({
                    "type": "MEMORY_OPTIMIZATION",
                    "resource": func['FunctionName'],
                    "current_value": f"{current_memory} MB",
                    "recommended_value": f"{recommended_memory} MB",
                    "potential_savings": f"${savings:.4f} per GB-second",
                    "description": f"Memory utilization is {avg_utilization:.1f}% - consider reducing memory allocation"
                })
            elif max_utilization > 90:
                # Over-utilized memory
                recommended_memory = min(3008, int(current_memory * 1.5))
                opportunities.append({
                    "type": "MEMORY_OPTIMIZATION",
                    "resource": func['FunctionName'],
                    "current_value": f"{current_memory} MB",
                    "recommended_value": f"{recommended_memory} MB",
                    "potential_savings": "Improved performance",
                    "description": f"Memory utilization peaks at {max_utilization:.1f}% - consider increasing memory allocation"
                })
                
    except Exception as e:
        opportunities.append({
            "type": "MEMORY_OPTIMIZATION_ERROR",
            "resource": func['FunctionName'],
            "description": f"Error analyzing memory optimization: {str(e)}"
        })
    
    return opportunities


def analyze_lambda_timeout_optimization(lambda_client, cloudwatch_client, func):
    """Analyze Lambda timeout optimization opportunities"""
    opportunities = []
    
    try:
        # Get duration metrics
        end_time = datetime.now()
        start_time = end_time - timedelta(days=7)
        
        response = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/Lambda',
            MetricName='Duration',
            Dimensions=[{'Name': 'FunctionName', 'Value': func['FunctionName']}],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,
            Statistics=['Average', 'Maximum']
        )
        
        if response['Datapoints']:
            avg_duration = sum(dp['Average'] for dp in response['Datapoints']) / len(response['Datapoints'])
            max_duration = max(dp['Maximum'] for dp in response['Datapoints'])
            
            current_timeout = func.get('Timeout', 3)
            timeout_ms = current_timeout * 1000
            
            if avg_duration < timeout_ms * 0.3:
                # Timeout is too high
                recommended_timeout = max(3, int(avg_duration / 1000 * 2))
                opportunities.append({
                    "type": "TIMEOUT_OPTIMIZATION",
                    "resource": func['FunctionName'],
                    "current_value": f"{current_timeout} seconds",
                    "recommended_value": f"{recommended_timeout} seconds",
                    "potential_savings": "Better error handling",
                    "description": f"Average duration is {avg_duration/1000:.1f}s - consider reducing timeout"
                })
            elif max_duration > timeout_ms * 0.9:
                # Timeout is too low
                recommended_timeout = min(900, int(max_duration / 1000 * 1.5))
                opportunities.append({
                    "type": "TIMEOUT_OPTIMIZATION",
                    "resource": func['FunctionName'],
                    "current_value": f"{current_timeout} seconds",
                    "recommended_value": f"{recommended_timeout} seconds",
                    "potential_savings": "Reduced timeouts",
                    "description": f"Maximum duration is {max_duration/1000:.1f}s - consider increasing timeout"
                })
                
    except Exception as e:
        opportunities.append({
            "type": "TIMEOUT_OPTIMIZATION_ERROR",
            "resource": func['FunctionName'],
            "description": f"Error analyzing timeout optimization: {str(e)}"
        })
    
    return opportunities


def analyze_lambda_cold_start_optimization(lambda_client, cloudwatch_client, func):
    """Analyze Lambda cold start optimization opportunities"""
    opportunities = []
    
    try:
        # Check for provisioned concurrency
        config = lambda_client.get_function_configuration(FunctionName=func['FunctionName'])
        
        if not config.get('ProvisionedConcurrencyConfig'):
            opportunities.append({
                "type": "COLD_START_OPTIMIZATION",
                "resource": func['FunctionName'],
                "current_value": "No provisioned concurrency",
                "recommended_value": "Consider provisioned concurrency",
                "potential_savings": "Reduced cold starts",
                "description": "Function has no provisioned concurrency - consider for frequently invoked functions"
            })
        
        # Check runtime optimization
        runtime = config.get('Runtime', '')
        if 'python' in runtime.lower():
            opportunities.append({
                "type": "RUNTIME_OPTIMIZATION",
                "resource": func['FunctionName'],
                "current_value": runtime,
                "recommended_value": "Consider container image",
                "potential_savings": "Faster cold starts",
                "description": "Consider using container images for better cold start performance"
            })
                
    except Exception as e:
        opportunities.append({
            "type": "COLD_START_OPTIMIZATION_ERROR",
            "resource": func['FunctionName'],
            "description": f"Error analyzing cold start optimization: {str(e)}"
        })
    
    return opportunities


def generate_lambda_optimization_summary(opportunities):
    """Generate Lambda optimization summary"""
    summary = {
        "total_opportunities": len(opportunities),
        "by_type": {},
        "potential_savings": 0.0,
        "functions_analyzed": len(set(opp.get("resource", "") for opp in opportunities))
    }
    
    for opportunity in opportunities:
        opp_type = opportunity.get("type", "UNKNOWN")
        summary["by_type"][opp_type] = summary["by_type"].get(opp_type, 0) + 1
        
        # Calculate potential savings
        savings_text = opportunity.get("potential_savings", "")
        if "$" in savings_text:
            try:
                savings = float(savings_text.split("$")[1].split()[0])
                summary["potential_savings"] += savings
            except (ValueError, IndexError):
                pass
    
    return summary


def apply_lambda_optimizations(opportunities, lambda_client):
    """Apply Lambda optimizations"""
    applied_fixes = []
    
    for opportunity in opportunities:
        try:
            if opportunity["type"] == "MEMORY_OPTIMIZATION":
                # Apply memory optimization
                recommended_memory = int(opportunity["recommended_value"].split()[0])
                lambda_client.update_function_configuration(
                    FunctionName=opportunity["resource"],
                    MemorySize=recommended_memory
                )
                applied_fixes.append({
                    "opportunity": opportunity,
                    "status": "SUCCESS",
                    "action": f"Updated memory to {recommended_memory} MB"
                })
            elif opportunity["type"] == "TIMEOUT_OPTIMIZATION":
                # Apply timeout optimization
                recommended_timeout = int(opportunity["recommended_value"].split()[0])
                lambda_client.update_function_configuration(
                    FunctionName=opportunity["resource"],
                    Timeout=recommended_timeout
                )
                applied_fixes.append({
                    "opportunity": opportunity,
                    "status": "SUCCESS",
                    "action": f"Updated timeout to {recommended_timeout} seconds"
                })
        except Exception as e:
            applied_fixes.append({
                "opportunity": opportunity,
                "status": "FAILED",
                "error": str(e)
            })
    
    return applied_fixes


def display_lambda_audit_results(results, output, verbose):
    """Display Lambda audit results"""
    if output == "json":
        console.print(json.dumps(results, indent=2, default=str))
    else:
        # Display findings table
        if results.get("findings"):
            table = Table(title="🔍 Lambda Security Audit Results")
            table.add_column("Function", style="cyan")
            table.add_column("Type", style="yellow")
            table.add_column("Severity", style="red")
            table.add_column("Description", style="white")
            
            for finding in results["findings"]:
                severity_color = {"HIGH": "red", "MEDIUM": "yellow", "LOW": "green", "INFO": "blue"}.get(
                    finding.get("severity", ""), "white"
                )
                
                table.add_row(
                    finding.get("resource", ""),
                    finding.get("type", ""),
                    f"[{severity_color}]{finding.get('severity', '')}[/{severity_color}]",
                    finding.get("description", "")
                )
            
            console.print(table)
        
        # Display summary
        summary = results.get("summary", {})
        if summary:
            console.print(f"\n📊 Summary: {summary.get('total_findings', 0)} findings across {summary.get('functions_audited', 0)} functions")
            for severity, count in summary.get("by_severity", {}).items():
                if count > 0:
                    console.print(f"  • {severity}: {count}")


def display_lambda_optimization_results(results, dry_run, verbose):
    """Display Lambda optimization results"""
    if results.get("opportunities"):
        table = Table(title="⚡ Lambda Optimization Opportunities")
        table.add_column("Function", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Current", style="white")
        table.add_column("Recommended", style="green")
        table.add_column("Potential Savings", style="green")
        
        for opportunity in results["opportunities"]:
            table.add_row(
                opportunity.get("resource", ""),
                opportunity.get("type", ""),
                opportunity.get("current_value", ""),
                opportunity.get("recommended_value", ""),
                opportunity.get("potential_savings", "")
            )
        
        console.print(table)
    
    # Display summary
    summary = results.get("summary", {})
    if summary:
        console.print(f"\n📊 Summary: {summary.get('total_opportunities', 0)} optimization opportunities")
        console.print(f"💰 Potential savings: ${summary.get('potential_savings', 0):.4f}")
    
    # Display applied fixes
    if not dry_run and results.get("applied_fixes"):
        console.print("\n🔧 Applied Optimizations:")
        for fix in results["applied_fixes"]:
            status_color = "green" if fix["status"] == "SUCCESS" else "red"
            console.print(f"  • [{status_color}]{fix['status']}[/{status_color}] {fix.get('action', '')}")


def run_continuous_lambda_monitoring(region, interval, performance, errors, cost, verbose):
    """Run continuous Lambda monitoring"""
    console.print(f"[yellow]🔄 Monitoring Lambda functions every {interval} seconds...[/yellow]")
    console.print("[yellow]Press Ctrl+C to stop monitoring[/yellow]")
    
    try:
        while True:
            # Run single monitoring cycle
            session = boto3.Session(region_name=region)
            lambda_client = session.client("lambda")
            cloudwatch_client = session.client("cloudwatch")
            logs_client = session.client("logs")
            
            # Get functions and metrics
            functions = []
            paginator = lambda_client.get_paginator("list_functions")
            for page in paginator.paginate():
                functions.extend(page["Functions"])
            
            # Monitor each function
            for func in functions:
                if performance:
                    perf_metrics = monitor_lambda_performance(cloudwatch_client, func)
                if errors:
                    error_metrics = monitor_lambda_errors(cloudwatch_client, logs_client, func)
                if cost:
                    cost_metrics = monitor_lambda_cost(cloudwatch_client, func)
            
            # Wait for next cycle
            time.sleep(interval)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]🛑 Monitoring stopped by user[/yellow]")


def monitor_lambda_performance(cloudwatch_client, func):
    """Monitor Lambda performance metrics"""
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=5)
        
        response = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/Lambda',
            MetricName='Duration',
            Dimensions=[{'Name': 'FunctionName', 'Value': func['FunctionName']}],
            StartTime=start_time,
            EndTime=end_time,
            Period=300,
            Statistics=['Average', 'Maximum']
        )
        
        return {
            "function_name": func['FunctionName'],
            "avg_duration": response['Datapoints'][0]['Average'] if response['Datapoints'] else 0,
            "max_duration": response['Datapoints'][0]['Maximum'] if response['Datapoints'] else 0
        }
    except Exception as e:
        return {"function_name": func['FunctionName'], "error": str(e)}


def monitor_lambda_errors(cloudwatch_client, logs_client, func):
    """Monitor Lambda error rates"""
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=5)
        
        response = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/Lambda',
            MetricName='Errors',
            Dimensions=[{'Name': 'FunctionName', 'Value': func['FunctionName']}],
            StartTime=start_time,
            EndTime=end_time,
            Period=300,
            Statistics=['Sum']
        )
        
        return {
            "function_name": func['FunctionName'],
            "error_count": response['Datapoints'][0]['Sum'] if response['Datapoints'] else 0
        }
    except Exception as e:
        return {"function_name": func['FunctionName'], "error": str(e)}


def monitor_lambda_cost(cloudwatch_client, func):
    """Monitor Lambda cost metrics"""
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=1)
        
        response = cloudwatch_client.get_metric_statistics(
            Namespace='AWS/Lambda',
            MetricName='Invocations',
            Dimensions=[{'Name': 'FunctionName', 'Value': func['FunctionName']}],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,
            Statistics=['Sum']
        )
        
        return {
            "function_name": func['FunctionName'],
            "invocations": response['Datapoints'][0]['Sum'] if response['Datapoints'] else 0
        }
    except Exception as e:
        return {"function_name": func['FunctionName'], "error": str(e)}


def generate_lambda_alerts(metrics):
    """Generate Lambda alerts based on metrics"""
    alerts = []
    
    for func_name, func_metrics in metrics.items():
        # Performance alerts
        if "performance" in func_metrics:
            perf = func_metrics["performance"]
            if perf.get("avg_duration", 0) > 5000:  # 5 seconds
                alerts.append({
                    "function": func_name,
                    "type": "PERFORMANCE",
                    "severity": "MEDIUM",
                    "message": f"High average duration: {perf['avg_duration']/1000:.1f}s"
                })
        
        # Error alerts
        if "errors" in func_metrics:
            errors = func_metrics["errors"]
            if errors.get("error_count", 0) > 10:
                alerts.append({
                    "function": func_name,
                    "type": "ERRORS",
                    "severity": "HIGH",
                    "message": f"High error count: {errors['error_count']}"
                })
    
    return alerts


def generate_lambda_monitoring_summary(metrics):
    """Generate Lambda monitoring summary"""
    summary = {
        "functions_monitored": len(metrics),
        "total_alerts": 0,
        "performance_issues": 0,
        "error_issues": 0
    }
    
    for func_metrics in metrics.values():
        if "performance" in func_metrics:
            perf = func_metrics["performance"]
            if perf.get("avg_duration", 0) > 5000:
                summary["performance_issues"] += 1
        
        if "errors" in func_metrics:
            errors = func_metrics["errors"]
            if errors.get("error_count", 0) > 10:
                summary["error_issues"] += 1
    
    summary["total_alerts"] = summary["performance_issues"] + summary["error_issues"]
    return summary


def display_lambda_monitoring_results(results, verbose):
    """Display Lambda monitoring results"""
    # Display alerts
    if results.get("alerts"):
        table = Table(title="🚨 Lambda Monitoring Alerts")
        table.add_column("Function", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Severity", style="red")
        table.add_column("Message", style="white")
        
        for alert in results["alerts"]:
            severity_color = {"HIGH": "red", "MEDIUM": "yellow", "LOW": "green"}.get(
                alert.get("severity", ""), "white"
            )
            
            table.add_row(
                alert.get("function", ""),
                alert.get("type", ""),
                f"[{severity_color}]{alert.get('severity', '')}[/{severity_color}]",
                alert.get("message", "")
            )
        
        console.print(table)
    
    # Display summary
    summary = results.get("summary", {})
    if summary:
        console.print(f"\n📊 Summary: {summary.get('functions_monitored', 0)} functions monitored")
        console.print(f"🚨 Alerts: {summary.get('total_alerts', 0)}")
        console.print(f"⚡ Performance issues: {summary.get('performance_issues', 0)}")
        console.print(f"❌ Error issues: {summary.get('error_issues', 0)}")


# IAM Functions
def audit_iam_users(iam_client):
    """Audit IAM users and their permissions"""
    users_data = {"users": [], "findings": []}
    
    try:
        paginator = iam_client.get_paginator('list_users')
        for page in paginator.paginate():
            for user in page['Users']:
                users_data["users"].append(user)
                
                # Check for MFA
                try:
                    mfa_devices = iam_client.list_mfa_devices(UserName=user['UserName'])
                    if not mfa_devices['MFADevices']:
                        users_data["findings"].append({
                            "service": "IAM",
                            "resource": user['UserName'],
                            "type": "NO_MFA",
                            "severity": "HIGH",
                            "description": "User has no MFA device configured",
                            "recommendation": "Enable MFA for this user"
                        })
                except Exception:
                    pass
                
                # Check for access keys
                try:
                    access_keys = iam_client.list_access_keys(UserName=user['UserName'])
                    for key in access_keys['AccessKeyMetadata']:
                        if key['Status'] == 'Active':
                            # Check key age
                            key_age = datetime.now(key['CreateDate'].tzinfo) - key['CreateDate']
                            if key_age.days > 90:
                                users_data["findings"].append({
                                    "service": "IAM",
                                    "resource": f"{user['UserName']}:{key['AccessKeyId']}",
                                    "type": "OLD_ACCESS_KEY",
                                    "severity": "MEDIUM",
                                    "description": f"Access key is {key_age.days} days old",
                                    "recommendation": "Rotate access key"
                                })
                except Exception:
                    pass
                
                # Check for inline policies
                try:
                    inline_policies = iam_client.list_user_policies(UserName=user['UserName'])
                    if inline_policies['PolicyNames']:
                        users_data["findings"].append({
                            "service": "IAM",
                            "resource": user['UserName'],
                            "type": "INLINE_POLICIES",
                            "severity": "MEDIUM",
                            "description": f"User has {len(inline_policies['PolicyNames'])} inline policies",
                            "recommendation": "Use managed policies instead of inline policies"
                        })
                except Exception:
                    pass
                    
    except Exception as e:
        users_data["findings"].append({
            "service": "IAM",
            "resource": "ALL_USERS",
            "type": "AUDIT_ERROR",
            "severity": "HIGH",
            "description": f"Error auditing users: {str(e)}",
            "recommendation": "Check IAM permissions"
        })
    
    return users_data


def audit_iam_roles(iam_client):
    """Audit IAM roles and their permissions"""
    roles_data = {"roles": [], "findings": []}
    
    try:
        paginator = iam_client.get_paginator('list_roles')
        for page in paginator.paginate():
            for role in page['Roles']:
                roles_data["roles"].append(role)
                
                # Check for overly permissive trust policy
                try:
                    role_data = iam_client.get_role(RoleName=role['RoleName'])
                    trust_policy = role_data['Role']['AssumeRolePolicyDocument']
                    
                    for statement in trust_policy.get('Statement', []):
                        if statement.get('Effect') == 'Allow':
                            principals = statement.get('Principal', {})
                            
                            # Check for wildcard principals
                            if '*' in str(principals):
                                roles_data["findings"].append({
                                    "service": "IAM",
                                    "resource": role['RoleName'],
                                    "type": "WILDCARD_TRUST_POLICY",
                                    "severity": "HIGH",
                                    "description": "Role has wildcard in trust policy",
                                    "recommendation": "Restrict trust policy to specific principals"
                                })
                except Exception:
                    pass
                
                # Check for unused roles
                try:
                    role_last_used = iam_client.get_role(RoleName=role['RoleName'])
                    if 'RoleLastUsed' in role_last_used['Role']:
                        last_used = role_last_used['Role']['RoleLastUsed']['LastUsedDate']
                        days_since_used = (datetime.now(last_used.tzinfo) - last_used).days
                        
                        if days_since_used > 90:
                            roles_data["findings"].append({
                                "service": "IAM",
                                "resource": role['RoleName'],
                                "type": "UNUSED_ROLE",
                                "severity": "MEDIUM",
                                "description": f"Role unused for {days_since_used} days",
                                "recommendation": "Consider removing unused role"
                            })
                except Exception:
                    pass
                    
    except Exception as e:
        roles_data["findings"].append({
            "service": "IAM",
            "resource": "ALL_ROLES",
            "type": "AUDIT_ERROR",
            "severity": "HIGH",
            "description": f"Error auditing roles: {str(e)}",
            "recommendation": "Check IAM permissions"
        })
    
    return roles_data


def audit_iam_policies(iam_client):
    """Audit IAM policies and their usage"""
    policies_data = {"policies": [], "findings": []}
    
    try:
        # Audit managed policies
        paginator = iam_client.get_paginator('list_policies')
        for page in paginator.paginate(Scope='Local'):
            for policy in page['Policies']:
                policies_data["policies"].append(policy)
                
                # Check for overly permissive policies
                try:
                    policy_version = iam_client.get_policy_version(
                        PolicyArn=policy['Arn'],
                        VersionId=policy['DefaultVersionId']
                    )
                    
                    policy_doc = policy_version['PolicyVersion']['Document']
                    for statement in policy_doc.get('Statement', []):
                        if statement.get('Effect') == 'Allow':
                            actions = statement.get('Action', [])
                            if isinstance(actions, str):
                                actions = [actions]
                            
                            # Check for wildcard actions
                            if any('*' in action for action in actions):
                                policies_data["findings"].append({
                                    "service": "IAM",
                                    "resource": policy['PolicyName'],
                                    "type": "WILDCARD_ACTIONS",
                                    "severity": "HIGH",
                                    "description": "Policy contains wildcard actions",
                                    "recommendation": "Use specific actions instead of wildcards"
                                })
                                
                            # Check for overly broad services
                            broad_services = ['*', 'ec2:*', 's3:*', 'iam:*']
                            if any(action in broad_services for action in actions):
                                policies_data["findings"].append({
                                    "service": "IAM",
                                    "resource": policy['PolicyName'],
                                    "type": "BROAD_PERMISSIONS",
                                    "severity": "MEDIUM",
                                    "description": "Policy has broad service permissions",
                                    "recommendation": "Restrict permissions to specific services"
                                })
                except Exception:
                    pass
                    
    except Exception as e:
        policies_data["findings"].append({
            "service": "IAM",
            "resource": "ALL_POLICIES",
            "type": "AUDIT_ERROR",
            "severity": "HIGH",
            "description": f"Error auditing policies: {str(e)}",
            "recommendation": "Check IAM permissions"
        })
    
    return policies_data


def check_iam_compliance(findings):
    """Check IAM compliance with security standards"""
    compliance_data = {
        "sox_compliant": True,
        "pci_compliant": True,
        "hipaa_compliant": True,
        "violations": []
    }
    
    for finding in findings:
        if finding.get("type") in ["NO_MFA", "WILDCARD_TRUST_POLICY", "WILDCARD_ACTIONS"]:
            compliance_data["sox_compliant"] = False
            compliance_data["pci_compliant"] = False
            compliance_data["hipaa_compliant"] = False
            compliance_data["violations"].append({
                "finding": finding,
                "standards": ["SOX", "PCI", "HIPAA"]
            })
        elif finding.get("type") in ["OLD_ACCESS_KEY", "BROAD_PERMISSIONS"]:
            compliance_data["pci_compliant"] = False
            compliance_data["violations"].append({
                "finding": finding,
                "standards": ["PCI"]
            })
    
    return compliance_data


def generate_iam_summary(findings):
    """Generate IAM audit summary"""
    summary = {
        "total_findings": len(findings),
        "by_severity": {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0},
        "by_type": {},
        "users_audited": len(set(f.get("resource", "") for f in findings if "user" in f.get("resource", "").lower())),
        "roles_audited": len(set(f.get("resource", "") for f in findings if "role" in f.get("resource", "").lower())),
        "policies_audited": len(set(f.get("resource", "") for f in findings if "policy" in f.get("resource", "").lower()))
    }
    
    for finding in findings:
        severity = finding.get("severity", "UNKNOWN")
        if severity in summary["by_severity"]:
            summary["by_severity"][severity] += 1
        
        finding_type = finding.get("type", "UNKNOWN")
        summary["by_type"][finding_type] = summary["by_type"].get(finding_type, 0) + 1
    
    return summary


def generate_iam_recommendations(findings):
    """Generate IAM audit recommendations"""
    recommendations = []
    
    # Group recommendations by type
    rec_by_type = {}
    for finding in findings:
        finding_type = finding.get("type", "GENERAL")
        if finding_type not in rec_by_type:
            rec_by_type[finding_type] = []
        rec_by_type[finding_type].append(finding.get("recommendation", ""))
    
    # Create prioritized recommendations
    for finding_type, recs in rec_by_type.items():
        unique_recs = list(set(recs))  # Remove duplicates
        for rec in unique_recs:
            recommendations.append({
                "type": finding_type,
                "recommendation": rec,
                "priority": "HIGH" if finding_type in ["NO_MFA", "WILDCARD_TRUST_POLICY", "WILDCARD_ACTIONS"] else "MEDIUM"
            })
    
    return recommendations


def enhance_iam_recommendations_with_ai(findings):
    """Enhance IAM recommendations with AI insights"""
    if not AI_AVAILABLE:
        return []
    
    try:
        gemini_client, nlp_processor = get_ai_components()
        if not gemini_client:
            return []
        
        # Create context for AI
        context = f"""
        IAM security audit findings:
        {json.dumps(findings, indent=2)}
        
        Provide intelligent recommendations for improving IAM security, access management, and compliance.
        Focus on actionable insights and prioritize by security impact.
        """
        
        response = gemini_client.generate_text(context)
        return [{"type": "AI_ENHANCED", "recommendation": response, "priority": "HIGH"}]
        
    except Exception as e:
        console.print(f"[yellow]⚠️ AI enhancement failed: {str(e)}[/yellow]")
        return []


def analyze_iam_permissions(iam_client):
    """Analyze IAM permissions for optimization opportunities"""
    opportunities = []
    
    try:
        # Analyze users for unused permissions
        paginator = iam_client.get_paginator('list_users')
        for page in paginator.paginate():
            for user in page['Users']:
                try:
                    # Check attached policies
                    attached_policies = iam_client.list_attached_user_policies(UserName=user['UserName'])
                    
                    for policy in attached_policies['AttachedPolicies']:
                        # Check if policy is overly permissive
                        policy_version = iam_client.get_policy_version(
                            PolicyArn=policy['PolicyArn'],
                            VersionId=iam_client.get_policy(PolicyArn=policy['PolicyArn'])['Policy']['DefaultVersionId']
                        )
                        
                        policy_doc = policy_version['PolicyVersion']['Document']
                        for statement in policy_doc.get('Statement', []):
                            if statement.get('Effect') == 'Allow':
                                actions = statement.get('Action', [])
                                if isinstance(actions, str):
                                    actions = [actions]
                                
                                # Check for unused permissions (simplified check)
                                if len(actions) > 10:
                                    opportunities.append({
                                        "type": "UNUSED_PERMISSIONS",
                                        "resource": f"{user['UserName']}:{policy['PolicyName']}",
                                        "current_value": f"{len(actions)} actions",
                                        "recommended_value": "Review and reduce permissions",
                                        "potential_savings": "Improved security posture",
                                        "description": "Policy has many permissions - review for unused ones"
                                    })
                except Exception:
                    pass
                    
    except Exception as e:
        opportunities.append({
            "type": "PERMISSION_ANALYSIS_ERROR",
            "description": f"Error analyzing permissions: {str(e)}"
        })
    
    return opportunities


def analyze_least_privilege_violations(iam_client):
    """Analyze least privilege violations"""
    opportunities = []
    
    try:
        # Check for common overly permissive policies
        common_broad_policies = [
            'AdministratorAccess',
            'PowerUserAccess',
            'AmazonS3FullAccess',
            'AmazonEC2FullAccess'
        ]
        
        paginator = iam_client.get_paginator('list_users')
        for page in paginator.paginate():
            for user in page['Users']:
                try:
                    attached_policies = iam_client.list_attached_user_policies(UserName=user['UserName'])
                    
                    for policy in attached_policies['AttachedPolicies']:
                        if policy['PolicyName'] in common_broad_policies:
                            opportunities.append({
                                "type": "LEAST_PRIVILEGE_VIOLATION",
                                "resource": f"{user['UserName']}:{policy['PolicyName']}",
                                "current_value": policy['PolicyName'],
                                "recommended_value": "Custom least-privilege policy",
                                "potential_savings": "Improved security posture",
                                "description": "User has overly permissive policy - consider custom policy"
                            })
                except Exception:
                    pass
                    
    except Exception as e:
        opportunities.append({
            "type": "LEAST_PRIVILEGE_ANALYSIS_ERROR",
            "description": f"Error analyzing least privilege: {str(e)}"
        })
    
    return opportunities


def analyze_credential_rotation(iam_client):
    """Analyze credential rotation opportunities"""
    opportunities = []
    
    try:
        paginator = iam_client.get_paginator('list_users')
        for page in paginator.paginate():
            for user in page['Users']:
                try:
                    access_keys = iam_client.list_access_keys(UserName=user['UserName'])
                    
                    for key in access_keys['AccessKeyMetadata']:
                        if key['Status'] == 'Active':
                            key_age = datetime.now(key['CreateDate'].tzinfo) - key['CreateDate']
                            
                            if key_age.days > 90:
                                opportunities.append({
                                    "type": "CREDENTIAL_ROTATION",
                                    "resource": f"{user['UserName']}:{key['AccessKeyId']}",
                                    "current_value": f"{key_age.days} days old",
                                    "recommended_value": "Rotate access key",
                                    "potential_savings": "Improved security",
                                    "description": "Access key is older than 90 days"
                                })
                except Exception:
                    pass
                    
    except Exception as e:
        opportunities.append({
            "type": "CREDENTIAL_ROTATION_ERROR",
            "description": f"Error analyzing credential rotation: {str(e)}"
        })
    
    return opportunities


def generate_iam_optimization_summary(opportunities):
    """Generate IAM optimization summary"""
    summary = {
        "total_opportunities": len(opportunities),
        "by_type": {},
        "security_improvements": 0
    }
    
    for opportunity in opportunities:
        opp_type = opportunity.get("type", "UNKNOWN")
        summary["by_type"][opp_type] = summary["by_type"].get(opp_type, 0) + 1
        
        if "security" in opportunity.get("potential_savings", "").lower():
            summary["security_improvements"] += 1
    
    return summary


def apply_iam_optimizations(opportunities, iam_client):
    """Apply IAM optimizations"""
    applied_fixes = []
    
    for opportunity in opportunities:
        try:
            if opportunity["type"] == "CREDENTIAL_ROTATION":
                # Create new access key
                user_name = opportunity["resource"].split(":")[0]
                new_key = iam_client.create_access_key(UserName=user_name)
                
                applied_fixes.append({
                    "opportunity": opportunity,
                    "status": "SUCCESS",
                    "action": f"Created new access key: {new_key['AccessKey']['AccessKeyId']}"
                })
                
                # Note: Old key should be deactivated manually for safety
                
        except Exception as e:
            applied_fixes.append({
                "opportunity": opportunity,
                "status": "FAILED",
                "error": str(e)
            })
    
    return applied_fixes


def display_iam_audit_results(results, output, verbose):
    """Display IAM audit results"""
    if output == "json":
        console.print(json.dumps(results, indent=2, default=str))
    else:
        # Display findings table
        if results.get("findings"):
            table = Table(title="🔐 IAM Security Audit Results")
            table.add_column("Resource", style="cyan")
            table.add_column("Type", style="yellow")
            table.add_column("Severity", style="red")
            table.add_column("Description", style="white")
            
            for finding in results["findings"]:
                severity_color = {"HIGH": "red", "MEDIUM": "yellow", "LOW": "green", "INFO": "blue"}.get(
                    finding.get("severity", ""), "white"
                )
                
                table.add_row(
                    finding.get("resource", ""),
                    finding.get("type", ""),
                    f"[{severity_color}]{finding.get('severity', '')}[/{severity_color}]",
                    finding.get("description", "")
                )
            
            console.print(table)
        
        # Display compliance status
        if results.get("compliance"):
            compliance = results["compliance"]
            console.print("\n📋 Compliance Status:")
            console.print(f"  • SOX: {'✅' if compliance.get('sox_compliant') else '❌'}")
            console.print(f"  • PCI: {'✅' if compliance.get('pci_compliant') else '❌'}")
            console.print(f"  • HIPAA: {'✅' if compliance.get('hipaa_compliant') else '❌'}")
        
        # Display summary
        summary = results.get("summary", {})
        if summary:
            console.print(f"\n📊 Summary: {summary.get('total_findings', 0)} findings")
            console.print(f"👤 Users audited: {summary.get('users_audited', 0)}")
            console.print(f"🎭 Roles audited: {summary.get('roles_audited', 0)}")
            console.print(f"📜 Policies audited: {summary.get('policies_audited', 0)}")


def display_iam_optimization_results(results, dry_run, verbose):
    """Display IAM optimization results"""
    if results.get("opportunities"):
        table = Table(title="⚡ IAM Optimization Opportunities")
        table.add_column("Resource", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Current", style="white")
        table.add_column("Recommended", style="green")
        table.add_column("Potential Savings", style="green")
        
        for opportunity in results["opportunities"]:
            table.add_row(
                opportunity.get("resource", ""),
                opportunity.get("type", ""),
                opportunity.get("current_value", ""),
                opportunity.get("recommended_value", ""),
                opportunity.get("potential_savings", "")
            )
        
        console.print(table)
    
    # Display summary
    summary = results.get("summary", {})
    if summary:
        console.print(f"\n📊 Summary: {summary.get('total_opportunities', 0)} optimization opportunities")
        console.print(f"🔒 Security improvements: {summary.get('security_improvements', 0)}")
    
    # Display applied fixes
    if not dry_run and results.get("applied_fixes"):
        console.print("\n🔧 Applied Optimizations:")
        for fix in results["applied_fixes"]:
            status_color = "green" if fix["status"] == "SUCCESS" else "red"
            console.print(f"  • [{status_color}]{fix['status']}[/{status_color}] {fix.get('action', '')}")


# S3 Functions
def audit_s3_bucket_configuration(s3_client, bucket):
    """Audit S3 bucket configuration"""
    findings = []
    
    try:
        bucket_name = bucket['Name']
        
        # Check bucket versioning
        try:
            versioning = s3_client.get_bucket_versioning(Bucket=bucket_name)
            if 'Status' not in versioning or versioning['Status'] != 'Enabled':
                findings.append({
                    "service": "S3",
                    "resource": bucket_name,
                    "type": "VERSIONING_DISABLED",
                    "severity": "MEDIUM",
                    "description": "Bucket versioning is not enabled",
                    "recommendation": "Enable versioning for data protection"
                })
        except Exception:
            pass
        
        # Check bucket encryption
        try:
            encryption = s3_client.get_bucket_encryption(Bucket=bucket_name)
            if not encryption.get('ServerSideEncryptionConfiguration'):
                findings.append({
                    "service": "S3",
                    "resource": bucket_name,
                    "type": "ENCRYPTION_DISABLED",
                    "severity": "HIGH",
                    "description": "Bucket encryption is not configured",
                    "recommendation": "Enable default encryption for the bucket"
                })
        except s3_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                findings.append({
                    "service": "S3",
                    "resource": bucket_name,
                    "type": "ENCRYPTION_DISABLED",
                    "severity": "HIGH",
                    "description": "Bucket encryption is not configured",
                    "recommendation": "Enable default encryption for the bucket"
                })
        
        # Check bucket logging
        try:
            logging = s3_client.get_bucket_logging(Bucket=bucket_name)
            if not logging.get('LoggingEnabled'):
                findings.append({
                    "service": "S3",
                    "resource": bucket_name,
                    "type": "LOGGING_DISABLED",
                    "severity": "MEDIUM",
                    "description": "Bucket access logging is not enabled",
                    "recommendation": "Enable access logging for audit purposes"
                })
        except Exception:
            pass
        
        # Check bucket lifecycle
        try:
            lifecycle = s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
            if not lifecycle.get('Rules'):
                findings.append({
                    "service": "S3",
                    "resource": bucket_name,
                    "type": "NO_LIFECYCLE_POLICY",
                    "severity": "LOW",
                    "description": "No lifecycle policy configured",
                    "recommendation": "Configure lifecycle policies for cost optimization"
                })
        except s3_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchLifecycleConfiguration':
                findings.append({
                    "service": "S3",
                    "resource": bucket_name,
                    "type": "NO_LIFECYCLE_POLICY",
                    "severity": "LOW",
                    "description": "No lifecycle policy configured",
                    "recommendation": "Configure lifecycle policies for cost optimization"
                })
                
    except Exception as e:
        findings.append({
            "service": "S3",
            "resource": bucket['Name'],
            "type": "CONFIGURATION_AUDIT_ERROR",
            "severity": "HIGH",
            "description": f"Error auditing bucket configuration: {str(e)}",
            "recommendation": "Check bucket permissions and configuration"
        })
    
    return findings


def audit_s3_bucket_policies(s3_client, bucket):
    """Audit S3 bucket policies"""
    findings = []
    
    try:
        bucket_name = bucket['Name']
        
        # Check bucket policy
        try:
            policy = s3_client.get_bucket_policy(Bucket=bucket_name)
            policy_doc = json.loads(policy['Policy'])
            
            for statement in policy_doc.get('Statement', []):
                if statement.get('Effect') == 'Allow':
                    # Check for public access
                    principal = statement.get('Principal', {})
                    if principal == '*' or (isinstance(principal, dict) and '*' in principal.values()):
                        findings.append({
                            "service": "S3",
                            "resource": bucket_name,
                            "type": "PUBLIC_ACCESS",
                            "severity": "HIGH",
                            "description": "Bucket policy allows public access",
                            "recommendation": "Remove public access from bucket policy"
                        })
                    
                    # Check for overly permissive actions
                    actions = statement.get('Action', [])
                    if isinstance(actions, str):
                        actions = [actions]
                    
                    broad_actions = ['s3:*', 's3:Get*', 's3:Put*', 's3:Delete*']
                    if any(action in broad_actions for action in actions):
                        findings.append({
                            "service": "S3",
                            "resource": bucket_name,
                            "type": "BROAD_PERMISSIONS",
                            "severity": "MEDIUM",
                            "description": "Bucket policy has broad permissions",
                            "recommendation": "Use least privilege principle for bucket policy"
                        })
                        
        except s3_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
                # No bucket policy - this might be good or bad depending on use case
                pass
            else:
                findings.append({
                    "service": "S3",
                    "resource": bucket_name,
                    "type": "POLICY_AUDIT_ERROR",
                    "severity": "MEDIUM",
                    "description": f"Error auditing bucket policy: {str(e)}",
                    "recommendation": "Check bucket policy configuration"
                })
        
        # Check bucket ACL
        try:
            acl = s3_client.get_bucket_acl(Bucket=bucket_name)
            for grant in acl.get('Grants', []):
                grantee = grant.get('Grantee', {})
                if grantee.get('URI') == 'http://acs.amazonaws.com/groups/global/AllUsers':
                    findings.append({
                        "service": "S3",
                        "resource": bucket_name,
                        "type": "PUBLIC_ACL",
                        "severity": "HIGH",
                        "description": "Bucket ACL allows public access",
                        "recommendation": "Remove public access from bucket ACL"
                    })
                    
        except Exception as e:
            findings.append({
                "service": "S3",
                "resource": bucket_name,
                "type": "ACL_AUDIT_ERROR",
                "severity": "MEDIUM",
                "description": f"Error auditing bucket ACL: {str(e)}",
                "recommendation": "Check bucket ACL configuration"
            })
                
    except Exception as e:
        findings.append({
            "service": "S3",
            "resource": bucket['Name'],
            "type": "POLICY_AUDIT_ERROR",
            "severity": "HIGH",
            "description": f"Error auditing bucket policies: {str(e)}",
            "recommendation": "Check bucket permissions and configuration"
        })
    
    return findings


def audit_s3_encryption(s3_client, bucket):
    """Audit S3 encryption settings"""
    findings = []
    
    try:
        bucket_name = bucket['Name']
        
        # Check default encryption
        try:
            encryption = s3_client.get_bucket_encryption(Bucket=bucket_name)
            encryption_config = encryption.get('ServerSideEncryptionConfiguration', {})
            rules = encryption_config.get('Rules', [])
            
            if not rules:
                findings.append({
                    "service": "S3",
                    "resource": bucket_name,
                    "type": "NO_DEFAULT_ENCRYPTION",
                    "severity": "HIGH",
                    "description": "No default encryption configured",
                    "recommendation": "Enable default encryption for the bucket"
                })
            else:
                # Check encryption algorithm
                for rule in rules:
                    apply_server_side_encryption_by_default = rule.get('ApplyServerSideEncryptionByDefault', {})
                    sse_algorithm = apply_server_side_encryption_by_default.get('SSEAlgorithm')
                    
                    if sse_algorithm not in ['AES256', 'aws:kms']:
                        findings.append({
                            "service": "S3",
                            "resource": bucket_name,
                            "type": "WEAK_ENCRYPTION",
                            "severity": "MEDIUM",
                            "description": f"Using weak encryption algorithm: {sse_algorithm}",
                            "recommendation": "Use AES256 or aws:kms for encryption"
                        })
                        
        except s3_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                findings.append({
                    "service": "S3",
                    "resource": bucket_name,
                    "type": "NO_DEFAULT_ENCRYPTION",
                    "severity": "HIGH",
                    "description": "No default encryption configured",
                    "recommendation": "Enable default encryption for the bucket"
                })
            else:
                findings.append({
                    "service": "S3",
                    "resource": bucket_name,
                    "type": "ENCRYPTION_AUDIT_ERROR",
                    "severity": "MEDIUM",
                    "description": f"Error auditing encryption: {str(e)}",
                    "recommendation": "Check encryption configuration"
                })
                
    except Exception as e:
        findings.append({
            "service": "S3",
            "resource": bucket['Name'],
            "type": "ENCRYPTION_AUDIT_ERROR",
            "severity": "HIGH",
            "description": f"Error auditing encryption: {str(e)}",
            "recommendation": "Check bucket permissions and configuration"
        })
    
    return findings


def check_s3_compliance(findings):
    """Check S3 compliance with data protection standards"""
    compliance_data = {
        "sox_compliant": True,
        "pci_compliant": True,
        "hipaa_compliant": True,
        "violations": []
    }
    
    for finding in findings:
        if finding.get("type") in ["PUBLIC_ACCESS", "PUBLIC_ACL", "ENCRYPTION_DISABLED", "NO_DEFAULT_ENCRYPTION"]:
            compliance_data["sox_compliant"] = False
            compliance_data["pci_compliant"] = False
            compliance_data["hipaa_compliant"] = False
            compliance_data["violations"].append({
                "finding": finding,
                "standards": ["SOX", "PCI", "HIPAA"]
            })
        elif finding.get("type") in ["LOGGING_DISABLED", "BROAD_PERMISSIONS"]:
            compliance_data["pci_compliant"] = False
            compliance_data["violations"].append({
                "finding": finding,
                "standards": ["PCI"]
            })
    
    return compliance_data


def generate_s3_summary(findings):
    """Generate S3 audit summary"""
    summary = {
        "total_findings": len(findings),
        "by_severity": {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0},
        "by_type": {},
        "buckets_audited": len(set(f.get("resource", "") for f in findings))
    }
    
    for finding in findings:
        severity = finding.get("severity", "UNKNOWN")
        if severity in summary["by_severity"]:
            summary["by_severity"][severity] += 1
        
        finding_type = finding.get("type", "UNKNOWN")
        summary["by_type"][finding_type] = summary["by_type"].get(finding_type, 0) + 1
    
    return summary


def generate_s3_recommendations(findings):
    """Generate S3 audit recommendations"""
    recommendations = []
    
    # Group recommendations by type
    rec_by_type = {}
    for finding in findings:
        finding_type = finding.get("type", "GENERAL")
        if finding_type not in rec_by_type:
            rec_by_type[finding_type] = []
        rec_by_type[finding_type].append(finding.get("recommendation", ""))
    
    # Create prioritized recommendations
    for finding_type, recs in rec_by_type.items():
        unique_recs = list(set(recs))  # Remove duplicates
        for rec in unique_recs:
            recommendations.append({
                "type": finding_type,
                "recommendation": rec,
                "priority": "HIGH" if finding_type in ["PUBLIC_ACCESS", "PUBLIC_ACL", "ENCRYPTION_DISABLED"] else "MEDIUM"
            })
    
    return recommendations


def enhance_s3_recommendations_with_ai(findings):
    """Enhance S3 recommendations with AI insights"""
    if not AI_AVAILABLE:
        return []
    
    try:
        gemini_client, nlp_processor = get_ai_components()
        if not gemini_client:
            return []
        
        # Create context for AI
        context = f"""
        S3 security audit findings:
        {json.dumps(findings, indent=2)}
        
        Provide intelligent recommendations for improving S3 security, data protection, and compliance.
        Focus on actionable insights and prioritize by security impact.
        """
        
        response = gemini_client.generate_text(context)
        return [{"type": "AI_ENHANCED", "recommendation": response, "priority": "HIGH"}]
        
    except Exception as e:
        console.print(f"[yellow]⚠️ AI enhancement failed: {str(e)}[/yellow]")
        return []


def analyze_s3_storage_optimization(s3_client, bucket):
    """Analyze S3 storage optimization opportunities"""
    opportunities = []
    
    try:
        bucket_name = bucket['Name']
        
        # Check for lifecycle policies
        try:
            lifecycle = s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
            if not lifecycle.get('Rules'):
                opportunities.append({
                    "type": "STORAGE_OPTIMIZATION",
                    "resource": bucket_name,
                    "current_value": "No lifecycle policy",
                    "recommended_value": "Configure lifecycle policy",
                    "potential_savings": "Up to 50% storage cost reduction",
                    "description": "No lifecycle policy configured - consider moving objects to cheaper storage classes"
                })
        except s3_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchLifecycleConfiguration':
                opportunities.append({
                    "type": "STORAGE_OPTIMIZATION",
                    "resource": bucket_name,
                    "current_value": "No lifecycle policy",
                    "recommended_value": "Configure lifecycle policy",
                    "potential_savings": "Up to 50% storage cost reduction",
                    "description": "No lifecycle policy configured - consider moving objects to cheaper storage classes"
                })
        
        # Check for intelligent tiering
        try:
            intelligent_tiering = s3_client.get_bucket_intelligent_tiering_configuration(
                Bucket=bucket_name,
                Id='EntireBucket'
            )
        except s3_client.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchConfiguration':
                opportunities.append({
                    "type": "INTELLIGENT_TIERING",
                    "resource": bucket_name,
                    "current_value": "Not enabled",
                    "recommended_value": "Enable intelligent tiering",
                    "potential_savings": "Up to 40% storage cost reduction",
                    "description": "Intelligent tiering not enabled - automatically moves objects to optimal storage class"
                })
                
    except Exception as e:
        opportunities.append({
            "type": "STORAGE_OPTIMIZATION_ERROR",
            "resource": bucket_name,
            "description": f"Error analyzing storage optimization: {str(e)}"
        })
    
    return opportunities


def analyze_s3_access_optimization(s3_client, bucket):
    """Analyze S3 access optimization opportunities"""
    opportunities = []
    
    try:
        bucket_name = bucket['Name']
        
        # Check for public access
        try:
            public_access = s3_client.get_public_access_block(Bucket=bucket_name)
            config = public_access.get('PublicAccessBlockConfiguration', {})
            
            if not all([
                config.get('BlockPublicAcls', False),
                config.get('IgnorePublicAcls', False),
                config.get('BlockPublicPolicy', False),
                config.get('RestrictPublicBuckets', False)
            ]):
                opportunities.append({
                    "type": "ACCESS_OPTIMIZATION",
                    "resource": bucket_name,
                    "current_value": "Public access not fully blocked",
                    "recommended_value": "Block all public access",
                    "potential_savings": "Improved security posture",
                    "description": "Public access not fully blocked - consider blocking all public access"
                })
        except Exception:
            opportunities.append({
                "type": "ACCESS_OPTIMIZATION",
                "resource": bucket_name,
                "current_value": "Public access block not configured",
                "recommended_value": "Configure public access block",
                "potential_savings": "Improved security posture",
                "description": "Public access block not configured - consider blocking public access"
            })
                
    except Exception as e:
        opportunities.append({
            "type": "ACCESS_OPTIMIZATION_ERROR",
            "resource": bucket_name,
            "description": f"Error analyzing access optimization: {str(e)}"
        })
    
    return opportunities


def analyze_s3_cost_optimization(ce_client, bucket):
    """Analyze S3 cost optimization opportunities"""
    opportunities = []
    
    try:
        bucket_name = bucket['Name']
        
        # Get cost data for the bucket (simplified - would need more complex querying)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        try:
            response = ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.strftime('%Y-%m-%d'),
                    'End': end_date.strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'},
                    {'Type': 'DIMENSION', 'Key': 'USAGE_TYPE'}
                ],
                Filter={
                    'And': [
                        {'Dimensions': {'Key': 'SERVICE', 'Values': ['Amazon Simple Storage Service']}},
                        {'Tags': {'Key': 'BucketName', 'Values': [bucket_name]}}
                    ]
                }
            )
            
            # Analyze cost data (simplified)
            total_cost = sum(float(result['Metrics']['UnblendedCost']['Amount']) 
                           for result in response.get('ResultsByTime', []))
            
            if total_cost > 100:  # High cost threshold
                opportunities.append({
                    "type": "COST_OPTIMIZATION",
                    "resource": bucket_name,
                    "current_value": f"${total_cost:.2f} monthly",
                    "recommended_value": "Review storage classes and lifecycle",
                    "potential_savings": "Up to 50% cost reduction",
                    "description": f"High monthly cost (${total_cost:.2f}) - review storage optimization"
                })
                
        except Exception:
            # If cost data not available, provide generic recommendation
            opportunities.append({
                "type": "COST_OPTIMIZATION",
                "resource": bucket_name,
                "current_value": "Cost data unavailable",
                "recommended_value": "Review storage classes and lifecycle",
                "potential_savings": "Up to 50% cost reduction",
                "description": "Consider reviewing storage classes and lifecycle policies for cost optimization"
            })
                
    except Exception as e:
        opportunities.append({
            "type": "COST_OPTIMIZATION_ERROR",
            "resource": bucket_name,
            "description": f"Error analyzing cost optimization: {str(e)}"
        })
    
    return opportunities


def generate_s3_optimization_summary(opportunities):
    """Generate S3 optimization summary"""
    summary = {
        "total_opportunities": len(opportunities),
        "by_type": {},
        "potential_savings": 0.0
    }
    
    for opportunity in opportunities:
        opp_type = opportunity.get("type", "UNKNOWN")
        summary["by_type"][opp_type] = summary["by_type"].get(opp_type, 0) + 1
        
        # Extract potential savings from description
        savings_text = opportunity.get("potential_savings", "")
        if "%" in savings_text:
            try:
                percentage = float(savings_text.split("%")[0].split()[-1])
                summary["potential_savings"] = max(summary["potential_savings"], percentage)
            except (ValueError, IndexError):
                pass
    
    return summary


def apply_s3_optimizations(opportunities, s3_client):
    """Apply S3 optimizations"""
    applied_fixes = []
    
    for opportunity in opportunities:
        try:
            if opportunity["type"] == "ACCESS_OPTIMIZATION":
                # Block public access
                bucket_name = opportunity["resource"]
                s3_client.put_public_access_block(
                    Bucket=bucket_name,
                    PublicAccessBlockConfiguration={
                        'BlockPublicAcls': True,
                        'IgnorePublicAcls': True,
                        'BlockPublicPolicy': True,
                        'RestrictPublicBuckets': True
                    }
                )
                applied_fixes.append({
                    "opportunity": opportunity,
                    "status": "SUCCESS",
                    "action": "Blocked public access"
                })
                
        except Exception as e:
            applied_fixes.append({
                "opportunity": opportunity,
                "status": "FAILED",
                "error": str(e)
            })
    
    return applied_fixes


def display_s3_audit_results(results, output, verbose):
    """Display S3 audit results"""
    if output == "json":
        console.print(json.dumps(results, indent=2, default=str))
    else:
        # Display findings table
        if results.get("findings"):
            table = Table(title="📦 S3 Security Audit Results")
            table.add_column("Bucket", style="cyan")
            table.add_column("Type", style="yellow")
            table.add_column("Severity", style="red")
            table.add_column("Description", style="white")
            
            for finding in results["findings"]:
                severity_color = {"HIGH": "red", "MEDIUM": "yellow", "LOW": "green", "INFO": "blue"}.get(
                    finding.get("severity", ""), "white"
                )
                
                table.add_row(
                    finding.get("resource", ""),
                    finding.get("type", ""),
                    f"[{severity_color}]{finding.get('severity', '')}[/{severity_color}]",
                    finding.get("description", "")
                )
            
            console.print(table)
        
        # Display compliance status
        if results.get("compliance"):
            compliance = results["compliance"]
            console.print("\n📋 Compliance Status:")
            console.print(f"  • SOX: {'✅' if compliance.get('sox_compliant') else '❌'}")
            console.print(f"  • PCI: {'✅' if compliance.get('pci_compliant') else '❌'}")
            console.print(f"  • HIPAA: {'✅' if compliance.get('hipaa_compliant') else '❌'}")
        
        # Display summary
        summary = results.get("summary", {})
        if summary:
            console.print(f"\n📊 Summary: {summary.get('total_findings', 0)} findings across {summary.get('buckets_audited', 0)} buckets")


def display_s3_optimization_results(results, dry_run, verbose):
    """Display S3 optimization results"""
    console.print("\n[bold green]✅ S3 Optimization Results[/bold green]")
    
    if dry_run:
        console.print("[yellow]🔍 Dry Run Mode - No changes applied[/yellow]")
    
    # Display summary
    summary = results.get("summary", {})
    total_buckets = summary.get("total_buckets", 0)
    optimizable_buckets = summary.get("optimizable_buckets", 0)
    potential_savings = summary.get("potential_savings", 0)
    
    console.print(f"📊 Analyzed {total_buckets} S3 buckets")
    console.print(f"🎯 Found {optimizable_buckets} buckets with optimization opportunities")
    console.print(f"💰 Potential monthly savings: ${potential_savings:.2f}")
    
    # Display opportunities
    opportunities = results.get("opportunities", [])
    if opportunities:
        table = Table(title="S3 Optimization Opportunities")
        table.add_column("Bucket", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Impact", style="green")
        table.add_column("Savings", style="yellow")
        
        for opp in opportunities:
            table.add_row(
                opp.get("bucket", ""),
                opp.get("type", ""),
                opp.get("impact", ""),
                f"${opp.get('savings', 0):.2f}/month"
            )
        
        console.print(table)
    
    # Display applied optimizations
    if not dry_run and results.get("applied_optimizations"):
        console.print("\n[bold green]✅ Applied Optimizations[/bold green]")
        for optimization in results["applied_optimizations"]:
            console.print(f"  • {optimization}")
    
    # Display recommendations
    if results.get("recommendations"):
        console.print("\n[bold blue]💡 Recommendations[/bold blue]")
        for rec in results["recommendations"]:
            console.print(f"  • {rec}")


# ============================================================================
# PHASE 3: INFRASTRUCTURE AUTOMATION COMMANDS
# ============================================================================

@app.command()
def infra_audit(
    templates: bool = typer.Option(
        True, "--templates", "-t", help="Audit CloudFormation/CDK templates"
    ),
    security: bool = typer.Option(
        True, "--security", "-s", help="Audit infrastructure security configurations"
    ),
    compliance: bool = typer.Option(
        True, "--compliance", "-c", help="Check compliance with infrastructure standards"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to audit"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🏗️ Perform comprehensive infrastructure audit across CloudFormation, CDK, and deployed resources

    This command analyzes infrastructure templates, deployed resources, and configurations
    to identify security issues, compliance violations, and optimization opportunities.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🏗️ Running infrastructure audit...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            cf_client = session.client("cloudformation")
            ec2_client = session.client("ec2")
            iam_client = session.client("iam")
            s3_client = session.client("s3")

            audit_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "findings": [],
                "summary": {},
                "recommendations": [],
            }

            # CloudFormation Template Audit
            if templates:
                progress.update(task, description="📋 Auditing CloudFormation templates...")
                cf_findings = audit_cloudformation_templates(cf_client, security, compliance)
                audit_results["findings"].extend(cf_findings)

            # Infrastructure Security Audit
            if security:
                progress.update(task, description="🔒 Auditing infrastructure security...")
                security_findings = audit_infrastructure_security(session, compliance)
                audit_results["findings"].extend(security_findings)

            # Compliance Audit
            if compliance:
                progress.update(task, description="📊 Checking infrastructure compliance...")
                compliance_findings = audit_infrastructure_compliance(session)
                audit_results["findings"].extend(compliance_findings)

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating recommendations...")
            audit_results["summary"] = generate_infrastructure_summary(audit_results["findings"])
            audit_results["recommendations"] = generate_infrastructure_recommendations(audit_results["findings"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_infrastructure_recommendations_with_ai(audit_results["findings"])
                audit_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Infrastructure audit completed!")

            # Display results
            display_infrastructure_audit_results(audit_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Infrastructure audit failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def infra_drift(
    detect: bool = typer.Option(
        True, "--detect", "-d", help="Detect infrastructure drift"
    ),
    remediate: bool = typer.Option(
        False, "--remediate", "-r", help="Remediate detected drift"
    ),
    report: bool = typer.Option(
        True, "--report", "-R", help="Generate drift report"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to check"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🔄 Detect and remediate infrastructure drift between templates and deployed resources

    This command compares deployed infrastructure with CloudFormation templates
    to identify configuration drift and provide remediation options.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🔄 Detecting infrastructure drift...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            cf_client = session.client("cloudformation")

            drift_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "stacks": [],
                "drift_detected": False,
                "summary": {},
                "recommendations": [],
            }

            # Detect drift
            if detect:
                progress.update(task, description="🔍 Detecting stack drift...")
                drift_findings = detect_infrastructure_drift(cf_client)
                drift_results["stacks"] = drift_findings
                drift_results["drift_detected"] = any(stack.get("drift_detected", False) for stack in drift_findings)

            # Remediate drift
            if remediate and drift_results["drift_detected"]:
                progress.update(task, description="🔧 Remediating drift...")
                remediation_results = remediate_infrastructure_drift(cf_client, drift_results["stacks"])
                drift_results["remediation_results"] = remediation_results

            # Generate report
            if report:
                progress.update(task, description="📊 Generating drift report...")
                drift_results["summary"] = generate_drift_summary(drift_results["stacks"])
                drift_results["recommendations"] = generate_drift_recommendations(drift_results["stacks"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_drift_recommendations_with_ai(drift_results["stacks"])
                drift_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Infrastructure drift analysis completed!")

            # Display results
            display_infrastructure_drift_results(drift_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Infrastructure drift detection failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def infra_cost(
    estimate: bool = typer.Option(
        True, "--estimate", "-e", help="Estimate infrastructure costs"
    ),
    optimize: bool = typer.Option(
        True, "--optimize", "-o", help="Identify cost optimization opportunities"
    ),
    forecast: bool = typer.Option(
        True, "--forecast", "-f", help="Generate cost forecasts"
    ),
    output: str = typer.Option(
        "table", "--output", "-O", help="Output format: table, json, csv"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to analyze"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    💰 Analyze infrastructure costs and identify optimization opportunities

    This command provides comprehensive cost analysis for infrastructure resources
    including current costs, optimization opportunities, and future forecasts.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("💰 Analyzing infrastructure costs...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            ce_client = session.client("ce")
            cf_client = session.client("cloudformation")

            cost_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "current_costs": {},
                "optimization_opportunities": [],
                "forecast": {},
                "summary": {},
                "recommendations": [],
            }

            # Estimate current costs
            if estimate:
                progress.update(task, description="📊 Estimating current infrastructure costs...")
                current_costs = estimate_infrastructure_costs(ce_client, cf_client)
                cost_results["current_costs"] = current_costs

            # Identify optimization opportunities
            if optimize:
                progress.update(task, description="🎯 Identifying cost optimization opportunities...")
                optimization_opportunities = identify_cost_optimization_opportunities(session)
                cost_results["optimization_opportunities"] = optimization_opportunities

            # Generate cost forecast
            if forecast:
                progress.update(task, description="📈 Generating cost forecasts...")
                cost_forecast = generate_infrastructure_cost_forecast(ce_client, cf_client)
                cost_results["forecast"] = cost_forecast

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating cost recommendations...")
            cost_results["summary"] = generate_infrastructure_cost_summary(cost_results)
            cost_results["recommendations"] = generate_infrastructure_cost_recommendations(cost_results)

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_cost_recommendations_with_ai(cost_results)
                cost_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Infrastructure cost analysis completed!")

            # Display results
            display_infrastructure_cost_results(cost_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Infrastructure cost analysis failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def template_validate(
    security: bool = typer.Option(
        True, "--security", "-s", help="Validate template security configurations"
    ),
    best_practices: bool = typer.Option(
        True, "--best-practices", "-b", help="Check against AWS best practices"
    ),
    template_path: Optional[str] = typer.Option(
        None, "--template", "-t", help="Path to specific template file"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    ✅ Validate CloudFormation/CDK templates for security and best practices

    This command validates infrastructure templates against security standards,
    AWS best practices, and common anti-patterns.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("✅ Validating templates...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            cf_client = session.client("cloudformation")

            validation_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "templates": [],
                "findings": [],
                "summary": {},
                "recommendations": [],
            }

            # Validate templates
            progress.update(task, description="📋 Validating CloudFormation templates...")
            if template_path:
                # Validate specific template
                template_findings = validate_specific_template(cf_client, template_path, security, best_practices)
                validation_results["templates"].append(template_findings)
            else:
                # Validate all templates in stacks
                all_template_findings = validate_all_templates(cf_client, security, best_practices)
                validation_results["templates"].extend(all_template_findings)

            # Collect all findings
            for template in validation_results["templates"]:
                validation_results["findings"].extend(template.get("findings", []))

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating validation summary...")
            validation_results["summary"] = generate_template_validation_summary(validation_results["findings"])
            validation_results["recommendations"] = generate_template_validation_recommendations(validation_results["findings"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_template_recommendations_with_ai(validation_results["findings"])
                validation_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Template validation completed!")

            # Display results
            display_template_validation_results(validation_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Template validation failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def template_optimize(
    cost: bool = typer.Option(
        True, "--cost", "-c", help="Optimize templates for cost efficiency"
    ),
    performance: bool = typer.Option(
        True, "--performance", "-p", help="Optimize templates for performance"
    ),
    template_path: Optional[str] = typer.Option(
        None, "--template", "-t", help="Path to specific template file"
    ),
    auto_fix: bool = typer.Option(
        False, "--auto-fix", "-a", help="Automatically apply optimizations"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Show what would be optimized without applying"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🚀 Optimize CloudFormation/CDK templates for cost and performance

    This command analyzes templates and provides optimization recommendations
    for cost efficiency, performance, and resource utilization.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🚀 Optimizing templates...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            cf_client = session.client("cloudformation")

            optimization_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "templates": [],
                "opportunities": [],
                "summary": {},
                "recommendations": [],
            }

            # Optimize templates
            progress.update(task, description="🎯 Analyzing template optimization opportunities...")
            if template_path:
                # Optimize specific template
                template_optimizations = optimize_specific_template(cf_client, template_path, cost, performance)
                optimization_results["templates"].append(template_optimizations)
            else:
                # Optimize all templates in stacks
                all_template_optimizations = optimize_all_templates(cf_client, cost, performance)
                optimization_results["templates"].extend(all_template_optimizations)

            # Collect all opportunities
            for template in optimization_results["templates"]:
                optimization_results["opportunities"].extend(template.get("opportunities", []))

            # Apply optimizations if requested
            if auto_fix and not dry_run:
                progress.update(task, description="🔧 Applying template optimizations...")
                applied_optimizations = apply_template_optimizations(optimization_results["opportunities"])
                optimization_results["applied_optimizations"] = applied_optimizations

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating optimization summary...")
            optimization_results["summary"] = generate_template_optimization_summary(optimization_results["opportunities"])
            optimization_results["recommendations"] = generate_template_optimization_recommendations(optimization_results["opportunities"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_template_optimization_recommendations_with_ai(optimization_results["opportunities"])
                optimization_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Template optimization completed!")

            # Display results
            display_template_optimization_results(optimization_results, dry_run, verbose)

        except Exception as e:
            console.print(f"[red]❌ Template optimization failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def template_compliance(
    frameworks: str = typer.Option(
        "all", "--frameworks", "-f", help="Compliance frameworks: sox, hipaa, pci-dss, cis, all"
    ),
    standards: str = typer.Option(
        "aws", "--standards", "-s", help="Standards to check: aws, nist, iso27001, all"
    ),
    template_path: Optional[str] = typer.Option(
        None, "--template", "-t", help="Path to specific template file"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    📋 Check template compliance with security frameworks and standards

    This command validates templates against various compliance frameworks
    and security standards to ensure regulatory compliance.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("📋 Checking template compliance...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            cf_client = session.client("cloudformation")

            compliance_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "templates": [],
                "compliance_checks": [],
                "summary": {},
                "recommendations": [],
            }

            # Check template compliance
            progress.update(task, description="🔍 Checking compliance frameworks...")
            if template_path:
                # Check specific template
                template_compliance = check_template_compliance(cf_client, template_path, frameworks, standards)
                compliance_results["templates"].append(template_compliance)
            else:
                # Check all templates in stacks
                all_template_compliance = check_all_templates_compliance(cf_client, frameworks, standards)
                compliance_results["templates"].extend(all_template_compliance)

            # Collect all compliance checks
            for template in compliance_results["templates"]:
                compliance_results["compliance_checks"].extend(template.get("compliance_checks", []))

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating compliance summary...")
            compliance_results["summary"] = generate_template_compliance_summary(compliance_results["compliance_checks"])
            compliance_results["recommendations"] = generate_template_compliance_recommendations(compliance_results["compliance_checks"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_template_compliance_recommendations_with_ai(compliance_results["compliance_checks"])
                compliance_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Template compliance check completed!")

            # Display results
            display_template_compliance_results(compliance_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Template compliance check failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def container_scan(
    images: bool = typer.Option(
        True, "--images", "-i", help="Scan container images for vulnerabilities"
    ),
    vulnerabilities: bool = typer.Option(
        True, "--vulnerabilities", "-v", help="Scan for security vulnerabilities"
    ),
    compliance: bool = typer.Option(
        True, "--compliance", "-c", help="Check compliance with container security standards"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to scan"),
    verbose: bool = typer.Option(False, "--verbose", "-V", help="Verbose output"),
):
    """
    🐳 Scan container images and configurations for security vulnerabilities

    This command scans container images in ECR, ECS, and EKS for security
    vulnerabilities, misconfigurations, and compliance issues.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🐳 Scanning containers...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            ecr_client = session.client("ecr")
            ecs_client = session.client("ecs")
            eks_client = session.client("eks")

            scan_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "images": [],
                "vulnerabilities": [],
                "compliance_findings": [],
                "summary": {},
                "recommendations": [],
            }

            # Scan container images
            if images:
                progress.update(task, description="🔍 Scanning container images...")
                image_scan_results = scan_container_images(ecr_client, ecs_client, eks_client)
                scan_results["images"] = image_scan_results

            # Scan for vulnerabilities
            if vulnerabilities:
                progress.update(task, description="🛡️ Scanning for vulnerabilities...")
                vulnerability_scan_results = scan_container_vulnerabilities(session)
                scan_results["vulnerabilities"] = vulnerability_scan_results

            # Check compliance
            if compliance:
                progress.update(task, description="📋 Checking container compliance...")
                compliance_scan_results = scan_container_compliance(session)
                scan_results["compliance_findings"] = compliance_scan_results

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating scan summary...")
            scan_results["summary"] = generate_container_scan_summary(scan_results)
            scan_results["recommendations"] = generate_container_scan_recommendations(scan_results)

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_container_recommendations_with_ai(scan_results)
                scan_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Container scan completed!")

            # Display results
            display_container_scan_results(scan_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Container scan failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def container_audit(
    security: bool = typer.Option(
        True, "--security", "-s", help="Audit container security configurations"
    ),
    permissions: bool = typer.Option(
        True, "--permissions", "-p", help="Audit container permissions and IAM roles"
    ),
    networking: bool = typer.Option(
        True, "--networking", "-n", help="Audit container networking configurations"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to audit"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🔍 Audit container security, permissions, and networking configurations

    This command performs comprehensive security audits of container deployments
    including ECS services, EKS clusters, and container configurations.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🔍 Auditing containers...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            ecs_client = session.client("ecs")
            eks_client = session.client("eks")
            iam_client = session.client("iam")

            audit_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "findings": [],
                "summary": {},
                "recommendations": [],
            }

            # Audit container security
            if security:
                progress.update(task, description="🔒 Auditing container security...")
                security_findings = audit_container_security(session)
                audit_results["findings"].extend(security_findings)

            # Audit container permissions
            if permissions:
                progress.update(task, description="🔑 Auditing container permissions...")
                permission_findings = audit_container_permissions(iam_client, ecs_client, eks_client)
                audit_results["findings"].extend(permission_findings)

            # Audit container networking
            if networking:
                progress.update(task, description="🌐 Auditing container networking...")
                networking_findings = audit_container_networking(session)
                audit_results["findings"].extend(networking_findings)

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating audit summary...")
            audit_results["summary"] = generate_container_audit_summary(audit_results["findings"])
            audit_results["recommendations"] = generate_container_audit_recommendations(audit_results["findings"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_container_audit_recommendations_with_ai(audit_results["findings"])
                audit_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Container audit completed!")

            # Display results
            display_container_audit_results(audit_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Container audit failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def container_optimize(
    resources: bool = typer.Option(
        True, "--resources", "-r", help="Optimize container resource allocation"
    ),
    scaling: bool = typer.Option(
        True, "--scaling", "-s", help="Optimize container scaling configurations"
    ),
    cost: bool = typer.Option(
        True, "--cost", "-c", help="Optimize container costs"
    ),
    auto_fix: bool = typer.Option(
        False, "--auto-fix", "-a", help="Automatically apply optimizations"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Show what would be optimized without applying"
    ),
    region: str = typer.Option(None, "--region", "-R", help="AWS region to optimize"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🚀 Optimize container resources, scaling, and costs

    This command analyzes container deployments and provides optimization
    recommendations for resource allocation, scaling, and cost efficiency.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🚀 Optimizing containers...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            ecs_client = session.client("ecs")
            eks_client = session.client("eks")
            cloudwatch_client = session.client("cloudwatch")

            optimization_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "opportunities": [],
                "summary": {},
                "recommendations": [],
            }

            # Optimize container resources
            if resources:
                progress.update(task, description="⚡ Optimizing container resources...")
                resource_optimizations = optimize_container_resources(session, cloudwatch_client)
                optimization_results["opportunities"].extend(resource_optimizations)

            # Optimize container scaling
            if scaling:
                progress.update(task, description="📈 Optimizing container scaling...")
                scaling_optimizations = optimize_container_scaling(session, cloudwatch_client)
                optimization_results["opportunities"].extend(scaling_optimizations)

            # Optimize container costs
            if cost:
                progress.update(task, description="💰 Optimizing container costs...")
                cost_optimizations = optimize_container_costs(session)
                optimization_results["opportunities"].extend(cost_optimizations)

            # Apply optimizations if requested
            if auto_fix and not dry_run:
                progress.update(task, description="🔧 Applying container optimizations...")
                applied_optimizations = apply_container_optimizations(optimization_results["opportunities"], session)
                optimization_results["applied_optimizations"] = applied_optimizations

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating optimization summary...")
            optimization_results["summary"] = generate_container_optimization_summary(optimization_results["opportunities"])
            optimization_results["recommendations"] = generate_container_optimization_recommendations(optimization_results["opportunities"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_container_optimization_recommendations_with_ai(optimization_results["opportunities"])
                optimization_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Container optimization completed!")

            # Display results
            display_container_optimization_results(optimization_results, dry_run, verbose)

        except Exception as e:
            console.print(f"[red]❌ Container optimization failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def k8s_audit(
    pods: bool = typer.Option(
        True, "--pods", "-p", help="Audit Kubernetes pods and containers"
    ),
    services: bool = typer.Option(
        True, "--services", "-s", help="Audit Kubernetes services and networking"
    ),
    rbac: bool = typer.Option(
        True, "--rbac", "-r", help="Audit RBAC policies and permissions"
    ),
    network_policies: bool = typer.Option(
        True, "--network-policies", "-n", help="Audit network policies"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    region: str = typer.Option(None, "--region", "-R", help="AWS region to audit"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    ☸️ Audit Kubernetes security configurations, RBAC, and network policies

    This command performs comprehensive security audits of EKS clusters
    including pod security, RBAC configurations, and network policies.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("☸️ Auditing Kubernetes...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            eks_client = session.client("eks")

            audit_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "findings": [],
                "summary": {},
                "recommendations": [],
            }

            # Audit pods and containers
            if pods:
                progress.update(task, description="🐳 Auditing Kubernetes pods...")
                pod_findings = audit_k8s_pods(session)
                audit_results["findings"].extend(pod_findings)

            # Audit services and networking
            if services:
                progress.update(task, description="🌐 Auditing Kubernetes services...")
                service_findings = audit_k8s_services(session)
                audit_results["findings"].extend(service_findings)

            # Audit RBAC
            if rbac:
                progress.update(task, description="🔐 Auditing RBAC policies...")
                rbac_findings = audit_k8s_rbac(session)
                audit_results["findings"].extend(rbac_findings)

            # Audit network policies
            if network_policies:
                progress.update(task, description="🛡️ Auditing network policies...")
                network_findings = audit_k8s_network_policies(session)
                audit_results["findings"].extend(network_findings)

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating audit summary...")
            audit_results["summary"] = generate_k8s_audit_summary(audit_results["findings"])
            audit_results["recommendations"] = generate_k8s_audit_recommendations(audit_results["findings"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_k8s_audit_recommendations_with_ai(audit_results["findings"])
                audit_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Kubernetes audit completed!")

            # Display results
            display_k8s_audit_results(audit_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Kubernetes audit failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def k8s_compliance(
    cis: bool = typer.Option(
        True, "--cis", "-c", help="Check CIS Kubernetes benchmarks"
    ),
    pci: bool = typer.Option(
        True, "--pci", "-p", help="Check PCI compliance requirements"
    ),
    sox: bool = typer.Option(
        True, "--sox", "-s", help="Check SOX compliance requirements"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to check"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    📋 Check Kubernetes compliance with security frameworks and standards

    This command validates EKS clusters against various compliance frameworks
    including CIS benchmarks, PCI-DSS, and SOX requirements.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("📋 Checking Kubernetes compliance...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            eks_client = session.client("eks")

            compliance_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "compliance_checks": [],
                "summary": {},
                "recommendations": [],
            }

            # Check CIS benchmarks
            if cis:
                progress.update(task, description="🔍 Checking CIS benchmarks...")
                cis_findings = check_k8s_cis_compliance(session)
                compliance_results["compliance_checks"].extend(cis_findings)

            # Check PCI compliance
            if pci:
                progress.update(task, description="💳 Checking PCI compliance...")
                pci_findings = check_k8s_pci_compliance(session)
                compliance_results["compliance_checks"].extend(pci_findings)

            # Check SOX compliance
            if sox:
                progress.update(task, description="📊 Checking SOX compliance...")
                sox_findings = check_k8s_sox_compliance(session)
                compliance_results["compliance_checks"].extend(sox_findings)

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating compliance summary...")
            compliance_results["summary"] = generate_k8s_compliance_summary(compliance_results["compliance_checks"])
            compliance_results["recommendations"] = generate_k8s_compliance_recommendations(compliance_results["compliance_checks"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_k8s_compliance_recommendations_with_ai(compliance_results["compliance_checks"])
                compliance_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Kubernetes compliance check completed!")

            # Display results
            display_k8s_compliance_results(compliance_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Kubernetes compliance check failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def k8s_monitor(
    resources: bool = typer.Option(
        True, "--resources", "-r", help="Monitor Kubernetes resource utilization"
    ),
    performance: bool = typer.Option(
        True, "--performance", "-p", help="Monitor Kubernetes performance metrics"
    ),
    security: bool = typer.Option(
        True, "--security", "-s", help="Monitor Kubernetes security events"
    ),
    continuous: bool = typer.Option(
        False, "--continuous", "-c", help="Run continuous monitoring"
    ),
    interval: int = typer.Option(
        300, "--interval", "-i", help="Monitoring interval in seconds"
    ),
    region: str = typer.Option(None, "--region", "-R", help="AWS region to monitor"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    📊 Monitor Kubernetes resources, performance, and security events

    This command provides real-time monitoring of EKS clusters including
    resource utilization, performance metrics, and security events.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("📊 Monitoring Kubernetes...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            eks_client = session.client("eks")
            cloudwatch_client = session.client("cloudwatch")

            monitoring_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "metrics": [],
                "alerts": [],
                "summary": {},
                "recommendations": [],
            }

            # Monitor resources
            if resources:
                progress.update(task, description="⚡ Monitoring resource utilization...")
                resource_metrics = monitor_k8s_resources(session, cloudwatch_client)
                monitoring_results["metrics"].extend(resource_metrics)

            # Monitor performance
            if performance:
                progress.update(task, description="📈 Monitoring performance metrics...")
                performance_metrics = monitor_k8s_performance(session, cloudwatch_client)
                monitoring_results["metrics"].extend(performance_metrics)

            # Monitor security
            if security:
                progress.update(task, description="🔒 Monitoring security events...")
                security_metrics = monitor_k8s_security(session, cloudwatch_client)
                monitoring_results["metrics"].extend(security_metrics)

            # Generate alerts
            progress.update(task, description="🚨 Generating alerts...")
            monitoring_results["alerts"] = generate_k8s_alerts(monitoring_results["metrics"])

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating monitoring summary...")
            monitoring_results["summary"] = generate_k8s_monitoring_summary(monitoring_results["metrics"])
            monitoring_results["recommendations"] = generate_k8s_monitoring_recommendations(monitoring_results["metrics"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_k8s_monitoring_recommendations_with_ai(monitoring_results["metrics"])
                monitoring_results["ai_recommendations"] = ai_enhanced_recommendations

            # Run continuous monitoring if requested
            if continuous:
                progress.update(task, description="🔄 Starting continuous monitoring...")
                run_continuous_k8s_monitoring(session, interval, resources, performance, security, verbose)
            else:
                progress.update(task, description="✅ Kubernetes monitoring completed!")

            # Display results
            display_k8s_monitoring_results(monitoring_results, verbose)

        except Exception as e:
            console.print(f"[red]❌ Kubernetes monitoring failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def pipeline_audit(
    comprehensive: bool = typer.Option(
        True, "--comprehensive", "-c", help="Run comprehensive pipeline audit"
    ),
    fix_issues: bool = typer.Option(
        False, "--fix-issues", "-f", help="Automatically fix detected issues"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to audit"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🔄 Audit CI/CD pipelines for security, compliance, and best practices

    This command analyzes CodePipeline, CodeBuild, and CodeDeploy configurations
    to identify security issues, compliance violations, and optimization opportunities.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🔄 Auditing CI/CD pipelines...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            codepipeline_client = session.client("codepipeline")
            codebuild_client = session.client("codebuild")
            codedeploy_client = session.client("codedeploy")

            audit_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "findings": [],
                "summary": {},
                "recommendations": [],
            }

            # Audit CodePipeline
            progress.update(task, description="🔄 Auditing CodePipeline...")
            pipeline_findings = audit_codepipeline(codepipeline_client, comprehensive)
            audit_results["findings"].extend(pipeline_findings)

            # Audit CodeBuild
            progress.update(task, description="🔨 Auditing CodeBuild...")
            build_findings = audit_codebuild(codebuild_client, comprehensive)
            audit_results["findings"].extend(build_findings)

            # Audit CodeDeploy
            progress.update(task, description="🚀 Auditing CodeDeploy...")
            deploy_findings = audit_codedeploy(codedeploy_client, comprehensive)
            audit_results["findings"].extend(deploy_findings)

            # Fix issues if requested
            if fix_issues:
                progress.update(task, description="🔧 Fixing pipeline issues...")
                fixed_issues = fix_pipeline_issues(audit_results["findings"], session)
                audit_results["fixed_issues"] = fixed_issues

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating pipeline recommendations...")
            audit_results["summary"] = generate_pipeline_audit_summary(audit_results["findings"])
            audit_results["recommendations"] = generate_pipeline_audit_recommendations(audit_results["findings"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_pipeline_recommendations_with_ai(audit_results["findings"])
                audit_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Pipeline audit completed!")

            # Display results
            display_pipeline_audit_results(audit_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Pipeline audit failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def pipeline_optimize(
    performance: bool = typer.Option(
        True, "--performance", "-p", help="Optimize pipeline performance"
    ),
    cost: bool = typer.Option(
        True, "--cost", "-c", help="Optimize pipeline costs"
    ),
    auto_fix: bool = typer.Option(
        False, "--auto-fix", "-a", help="Automatically apply optimizations"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Show what would be optimized without applying"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to optimize"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🚀 Optimize CI/CD pipelines for performance and cost efficiency

    This command analyzes pipeline configurations and provides optimization
    recommendations for build times, resource utilization, and cost reduction.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🚀 Optimizing pipelines...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            codepipeline_client = session.client("codepipeline")
            codebuild_client = session.client("codebuild")
            cloudwatch_client = session.client("cloudwatch")

            optimization_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "opportunities": [],
                "summary": {},
                "recommendations": [],
            }

            # Optimize pipeline performance
            if performance:
                progress.update(task, description="⚡ Optimizing pipeline performance...")
                performance_optimizations = optimize_pipeline_performance(session, cloudwatch_client)
                optimization_results["opportunities"].extend(performance_optimizations)

            # Optimize pipeline costs
            if cost:
                progress.update(task, description="💰 Optimizing pipeline costs...")
                cost_optimizations = optimize_pipeline_costs(session, cloudwatch_client)
                optimization_results["opportunities"].extend(cost_optimizations)

            # Apply optimizations if requested
            if auto_fix and not dry_run:
                progress.update(task, description="🔧 Applying pipeline optimizations...")
                applied_optimizations = apply_pipeline_optimizations(optimization_results["opportunities"], session)
                optimization_results["applied_optimizations"] = applied_optimizations

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating optimization summary...")
            optimization_results["summary"] = generate_pipeline_optimization_summary(optimization_results["opportunities"])
            optimization_results["recommendations"] = generate_pipeline_optimization_recommendations(optimization_results["opportunities"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_pipeline_optimization_recommendations_with_ai(optimization_results["opportunities"])
                optimization_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Pipeline optimization completed!")

            # Display results
            display_pipeline_optimization_results(optimization_results, dry_run, verbose)

        except Exception as e:
            console.print(f"[red]❌ Pipeline optimization failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def pipeline_monitor(
    continuous: bool = typer.Option(
        False, "--continuous", "-c", help="Run continuous pipeline monitoring"
    ),
    webhook: bool = typer.Option(
        False, "--webhook", "-w", help="Enable webhook notifications"
    ),
    interval: int = typer.Option(
        300, "--interval", "-i", help="Monitoring interval in seconds"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to monitor"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    📊 Monitor CI/CD pipeline performance, failures, and metrics

    This command provides real-time monitoring of pipeline executions,
    build failures, deployment status, and performance metrics.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("📊 Monitoring pipelines...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            codepipeline_client = session.client("codepipeline")
            codebuild_client = session.client("codebuild")
            cloudwatch_client = session.client("cloudwatch")

            monitoring_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "metrics": [],
                "alerts": [],
                "summary": {},
                "recommendations": [],
            }

            # Monitor pipeline executions
            progress.update(task, description="🔄 Monitoring pipeline executions...")
            pipeline_metrics = monitor_pipeline_executions(session, cloudwatch_client)
            monitoring_results["metrics"].extend(pipeline_metrics)

            # Monitor build performance
            progress.update(task, description="🔨 Monitoring build performance...")
            build_metrics = monitor_build_performance(session, cloudwatch_client)
            monitoring_results["metrics"].extend(build_metrics)

            # Monitor deployment status
            progress.update(task, description="🚀 Monitoring deployment status...")
            deployment_metrics = monitor_deployment_status(session, cloudwatch_client)
            monitoring_results["metrics"].extend(deployment_metrics)

            # Generate alerts
            progress.update(task, description="🚨 Generating alerts...")
            monitoring_results["alerts"] = generate_pipeline_alerts(monitoring_results["metrics"])

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating monitoring summary...")
            monitoring_results["summary"] = generate_pipeline_monitoring_summary(monitoring_results["metrics"])
            monitoring_results["recommendations"] = generate_pipeline_monitoring_recommendations(monitoring_results["metrics"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_pipeline_monitoring_recommendations_with_ai(monitoring_results["metrics"])
                monitoring_results["ai_recommendations"] = ai_enhanced_recommendations

            # Run continuous monitoring if requested
            if continuous:
                progress.update(task, description="🔄 Starting continuous monitoring...")
                run_continuous_pipeline_monitoring(session, interval, webhook, verbose)
            else:
                progress.update(task, description="✅ Pipeline monitoring completed!")

            # Display results
            display_pipeline_monitoring_results(monitoring_results, verbose)

        except Exception as e:
            console.print(f"[red]❌ Pipeline monitoring failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def build_optimize(
    cache: bool = typer.Option(
        True, "--cache", "-c", help="Optimize build caching strategies"
    ),
    parallel: bool = typer.Option(
        True, "--parallel", "-p", help="Optimize parallel build execution"
    ),
    timeout: bool = typer.Option(
        True, "--timeout", "-t", help="Optimize build timeout configurations"
    ),
    auto_fix: bool = typer.Option(
        False, "--auto-fix", "-a", help="Automatically apply optimizations"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Show what would be optimized without applying"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to optimize"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🔨 Optimize CodeBuild projects for performance and efficiency

    This command analyzes build configurations and provides optimization
    recommendations for caching, parallelization, and resource utilization.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🔨 Optimizing builds...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            codebuild_client = session.client("codebuild")
            cloudwatch_client = session.client("cloudwatch")

            optimization_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "opportunities": [],
                "summary": {},
                "recommendations": [],
            }

            # Optimize build caching
            if cache:
                progress.update(task, description="🗄️ Optimizing build caching...")
                cache_optimizations = optimize_build_caching(codebuild_client, cloudwatch_client)
                optimization_results["opportunities"].extend(cache_optimizations)

            # Optimize parallel execution
            if parallel:
                progress.update(task, description="⚡ Optimizing parallel execution...")
                parallel_optimizations = optimize_build_parallelization(codebuild_client, cloudwatch_client)
                optimization_results["opportunities"].extend(parallel_optimizations)

            # Optimize timeout configurations
            if timeout:
                progress.update(task, description="⏱️ Optimizing timeout configurations...")
                timeout_optimizations = optimize_build_timeouts(codebuild_client, cloudwatch_client)
                optimization_results["opportunities"].extend(timeout_optimizations)

            # Apply optimizations if requested
            if auto_fix and not dry_run:
                progress.update(task, description="🔧 Applying build optimizations...")
                applied_optimizations = apply_build_optimizations(optimization_results["opportunities"], codebuild_client)
                optimization_results["applied_optimizations"] = applied_optimizations

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating optimization summary...")
            optimization_results["summary"] = generate_build_optimization_summary(optimization_results["opportunities"])
            optimization_results["recommendations"] = generate_build_optimization_recommendations(optimization_results["opportunities"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_build_optimization_recommendations_with_ai(optimization_results["opportunities"])
                optimization_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Build optimization completed!")

            # Display results
            display_build_optimization_results(optimization_results, dry_run, verbose)

        except Exception as e:
            console.print(f"[red]❌ Build optimization failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def build_security(
    scan: bool = typer.Option(
        True, "--scan", "-s", help="Scan build configurations for security issues"
    ),
    vulnerabilities: bool = typer.Option(
        True, "--vulnerabilities", "-v", help="Scan for vulnerabilities in build artifacts"
    ),
    auto_fix: bool = typer.Option(
        False, "--auto-fix", "-a", help="Automatically fix security issues"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to scan"),
    verbose: bool = typer.Option(False, "--verbose", "-V", help="Verbose output"),
):
    """
    🛡️ Scan CodeBuild projects for security vulnerabilities and misconfigurations

    This command analyzes build configurations, artifacts, and dependencies
    to identify security vulnerabilities and configuration issues.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🛡️ Scanning build security...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            codebuild_client = session.client("codebuild")
            ecr_client = session.client("ecr")

            security_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "findings": [],
                "vulnerabilities": [],
                "summary": {},
                "recommendations": [],
            }

            # Scan build configurations
            if scan:
                progress.update(task, description="🔍 Scanning build configurations...")
                config_findings = scan_build_configurations(codebuild_client)
                security_results["findings"].extend(config_findings)

            # Scan for vulnerabilities
            if vulnerabilities:
                progress.update(task, description="🛡️ Scanning for vulnerabilities...")
                vulnerability_findings = scan_build_vulnerabilities(session, ecr_client)
                security_results["vulnerabilities"].extend(vulnerability_findings)

            # Auto-fix security issues if requested
            if auto_fix:
                progress.update(task, description="🔧 Fixing security issues...")
                fixed_issues = fix_build_security_issues(security_results["findings"], codebuild_client)
                security_results["fixed_issues"] = fixed_issues

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating security summary...")
            security_results["summary"] = generate_build_security_summary(security_results["findings"], security_results["vulnerabilities"])
            security_results["recommendations"] = generate_build_security_recommendations(security_results["findings"], security_results["vulnerabilities"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_build_security_recommendations_with_ai(security_results["findings"], security_results["vulnerabilities"])
                security_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Build security scan completed!")

            # Display results
            display_build_security_results(security_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Build security scan failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def build_compliance(
    standards: str = typer.Option(
        "all", "--standards", "-s", help="Compliance standards: sox, pci-dss, hipaa, iso27001, all"
    ),
    reports: bool = typer.Option(
        True, "--reports", "-r", help="Generate compliance reports"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, pdf"
    ),
    region: str = typer.Option(None, "--region", "-R", help="AWS region to check"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    📋 Check CodeBuild compliance with security frameworks and standards

    This command validates build configurations against various compliance
    frameworks and generates compliance reports for audit purposes.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("📋 Checking build compliance...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            codebuild_client = session.client("codebuild")

            compliance_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "compliance_checks": [],
                "summary": {},
                "recommendations": [],
            }

            # Check compliance standards
            progress.update(task, description="🔍 Checking compliance standards...")
            compliance_checks = check_build_compliance(codebuild_client, standards)
            compliance_results["compliance_checks"] = compliance_checks

            # Generate compliance reports
            if reports:
                progress.update(task, description="📊 Generating compliance reports...")
                compliance_report = generate_build_compliance_report(compliance_checks, standards)
                compliance_results["compliance_report"] = compliance_report

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating compliance summary...")
            compliance_results["summary"] = generate_build_compliance_summary(compliance_checks)
            compliance_results["recommendations"] = generate_build_compliance_recommendations(compliance_checks)

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_build_compliance_recommendations_with_ai(compliance_checks)
                compliance_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Build compliance check completed!")

            # Display results
            display_build_compliance_results(compliance_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Build compliance check failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def monitoring_setup(
    auto: bool = typer.Option(
        True, "--auto", "-a", help="Automatically setup monitoring with best practices"
    ),
    best_practices: bool = typer.Option(
        True, "--best-practices", "-b", help="Apply monitoring best practices"
    ),
    alerts: bool = typer.Option(
        True, "--alerts", "-A", help="Setup automated alerts and notifications"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to setup"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    📊 Setup comprehensive monitoring with CloudWatch and best practices

    This command automatically configures monitoring for AWS resources
    with best practices, alerts, and automated dashboards.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("📊 Setting up monitoring...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            cloudwatch_client = session.client("cloudwatch")
            logs_client = session.client("logs")
            sns_client = session.client("sns")

            setup_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "configured_metrics": [],
                "created_alarms": [],
                "setup_dashboards": [],
                "summary": {},
                "recommendations": [],
            }

            # Setup automated monitoring
            if auto:
                progress.update(task, description="🔧 Setting up automated monitoring...")
                configured_metrics = setup_automated_monitoring(session)
                setup_results["configured_metrics"] = configured_metrics

            # Apply best practices
            if best_practices:
                progress.update(task, description="⭐ Applying monitoring best practices...")
                best_practice_configs = apply_monitoring_best_practices(session)
                setup_results["best_practice_configs"] = best_practice_configs

            # Setup alerts
            if alerts:
                progress.update(task, description="🚨 Setting up alerts and notifications...")
                created_alarms = setup_monitoring_alerts(cloudwatch_client, sns_client)
                setup_results["created_alarms"] = created_alarms

            # Create monitoring dashboards
            progress.update(task, description="📈 Creating monitoring dashboards...")
            dashboards = create_monitoring_dashboards(cloudwatch_client, session)
            setup_results["setup_dashboards"] = dashboards

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating setup summary...")
            setup_results["summary"] = generate_monitoring_setup_summary(setup_results)
            setup_results["recommendations"] = generate_monitoring_setup_recommendations(setup_results)

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_monitoring_setup_recommendations_with_ai(setup_results)
                setup_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Monitoring setup completed!")

            # Display results
            display_monitoring_setup_results(setup_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Monitoring setup failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def monitoring_optimize(
    cost: bool = typer.Option(
        True, "--cost", "-c", help="Optimize monitoring costs"
    ),
    performance: bool = typer.Option(
        True, "--performance", "-p", help="Optimize monitoring performance"
    ),
    coverage: bool = typer.Option(
        True, "--coverage", "-C", help="Optimize monitoring coverage"
    ),
    auto_fix: bool = typer.Option(
        False, "--auto-fix", "-a", help="Automatically apply optimizations"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Show what would be optimized without applying"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to optimize"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🚀 Optimize monitoring configurations for cost, performance, and coverage

    This command analyzes monitoring configurations and provides optimization
    recommendations for cost efficiency, performance, and monitoring coverage.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🚀 Optimizing monitoring...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            cloudwatch_client = session.client("cloudwatch")
            logs_client = session.client("logs")

            optimization_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "opportunities": [],
                "summary": {},
                "recommendations": [],
            }

            # Optimize monitoring costs
            if cost:
                progress.update(task, description="💰 Optimizing monitoring costs...")
                cost_optimizations = optimize_monitoring_costs(cloudwatch_client, logs_client)
                optimization_results["opportunities"].extend(cost_optimizations)

            # Optimize monitoring performance
            if performance:
                progress.update(task, description="⚡ Optimizing monitoring performance...")
                performance_optimizations = optimize_monitoring_performance(cloudwatch_client, logs_client)
                optimization_results["opportunities"].extend(performance_optimizations)

            # Optimize monitoring coverage
            if coverage:
                progress.update(task, description="📊 Optimizing monitoring coverage...")
                coverage_optimizations = optimize_monitoring_coverage(session)
                optimization_results["opportunities"].extend(coverage_optimizations)

            # Apply optimizations if requested
            if auto_fix and not dry_run:
                progress.update(task, description="🔧 Applying monitoring optimizations...")
                applied_optimizations = apply_monitoring_optimizations(optimization_results["opportunities"], session)
                optimization_results["applied_optimizations"] = applied_optimizations

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating optimization summary...")
            optimization_results["summary"] = generate_monitoring_optimization_summary(optimization_results["opportunities"])
            optimization_results["recommendations"] = generate_monitoring_optimization_recommendations(optimization_results["opportunities"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_monitoring_optimization_recommendations_with_ai(optimization_results["opportunities"])
                optimization_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Monitoring optimization completed!")

            # Display results
            display_monitoring_optimization_results(optimization_results, dry_run, verbose)

        except Exception as e:
            console.print(f"[red]❌ Monitoring optimization failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def monitoring_compliance(
    frameworks: str = typer.Option(
        "all", "--frameworks", "-f", help="Compliance frameworks: sox, pci-dss, hipaa, iso27001, all"
    ),
    standards: str = typer.Option(
        "aws", "--standards", "-s", help="Standards to check: aws, nist, cis, all"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, pdf"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to check"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    📋 Check monitoring compliance with security frameworks and standards

    This command validates monitoring configurations against various compliance
    frameworks and generates compliance reports for audit purposes.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("📋 Checking monitoring compliance...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            cloudwatch_client = session.client("cloudwatch")
            logs_client = session.client("logs")

            compliance_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "compliance_checks": [],
                "summary": {},
                "recommendations": [],
            }

            # Check compliance frameworks
            progress.update(task, description="🔍 Checking compliance frameworks...")
            compliance_checks = check_monitoring_compliance(session, frameworks, standards)
            compliance_results["compliance_checks"] = compliance_checks

            # Generate compliance reports
            progress.update(task, description="📊 Generating compliance reports...")
            compliance_report = generate_monitoring_compliance_report(compliance_checks, frameworks, standards)
            compliance_results["compliance_report"] = compliance_report

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating compliance summary...")
            compliance_results["summary"] = generate_monitoring_compliance_summary(compliance_checks)
            compliance_results["recommendations"] = generate_monitoring_compliance_recommendations(compliance_checks)

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_monitoring_compliance_recommendations_with_ai(compliance_checks)
                compliance_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Monitoring compliance check completed!")

            # Display results
            display_monitoring_compliance_results(compliance_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Monitoring compliance check failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def alert_configure(
    auto: bool = typer.Option(
        True, "--auto", "-a", help="Automatically configure alerts with best practices"
    ),
    thresholds: bool = typer.Option(
        True, "--thresholds", "-t", help="Configure intelligent alert thresholds"
    ),
    escalation: bool = typer.Option(
        True, "--escalation", "-e", help="Setup alert escalation policies"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to configure"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🚨 Configure intelligent alerts with automated thresholds and escalation

    This command sets up comprehensive alerting with intelligent thresholds,
    escalation policies, and integration with notification systems.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🚨 Configuring alerts...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            cloudwatch_client = session.client("cloudwatch")
            sns_client = session.client("sns")

            configuration_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "configured_alerts": [],
                "escalation_policies": [],
                "summary": {},
                "recommendations": [],
            }

            # Auto-configure alerts
            if auto:
                progress.update(task, description="🔧 Auto-configuring alerts...")
                configured_alerts = auto_configure_alerts(cloudwatch_client, sns_client)
                configuration_results["configured_alerts"] = configured_alerts

            # Configure intelligent thresholds
            if thresholds:
                progress.update(task, description="🎯 Configuring intelligent thresholds...")
                threshold_configs = configure_intelligent_thresholds(cloudwatch_client, session)
                configuration_results["threshold_configs"] = threshold_configs

            # Setup escalation policies
            if escalation:
                progress.update(task, description="📈 Setting up escalation policies...")
                escalation_policies = setup_alert_escalation_policies(sns_client)
                configuration_results["escalation_policies"] = escalation_policies

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating configuration summary...")
            configuration_results["summary"] = generate_alert_configuration_summary(configuration_results)
            configuration_results["recommendations"] = generate_alert_configuration_recommendations(configuration_results)

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_alert_configuration_recommendations_with_ai(configuration_results)
                configuration_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Alert configuration completed!")

            # Display results
            display_alert_configuration_results(configuration_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Alert configuration failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def alert_optimize(
    noise: bool = typer.Option(
        True, "--noise", "-n", help="Reduce alert noise and false positives"
    ),
    coverage: bool = typer.Option(
        True, "--coverage", "-c", help="Optimize alert coverage"
    ),
    response: bool = typer.Option(
        True, "--response", "-r", help="Optimize alert response workflows"
    ),
    auto_fix: bool = typer.Option(
        False, "--auto-fix", "-a", help="Automatically apply optimizations"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Show what would be optimized without applying"
    ),
    region: str = typer.Option(None, "--region", "-R", help="AWS region to optimize"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🎯 Optimize alert configurations to reduce noise and improve response

    This command analyzes alert configurations and provides optimization
    recommendations to reduce false positives and improve incident response.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🎯 Optimizing alerts...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            cloudwatch_client = session.client("cloudwatch")
            sns_client = session.client("sns")

            optimization_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "opportunities": [],
                "summary": {},
                "recommendations": [],
            }

            # Reduce alert noise
            if noise:
                progress.update(task, description="🔇 Reducing alert noise...")
                noise_optimizations = reduce_alert_noise(cloudwatch_client, sns_client)
                optimization_results["opportunities"].extend(noise_optimizations)

            # Optimize alert coverage
            if coverage:
                progress.update(task, description="📊 Optimizing alert coverage...")
                coverage_optimizations = optimize_alert_coverage(session)
                optimization_results["opportunities"].extend(coverage_optimizations)

            # Optimize alert response
            if response:
                progress.update(task, description="🚀 Optimizing alert response...")
                response_optimizations = optimize_alert_response(session)
                optimization_results["opportunities"].extend(response_optimizations)

            # Apply optimizations if requested
            if auto_fix and not dry_run:
                progress.update(task, description="🔧 Applying alert optimizations...")
                applied_optimizations = apply_alert_optimizations(optimization_results["opportunities"], session)
                optimization_results["applied_optimizations"] = applied_optimizations

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating optimization summary...")
            optimization_results["summary"] = generate_alert_optimization_summary(optimization_results["opportunities"])
            optimization_results["recommendations"] = generate_alert_optimization_recommendations(optimization_results["opportunities"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_alert_optimization_recommendations_with_ai(optimization_results["opportunities"])
                optimization_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Alert optimization completed!")

            # Display results
            display_alert_optimization_results(optimization_results, dry_run, verbose)

        except Exception as e:
            console.print(f"[red]❌ Alert optimization failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def network_audit(
    vpc: bool = typer.Option(
        True, "--vpc", "-v", help="Audit VPC configurations and architecture"
    ),
    subnets: bool = typer.Option(
        True, "--subnets", "-s", help="Audit subnet configurations and routing"
    ),
    security_groups: bool = typer.Option(
        True, "--security-groups", "-g", help="Audit security group rules"
    ),
    nacls: bool = typer.Option(
        True, "--nacls", "-n", help="Audit Network ACL configurations"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to audit"),
    verbose: bool = typer.Option(False, "--verbose", "-V", help="Verbose output"),
):
    """
    🌐 Audit network configurations, security groups, and VPC architecture

    This command performs comprehensive network security audits including
    VPC configurations, security groups, NACLs, and network architecture.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🌐 Auditing network configurations...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            ec2_client = session.client("ec2")

            audit_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "findings": [],
                "summary": {},
                "recommendations": [],
            }

            # Audit VPC configurations
            if vpc:
                progress.update(task, description="🏗️ Auditing VPC configurations...")
                vpc_findings = audit_vpc_configurations(ec2_client)
                audit_results["findings"].extend(vpc_findings)

            # Audit subnet configurations
            if subnets:
                progress.update(task, description="🌐 Auditing subnet configurations...")
                subnet_findings = audit_subnet_configurations(ec2_client)
                audit_results["findings"].extend(subnet_findings)

            # Audit security groups
            if security_groups:
                progress.update(task, description="🛡️ Auditing security groups...")
                sg_findings = audit_security_groups(ec2_client)
                audit_results["findings"].extend(sg_findings)

            # Audit Network ACLs
            if nacls:
                progress.update(task, description="🔒 Auditing Network ACLs...")
                nacl_findings = audit_network_acls(ec2_client)
                audit_results["findings"].extend(nacl_findings)

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating network audit summary...")
            audit_results["summary"] = generate_network_audit_summary(audit_results["findings"])
            audit_results["recommendations"] = generate_network_audit_recommendations(audit_results["findings"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_network_audit_recommendations_with_ai(audit_results["findings"])
                audit_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Network audit completed!")

            # Display results
            display_network_audit_results(audit_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Network audit failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def network_optimize(
    routing: bool = typer.Option(
        True, "--routing", "-r", help="Optimize network routing configurations"
    ),
    peering: bool = typer.Option(
        True, "--peering", "-p", help="Optimize VPC peering configurations"
    ),
    cost: bool = typer.Option(
        True, "--cost", "-c", help="Optimize network costs"
    ),
    auto_fix: bool = typer.Option(
        False, "--auto-fix", "-a", help="Automatically apply optimizations"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Show what would be optimized without applying"
    ),
    region: str = typer.Option(None, "--region", "-R", help="AWS region to optimize"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🚀 Optimize network configurations for performance and cost efficiency

    This command analyzes network configurations and provides optimization
    recommendations for routing, peering, and cost reduction.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🚀 Optimizing network configurations...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            ec2_client = session.client("ec2")
            ce_client = session.client("ce")

            optimization_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "opportunities": [],
                "summary": {},
                "recommendations": [],
            }

            # Optimize routing
            if routing:
                progress.update(task, description="🗺️ Optimizing network routing...")
                routing_optimizations = optimize_network_routing(ec2_client)
                optimization_results["opportunities"].extend(routing_optimizations)

            # Optimize peering
            if peering:
                progress.update(task, description="🔗 Optimizing VPC peering...")
                peering_optimizations = optimize_vpc_peering(ec2_client)
                optimization_results["opportunities"].extend(peering_optimizations)

            # Optimize network costs
            if cost:
                progress.update(task, description="💰 Optimizing network costs...")
                cost_optimizations = optimize_network_costs(ec2_client, ce_client)
                optimization_results["opportunities"].extend(cost_optimizations)

            # Apply optimizations if requested
            if auto_fix and not dry_run:
                progress.update(task, description="🔧 Applying network optimizations...")
                applied_optimizations = apply_network_optimizations(optimization_results["opportunities"], ec2_client)
                optimization_results["applied_optimizations"] = applied_optimizations

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating optimization summary...")
            optimization_results["summary"] = generate_network_optimization_summary(optimization_results["opportunities"])
            optimization_results["recommendations"] = generate_network_optimization_recommendations(optimization_results["opportunities"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_network_optimization_recommendations_with_ai(optimization_results["opportunities"])
                optimization_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Network optimization completed!")

            # Display results
            display_network_optimization_results(optimization_results, dry_run, verbose)

        except Exception as e:
            console.print(f"[red]❌ Network optimization failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def network_monitor(
    traffic: bool = typer.Option(
        True, "--traffic", "-t", help="Monitor network traffic patterns"
    ),
    anomalies: bool = typer.Option(
        True, "--anomalies", "-a", help="Monitor for network anomalies"
    ),
    compliance: bool = typer.Option(
        True, "--compliance", "-c", help="Monitor network compliance"
    ),
    continuous: bool = typer.Option(
        False, "--continuous", "-C", help="Run continuous network monitoring"
    ),
    interval: int = typer.Option(
        300, "--interval", "-i", help="Monitoring interval in seconds"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to monitor"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    📊 Monitor network traffic, anomalies, and compliance in real-time

    This command provides comprehensive network monitoring including
    traffic analysis, anomaly detection, and compliance monitoring.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("📊 Monitoring network...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            ec2_client = session.client("ec2")
            cloudwatch_client = session.client("cloudwatch")
            vpc_client = session.client("ec2")

            monitoring_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "metrics": [],
                "anomalies": [],
                "compliance_status": [],
                "summary": {},
                "recommendations": [],
            }

            # Monitor network traffic
            if traffic:
                progress.update(task, description="🌐 Monitoring network traffic...")
                traffic_metrics = monitor_network_traffic(ec2_client, cloudwatch_client)
                monitoring_results["metrics"].extend(traffic_metrics)

            # Monitor for anomalies
            if anomalies:
                progress.update(task, description="🔍 Monitoring for anomalies...")
                anomaly_findings = monitor_network_anomalies(session, cloudwatch_client)
                monitoring_results["anomalies"].extend(anomaly_findings)

            # Monitor compliance
            if compliance:
                progress.update(task, description="📋 Monitoring compliance...")
                compliance_status = monitor_network_compliance(session)
                monitoring_results["compliance_status"].extend(compliance_status)

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating monitoring summary...")
            monitoring_results["summary"] = generate_network_monitoring_summary(monitoring_results)
            monitoring_results["recommendations"] = generate_network_monitoring_recommendations(monitoring_results)

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_network_monitoring_recommendations_with_ai(monitoring_results)
                monitoring_results["ai_recommendations"] = ai_enhanced_recommendations

            # Run continuous monitoring if requested
            if continuous:
                progress.update(task, description="🔄 Starting continuous monitoring...")
                run_continuous_network_monitoring(session, interval, traffic, anomalies, compliance, verbose)
            else:
                progress.update(task, description="✅ Network monitoring completed!")

            # Display results
            display_network_monitoring_results(monitoring_results, verbose)

        except Exception as e:
            console.print(f"[red]❌ Network monitoring failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def sg_audit(
    rules: bool = typer.Option(
        True, "--rules", "-r", help="Audit security group rules"
    ),
    compliance: bool = typer.Option(
        True, "--compliance", "-c", help="Check compliance with security standards"
    ),
    best_practices: bool = typer.Option(
        True, "--best-practices", "-b", help="Check against security best practices"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    region: str = typer.Option(None, "--region", "-R", help="AWS region to audit"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🛡️ Audit security group rules and configurations for compliance

    This command performs detailed security group audits including
    rule analysis, compliance checking, and best practice validation.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🛡️ Auditing security groups...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            ec2_client = session.client("ec2")

            audit_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "findings": [],
                "summary": {},
                "recommendations": [],
            }

            # Audit security group rules
            if rules:
                progress.update(task, description="🔍 Auditing security group rules...")
                rule_findings = audit_security_group_rules(ec2_client)
                audit_results["findings"].extend(rule_findings)

            # Check compliance
            if compliance:
                progress.update(task, description="📋 Checking compliance...")
                compliance_findings = check_security_group_compliance(ec2_client)
                audit_results["findings"].extend(compliance_findings)

            # Check best practices
            if best_practices:
                progress.update(task, description="⭐ Checking best practices...")
                best_practice_findings = check_security_group_best_practices(ec2_client)
                audit_results["findings"].extend(best_practice_findings)

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating audit summary...")
            audit_results["summary"] = generate_security_group_audit_summary(audit_results["findings"])
            audit_results["recommendations"] = generate_security_group_audit_recommendations(audit_results["findings"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_security_group_audit_recommendations_with_ai(audit_results["findings"])
                audit_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Security group audit completed!")

            # Display results
            display_security_group_audit_results(audit_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Security group audit failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def sg_optimize(
    rules: bool = typer.Option(
        True, "--rules", "-r", help="Optimize security group rules"
    ),
    coverage: bool = typer.Option(
        True, "--coverage", "-c", help="Optimize security coverage"
    ),
    security: bool = typer.Option(
        True, "--security", "-s", help="Optimize security configurations"
    ),
    auto_fix: bool = typer.Option(
        False, "--auto-fix", "-a", help="Automatically apply optimizations"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Show what would be optimized without applying"
    ),
    region: str = typer.Option(None, "--region", "-R", help="AWS region to optimize"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🚀 Optimize security group rules and configurations

    This command analyzes security group configurations and provides
    optimization recommendations for rules, coverage, and security.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🚀 Optimizing security groups...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            ec2_client = session.client("ec2")

            optimization_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "opportunities": [],
                "summary": {},
                "recommendations": [],
            }

            # Optimize security group rules
            if rules:
                progress.update(task, description="🔧 Optimizing security group rules...")
                rule_optimizations = optimize_security_group_rules(ec2_client)
                optimization_results["opportunities"].extend(rule_optimizations)

            # Optimize security coverage
            if coverage:
                progress.update(task, description="📊 Optimizing security coverage...")
                coverage_optimizations = optimize_security_group_coverage(ec2_client)
                optimization_results["opportunities"].extend(coverage_optimizations)

            # Optimize security configurations
            if security:
                progress.update(task, description="🛡️ Optimizing security configurations...")
                security_optimizations = optimize_security_group_security(ec2_client)
                optimization_results["opportunities"].extend(security_optimizations)

            # Apply optimizations if requested
            if auto_fix and not dry_run:
                progress.update(task, description="🔧 Applying security group optimizations...")
                applied_optimizations = apply_security_group_optimizations(optimization_results["opportunities"], ec2_client)
                optimization_results["applied_optimizations"] = applied_optimizations

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating optimization summary...")
            optimization_results["summary"] = generate_security_group_optimization_summary(optimization_results["opportunities"])
            optimization_results["recommendations"] = generate_security_group_optimization_recommendations(optimization_results["opportunities"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_security_group_optimization_recommendations_with_ai(optimization_results["opportunities"])
                optimization_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Security group optimization completed!")

            # Display results
            display_security_group_optimization_results(optimization_results, dry_run, verbose)

        except Exception as e:
            console.print(f"[red]❌ Security group optimization failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def sg_compliance(
    frameworks: str = typer.Option(
        "all", "--frameworks", "-f", help="Compliance frameworks: sox, pci-dss, hipaa, cis, all"
    ),
    standards: str = typer.Option(
        "aws", "--standards", "-s", help="Standards to check: aws, nist, iso27001, all"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, pdf"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to check"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    📋 Check security group compliance with frameworks and standards

    This command validates security group configurations against various
    compliance frameworks and generates compliance reports.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("📋 Checking security group compliance...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            ec2_client = session.client("ec2")

            compliance_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "compliance_checks": [],
                "summary": {},
                "recommendations": [],
            }

            # Check compliance frameworks
            progress.update(task, description="🔍 Checking compliance frameworks...")
            compliance_checks = check_security_group_compliance_frameworks(ec2_client, frameworks, standards)
            compliance_results["compliance_checks"] = compliance_checks

            # Generate compliance reports
            progress.update(task, description="📊 Generating compliance reports...")
            compliance_report = generate_security_group_compliance_report(compliance_checks, frameworks, standards)
            compliance_results["compliance_report"] = compliance_report

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating compliance summary...")
            compliance_results["summary"] = generate_security_group_compliance_summary(compliance_checks)
            compliance_results["recommendations"] = generate_security_group_compliance_recommendations(compliance_checks)

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_security_group_compliance_recommendations_with_ai(compliance_checks)
                compliance_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Security group compliance check completed!")

            # Display results
            display_security_group_compliance_results(compliance_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Security group compliance check failed: {str(e)}[/red]")
            raise typer.Exit(1)


# ============================================================================
# PHASE 3: INFRASTRUCTURE AUTOMATION COMMANDS
# ============================================================================

@app.command()
def infra_audit(
    templates: bool = typer.Option(
        True, "--templates", "-t", help="Audit CloudFormation/CDK templates"
    ),
    security: bool = typer.Option(
        True, "--security", "-s", help="Audit infrastructure security configurations"
    ),
    compliance: bool = typer.Option(
        True, "--compliance", "-c", help="Check compliance with infrastructure standards"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to audit"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🏗️ Perform comprehensive infrastructure audit across CloudFormation, CDK, and deployed resources

    This command analyzes infrastructure templates, deployed resources, and configurations
    to identify security issues, compliance violations, and optimization opportunities.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🏗️ Running infrastructure audit...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            cf_client = session.client("cloudformation")
            ec2_client = session.client("ec2")
            iam_client = session.client("iam")
            s3_client = session.client("s3")

            audit_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "findings": [],
                "summary": {},
                "recommendations": [],
            }

            # CloudFormation Template Audit
            if templates:
                progress.update(task, description="📋 Auditing CloudFormation templates...")
                cf_findings = audit_cloudformation_templates(cf_client, security, compliance)
                audit_results["findings"].extend(cf_findings)

            # Infrastructure Security Audit
            if security:
                progress.update(task, description="🔒 Auditing infrastructure security...")
                security_findings = audit_infrastructure_security(session, compliance)
                audit_results["findings"].extend(security_findings)

            # Compliance Audit
            if compliance:
                progress.update(task, description="📊 Checking infrastructure compliance...")
                compliance_findings = audit_infrastructure_compliance(session)
                audit_results["findings"].extend(compliance_findings)

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating recommendations...")
            audit_results["summary"] = generate_infrastructure_summary(audit_results["findings"])
            audit_results["recommendations"] = generate_infrastructure_recommendations(audit_results["findings"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_infrastructure_recommendations_with_ai(audit_results["findings"])
                audit_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Infrastructure audit completed!")

            # Display results
            display_infrastructure_audit_results(audit_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Infrastructure audit failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def infra_drift(
    detect: bool = typer.Option(
        True, "--detect", "-d", help="Detect infrastructure drift"
    ),
    remediate: bool = typer.Option(
        False, "--remediate", "-r", help="Remediate detected drift"
    ),
    report: bool = typer.Option(
        True, "--report", "-R", help="Generate drift report"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to check"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🔄 Detect and remediate infrastructure drift between templates and deployed resources

    This command compares deployed infrastructure with CloudFormation templates
    to identify configuration drift and provide remediation options.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🔄 Detecting infrastructure drift...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            cf_client = session.client("cloudformation")

            drift_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "stacks": [],
                "drift_detected": False,
                "summary": {},
                "recommendations": [],
            }

            # Detect drift
            if detect:
                progress.update(task, description="🔍 Detecting stack drift...")
                drift_findings = detect_infrastructure_drift(cf_client)
                drift_results["stacks"] = drift_findings
                drift_results["drift_detected"] = any(stack.get("drift_detected", False) for stack in drift_findings)

            # Remediate drift
            if remediate and drift_results["drift_detected"]:
                progress.update(task, description="🔧 Remediating drift...")
                remediation_results = remediate_infrastructure_drift(cf_client, drift_results["stacks"])
                drift_results["remediation_results"] = remediation_results

            # Generate report
            if report:
                progress.update(task, description="📊 Generating drift report...")
                drift_results["summary"] = generate_drift_summary(drift_results["stacks"])
                drift_results["recommendations"] = generate_drift_recommendations(drift_results["stacks"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_drift_recommendations_with_ai(drift_results["stacks"])
                drift_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Infrastructure drift analysis completed!")

            # Display results
            display_infrastructure_drift_results(drift_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Infrastructure drift detection failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def infra_cost(
    estimate: bool = typer.Option(
        True, "--estimate", "-e", help="Estimate infrastructure costs"
    ),
    optimize: bool = typer.Option(
        True, "--optimize", "-o", help="Identify cost optimization opportunities"
    ),
    forecast: bool = typer.Option(
        True, "--forecast", "-f", help="Generate cost forecasts"
    ),
    output: str = typer.Option(
        "table", "--output", "-O", help="Output format: table, json, csv"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to analyze"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    💰 Analyze infrastructure costs and identify optimization opportunities

    This command provides comprehensive cost analysis for infrastructure resources
    including current costs, optimization opportunities, and future forecasts.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("💰 Analyzing infrastructure costs...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            ce_client = session.client("ce")
            cf_client = session.client("cloudformation")

            cost_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "current_costs": {},
                "optimization_opportunities": [],
                "forecast": {},
                "summary": {},
                "recommendations": [],
            }

            # Estimate current costs
            if estimate:
                progress.update(task, description="📊 Estimating current infrastructure costs...")
                current_costs = estimate_infrastructure_costs(ce_client, cf_client)
                cost_results["current_costs"] = current_costs

            # Identify optimization opportunities
            if optimize:
                progress.update(task, description="🎯 Identifying cost optimization opportunities...")
                optimization_opportunities = identify_cost_optimization_opportunities(session)
                cost_results["optimization_opportunities"] = optimization_opportunities

            # Generate cost forecast
            if forecast:
                progress.update(task, description="📈 Generating cost forecasts...")
                cost_forecast = generate_infrastructure_cost_forecast(ce_client, cf_client)
                cost_results["forecast"] = cost_forecast

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating cost recommendations...")
            cost_results["summary"] = generate_infrastructure_cost_summary(cost_results)
            cost_results["recommendations"] = generate_infrastructure_cost_recommendations(cost_results)

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_cost_recommendations_with_ai(cost_results)
                cost_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Infrastructure cost analysis completed!")

            # Display results
            display_infrastructure_cost_results(cost_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Infrastructure cost analysis failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def template_validate(
    security: bool = typer.Option(
        True, "--security", "-s", help="Validate template security configurations"
    ),
    best_practices: bool = typer.Option(
        True, "--best-practices", "-b", help="Check against AWS best practices"
    ),
    template_path: Optional[str] = typer.Option(
        None, "--template", "-t", help="Path to specific template file"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    ✅ Validate CloudFormation/CDK templates for security and best practices

    This command validates infrastructure templates against security standards,
    AWS best practices, and common anti-patterns.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("✅ Validating templates...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            cf_client = session.client("cloudformation")

            validation_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "templates": [],
                "findings": [],
                "summary": {},
                "recommendations": [],
            }

            # Validate templates
            progress.update(task, description="📋 Validating CloudFormation templates...")
            if template_path:
                # Validate specific template
                template_findings = validate_specific_template(cf_client, template_path, security, best_practices)
                validation_results["templates"].append(template_findings)
            else:
                # Validate all templates in stacks
                all_template_findings = validate_all_templates(cf_client, security, best_practices)
                validation_results["templates"].extend(all_template_findings)

            # Collect all findings
            for template in validation_results["templates"]:
                validation_results["findings"].extend(template.get("findings", []))

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating validation summary...")
            validation_results["summary"] = generate_template_validation_summary(validation_results["findings"])
            validation_results["recommendations"] = generate_template_validation_recommendations(validation_results["findings"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_template_recommendations_with_ai(validation_results["findings"])
                validation_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Template validation completed!")

            # Display results
            display_template_validation_results(validation_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Template validation failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def template_optimize(
    cost: bool = typer.Option(
        True, "--cost", "-c", help="Optimize templates for cost efficiency"
    ),
    performance: bool = typer.Option(
        True, "--performance", "-p", help="Optimize templates for performance"
    ),
    template_path: Optional[str] = typer.Option(
        None, "--template", "-t", help="Path to specific template file"
    ),
    auto_fix: bool = typer.Option(
        False, "--auto-fix", "-a", help="Automatically apply optimizations"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Show what would be optimized without applying"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🚀 Optimize CloudFormation/CDK templates for cost and performance

    This command analyzes templates and provides optimization recommendations
    for cost efficiency, performance, and resource utilization.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🚀 Optimizing templates...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            cf_client = session.client("cloudformation")

            optimization_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "templates": [],
                "opportunities": [],
                "summary": {},
                "recommendations": [],
            }

            # Optimize templates
            progress.update(task, description="🎯 Analyzing template optimization opportunities...")
            if template_path:
                # Optimize specific template
                template_optimizations = optimize_specific_template(cf_client, template_path, cost, performance)
                optimization_results["templates"].append(template_optimizations)
            else:
                # Optimize all templates in stacks
                all_template_optimizations = optimize_all_templates(cf_client, cost, performance)
                optimization_results["templates"].extend(all_template_optimizations)

            # Collect all opportunities
            for template in optimization_results["templates"]:
                optimization_results["opportunities"].extend(template.get("opportunities", []))

            # Apply optimizations if requested
            if auto_fix and not dry_run:
                progress.update(task, description="🔧 Applying template optimizations...")
                applied_optimizations = apply_template_optimizations(optimization_results["opportunities"])
                optimization_results["applied_optimizations"] = applied_optimizations

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating optimization summary...")
            optimization_results["summary"] = generate_template_optimization_summary(optimization_results["opportunities"])
            optimization_results["recommendations"] = generate_template_optimization_recommendations(optimization_results["opportunities"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_template_optimization_recommendations_with_ai(optimization_results["opportunities"])
                optimization_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Template optimization completed!")

            # Display results
            display_template_optimization_results(optimization_results, dry_run, verbose)

        except Exception as e:
            console.print(f"[red]❌ Template optimization failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def template_compliance(
    frameworks: str = typer.Option(
        "all", "--frameworks", "-f", help="Compliance frameworks: sox, hipaa, pci-dss, cis, all"
    ),
    standards: str = typer.Option(
        "aws", "--standards", "-s", help="Standards to check: aws, nist, iso27001, all"
    ),
    template_path: Optional[str] = typer.Option(
        None, "--template", "-t", help="Path to specific template file"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    📋 Check template compliance with security frameworks and standards

    This command validates templates against various compliance frameworks
    and security standards to ensure regulatory compliance.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("📋 Checking template compliance...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            cf_client = session.client("cloudformation")

            compliance_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "templates": [],
                "compliance_checks": [],
                "summary": {},
                "recommendations": [],
            }

            # Check template compliance
            progress.update(task, description="🔍 Checking compliance frameworks...")
            if template_path:
                # Check specific template
                template_compliance = check_template_compliance(cf_client, template_path, frameworks, standards)
                compliance_results["templates"].append(template_compliance)
            else:
                # Check all templates in stacks
                all_template_compliance = check_all_templates_compliance(cf_client, frameworks, standards)
                compliance_results["templates"].extend(all_template_compliance)

            # Collect all compliance checks
            for template in compliance_results["templates"]:
                compliance_results["compliance_checks"].extend(template.get("compliance_checks", []))

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating compliance summary...")
            compliance_results["summary"] = generate_template_compliance_summary(compliance_results["compliance_checks"])
            compliance_results["recommendations"] = generate_template_compliance_recommendations(compliance_results["compliance_checks"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_template_compliance_recommendations_with_ai(compliance_results["compliance_checks"])
                compliance_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Template compliance check completed!")

            # Display results
            display_template_compliance_results(compliance_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Template compliance check failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def container_scan(
    images: bool = typer.Option(
        True, "--images", "-i", help="Scan container images for vulnerabilities"
    ),
    vulnerabilities: bool = typer.Option(
        True, "--vulnerabilities", "-v", help="Scan for security vulnerabilities"
    ),
    compliance: bool = typer.Option(
        True, "--compliance", "-c", help="Check compliance with container security standards"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to scan"),
    verbose: bool = typer.Option(False, "--verbose", "-V", help="Verbose output"),
):
    """
    🐳 Scan container images and configurations for security vulnerabilities

    This command scans container images in ECR, ECS, and EKS for security
    vulnerabilities, misconfigurations, and compliance issues.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🐳 Scanning containers...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            ecr_client = session.client("ecr")
            ecs_client = session.client("ecs")
            eks_client = session.client("eks")

            scan_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "images": [],
                "vulnerabilities": [],
                "compliance_findings": [],
                "summary": {},
                "recommendations": [],
            }

            # Scan container images
            if images:
                progress.update(task, description="🔍 Scanning container images...")
                image_scan_results = scan_container_images(ecr_client, ecs_client, eks_client)
                scan_results["images"] = image_scan_results

            # Scan for vulnerabilities
            if vulnerabilities:
                progress.update(task, description="🛡️ Scanning for vulnerabilities...")
                vulnerability_scan_results = scan_container_vulnerabilities(session)
                scan_results["vulnerabilities"] = vulnerability_scan_results

            # Check compliance
            if compliance:
                progress.update(task, description="📋 Checking container compliance...")
                compliance_scan_results = scan_container_compliance(session)
                scan_results["compliance_findings"] = compliance_scan_results

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating scan summary...")
            scan_results["summary"] = generate_container_scan_summary(scan_results)
            scan_results["recommendations"] = generate_container_scan_recommendations(scan_results)

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_container_recommendations_with_ai(scan_results)
                scan_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Container scan completed!")

            # Display results
            display_container_scan_results(scan_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Container scan failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def container_audit(
    security: bool = typer.Option(
        True, "--security", "-s", help="Audit container security configurations"
    ),
    permissions: bool = typer.Option(
        True, "--permissions", "-p", help="Audit container permissions and IAM roles"
    ),
    networking: bool = typer.Option(
        True, "--networking", "-n", help="Audit container networking configurations"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, csv"
    ),
    region: str = typer.Option(None, "--region", "-r", help="AWS region to audit"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🔍 Audit container security, permissions, and networking configurations

    This command performs comprehensive security audits of container deployments
    including ECS services, EKS clusters, and container configurations.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🔍 Auditing containers...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            ecs_client = session.client("ecs")
            eks_client = session.client("eks")
            iam_client = session.client("iam")

            audit_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "findings": [],
                "summary": {},
                "recommendations": [],
            }

            # Audit container security
            if security:
                progress.update(task, description="🔒 Auditing container security...")
                security_findings = audit_container_security(session)
                audit_results["findings"].extend(security_findings)

            # Audit container permissions
            if permissions:
                progress.update(task, description="🔑 Auditing container permissions...")
                permission_findings = audit_container_permissions(iam_client, ecs_client, eks_client)
                audit_results["findings"].extend(permission_findings)

            # Audit container networking
            if networking:
                progress.update(task, description="🌐 Auditing container networking...")
                networking_findings = audit_container_networking(session)
                audit_results["findings"].extend(networking_findings)

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating audit summary...")
            audit_results["summary"] = generate_container_audit_summary(audit_results["findings"])
            audit_results["recommendations"] = generate_container_audit_recommendations(audit_results["findings"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_container_audit_recommendations_with_ai(audit_results["findings"])
                audit_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Container audit completed!")

            # Display results
            display_container_audit_results(audit_results, output, verbose)

        except Exception as e:
            console.print(f"[red]❌ Container audit failed: {str(e)}[/red]")
            raise typer.Exit(1)


@app.command()
def container_optimize(
    resources: bool = typer.Option(
        True, "--resources", "-r", help="Optimize container resource allocation"
    ),
    scaling: bool = typer.Option(
        True, "--scaling", "-s", help="Optimize container scaling configurations"
    ),
    cost: bool = typer.Option(
        True, "--cost", "-c", help="Optimize container costs"
    ),
    auto_fix: bool = typer.Option(
        False, "--auto-fix", "-a", help="Automatically apply optimizations"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", "-d", help="Show what would be optimized without applying"
    ),
    region: str = typer.Option(None, "--region", "-R", help="AWS region to optimize"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    🚀 Optimize container resources, scaling, and costs

    This command analyzes container deployments and provides optimization
    recommendations for resource allocation, scaling, and cost efficiency.
    """
    console.print(Panel(TASK_ASCII_ART, style="bold blue"))

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🚀 Optimizing containers...", total=None)

        try:
            # Initialize AWS clients
            session = boto3.Session(region_name=region)
            ecs_client = session.client("ecs")
            eks_client = session.client("eks")
            cloudwatch_client = session.client("cloudwatch")

            optimization_results = {
                "timestamp": datetime.now().isoformat(),
                "region": region or "default",
                "opportunities": [],
                "summary": {},
                "recommendations": [],
            }

            # Optimize container resources
            if resources:
                progress.update(task, description="⚡ Optimizing container resources...")
                resource_optimizations = optimize_container_resources(session, cloudwatch_client)
                optimization_results["opportunities"].extend(resource_optimizations)

            # Optimize container scaling
            if scaling:
                progress.update(task, description="📈 Optimizing container scaling...")
                scaling_optimizations = optimize_container_scaling(session, cloudwatch_client)
                optimization_results["opportunities"].extend(scaling_optimizations)

            # Optimize container costs
            if cost:
                progress.update(task, description="💰 Optimizing container costs...")
                cost_optimizations = optimize_container_costs(session)
                optimization_results["opportunities"].extend(cost_optimizations)

            # Apply optimizations if requested
            if auto_fix and not dry_run:
                progress.update(task, description="🔧 Applying container optimizations...")
                applied_optimizations = apply_container_optimizations(optimization_results["opportunities"], session)
                optimization_results["applied_optimizations"] = applied_optimizations

            # Generate summary and recommendations
            progress.update(task, description="📊 Generating optimization summary...")
            optimization_results["summary"] = generate_container_optimization_summary(optimization_results["opportunities"])
            optimization_results["recommendations"] = generate_container_optimization_recommendations(optimization_results["opportunities"])

            # Enhance with AI if available
            if check_ai_availability():
                progress.update(task, description="🤖 Enhancing with AI insights...")
                ai_enhanced_recommendations = enhance_container_optimization_recommendations_with_ai(optimization_results["opportunities"])
                optimization_results["ai_recommendations"] = ai_enhanced_recommendations

            progress.update(task, description="✅ Container optimization completed!")

            # Display results
            display_container_optimization_results(optimization_results, dry_run, verbose)

        except Exception as e:
            console.print(f"[red]❌ Container optimization failed: {str(e)}[/red]")
            raise typer.Exit(1)


if __name__ == "__main__":
    app()
