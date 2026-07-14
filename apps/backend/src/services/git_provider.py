import hmac
import hashlib
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import httpx

# ==========================================
# Git Provider Interface
# ==========================================

class GitProviderBase(ABC):
    @abstractmethod
    async def list_repositories(self, token: str) -> List[Dict[str, Any]]:
        """
        Lists available remote repositories for the authenticated user.
        """
        pass

    @abstractmethod
    async def create_webhook(self, token: str, repo_full_name: str, target_url: str, secret: str) -> str:
        """
        Registers a push webhook at the Git host, returning the external webhook ID.
        """
        pass

    @abstractmethod
    def verify_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """
        Verifies that a received webhook payload matches the host signature secret.
        """
        pass

    @abstractmethod
    async def list_branches(self, token: str, repo_full_name: str) -> List[str]:
        """
        Fetches the branch list for the specified repository.
        """
        pass

    @abstractmethod
    async def list_commits(self, token: str, repo_full_name: str, branch: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves the commit history log.
        """
        pass

# ==========================================
# GitHub Implementation
# ==========================================

class GitHubProvider(GitProviderBase):
    def __init__(self, base_url: str = "https://api.github.com"):
        self.base_url = base_url

    async def list_repositories(self, token: str) -> List[Dict[str, Any]]:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{self.base_url}/user/repos?per_page=100", headers=headers)
            if res.status_code != 200:
                raise Exception(f"GitHub repo listing failed: {res.text}")
            repos = res.json()
            return [
                {
                    "external_id": str(r["id"]),
                    "name": r["name"],
                    "full_name": r["full_name"],
                    "clone_url": r["clone_url"],
                    "default_branch": r.get("default_branch", "main"),
                }
                for r in repos
            ]

    async def create_webhook(self, token: str, repo_full_name: str, target_url: str, secret: str) -> str:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        payload = {
            "name": "web",
            "active": True,
            "events": ["push"],
            "config": {
                "url": target_url,
                "content_type": "json",
                "secret": secret,
            }
        }
        async with httpx.AsyncClient() as client:
            res = await client.post(
                f"{self.base_url}/repos/{repo_full_name}/hooks",
                headers=headers,
                json=payload
            )
            if res.status_code not in [200, 201]:
                # If webhook already exists, attempt to parse or raise
                raise Exception(f"GitHub webhook registration failed: {res.text}")
            hook_data = res.json()
            return str(hook_data["id"])

    def verify_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """
        Verifies GitHub's X-Hub-Signature-256 HMAC header.
        """
        if not signature or not signature.startswith("sha256="):
            return False
        
        expected_sig = "sha256=" + hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_sig, signature)

    async def list_branches(self, token: str, repo_full_name: str) -> List[str]:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{self.base_url}/repos/{repo_full_name}/branches", headers=headers)
            if res.status_code != 200:
                raise Exception(f"GitHub branch fetch failed: {res.text}")
            branches = res.json()
            return [b["name"] for b in branches]

    async def list_commits(self, token: str, repo_full_name: str, branch: Optional[str] = None) -> List[Dict[str, Any]]:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        url = f"{self.base_url}/repos/{repo_full_name}/commits"
        if branch:
            url += f"?sha={branch}"
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=headers)
            if res.status_code != 200:
                raise Exception(f"GitHub commits fetch failed: {res.text}")
            commits = res.json()
            return [
                {
                    "sha": c["sha"],
                    "message": c["commit"]["message"],
                    "author": c["commit"]["author"]["name"],
                    "date": c["commit"]["author"]["date"],
                }
                for c in commits
            ]
