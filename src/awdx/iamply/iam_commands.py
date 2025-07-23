import csv
import json
import os
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import boto3
import typer
from botocore.exceptions import ClientError, NoCredentialsError, ProfileNotFound

iam_app = typer.Typer(help="AWS IAM management and security analysis commands.")

# Emoji constants for consistent UI
IAM_EMOJI = "👤"
ROLE_EMOJI = "🎭"
POLICY_EMOJI = "📜"
GROUP_EMOJI = "👥"
SECURITY_EMOJI = "🔒"
WARNING_EMOJI = "⚠️"
SUCCESS_EMOJI = "✅"
ERROR_EMOJI = "❌"
TIP_EMOJI = "💡"
DANGER_EMOJI = "❗"
BEST_PRACTICE_EMOJI = "✅"
AVOID_EMOJI = "🚫"
ANALYSIS_EMOJI = "📊"
AUDIT_EMOJI = "🔍"
COMPLIANCE_EMOJI = "📋"
ROTATION_EMOJI = "🔄"
ACCESS_EMOJI = "🔑"
PERMISSION_EMOJI = "⚡"
RISK_EMOJI = "🎯"
INNOVATION_EMOJI = "🚀"


@dataclass
class IAMRisk:
    """Data class for IAM risk assessment."""

    risk_level: str
    description: str
    impact: str
    recommendation: str
    priority: int


def get_iam_client(profile: Optional[str] = None):
    """Get AWS IAM client for the specified profile."""
    try:
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        return session.client("iam")
    except ProfileNotFound:
        raise typer.BadParameter(f"Profile '{profile}' not found")
    except NoCredentialsError:
        raise typer.BadParameter(
            "No AWS credentials found. Please configure your AWS credentials."
        )
    except Exception as e:
        raise typer.BadParameter(f"Error creating IAM client: {e}")


def format_arn(arn: str) -> str:
    """Format ARN for better readability."""
    if not arn:
        return "N/A"
    parts = arn.split(":")
    if len(parts) >= 6:
        return f"{parts[2]}:{parts[4]}:{parts[5]}"
    return arn


def get_risk_level_color(risk_level: str) -> str:
    """Get emoji for risk level."""
    risk_colors = {
        "CRITICAL": "🔴",
        "HIGH": "🟠",
        "MEDIUM": "🟡",
        "LOW": "🟢",
        "INFO": "🔵",
    }
    return risk_colors.get(risk_level.upper(), "⚪")


def analyze_policy_permissions(policy_document: Dict) -> List[str]:
    """Analyze policy document and extract permissions."""
    permissions = []

    def extract_from_statement(statement):
        if isinstance(statement.get("Action"), list):
            permissions.extend(statement["Action"])
        elif isinstance(statement.get("Action"), str):
            permissions.append(statement["Action"])
        if isinstance(statement.get("NotAction"), list):
            permissions.extend([f"NOT:{action}" for action in statement["NotAction"]])
        elif isinstance(statement.get("NotAction"), str):
            permissions.append(f"NOT:{statement['NotAction']}")

    if "Statement" in policy_document:
        for statement in policy_document["Statement"]:
            extract_from_statement(statement)

    return list(set(permissions))


def is_privileged_permission(permission: str) -> bool:
    """Check if a permission is considered privileged."""
    privileged_patterns = [
        r"iam:CreateAccessKey",
        r"iam:DeleteAccessKey",
        r"iam:UpdateAccessKey",
        r"iam:CreateUser",
        r"iam:DeleteUser",
        r"iam:AttachUserPolicy",
        r"iam:DetachUserPolicy",
        r"iam:CreateRole",
        r"iam:DeleteRole",
        r"iam:AttachRolePolicy",
        r"iam:DetachRolePolicy",
        r"iam:CreatePolicy",
        r"iam:DeletePolicy",
        r"iam:PutUserPolicy",
        r"iam:PutRolePolicy",
        r"iam:PassRole",
        r"iam:AssumeRole",
        r"sts:AssumeRole",
        r"sts:GetFederationToken",
        r"sts:GetSessionToken",
        r"organizations:",
        r"account:",
        r"billing:",
        r"budgets:",
        r"ce:",
        r"config:",
        r"cloudtrail:",
        r"cloudwatch:",
        r"logs:",
        r"kms:",
        r"secretsmanager:",
        r"ssm:",
        r"ec2:RunInstances",
        r"ec2:TerminateInstances",
        r"ec2:StopInstances",
        r"ec2:StartInstances",
        r"s3:DeleteBucket",
        r"s3:DeleteObject",
        r"rds:DeleteDBInstance",
        r"rds:ModifyDBInstance",
        r"lambda:DeleteFunction",
        r"lambda:UpdateFunctionCode",
        r"eks:DeleteCluster",
        r"eks:UpdateClusterConfig",
    ]

    for pattern in privileged_patterns:
        if re.match(pattern, permission, re.IGNORECASE):
            return True
    return False


@iam_app.command("users", help="List and manage IAM users 👤")
def list_users(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    detailed: bool = typer.Option(
        False, "--detailed", "-d", help="Show detailed user information"
    ),
    inactive: bool = typer.Option(
        False, "--inactive", "-i", help="Show only inactive users"
    ),
):
    """List IAM users with security insights."""
    try:
        iam_client = get_iam_client(profile)

        typer.echo(f"{IAM_EMOJI} Listing IAM users...")
        typer.echo(f"👤 Profile: {profile or 'default'}")
        typer.echo()

        paginator = iam_client.get_paginator("list_users")
        users = []

        for page in paginator.paginate():
            for user in page["Users"]:
                if not inactive or user["PasswordLastUsed"] is None:
                    users.append(user)

        if not users:
            typer.echo(f"{INFO_EMOJI} No users found matching criteria.")
            return

        typer.echo(f"{SUCCESS_EMOJI} Found {len(users)} users:")
        typer.echo()

        for user in users:
            username = user["UserName"]
            created = user["CreateDate"].strftime("%Y-%m-%d")
            last_used = user.get("PasswordLastUsed", "Never")
            if last_used != "Never":
                last_used = last_used.strftime("%Y-%m-%d")

            # Security indicators
            security_status = []
            if user["PasswordLastUsed"] is None:
                security_status.append(f"{WARNING_EMOJI} Never logged in")
            elif (
                datetime.now(user["PasswordLastUsed"].tzinfo) - user["PasswordLastUsed"]
            ).days > 90:
                security_status.append(f"{DANGER_EMOJI} Inactive for >90 days")

            # Check for access keys
            try:
                access_keys = iam_client.list_access_keys(UserName=username)
                active_keys = [
                    key
                    for key in access_keys["AccessKeyMetadata"]
                    if key["Status"] == "Active"
                ]
                if active_keys:
                    security_status.append(
                        f"{ACCESS_EMOJI} {len(active_keys)} active access key(s)"
                    )

                    # Check for old access keys
                    for key in active_keys:
                        if (
                            datetime.now(key["CreateDate"].tzinfo) - key["CreateDate"]
                        ).days > 365:
                            security_status.append(
                                f"{ROTATION_EMOJI} Access key >1 year old"
                            )
            except ClientError:
                pass

            typer.echo(f"{IAM_EMOJI} {username}")
            typer.echo(f"   📅 Created: {created}")
            typer.echo(f"   🔑 Last Login: {last_used}")

            if detailed:
                typer.echo(f"   🆔 ARN: {format_arn(user['Arn'])}")

                # Get attached policies
                try:
                    attached_policies = iam_client.list_attached_user_policies(
                        UserName=username
                    )
                    inline_policies = iam_client.list_user_policies(UserName=username)

                    if attached_policies["AttachedPolicies"]:
                        typer.echo(
                            f"   📜 Attached Policies: {len(attached_policies['AttachedPolicies'])}"
                        )
                    if inline_policies["PolicyNames"]:
                        typer.echo(
                            f"   📜 Inline Policies: {len(inline_policies['PolicyNames'])}"
                        )
                except ClientError:
                    pass

            if security_status:
                typer.echo(f"   {' '.join(security_status)}")

            typer.echo()

        typer.echo(f"{TIP_EMOJI} Security Tips:")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Regularly rotate access keys")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Remove unused users and access keys")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Use MFA for all users")
        typer.echo(f"  {AVOID_EMOJI} Avoid long-lived access keys")

    except Exception as e:
        typer.echo(f"{DANGER_EMOJI} {ERROR_EMOJI} Error listing users: {e}")
        raise typer.Exit(1)


@iam_app.command("roles", help="List and analyze IAM roles 🎭")
def list_roles(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    detailed: bool = typer.Option(
        False, "--detailed", "-d", help="Show detailed role information"
    ),
    unused: bool = typer.Option(False, "--unused", "-u", help="Show only unused roles"),
):
    """List IAM roles with trust relationship analysis."""
    try:
        iam_client = get_iam_client(profile)

        typer.echo(f"{ROLE_EMOJI} Listing IAM roles...")
        typer.echo(f"👤 Profile: {profile or 'default'}")
        typer.echo()

        paginator = iam_client.get_paginator("list_roles")
        roles = []

        for page in paginator.paginate():
            for role in page["Roles"]:
                roles.append(role)

        if not roles:
            typer.echo(f"{INFO_EMOJI} No roles found.")
            return

        typer.echo(f"{SUCCESS_EMOJI} Found {len(roles)} roles:")
        typer.echo()

        for role in roles:
            role_name = role["RoleName"]
            created = role["CreateDate"].strftime("%Y-%m-%d")
            last_used = role.get("RoleLastUsed", {})

            # Check if role is unused
            is_unused = True
            if last_used.get("LastUsedDate"):
                is_unused = False
                last_used_date = last_used["LastUsedDate"].strftime("%Y-%m-%d")
            else:
                last_used_date = "Never"

            if unused and not is_unused:
                continue

            typer.echo(f"{ROLE_EMOJI} {role_name}")
            typer.echo(f"   📅 Created: {created}")
            typer.echo(f"   🔑 Last Used: {last_used_date}")

            if detailed:
                typer.echo(f"   🆔 ARN: {format_arn(role['Arn'])}")

                # Analyze trust relationship
                try:
                    trust_policy = iam_client.get_role(RoleName=role_name)["Role"][
                        "AssumeRolePolicyDocument"
                    ]
                    trust_entities = []

                    for statement in trust_policy.get("Statement", []):
                        if "Principal" in statement:
                            principal = statement["Principal"]
                            if "AWS" in principal:
                                trust_entities.extend(principal["AWS"])
                            if "Service" in principal:
                                trust_entities.extend(principal["Service"])
                            if "Federated" in principal:
                                trust_entities.extend(principal["Federated"])

                    if trust_entities:
                        typer.echo(f"   🤝 Trusted Entities: {len(trust_entities)}")
                        for entity in trust_entities[:3]:  # Show first 3
                            typer.echo(f"      - {entity}")
                        if len(trust_entities) > 3:
                            typer.echo(f"      ... and {len(trust_entities) - 3} more")

                    # Security analysis
                    security_issues = []
                    if any("*" in entity for entity in trust_entities):
                        security_issues.append(f"{DANGER_EMOJI} Wildcard trust")
                    if any("root" in entity.lower() for entity in trust_entities):
                        security_issues.append(f"{DANGER_EMOJI} Root account trust")

                    if security_issues:
                        typer.echo(f"   {' '.join(security_issues)}")

                except ClientError:
                    pass

                # Get attached policies
                try:
                    attached_policies = iam_client.list_attached_role_policies(
                        RoleName=role_name
                    )
                    inline_policies = iam_client.list_role_policies(RoleName=role_name)

                    if attached_policies["AttachedPolicies"]:
                        typer.echo(
                            f"   📜 Attached Policies: {len(attached_policies['AttachedPolicies'])}"
                        )
                    if inline_policies["PolicyNames"]:
                        typer.echo(
                            f"   📜 Inline Policies: {len(inline_policies['PolicyNames'])}"
                        )
                except ClientError:
                    pass

            if is_unused:
                typer.echo(f"   {WARNING_EMOJI} Unused role")

            typer.echo()

        typer.echo(f"{TIP_EMOJI} Role Security Tips:")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Use least privilege principle")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Avoid wildcard trust relationships")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Regularly review and remove unused roles")
        typer.echo(f"  {AVOID_EMOJI} Avoid trusting root account")

    except Exception as e:
        typer.echo(f"{DANGER_EMOJI} {ERROR_EMOJI} Error listing roles: {e}")
        raise typer.Exit(1)


@iam_app.command("policies", help="List and analyze IAM policies 📜")
def list_policies(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    scope: str = typer.Option(
        "All", "--scope", "-s", help="Policy scope (All/Local/AWS)"
    ),
    detailed: bool = typer.Option(
        False, "--detailed", "-d", help="Show detailed policy information"
    ),
):
    """List IAM policies with permission analysis."""
    try:
        iam_client = get_iam_client(profile)

        typer.echo(f"{POLICY_EMOJI} Listing IAM policies...")
        typer.echo(f"👤 Profile: {profile or 'default'}")
        typer.echo(f"📋 Scope: {scope}")
        typer.echo()

        paginator = iam_client.get_paginator("list_policies")
        policies = []

        for page in paginator.paginate(Scope=scope):
            for policy in page["Policies"]:
                policies.append(policy)

        if not policies:
            typer.echo(f"{INFO_EMOJI} No policies found.")
            return

        typer.echo(f"{SUCCESS_EMOJI} Found {len(policies)} policies:")
        typer.echo()

        for policy in policies:
            policy_name = policy["PolicyName"]
            policy_arn = policy["Arn"]
            created = policy["CreateDate"].strftime("%Y-%m-%d")
            updated = policy["UpdateDate"].strftime("%Y-%m-%d")
            attachment_count = policy["AttachmentCount"]

            typer.echo(f"{POLICY_EMOJI} {policy_name}")
            typer.echo(f"   📅 Created: {created}")
            typer.echo(f"   🔄 Updated: {updated}")
            typer.echo(f"   📎 Attachments: {attachment_count}")

            if detailed:
                typer.echo(f"   🆔 ARN: {format_arn(policy_arn)}")

                # Get policy version and analyze permissions
                try:
                    policy_version = iam_client.get_policy_version(
                        PolicyArn=policy_arn, VersionId=policy["DefaultVersionId"]
                    )

                    policy_doc = policy_version["PolicyVersion"]["Document"]
                    permissions = analyze_policy_permissions(policy_doc)

                    if permissions:
                        privileged_permissions = [
                            p for p in permissions if is_privileged_permission(p)
                        ]

                        typer.echo(f"   ⚡ Total Permissions: {len(permissions)}")
                        if privileged_permissions:
                            typer.echo(
                                f"   {RISK_EMOJI} Privileged Permissions: {len(privileged_permissions)}"
                            )
                            for perm in privileged_permissions[:3]:
                                typer.echo(f"      - {perm}")
                            if len(privileged_permissions) > 3:
                                typer.echo(
                                    f"      ... and {len(privileged_permissions) - 3} more"
                                )

                        # Check for wildcard permissions
                        wildcard_permissions = [p for p in permissions if "*" in p]
                        if wildcard_permissions:
                            typer.echo(
                                f"   {DANGER_EMOJI} Wildcard Permissions: {len(wildcard_permissions)}"
                            )

                except ClientError:
                    pass

            typer.echo()

        typer.echo(f"{TIP_EMOJI} Policy Security Tips:")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Use least privilege principle")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Avoid wildcard permissions")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Regularly review policy attachments")
        typer.echo(f"  {AVOID_EMOJI} Avoid overly permissive policies")

    except Exception as e:
        typer.echo(f"{DANGER_EMOJI} {ERROR_EMOJI} Error listing policies: {e}")
        raise typer.Exit(1)


@iam_app.command("groups", help="List and manage IAM groups 👥")
def list_groups(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    detailed: bool = typer.Option(
        False, "--detailed", "-d", help="Show detailed group information"
    ),
):
    """List IAM groups with member analysis."""
    try:
        iam_client = get_iam_client(profile)

        typer.echo(f"{GROUP_EMOJI} Listing IAM groups...")
        typer.echo(f"👤 Profile: {profile or 'default'}")
        typer.echo()

        paginator = iam_client.get_paginator("list_groups")
        groups = []

        for page in paginator.paginate():
            for group in page["Groups"]:
                groups.append(group)

        if not groups:
            typer.echo(f"{INFO_EMOJI} No groups found.")
            return

        typer.echo(f"{SUCCESS_EMOJI} Found {len(groups)} groups:")
        typer.echo()

        for group in groups:
            group_name = group["GroupName"]
            created = group["CreateDate"].strftime("%Y-%m-%d")

            typer.echo(f"{GROUP_EMOJI} {group_name}")
            typer.echo(f"   📅 Created: {created}")

            if detailed:
                typer.echo(f"   🆔 ARN: {format_arn(group['Arn'])}")

                # Get group members
                try:
                    members = iam_client.get_group(GroupName=group_name)
                    user_count = len(members["Users"])
                    typer.echo(f"   👤 Members: {user_count}")

                    if user_count > 0:
                        for user in members["Users"][:3]:
                            typer.echo(f"      - {user['UserName']}")
                        if user_count > 3:
                            typer.echo(f"      ... and {user_count - 3} more")

                except ClientError:
                    pass

                # Get attached policies
                try:
                    attached_policies = iam_client.list_attached_group_policies(
                        GroupName=group_name
                    )
                    inline_policies = iam_client.list_group_policies(
                        GroupName=group_name
                    )

                    if attached_policies["AttachedPolicies"]:
                        typer.echo(
                            f"   📜 Attached Policies: {len(attached_policies['AttachedPolicies'])}"
                        )
                    if inline_policies["PolicyNames"]:
                        typer.echo(
                            f"   📜 Inline Policies: {len(inline_policies['PolicyNames'])}"
                        )

                except ClientError:
                    pass

            typer.echo()

        typer.echo(f"{TIP_EMOJI} Group Management Tips:")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Use groups for permission management")
        typer.echo(
            f"  {BEST_PRACTICE_EMOJI} Assign users to groups instead of direct policies"
        )
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Regularly review group memberships")
        typer.echo(f"  {AVOID_EMOJI} Avoid empty groups")

    except Exception as e:
        typer.echo(f"{DANGER_EMOJI} {ERROR_EMOJI} Error listing groups: {e}")
        raise typer.Exit(1)


@iam_app.command("audit", help="Comprehensive IAM security audit 🔍")
def security_audit(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    export: Optional[str] = typer.Option(
        None, "--export", "-e", help="Export results to file (csv/json)"
    ),
):
    """Perform comprehensive IAM security audit with risk assessment."""
    try:
        iam_client = get_iam_client(profile)

        typer.echo(f"{AUDIT_EMOJI} Starting comprehensive IAM security audit...")
        typer.echo(f"👤 Profile: {profile or 'default'}")
        typer.echo()

        audit_results = {
            "critical_issues": [],
            "high_issues": [],
            "medium_issues": [],
            "low_issues": [],
            "recommendations": [],
        }

        # 1. Check for root account usage
        typer.echo(f"{AUDIT_EMOJI} Checking root account usage...")
        try:
            sts_client = (
                boto3.Session(profile_name=profile).client("sts")
                if profile
                else boto3.Session().client("sts")
            )
            caller_identity = sts_client.get_caller_identity()
            if caller_identity["Arn"].endswith(":root"):
                audit_results["critical_issues"].append(
                    {
                        "issue": "Root account in use",
                        "description": "Using root account credentials is a critical security risk",
                        "impact": "Full account access, no audit trail",
                        "recommendation": "Switch to IAM user with appropriate permissions",
                    }
                )
                typer.echo(f"   {DANGER_EMOJI} CRITICAL: Root account in use!")
            else:
                typer.echo(f"   {SUCCESS_EMOJI} Using IAM user/role")
        except Exception as e:
            typer.echo(f"   {WARNING_EMOJI} Could not verify account type: {e}")

        # 2. Check for users without MFA
        typer.echo(f"{AUDIT_EMOJI} Checking MFA configuration...")
        try:
            paginator = iam_client.get_paginator("list_users")
            users_without_mfa = []

            for page in paginator.paginate():
                for user in page["Users"]:
                    try:
                        mfa_devices = iam_client.list_mfa_devices(
                            UserName=user["UserName"]
                        )
                        if not mfa_devices["MFADevices"]:
                            users_without_mfa.append(user["UserName"])
                    except ClientError:
                        users_without_mfa.append(user["UserName"])

            if users_without_mfa:
                audit_results["high_issues"].append(
                    {
                        "issue": f"{len(users_without_mfa)} users without MFA",
                        "description": "Users without MFA are vulnerable to credential theft",
                        "impact": "Account compromise risk",
                        "recommendation": "Enable MFA for all users",
                    }
                )
                typer.echo(
                    f"   {DANGER_EMOJI} HIGH: {len(users_without_mfa)} users without MFA"
                )
                for user in users_without_mfa[:5]:
                    typer.echo(f"      - {user}")
                if len(users_without_mfa) > 5:
                    typer.echo(f"      ... and {len(users_without_mfa) - 5} more")
            else:
                typer.echo(f"   {SUCCESS_EMOJI} All users have MFA enabled")
        except Exception as e:
            typer.echo(f"   {WARNING_EMOJI} Could not check MFA: {e}")

        # 3. Check for old access keys
        typer.echo(f"{AUDIT_EMOJI} Checking access key age...")
        try:
            old_keys = []
            paginator = iam_client.get_paginator("list_users")

            for page in paginator.paginate():
                for user in page["Users"]:
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
                                if key_age > 365:
                                    old_keys.append(
                                        {
                                            "user": user["UserName"],
                                            "key_id": key["AccessKeyId"],
                                            "age_days": key_age,
                                        }
                                    )
                    except ClientError:
                        pass

            if old_keys:
                audit_results["medium_issues"].append(
                    {
                        "issue": f"{len(old_keys)} old access keys",
                        "description": "Access keys older than 1 year should be rotated",
                        "impact": "Increased risk of key compromise",
                        "recommendation": "Rotate access keys every 90 days",
                    }
                )
                typer.echo(
                    f"   {WARNING_EMOJI} MEDIUM: {len(old_keys)} old access keys found"
                )
                for key in old_keys[:3]:
                    typer.echo(
                        f"      - {key['user']}: {key['key_id']} ({key['age_days']} days)"
                    )
                if len(old_keys) > 3:
                    typer.echo(f"      ... and {len(old_keys) - 3} more")
            else:
                typer.echo(f"   {SUCCESS_EMOJI} No old access keys found")
        except Exception as e:
            typer.echo(f"   {WARNING_EMOJI} Could not check access keys: {e}")

        # 4. Check for unused IAM entities
        typer.echo(f"{AUDIT_EMOJI} Checking for unused IAM entities...")
        try:
            unused_users = []
            unused_roles = []

            # Check unused users
            paginator = iam_client.get_paginator("list_users")
            for page in paginator.paginate():
                for user in page["Users"]:
                    if user.get("PasswordLastUsed") is None:
                        unused_users.append(user["UserName"])

            # Check unused roles
            paginator = iam_client.get_paginator("list_roles")
            for page in paginator.paginate():
                for role in page["Roles"]:
                    if not role.get("RoleLastUsed", {}).get("LastUsedDate"):
                        unused_roles.append(role["RoleName"])

            if unused_users:
                audit_results["low_issues"].append(
                    {
                        "issue": f"{len(unused_users)} unused users",
                        "description": "Unused users should be removed",
                        "impact": "Attack surface expansion",
                        "recommendation": "Remove unused users",
                    }
                )
                typer.echo(f"   {WARNING_EMOJI} LOW: {len(unused_users)} unused users")

            if unused_roles:
                audit_results["low_issues"].append(
                    {
                        "issue": f"{len(unused_roles)} unused roles",
                        "description": "Unused roles should be removed",
                        "impact": "Attack surface expansion",
                        "recommendation": "Remove unused roles",
                    }
                )
                typer.echo(f"   {WARNING_EMOJI} LOW: {len(unused_roles)} unused roles")

            if not unused_users and not unused_roles:
                typer.echo(f"   {SUCCESS_EMOJI} No unused entities found")
        except Exception as e:
            typer.echo(f"   {WARNING_EMOJI} Could not check unused entities: {e}")

        # 5. Check for overly permissive policies
        typer.echo(f"{AUDIT_EMOJI} Checking for overly permissive policies...")
        try:
            wildcard_policies = []
            paginator = iam_client.get_paginator("list_policies")

            for page in paginator.paginate(Scope="Local"):
                for policy in page["Policies"]:
                    try:
                        policy_version = iam_client.get_policy_version(
                            PolicyArn=policy["Arn"],
                            VersionId=policy["DefaultVersionId"],
                        )
                        policy_doc = policy_version["PolicyVersion"]["Document"]
                        permissions = analyze_policy_permissions(policy_doc)

                        wildcard_perms = [p for p in permissions if "*" in p]
                        if wildcard_perms:
                            wildcard_policies.append(
                                {
                                    "policy": policy["PolicyName"],
                                    "wildcard_count": len(wildcard_perms),
                                }
                            )
                    except ClientError:
                        pass

            if wildcard_policies:
                audit_results["high_issues"].append(
                    {
                        "issue": f"{len(wildcard_policies)} policies with wildcards",
                        "description": "Wildcard permissions are overly permissive",
                        "impact": "Potential privilege escalation",
                        "recommendation": "Replace wildcards with specific permissions",
                    }
                )
                typer.echo(
                    f"   {DANGER_EMOJI} HIGH: {len(wildcard_policies)} policies with wildcards"
                )
                for policy in wildcard_policies[:3]:
                    typer.echo(
                        f"      - {policy['policy']}: {policy['wildcard_count']} wildcards"
                    )
                if len(wildcard_policies) > 3:
                    typer.echo(f"      ... and {len(wildcard_policies) - 3} more")
            else:
                typer.echo(f"   {SUCCESS_EMOJI} No overly permissive policies found")
        except Exception as e:
            typer.echo(f"   {WARNING_EMOJI} Could not check policies: {e}")

        # Display audit summary
        typer.echo()
        typer.echo(f"{AUDIT_EMOJI} Audit Summary:")
        typer.echo(
            f"  {get_risk_level_color('CRITICAL')} Critical Issues: {len(audit_results['critical_issues'])}"
        )
        typer.echo(
            f"  {get_risk_level_color('HIGH')} High Issues: {len(audit_results['high_issues'])}"
        )
        typer.echo(
            f"  {get_risk_level_color('MEDIUM')} Medium Issues: {len(audit_results['medium_issues'])}"
        )
        typer.echo(
            f"  {get_risk_level_color('LOW')} Low Issues: {len(audit_results['low_issues'])}"
        )

        # Export results if requested
        if export:
            try:
                if export.endswith(".json"):
                    with open(export, "w") as f:
                        json.dump(audit_results, f, indent=2, default=str)
                elif export.endswith(".csv"):
                    with open(export, "w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(
                            [
                                "Severity",
                                "Issue",
                                "Description",
                                "Impact",
                                "Recommendation",
                            ]
                        )
                        for severity, issues in audit_results.items():
                            if severity != "recommendations":
                                for issue in issues:
                                    writer.writerow(
                                        [
                                            severity.upper(),
                                            issue["issue"],
                                            issue["description"],
                                            issue["impact"],
                                            issue["recommendation"],
                                        ]
                                    )

                typer.echo(f"{SUCCESS_EMOJI} Audit results exported to {export}")
            except Exception as e:
                typer.echo(f"{ERROR_EMOJI} Failed to export results: {e}")

        typer.echo()
        typer.echo(f"{TIP_EMOJI} Security Recommendations:")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Enable MFA for all users")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Rotate access keys every 90 days")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Remove unused IAM entities")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Use least privilege principle")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Regular security audits")

    except Exception as e:
        typer.echo(f"{DANGER_EMOJI} {ERROR_EMOJI} Error during security audit: {e}")
        raise typer.Exit(1)


@iam_app.command("access", help="Analyze effective permissions and access patterns 🔑")
def analyze_access(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    entity: Optional[str] = typer.Option(
        None, "--entity", "-e", help="Specific user/role to analyze"
    ),
    service: Optional[str] = typer.Option(
        None, "--service", "-s", help="Specific AWS service to analyze"
    ),
):
    """Analyze effective permissions and access patterns for IAM entities."""
    try:
        iam_client = get_iam_client(profile)

        typer.echo(f"{ACCESS_EMOJI} Analyzing IAM access patterns...")
        typer.echo(f"👤 Profile: {profile or 'default'}")
        if entity:
            typer.echo(f"🎯 Entity: {entity}")
        if service:
            typer.echo(f"🔧 Service: {service}")
        typer.echo()

        # Get all permissions for entities
        all_permissions = {}

        if entity:
            # Analyze specific entity
            entities_to_analyze = [entity]
        else:
            # Analyze all users and roles
            entities_to_analyze = []

            # Get users
            try:
                paginator = iam_client.get_paginator("list_users")
                for page in paginator.paginate():
                    for user in page["Users"]:
                        entities_to_analyze.append(("user", user["UserName"]))
            except ClientError:
                pass

            # Get roles
            try:
                paginator = iam_client.get_paginator("list_roles")
                for page in paginator.paginate():
                    for role in page["Roles"]:
                        entities_to_analyze.append(("role", role["RoleName"]))
            except ClientError:
                pass

        typer.echo(f"{ANALYSIS_EMOJI} Analyzing {len(entities_to_analyze)} entities...")
        typer.echo()

        for entity_type, entity_name in entities_to_analyze:
            try:
                permissions = set()

                # Get attached policies
                if entity_type == "user":
                    attached_policies = iam_client.list_attached_user_policies(
                        UserName=entity_name
                    )
                    inline_policies = iam_client.list_user_policies(
                        UserName=entity_name
                    )
                else:  # role
                    attached_policies = iam_client.list_attached_role_policies(
                        RoleName=entity_name
                    )
                    inline_policies = iam_client.list_role_policies(
                        RoleName=entity_name
                    )

                # Analyze attached policies
                for policy in attached_policies["AttachedPolicies"]:
                    try:
                        policy_version = iam_client.get_policy_version(
                            PolicyArn=policy["PolicyArn"],
                            VersionId=iam_client.get_policy(
                                PolicyArn=policy["PolicyArn"]
                            )["Policy"]["DefaultVersionId"],
                        )
                        policy_doc = policy_version["PolicyVersion"]["Document"]
                        policy_permissions = analyze_policy_permissions(policy_doc)
                        permissions.update(policy_permissions)
                    except ClientError:
                        pass

                # Analyze inline policies
                for policy_name in inline_policies["PolicyNames"]:
                    try:
                        if entity_type == "user":
                            policy_doc = iam_client.get_user_policy(
                                UserName=entity_name, PolicyName=policy_name
                            )["PolicyDocument"]
                        else:
                            policy_doc = iam_client.get_role_policy(
                                RoleName=entity_name, PolicyName=policy_name
                            )["PolicyDocument"]
                        policy_permissions = analyze_policy_permissions(policy_doc)
                        permissions.update(policy_permissions)
                    except ClientError:
                        pass

                # Filter by service if specified
                if service:
                    filtered_permissions = [
                        p for p in permissions if p.lower().startswith(service.lower())
                    ]
                    permissions = set(filtered_permissions)

                if permissions:
                    all_permissions[entity_name] = {
                        "type": entity_type,
                        "permissions": list(permissions),
                        "privileged_count": len(
                            [p for p in permissions if is_privileged_permission(p)]
                        ),
                        "wildcard_count": len([p for p in permissions if "*" in p]),
                    }

                    # Display entity analysis
                    entity_emoji = IAM_EMOJI if entity_type == "user" else ROLE_EMOJI
                    typer.echo(f"{entity_emoji} {entity_name} ({entity_type})")
                    typer.echo(f"   ⚡ Total Permissions: {len(permissions)}")
                    typer.echo(
                        f"   {RISK_EMOJI} Privileged: {all_permissions[entity_name]['privileged_count']}"
                    )
                    typer.echo(
                        f"   {DANGER_EMOJI} Wildcards: {all_permissions[entity_name]['wildcard_count']}"
                    )

                    # Show top permissions
                    if len(permissions) <= 10:
                        for perm in sorted(permissions):
                            risk_emoji = (
                                RISK_EMOJI if is_privileged_permission(perm) else ""
                            )
                            wildcard_emoji = DANGER_EMOJI if "*" in perm else ""
                            typer.echo(f"      {risk_emoji}{wildcard_emoji} {perm}")
                    else:
                        # Show top 5 and bottom 5
                        sorted_perms = sorted(permissions)
                        for perm in sorted_perms[:5]:
                            risk_emoji = (
                                RISK_EMOJI if is_privileged_permission(perm) else ""
                            )
                            wildcard_emoji = DANGER_EMOJI if "*" in perm else ""
                            typer.echo(f"      {risk_emoji}{wildcard_emoji} {perm}")
                        typer.echo(f"      ... and {len(permissions) - 10} more ...")
                        for perm in sorted_perms[-5:]:
                            risk_emoji = (
                                RISK_EMOJI if is_privileged_permission(perm) else ""
                            )
                            wildcard_emoji = DANGER_EMOJI if "*" in perm else ""
                            typer.echo(f"      {risk_emoji}{wildcard_emoji} {perm}")

                    typer.echo()

            except ClientError as e:
                typer.echo(f"   {ERROR_EMOJI} Error analyzing {entity_name}: {e}")

        # Summary statistics
        if all_permissions:
            total_entities = len(all_permissions)
            total_permissions = sum(
                len(data["permissions"]) for data in all_permissions.values()
            )
            total_privileged = sum(
                data["privileged_count"] for data in all_permissions.values()
            )
            total_wildcards = sum(
                data["wildcard_count"] for data in all_permissions.values()
            )

            typer.echo(f"{ANALYSIS_EMOJI} Access Analysis Summary:")
            typer.echo(f"  📊 Total Entities: {total_entities}")
            typer.echo(f"  ⚡ Total Permissions: {total_permissions}")
            typer.echo(f"  {RISK_EMOJI} Privileged Permissions: {total_privileged}")
            typer.echo(f"  {DANGER_EMOJI} Wildcard Permissions: {total_wildcards}")

            # Identify high-risk entities
            high_risk_entities = [
                (name, data)
                for name, data in all_permissions.items()
                if data["privileged_count"] > 5 or data["wildcard_count"] > 3
            ]

            if high_risk_entities:
                typer.echo()
                typer.echo(f"{DANGER_EMOJI} High-Risk Entities:")
                for name, data in high_risk_entities:
                    entity_emoji = IAM_EMOJI if data["type"] == "user" else ROLE_EMOJI
                    typer.echo(
                        f"  {entity_emoji} {name}: {data['privileged_count']} privileged, {data['wildcard_count']} wildcards"
                    )

        typer.echo()
        typer.echo(f"{TIP_EMOJI} Access Management Tips:")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Use least privilege principle")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Regularly review permissions")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Remove unnecessary permissions")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Avoid wildcard permissions")

    except Exception as e:
        typer.echo(f"{DANGER_EMOJI} {ERROR_EMOJI} Error analyzing access: {e}")
        raise typer.Exit(1)


@iam_app.command("compliance", help="Check IAM compliance with security standards 📋")
def check_compliance(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    standard: str = typer.Option(
        "CIS", "--standard", "-s", help="Compliance standard (CIS/SOC2/PCI)"
    ),
):
    """Check IAM compliance with security standards."""
    try:
        iam_client = get_iam_client(profile)

        typer.echo(f"{COMPLIANCE_EMOJI} Checking IAM compliance with {standard}...")
        typer.echo(f"👤 Profile: {profile or 'default'}")
        typer.echo()

        compliance_results = {
            "passed": [],
            "failed": [],
            "warnings": [],
            "not_applicable": [],
        }

        # CIS AWS Foundations Benchmark checks
        if standard.upper() == "CIS":
            typer.echo(f"{COMPLIANCE_EMOJI} CIS AWS Foundations Benchmark Checks:")
            typer.echo()

            # 1.1 - Avoid the use of the "root" account for administrative and daily tasks
            typer.echo(f"{COMPLIANCE_EMOJI} 1.1 - Root Account Usage")
            try:
                sts_client = (
                    boto3.Session(profile_name=profile).client("sts")
                    if profile
                    else boto3.Session().client("sts")
                )
                caller_identity = sts_client.get_caller_identity()
                if caller_identity["Arn"].endswith(":root"):
                    compliance_results["failed"].append(
                        {
                            "check": "1.1",
                            "title": "Root Account Usage",
                            "description": "Root account should not be used for administrative tasks",
                            "remediation": "Use IAM users with appropriate permissions",
                        }
                    )
                    typer.echo(f"   {ERROR_EMOJI} FAILED: Root account in use")
                else:
                    compliance_results["passed"].append(
                        {
                            "check": "1.1",
                            "title": "Root Account Usage",
                            "description": "Not using root account for administrative tasks",
                        }
                    )
                    typer.echo(f"   {SUCCESS_EMOJI} PASSED: Using IAM user/role")
            except Exception as e:
                compliance_results["warnings"].append(
                    {
                        "check": "1.1",
                        "title": "Root Account Usage",
                        "description": f"Could not verify: {e}",
                    }
                )
                typer.echo(f"   {WARNING_EMOJI} WARNING: Could not verify")

            # 1.2 - Ensure multi-factor authentication (MFA) is enabled for all IAM users that have a console password
            typer.echo(f"{COMPLIANCE_EMOJI} 1.2 - MFA for Console Users")
            try:
                users_without_mfa = []
                paginator = iam_client.get_paginator("list_users")

                for page in paginator.paginate():
                    for user in page["Users"]:
                        try:
                            mfa_devices = iam_client.list_mfa_devices(
                                UserName=user["UserName"]
                            )
                            if not mfa_devices["MFADevices"]:
                                users_without_mfa.append(user["UserName"])
                        except ClientError:
                            users_without_mfa.append(user["UserName"])

                if users_without_mfa:
                    compliance_results["failed"].append(
                        {
                            "check": "1.2",
                            "title": "MFA for Console Users",
                            "description": f"{len(users_without_mfa)} users without MFA",
                            "remediation": "Enable MFA for all console users",
                        }
                    )
                    typer.echo(
                        f"   {ERROR_EMOJI} FAILED: {len(users_without_mfa)} users without MFA"
                    )
                else:
                    compliance_results["passed"].append(
                        {
                            "check": "1.2",
                            "title": "MFA for Console Users",
                            "description": "All users have MFA enabled",
                        }
                    )
                    typer.echo(f"   {SUCCESS_EMOJI} PASSED: All users have MFA")
            except Exception as e:
                compliance_results["warnings"].append(
                    {
                        "check": "1.2",
                        "title": "MFA for Console Users",
                        "description": f"Could not verify: {e}",
                    }
                )
                typer.echo(f"   {WARNING_EMOJI} WARNING: Could not verify")

            # 1.3 - Ensure credentials unused for 90 days or greater are disabled
            typer.echo(f"{COMPLIANCE_EMOJI} 1.3 - Unused Credentials")
            try:
                inactive_users = []
                old_access_keys = []

                paginator = iam_client.get_paginator("list_users")
                for page in paginator.paginate():
                    for user in page["Users"]:
                        # Check password last used
                        if user.get("PasswordLastUsed"):
                            days_since_login = (
                                datetime.now(user["PasswordLastUsed"].tzinfo)
                                - user["PasswordLastUsed"]
                            ).days
                            if days_since_login > 90:
                                inactive_users.append(user["UserName"])

                        # Check access keys
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
                                        old_access_keys.append(
                                            f"{user['UserName']}:{key['AccessKeyId']}"
                                        )
                        except ClientError:
                            pass

                if inactive_users or old_access_keys:
                    compliance_results["failed"].append(
                        {
                            "check": "1.3",
                            "title": "Unused Credentials",
                            "description": f"{len(inactive_users)} inactive users, {len(old_access_keys)} old access keys",
                            "remediation": "Disable unused credentials",
                        }
                    )
                    typer.echo(
                        f"   {ERROR_EMOJI} FAILED: {len(inactive_users)} inactive users, {len(old_access_keys)} old keys"
                    )
                else:
                    compliance_results["passed"].append(
                        {
                            "check": "1.3",
                            "title": "Unused Credentials",
                            "description": "No unused credentials found",
                        }
                    )
                    typer.echo(f"   {SUCCESS_EMOJI} PASSED: No unused credentials")
            except Exception as e:
                compliance_results["warnings"].append(
                    {
                        "check": "1.3",
                        "title": "Unused Credentials",
                        "description": f"Could not verify: {e}",
                    }
                )
                typer.echo(f"   {WARNING_EMOJI} WARNING: Could not verify")

            # 1.4 - Ensure access keys are rotated every 90 days or less
            typer.echo(f"{COMPLIANCE_EMOJI} 1.4 - Access Key Rotation")
            try:
                old_keys = []
                paginator = iam_client.get_paginator("list_users")

                for page in paginator.paginate():
                    for user in page["Users"]:
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
                                        old_keys.append(
                                            f"{user['UserName']}:{key['AccessKeyId']}"
                                        )
                        except ClientError:
                            pass

                if old_keys:
                    compliance_results["failed"].append(
                        {
                            "check": "1.4",
                            "title": "Access Key Rotation",
                            "description": f"{len(old_keys)} access keys older than 90 days",
                            "remediation": "Rotate access keys every 90 days",
                        }
                    )
                    typer.echo(
                        f"   {ERROR_EMOJI} FAILED: {len(old_keys)} old access keys"
                    )
                else:
                    compliance_results["passed"].append(
                        {
                            "check": "1.4",
                            "title": "Access Key Rotation",
                            "description": "All access keys are recent",
                        }
                    )
                    typer.echo(f"   {SUCCESS_EMOJI} PASSED: All keys are recent")
            except Exception as e:
                compliance_results["warnings"].append(
                    {
                        "check": "1.4",
                        "title": "Access Key Rotation",
                        "description": f"Could not verify: {e}",
                    }
                )
                typer.echo(f"   {WARNING_EMOJI} WARNING: Could not verify")

        # Display compliance summary
        typer.echo()
        typer.echo(f"{COMPLIANCE_EMOJI} Compliance Summary:")
        typer.echo(f"  {SUCCESS_EMOJI} Passed: {len(compliance_results['passed'])}")
        typer.echo(f"  {ERROR_EMOJI} Failed: {len(compliance_results['failed'])}")
        typer.echo(f"  {WARNING_EMOJI} Warnings: {len(compliance_results['warnings'])}")
        typer.echo(f"  ℹ️ Not Applicable: {len(compliance_results['not_applicable'])}")

        # Show failed checks
        if compliance_results["failed"]:
            typer.echo()
            typer.echo(f"{ERROR_EMOJI} Failed Compliance Checks:")
            for check in compliance_results["failed"]:
                typer.echo(f"  {check['check']} - {check['title']}")
                typer.echo(f"     Description: {check['description']}")
                typer.echo(f"     Remediation: {check['remediation']}")
                typer.echo()

        typer.echo(f"{TIP_EMOJI} Compliance Tips:")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Regular compliance audits")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Automated compliance monitoring")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Document compliance procedures")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Remediate issues promptly")

    except Exception as e:
        typer.echo(f"{DANGER_EMOJI} {ERROR_EMOJI} Error checking compliance: {e}")
        raise typer.Exit(1)


@iam_app.command("smart", help="Smart IAM recommendations and automation 🚀")
def smart_recommendations(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    auto_fix: bool = typer.Option(
        False, "--auto-fix", "-a", help="Automatically apply safe fixes"
    ),
    dry_run: bool = typer.Option(
        True, "--dry-run", "-d", help="Show what would be changed without applying"
    ),
):
    """Provide smart IAM recommendations and automation."""
    try:
        iam_client = get_iam_client(profile)

        typer.echo(f"{INNOVATION_EMOJI} Generating smart IAM recommendations...")
        typer.echo(f"👤 Profile: {profile or 'default'}")
        if auto_fix:
            typer.echo(f"🔧 Auto-fix mode: {'ENABLED' if not dry_run else 'DRY RUN'}")
        typer.echo()

        recommendations = []

        # 1. Identify unused IAM entities
        typer.echo(f"{INNOVATION_EMOJI} Analyzing unused entities...")
        try:
            unused_users = []
            unused_roles = []

            # Find unused users
            paginator = iam_client.get_paginator("list_users")
            for page in paginator.paginate():
                for user in page["Users"]:
                    if user.get("PasswordLastUsed") is None:
                        # Check if user has access keys
                        try:
                            access_keys = iam_client.list_access_keys(
                                UserName=user["UserName"]
                            )
                            if not access_keys["AccessKeyMetadata"]:
                                unused_users.append(user["UserName"])
                        except ClientError:
                            unused_users.append(user["UserName"])

            # Find unused roles
            paginator = iam_client.get_paginator("list_roles")
            for page in paginator.paginate():
                for role in page["Roles"]:
                    if not role.get("RoleLastUsed", {}).get("LastUsedDate"):
                        unused_roles.append(role["RoleName"])

            if unused_users:
                recommendations.append(
                    {
                        "type": "cleanup",
                        "action": "Remove unused users",
                        "entities": unused_users,
                        "impact": "Reduces attack surface",
                        "risk": "LOW",
                        "auto_fixable": True,
                    }
                )
                typer.echo(f"   {TIP_EMOJI} Found {len(unused_users)} unused users")

            if unused_roles:
                recommendations.append(
                    {
                        "type": "cleanup",
                        "action": "Remove unused roles",
                        "entities": unused_roles,
                        "impact": "Reduces attack surface",
                        "risk": "LOW",
                        "auto_fixable": True,
                    }
                )
                typer.echo(f"   {TIP_EMOJI} Found {len(unused_roles)} unused roles")

        except Exception as e:
            typer.echo(f"   {WARNING_EMOJI} Could not analyze unused entities: {e}")

        # 2. Identify old access keys
        typer.echo(f"{INNOVATION_EMOJI} Analyzing access key age...")
        try:
            old_keys = []
            paginator = iam_client.get_paginator("list_users")

            for page in paginator.paginate():
                for user in page["Users"]:
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
                                    old_keys.append(
                                        {
                                            "user": user["UserName"],
                                            "key_id": key["AccessKeyId"],
                                            "age_days": key_age,
                                        }
                                    )
                    except ClientError:
                        pass

            if old_keys:
                recommendations.append(
                    {
                        "type": "rotation",
                        "action": "Rotate old access keys",
                        "entities": [f"{k['user']}:{k['key_id']}" for k in old_keys],
                        "impact": "Improves security posture",
                        "risk": "MEDIUM",
                        "auto_fixable": False,  # Requires user action
                    }
                )
                typer.echo(f"   {TIP_EMOJI} Found {len(old_keys)} old access keys")

        except Exception as e:
            typer.echo(f"   {WARNING_EMOJI} Could not analyze access keys: {e}")

        # 3. Identify overly permissive policies
        typer.echo(f"{INNOVATION_EMOJI} Analyzing policy permissions...")
        try:
            wildcard_policies = []
            paginator = iam_client.get_paginator("list_policies")

            for page in paginator.paginate(Scope="Local"):
                for policy in page["Policies"]:
                    try:
                        policy_version = iam_client.get_policy_version(
                            PolicyArn=policy["Arn"],
                            VersionId=policy["DefaultVersionId"],
                        )
                        policy_doc = policy_version["PolicyVersion"]["Document"]
                        permissions = analyze_policy_permissions(policy_doc)

                        wildcard_perms = [p for p in permissions if "*" in p]
                        if wildcard_perms:
                            wildcard_policies.append(
                                {
                                    "policy": policy["PolicyName"],
                                    "wildcard_count": len(wildcard_perms),
                                    "wildcards": wildcard_perms[:5],  # Show first 5
                                }
                            )
                    except ClientError:
                        pass

            if wildcard_policies:
                recommendations.append(
                    {
                        "type": "security",
                        "action": "Review wildcard permissions",
                        "entities": [p["policy"] for p in wildcard_policies],
                        "impact": "Reduces privilege escalation risk",
                        "risk": "HIGH",
                        "auto_fixable": False,  # Requires manual review
                    }
                )
                typer.echo(
                    f"   {TIP_EMOJI} Found {len(wildcard_policies)} policies with wildcards"
                )

        except Exception as e:
            typer.echo(f"   {WARNING_EMOJI} Could not analyze policies: {e}")

        # 4. Identify users without MFA
        typer.echo(f"{INNOVATION_EMOJI} Analyzing MFA configuration...")
        try:
            users_without_mfa = []
            paginator = iam_client.get_paginator("list_users")

            for page in paginator.paginate():
                for user in page["Users"]:
                    try:
                        mfa_devices = iam_client.list_mfa_devices(
                            UserName=user["UserName"]
                        )
                        if not mfa_devices["MFADevices"]:
                            users_without_mfa.append(user["UserName"])
                    except ClientError:
                        users_without_mfa.append(user["UserName"])

            if users_without_mfa:
                recommendations.append(
                    {
                        "type": "security",
                        "action": "Enable MFA for users",
                        "entities": users_without_mfa,
                        "impact": "Improves account security",
                        "risk": "HIGH",
                        "auto_fixable": False,  # Requires user action
                    }
                )
                typer.echo(
                    f"   {TIP_EMOJI} Found {len(users_without_mfa)} users without MFA"
                )

        except Exception as e:
            typer.echo(f"   {WARNING_EMOJI} Could not analyze MFA: {e}")

        # Display recommendations
        typer.echo()
        typer.echo(f"{INNOVATION_EMOJI} Smart Recommendations:")
        typer.echo()

        for i, rec in enumerate(recommendations, 1):
            risk_color = get_risk_level_color(rec["risk"])
            auto_fix_emoji = "🤖" if rec["auto_fixable"] else "👤"

            typer.echo(f"{i}. {risk_color} {rec['action']} {auto_fix_emoji}")
            typer.echo(f"   📊 Type: {rec['type'].title()}")
            typer.echo(f"   🎯 Impact: {rec['impact']}")
            typer.echo(f"   ⚠️ Risk: {rec['risk']}")
            typer.echo(f"   🔧 Auto-fixable: {'Yes' if rec['auto_fixable'] else 'No'}")

            if len(rec["entities"]) <= 5:
                for entity in rec["entities"]:
                    typer.echo(f"      - {entity}")
            else:
                for entity in rec["entities"][:3]:
                    typer.echo(f"      - {entity}")
                typer.echo(f"      ... and {len(rec['entities']) - 3} more")

            typer.echo()

        # Apply auto-fixes if requested
        if auto_fix and not dry_run:
            typer.echo(f"{INNOVATION_EMOJI} Applying auto-fixes...")

            for rec in recommendations:
                if rec["auto_fixable"]:
                    try:
                        if rec["action"] == "Remove unused users":
                            for user in rec["entities"]:
                                try:
                                    # Delete access keys first
                                    access_keys = iam_client.list_access_keys(
                                        UserName=user
                                    )
                                    for key in access_keys["AccessKeyMetadata"]:
                                        iam_client.delete_access_key(
                                            UserName=user,
                                            AccessKeyId=key["AccessKeyId"],
                                        )

                                    # Delete user
                                    iam_client.delete_user(UserName=user)
                                    typer.echo(
                                        f"   {SUCCESS_EMOJI} Removed user: {user}"
                                    )
                                except ClientError as e:
                                    typer.echo(
                                        f"   {ERROR_EMOJI} Failed to remove user {user}: {e}"
                                    )

                        elif rec["action"] == "Remove unused roles":
                            for role in rec["entities"]:
                                try:
                                    # Detach policies first
                                    attached_policies = (
                                        iam_client.list_attached_role_policies(
                                            RoleName=role
                                        )
                                    )
                                    for policy in attached_policies["AttachedPolicies"]:
                                        iam_client.detach_role_policy(
                                            RoleName=role, PolicyArn=policy["PolicyArn"]
                                        )

                                    # Delete role
                                    iam_client.delete_role(RoleName=role)
                                    typer.echo(
                                        f"   {SUCCESS_EMOJI} Removed role: {role}"
                                    )
                                except ClientError as e:
                                    typer.echo(
                                        f"   {ERROR_EMOJI} Failed to remove role {role}: {e}"
                                    )

                    except Exception as e:
                        typer.echo(
                            f"   {ERROR_EMOJI} Error applying {rec['action']}: {e}"
                        )

        elif auto_fix and dry_run:
            typer.echo(f"{INNOVATION_EMOJI} Dry run mode - no changes applied")
            typer.echo(f"   Use --no-dry-run to apply changes")

        typer.echo()
        typer.echo(f"{TIP_EMOJI} Smart IAM Tips:")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Regular automated audits")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Implement least privilege")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Use IAM Access Analyzer")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Monitor IAM changes")

    except Exception as e:
        typer.echo(
            f"{DANGER_EMOJI} {ERROR_EMOJI} Error generating recommendations: {e}"
        )
        raise typer.Exit(1)


@iam_app.command("export", help="Export IAM data to file 📤")
def export_iam_data(
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", help="AWS profile to use"
    ),
    format: str = typer.Option(
        "json", "--format", "-f", help="Export format (json/csv)"
    ),
    output: str = typer.Option(
        "iam_data", "--output", "-o", help="Output filename (without extension)"
    ),
    include_policies: bool = typer.Option(
        True, "--include-policies", "-p", help="Include policy details"
    ),
    include_permissions: bool = typer.Option(
        True, "--include-permissions", "-m", help="Include permission analysis"
    ),
):
    """Export IAM data for analysis and reporting."""
    try:
        iam_client = get_iam_client(profile)

        typer.echo(f"{ANALYSIS_EMOJI} Exporting IAM data...")
        typer.echo(f"👤 Profile: {profile or 'default'}")
        typer.echo(f"📁 Format: {format}")
        typer.echo(f"📄 Output: {output}.{format}")
        typer.echo()

        export_data = {
            "export_info": {
                "timestamp": datetime.now().isoformat(),
                "profile": profile or "default",
                "format": format,
            },
            "users": [],
            "roles": [],
            "groups": [],
            "policies": [],
        }

        # Export users
        typer.echo(f"{IAM_EMOJI} Exporting users...")
        try:
            paginator = iam_client.get_paginator("list_users")
            for page in paginator.paginate():
                for user in page["Users"]:
                    user_data = {
                        "UserName": user["UserName"],
                        "Arn": user["Arn"],
                        "CreateDate": user["CreateDate"].isoformat(),
                        "PasswordLastUsed": (
                            user.get("PasswordLastUsed", "").isoformat()
                            if user.get("PasswordLastUsed")
                            else None
                        ),
                    }

                    if include_policies:
                        try:
                            attached_policies = iam_client.list_attached_user_policies(
                                UserName=user["UserName"]
                            )
                            inline_policies = iam_client.list_user_policies(
                                UserName=user["UserName"]
                            )
                            user_data["AttachedPolicies"] = [
                                p["PolicyName"]
                                for p in attached_policies["AttachedPolicies"]
                            ]
                            user_data["InlinePolicies"] = inline_policies["PolicyNames"]
                        except ClientError:
                            user_data["AttachedPolicies"] = []
                            user_data["InlinePolicies"] = []

                    if include_permissions:
                        try:
                            access_keys = iam_client.list_access_keys(
                                UserName=user["UserName"]
                            )
                            user_data["AccessKeys"] = [
                                {
                                    "AccessKeyId": key["AccessKeyId"],
                                    "Status": key["Status"],
                                    "CreateDate": key["CreateDate"].isoformat(),
                                }
                                for key in access_keys["AccessKeyMetadata"]
                            ]
                        except ClientError:
                            user_data["AccessKeys"] = []

                    export_data["users"].append(user_data)
        except Exception as e:
            typer.echo(f"   {WARNING_EMOJI} Error exporting users: {e}")

        # Export roles
        typer.echo(f"{ROLE_EMOJI} Exporting roles...")
        try:
            paginator = iam_client.get_paginator("list_roles")
            for page in paginator.paginate():
                for role in page["Roles"]:
                    role_data = {
                        "RoleName": role["RoleName"],
                        "Arn": role["Arn"],
                        "CreateDate": role["CreateDate"].isoformat(),
                        "RoleLastUsed": (
                            role.get("RoleLastUsed", {})
                            .get("LastUsedDate", "")
                            .isoformat()
                            if role.get("RoleLastUsed", {}).get("LastUsedDate")
                            else None
                        ),
                    }

                    if include_policies:
                        try:
                            attached_policies = iam_client.list_attached_role_policies(
                                RoleName=role["RoleName"]
                            )
                            inline_policies = iam_client.list_role_policies(
                                RoleName=role["RoleName"]
                            )
                            role_data["AttachedPolicies"] = [
                                p["PolicyName"]
                                for p in attached_policies["AttachedPolicies"]
                            ]
                            role_data["InlinePolicies"] = inline_policies["PolicyNames"]
                        except ClientError:
                            role_data["AttachedPolicies"] = []
                            role_data["InlinePolicies"] = []

                    export_data["roles"].append(role_data)
        except Exception as e:
            typer.echo(f"   {WARNING_EMOJI} Error exporting roles: {e}")

        # Export groups
        typer.echo(f"{GROUP_EMOJI} Exporting groups...")
        try:
            paginator = iam_client.get_paginator("list_groups")
            for page in paginator.paginate():
                for group in page["Groups"]:
                    group_data = {
                        "GroupName": group["GroupName"],
                        "Arn": group["Arn"],
                        "CreateDate": group["CreateDate"].isoformat(),
                    }

                    if include_policies:
                        try:
                            attached_policies = iam_client.list_attached_group_policies(
                                GroupName=group["GroupName"]
                            )
                            inline_policies = iam_client.list_group_policies(
                                GroupName=group["GroupName"]
                            )
                            group_data["AttachedPolicies"] = [
                                p["PolicyName"]
                                for p in attached_policies["AttachedPolicies"]
                            ]
                            group_data["InlinePolicies"] = inline_policies[
                                "PolicyNames"
                            ]
                        except ClientError:
                            group_data["AttachedPolicies"] = []
                            group_data["InlinePolicies"] = []

                    export_data["groups"].append(group_data)
        except Exception as e:
            typer.echo(f"   {WARNING_EMOJI} Error exporting groups: {e}")

        # Export policies
        if include_policies:
            typer.echo(f"{POLICY_EMOJI} Exporting policies...")
            try:
                paginator = iam_client.get_paginator("list_policies")
                for page in paginator.paginate(Scope="Local"):
                    for policy in page["Policies"]:
                        policy_data = {
                            "PolicyName": policy["PolicyName"],
                            "Arn": policy["Arn"],
                            "CreateDate": policy["CreateDate"].isoformat(),
                            "UpdateDate": policy["UpdateDate"].isoformat(),
                            "AttachmentCount": policy["AttachmentCount"],
                        }

                        if include_permissions:
                            try:
                                policy_version = iam_client.get_policy_version(
                                    PolicyArn=policy["Arn"],
                                    VersionId=policy["DefaultVersionId"],
                                )
                                policy_doc = policy_version["PolicyVersion"]["Document"]
                                permissions = analyze_policy_permissions(policy_doc)
                                policy_data["Permissions"] = permissions
                                policy_data["PrivilegedPermissions"] = [
                                    p
                                    for p in permissions
                                    if is_privileged_permission(p)
                                ]
                                policy_data["WildcardPermissions"] = [
                                    p for p in permissions if "*" in p
                                ]
                            except ClientError:
                                policy_data["Permissions"] = []
                                policy_data["PrivilegedPermissions"] = []
                                policy_data["WildcardPermissions"] = []

                        export_data["policies"].append(policy_data)
            except Exception as e:
                typer.echo(f"   {WARNING_EMOJI} Error exporting policies: {e}")

        # Write to file
        filename = f"{output}.{format}"
        try:
            if format.lower() == "json":
                with open(filename, "w") as f:
                    json.dump(export_data, f, indent=2, default=str)
            elif format.lower() == "csv":
                # Create separate CSV files for each entity type
                for entity_type, data in export_data.items():
                    if entity_type == "export_info":
                        continue
                    if data:
                        csv_filename = f"{output}_{entity_type}.csv"
                        with open(csv_filename, "w", newline="") as f:
                            if data:
                                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                                writer.writeheader()
                                writer.writerows(data)
                        typer.echo(
                            f"   {SUCCESS_EMOJI} Exported {entity_type} to {csv_filename}"
                        )
                filename = f"{output}_*.csv"
            else:
                raise ValueError(f"Unsupported format: {format}")

            typer.echo(f"{SUCCESS_EMOJI} IAM data exported to {filename}")

        except Exception as e:
            typer.echo(f"{ERROR_EMOJI} Failed to write file: {e}")
            raise typer.Exit(1)

        # Summary
        typer.echo()
        typer.echo(f"{ANALYSIS_EMOJI} Export Summary:")
        typer.echo(f"  👤 Users: {len(export_data['users'])}")
        typer.echo(f"  🎭 Roles: {len(export_data['roles'])}")
        typer.echo(f"  👥 Groups: {len(export_data['groups'])}")
        typer.echo(f"  📜 Policies: {len(export_data['policies'])}")

        typer.echo()
        typer.echo(f"{TIP_EMOJI} Export Tips:")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Use JSON for detailed analysis")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Use CSV for spreadsheet analysis")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Regular exports for compliance")
        typer.echo(f"  {BEST_PRACTICE_EMOJI} Secure exported files")

    except Exception as e:
        typer.echo(f"{DANGER_EMOJI} {ERROR_EMOJI} Error exporting IAM data: {e}")
        raise typer.Exit(1)


@iam_app.command("help", help="Show IAM management help and best practices 💡")
def show_iam_help():
    """Show comprehensive IAM management help and best practices."""
    typer.echo(f"{TIP_EMOJI} IAM Management Help & Best Practices")
    typer.echo("=" * 50)
    typer.echo()

    typer.echo(f"{IAM_EMOJI} Basic Commands:")
    typer.echo(f"  awdx iam users     - List and manage IAM users")
    typer.echo(f"  awdx iam roles     - List and analyze IAM roles")
    typer.echo(f"  awdx iam policies  - List and analyze IAM policies")
    typer.echo(f"  awdx iam groups    - List and manage IAM groups")
    typer.echo()

    typer.echo(f"{AUDIT_EMOJI} Security & Compliance:")
    typer.echo(f"  awdx iam audit     - Comprehensive security audit")
    typer.echo(f"  awdx iam access    - Analyze effective permissions")
    typer.echo(f"  awdx iam compliance - Check compliance standards")
    typer.echo(f"  awdx iam smart     - Smart recommendations")
    typer.echo()

    typer.echo(f"{ANALYSIS_EMOJI} Data & Reporting:")
    typer.echo(f"  awdx iam export    - Export IAM data for analysis")
    typer.echo()

    typer.echo(f"{SECURITY_EMOJI} Security Best Practices:")
    typer.echo(f"  {BEST_PRACTICE_EMOJI} Use least privilege principle")
    typer.echo(f"  {BEST_PRACTICE_EMOJI} Enable MFA for all users")
    typer.echo(f"  {BEST_PRACTICE_EMOJI} Rotate access keys every 90 days")
    typer.echo(f"  {BEST_PRACTICE_EMOJI} Remove unused IAM entities")
    typer.echo(f"  {BEST_PRACTICE_EMOJI} Avoid wildcard permissions")
    typer.echo(f"  {BEST_PRACTICE_EMOJI} Use IAM Access Analyzer")
    typer.echo(f"  {BEST_PRACTICE_EMOJI} Monitor IAM changes")
    typer.echo(f"  {BEST_PRACTICE_EMOJI} Regular security audits")
    typer.echo()

    typer.echo(f"{AVOID_EMOJI} Common Mistakes to Avoid:")
    typer.echo(f"  {AVOID_EMOJI} Using root account for daily tasks")
    typer.echo(f"  {AVOID_EMOJI} Sharing access keys")
    typer.echo(f"  {AVOID_EMOJI} Overly permissive policies")
    typer.echo(f"  {AVOID_EMOJI} Long-lived access keys")
    typer.echo(f"  {AVOID_EMOJI} Not using MFA")
    typer.echo(f"  {AVOID_EMOJI} Ignoring unused entities")
    typer.echo()

    typer.echo(f"{INNOVATION_EMOJI} Advanced Features:")
    typer.echo(f"  {INNOVATION_EMOJI} Automated security audits")
    typer.echo(f"  {INNOVATION_EMOJI} Compliance checking")
    typer.echo(f"  {INNOVATION_EMOJI} Smart recommendations")
    typer.echo(f"  {INNOVATION_EMOJI} Permission analysis")
    typer.echo(f"  {INNOVATION_EMOJI} Data export capabilities")
    typer.echo()

    typer.echo(f"{TIP_EMOJI} For more detailed help on any command:")
    typer.echo(f"  awdx iam <command> --help")
    typer.echo()
    typer.echo(f"{TIP_EMOJI} Example workflow:")
    typer.echo(f"  1. awdx iam audit --export audit_results.json")
    typer.echo(f"  2. awdx iam smart --auto-fix --dry-run")
    typer.echo(f"  3. awdx iam compliance --standard CIS")
    typer.echo(f"  4. awdx iam export --format csv --output iam_report")
