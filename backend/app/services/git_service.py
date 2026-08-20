import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

class GitService:
    """
    Git Version Control Service:
    Manages local Git feature branches and commits generated/modified Salesforce code.
    """

    def __init__(self):
        self.repo_dir = Path(__file__).resolve().parent.parent.parent.parent
        self._ensure_git_repo()

    def _ensure_git_repo(self):
        """Ensure git repository is initialized."""
        if not (self.repo_dir / ".git").exists():
            logger.info("Initializing Git repository in workspace root...")
            subprocess.run(["git", "init"], cwd=self.repo_dir, capture_output=True)

    def create_or_checkout_branch(self, branch_name: str = "feature/agent-sdlc") -> str:
        """Create or checkout a Git feature branch for agent development."""
        try:
            # Check if branch exists
            res = subprocess.run(["git", "checkout", "-b", branch_name], cwd=self.repo_dir, capture_output=True, text=True)
            if res.returncode != 0:
                # Switch if already exists
                subprocess.run(["git", "checkout", branch_name], cwd=self.repo_dir, capture_output=True, text=True)
            logger.info(f"Git feature branch active: '{branch_name}'")
            return branch_name
        except Exception as e:
            logger.warning(f"Note on Git branch checkout: {e}")
            return "main"

    def commit_changes(self, commit_message: str = "feat(agent): update generated salesforce components") -> str:
        """Stage force-app changes and commit to current branch."""
        try:
            # Stage force-app files
            subprocess.run(["git", "add", "force-app/"], cwd=self.repo_dir, capture_output=True)
            
            # Commit changes
            res = subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.repo_dir,
                capture_output=True,
                text=True
            )
            
            # Get latest commit SHA
            sha_res = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=self.repo_dir,
                capture_output=True,
                text=True
            )
            commit_sha = sha_res.stdout.strip() if sha_res.returncode == 0 else "head-commit"
            logger.info(f"Committed changes to Git branch. Commit SHA: {commit_sha}")
            return commit_sha
        except Exception as e:
            logger.warning(f"Note on Git commit: {e}")
            return "local-commit"

    def push_branch(self, branch_name: str = None) -> bool:
        """Push current branch to remote GitHub repository."""
        try:
            target_branch = branch_name or "main"
            res = subprocess.run(
                ["git", "push", "-u", "origin", target_branch],
                cwd=self.repo_dir,
                capture_output=True,
                text=True
            )
            if res.returncode == 0:
                logger.info(f"Successfully pushed branch '{target_branch}' to remote origin.")
                return True
            else:
                logger.warning(f"Git push returned non-zero code: {res.stderr}")
                return False
        except Exception as e:
            logger.warning(f"Error during Git push: {e}")
            return False

git_service = GitService()
