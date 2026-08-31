import logging
import subprocess
from typing import Dict, Any
from google import genai
from google.genai import types
from app.config import settings
from app.services.git_service import git_service
from app.mcp.mcp_client import mcp_client

logger = logging.getLogger(__name__)

class GitOpsAgent:
    """
    GitOps & Version Control Agent (Google ADK / Gemini 3.6 Flash)
    Manages automated Git workflows:
    - Generates conventional AI commit messages from git diffs
    - Formulates structured GitHub Pull Request summaries
    - Manages feature branching and pushes branches to remote repositories.
    """

    def __init__(self):
        raw_key = settings.gemini_api_key or ""
        self.api_key = raw_key.strip().strip("'").strip('"')
        self.client = genai.Client(api_key=self.api_key) if self.api_key and len(self.api_key) > 10 else None

    def commit_and_generate_pr(self, task_title: str, branch_name: str = "feature/agent-sdlc") -> Dict[str, Any]:
        """
        Full GitOps Workflow:
        1. Checkout/Create feature branch
        2. Analyze workspace git diff via Gemini 3.6 Flash
        3. Generate conventional commit message
        4. Commit staged code
        5. Generate AI Pull Request summary
        6. Push feature branch to GitHub remote origin
        """
        # Step 1: Checkout/Create Branch via MCP Tool Gateway
        branch_res = mcp_client.execute_mcp_tool("git_checkout_branch", {"branch_name": branch_name})
        active_branch = branch_res.get("branch", branch_name)
        
        # Step 2: Get Git Diff / Changed Files context
        diff_summary = self._get_staged_diff_summary()

        # Step 3: Generate AI Commit Message using ADK / Gemini 3.6 Flash
        commit_message = self._generate_ai_commit_message(task_title, diff_summary)

        # Step 4: Commit changes to local git repo via MCP Tool Gateway
        commit_res = mcp_client.execute_mcp_tool("git_commit_staged", {"commit_message": commit_message})
        commit_sha = commit_res.get("commit_sha", "head-commit")

        # Step 5: Generate AI Pull Request Summary using ADK / Gemini 3.6 Flash
        pr_summary = self._generate_pr_summary(task_title, active_branch, commit_sha, diff_summary)

        # Step 6: Push branch to GitHub via MCP Tool Gateway
        push_res = mcp_client.execute_mcp_tool("git_push_remote", {"branch_name": active_branch})
        push_success = push_res.get("pushed", True)

        from app.services.telemetry import telemetry
        telemetry.log_agent_event(
            agent_name="GitOps Agent",
            event_type="GITOPS_COMMIT",
            pipeline_id=f"pipe-{active_branch}",
            summary=f"Committed changes to {active_branch} ({commit_sha[:7]}): '{commit_message}'",
            details={
                "branch": active_branch,
                "commit_sha": commit_sha,
                "commit_message": commit_message,
                "pushed": push_success
            }
        )

        return {
            "success": True,
            "branch": active_branch,
            "commit_sha": commit_sha,
            "commit_message": commit_message,
            "pr_summary": pr_summary,
            "pushed_to_remote": push_success,
            "pr_url": f"{settings.git_repo_url.replace('.git', '')}/pull/new/{active_branch}"
        }

    def _generate_ai_commit_message(self, task_title: str, diff_summary: str) -> str:
        """Use Gemini 3.6 Flash to format conventional semantic commit message."""
        if not self.client:
            return f"feat(agent): update {task_title}"

        prompt = f"""
        Task Title: {task_title}
        Git Diff Summary:
        {diff_summary}

        Generate a single-line conventional git commit message (e.g. 'feat(apex): add student controller and LWC form').
        Do not add backticks or markdown formatting. Keep under 72 characters.
        """
        from pathlib import Path
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        skill_file = base_dir / ".agents" / "skills" / "gitops-conventions" / "SKILL.md"
        skill_context = skill_file.read_text(encoding="utf-8") if skill_file.exists() else ""

        from app.agents.adk_tools import execute_git_commit, push_git_feature_branch

        try:
            response = self.client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=f"You are a Senior DevOps Engineer. Follow SKILL INSTRUCTIONS (gitops-conventions):\n{skill_context}",
                    tools=[execute_git_commit, push_git_feature_branch],
                    temperature=0.1
                )
            )
            msg = response.text.strip().replace("`", "")
            return msg if len(msg) > 5 else f"feat(agent): update {task_title}"
        except Exception as e:
            logger.warning(f"Gemini commit message generation fallback: {e}")
            return f"feat(agent): update {task_title}"

    def _generate_pr_summary(self, task_title: str, branch: str, commit_sha: str, diff_summary: str) -> str:
        """Use Gemini 3.6 Flash to generate detailed GitHub Pull Request documentation."""
        if not self.client:
            return f"### PR: {task_title}\n\n- **Branch:** `{branch}`\n- **Commit:** `{commit_sha}`\n- Automated SDLC pull request generated by NexusDev AI GitOps Agent."

        prompt = f"""
        Generate a Markdown GitHub Pull Request summary for:
        Task Title: {task_title}
        Feature Branch: {branch}
        Commit SHA: {commit_sha}
        Modified Metadata Summary:
        {diff_summary}

        Structure:
        1. ## Overview
        2. ## Key Modifications (Apex Classes, LWC Bundles, Metadata)
        3. ## Risk Assessment (Low/Medium/High)
        4. ## Verification & Testing Completed
        """
        try:
            response = self.client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction="You are a Lead Software Architect drafting GitHub PR notes.",
                    temperature=0.2
                )
            )
            return response.text.strip()
        except Exception as e:
            logger.warning(f"Gemini PR summary generation fallback: {e}")
            return f"### PR: {task_title}\n\n- **Branch:** `{branch}`\n- **Commit:** `{commit_sha}`\n- Automated SDLC pull request generated by NexusDev AI GitOps Agent."

    def _get_staged_diff_summary(self) -> str:
        """Retrieve list of modified force-app files from git status."""
        try:
            repo_dir = git_service.repo_dir
            res = subprocess.run(["git", "status", "--porcelain", "force-app/"], cwd=repo_dir, capture_output=True, text=True)
            output = res.stdout.strip()
            return output if output else "force-app/main/default/classes and LWC bundles modified."
        except Exception:
            return "force-app components created or updated."

git_agent = GitOpsAgent()
