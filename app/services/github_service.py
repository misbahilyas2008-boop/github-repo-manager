import httpx

from config.github import GitHubConfig
from core.exceptions import GitHubAPIException, RepositoryAlreadyExistsException
from utils.github_utils import encode_content_to_base64, parse_github_error_message


class GitHubService:
    """
    Thin, stateless wrapper around GitHub's REST API.
    Knows nothing about our DB or business rules — only how to talk to GitHub.
    Every method takes the user's access_token explicitly (no hidden global state).
    """

    def __init__(self, access_token: str):
        self._access_token = access_token
        self._headers = GitHubConfig.build_auth_headers(access_token)

    async def create_repository(
        self,
        name: str,
        description: str | None = None,
        private: bool = True,
    ) -> dict:
        """
        Creates a repository under the authenticated user's account.
        Docs: POST /user/repos
        """
        payload = {
            "name": name,
            "description": description or "",
            "private": private,
            "auto_init": False,  # we push README/gitignore ourselves for full control
        }

        async with httpx.AsyncClient(timeout=GitHubConfig.REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.post(
                GitHubConfig.CREATE_REPO_ENDPOINT,
                headers=self._headers,
                json=payload,
            )

        if response.status_code == 201:
            return response.json()

        response_json = self._safe_json(response)

        if response.status_code == 422 and self._is_name_conflict(response_json):
            raise RepositoryAlreadyExistsException(name)

        raise GitHubAPIException(
            message=parse_github_error_message(response_json),
            status_code=response.status_code,
            github_response=response_json,
        )

    async def create_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content: str,
        commit_message: str,
        branch: str | None = None,
    ) -> dict:
        """
        Creates a single file in the repo via the Contents API.
        Docs: PUT /repos/{owner}/{repo}/contents/{path}
        """
        url = GitHubConfig.REPO_CONTENTS_ENDPOINT_TMPL.format(owner=owner, repo=repo, path=path)

        payload = {
            "message": commit_message,
            "content": encode_content_to_base64(content),
        }
        if branch:
            payload["branch"] = branch

        async with httpx.AsyncClient(timeout=GitHubConfig.REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.put(url, headers=self._headers, json=payload)

        if response.status_code in (200, 201):
            return response.json()

        response_json = self._safe_json(response)
        raise GitHubAPIException(
            message=parse_github_error_message(response_json),
            status_code=response.status_code,
            github_response=response_json,
        )

    async def get_repository(self, owner: str, repo: str) -> dict:
        """
        Fetches repo metadata. Useful for verifying creation / later modules.
        Docs: GET /repos/{owner}/{repo}
        """
        url = GitHubConfig.GET_REPO_ENDPOINT_TMPL.format(owner=owner, repo=repo)

        async with httpx.AsyncClient(timeout=GitHubConfig.REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.get(url, headers=self._headers)

        if response.status_code == 200:
            return response.json()

        response_json = self._safe_json(response)
        raise GitHubAPIException(
            message=parse_github_error_message(response_json),
            status_code=response.status_code,
            github_response=response_json,
        )

    @staticmethod
    def _safe_json(response: httpx.Response) -> dict:
        try:
            return response.json()
        except ValueError:
            return {"message": response.text or "Unknown error (non-JSON response)."}

    @staticmethod
    def _is_name_conflict(response_json: dict) -> bool:
        errors = response_json.get("errors") or []
        return any(
            isinstance(err, dict) and "already exists" in (err.get("message") or "")
            for err in errors
        )
