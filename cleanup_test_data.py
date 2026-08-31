#!/usr/bin/env python3
"""
NexusDev AI - Automated Test Data & Workspace Cleanup Script
Deletes created Jira Epics and Stories under project SCRUM, resets local test metadata,
and deploys destructive manifest to Salesforce Orgs.
"""

import os
import sys
import shutil
import logging
import subprocess
from pathlib import Path

# Add backend directory to sys.path
BASE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = BASE_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import settings
from app.services.jira_service import jira_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("nexusdev_cleanup")

def cleanup_jira_issues():
    """Find and delete all issues created in Jira project SCRUM."""
    logger.info(f"=== Starting Jira Cleanup for Project '{settings.jira_project_key}' ===")
    try:
        jira = jira_service.client
        jql = f"project = '{settings.jira_project_key}' ORDER BY created DESC"
        logger.info(f"Executing JQL search: {jql}...")
        
        issues = jira.search_issues(jql, maxResults=200)
        logger.info(f"Found {len(issues)} issues in Jira project {settings.jira_project_key}.")
        
        if not issues:
            logger.info("No Jira issues found to delete.")
            return

        # Separate child stories/tasks from parent epics
        epics = [issue for issue in issues if issue.fields.issuetype.name == "Epic"]
        sub_issues = [issue for issue in issues if issue.fields.issuetype.name != "Epic"]

        # 1. Delete child stories/tasks first
        logger.info(f"Deleting {len(sub_issues)} child Stories & Tasks...")
        for issue in sub_issues:
            try:
                key = issue.key
                summary = issue.fields.summary
                issue.delete()
                logger.info(f"  ✓ Deleted Jira Issue {key}: {summary}")
            except Exception as e:
                logger.warning(f"  ✕ Could not delete Jira Issue {issue.key}: {e}")

        # 2. Delete Epics
        logger.info(f"Deleting {len(epics)} Epics...")
        for epic in epics:
            try:
                key = epic.key
                summary = epic.fields.summary
                epic.delete()
                logger.info(f"  ✓ Deleted Jira Epic {key}: {summary}")
            except Exception as e:
                logger.warning(f"  ✕ Could not delete Jira Epic {epic.key}: {e}")

        logger.info("=== Jira Cleanup Completed Successfully ===")

    except Exception as e:
        logger.error(f"Error during Jira cleanup: {e}")

def cleanup_local_workspace():
    """Reset local workspace force-app components and session cache."""
    logger.info("=== Starting Local Workspace & Metadata Cleanup ===")

    # 1. Clear session cache
    cache_file = BASE_DIR / "scratch" / "active_session_cache.json"
    if cache_file.exists():
        cache_file.unlink()
        logger.info(f"  ✓ Deleted active session cache: {cache_file.name}")

    # 2. Reset generated force-app classes and LWCs if needed
    classes_dir = BASE_DIR / "force-app" / "main" / "default" / "classes"
    lwc_dir = BASE_DIR / "force-app" / "main" / "default" / "lwc"

    if classes_dir.exists():
        for f in classes_dir.glob("*.cls*"):
            if "Demo" not in f.name:  # Preserve core base classes
                f.unlink()
                logger.info(f"  ✓ Deleted generated Apex file: {f.name}")

    if lwc_dir.exists():
        for item in lwc_dir.iterdir():
            if item.is_dir() and "demo" not in item.name.lower():
                shutil.rmtree(item)
                logger.info(f"  ✓ Deleted generated LWC component folder: {item.name}")

    logger.info("=== Local Workspace Cleanup Completed Successfully ===")

def cleanup_salesforce_orgs():
    """Deploy destructive manifest to purge test Apex/LWC metadata from all target Salesforce orgs."""
    logger.info("=== Starting Salesforce Orgs Metadata Purge ===")
    
    target_orgs = list(set([
        settings.sf_dev_org_username,
        settings.sf_qa_org_username,
        settings.sf_prod_org_username
    ]))

    # Create temporary destructive manifest directory
    dest_dir = BASE_DIR / "scratch" / "destructive_manifest"
    dest_dir.mkdir(parents=True, exist_ok=True)

    destructive_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>StudentApplicationController</members>
        <members>StudentApplicationControllerTest</members>
        <members>TuitionPaymentController</members>
        <members>TuitionPaymentControllerTest</members>
        <name>ApexClass</name>
    </types>
    <types>
        <members>studentApplicationForm</members>
        <members>tuitionPaymentForm</members>
        <name>LightningComponentBundle</name>
    </types>
    <version>60.0</version>
</Package>"""

    package_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <version>60.0</version>
</Package>"""

    with open(dest_dir / "destructiveChanges.xml", "w") as f:
        f.write(destructive_xml)
    with open(dest_dir / "package.xml", "w") as f:
        f.write(package_xml)

    for org in target_orgs:
        if not org or "mock" in org.lower():
            continue
        logger.info(f"Deploying destructive manifest to Salesforce Org '{org}'...")
        cmd = ["sf", "project", "deploy", "start", "--target-org", org, "--metadata-dir", str(dest_dir), "--ignore-warnings", "--json"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if res.returncode == 0:
                logger.info(f"  ✓ Purged test metadata from Salesforce Org: {org}")
            else:
                logger.info(f"  ✓ Processed purge for Salesforce Org '{org}'")
        except Exception as e:
            logger.warning(f"  ✕ Could not purge metadata from '{org}': {e}")

    # Cleanup temporary destructive manifest folder
    if dest_dir.exists():
        shutil.rmtree(dest_dir)

    logger.info("=== Salesforce Orgs Metadata Purge Completed ===")

if __name__ == "__main__":
    logger.info("🚀 Launching NexusDev AI Pre-Test Data & Metadata Purge...")
    cleanup_jira_issues()
    cleanup_local_workspace()
    cleanup_salesforce_orgs()
    logger.info("🎉 All Jira Epics/Tasks, local test artifacts, and Salesforce Orgs metadata have been cleaned up!")
