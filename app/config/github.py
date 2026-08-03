from urllib.parse import urlencode

from config.settings import settings


class GitHubConfig:
    """
    Centralized GitHub OAuth + REST API configuration.
    Keep ALL GitHub-related URLs/constants here so services never hardcode strings.
    """

    CLIENT_ID = settings.GITHUB_CLIENT_ID
    CLIENT_SECRET = settings.GITHUB_CLIENT_SECRET
    REDIRECT_URI = settings.GITHUB_REDIRECT_URI

    # ---- OAuth ----
    AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"

    USER_API_URL = "https://api.github.com/user"
    USER_EMAILS_API_URL = "https://api.github.com/user/emails"

    DEFAULT_SCOPE = (
        "read:user",
        "user:email",
        "repo",
    )

    # ---- REST API base ----
    API_BASE_URL = "https://api.github.com"
    API_VERSION_HEADER = "2022-11-28"  # X-GitHub-Api-Version

    # ---- Repository endpoints (templated, filled by service) ----
    CREATE_REPO_ENDPOINT = f"{API_BASE_URL}/user/repos"
    CREATE_ORG_REPO_ENDPOINT_TMPL = API_BASE_URL + "/orgs/{org}/repos"
    REPO_CONTENTS_ENDPOINT_TMPL = API_BASE_URL + "/repos/{owner}/{repo}/contents/{path}"
    GET_REPO_ENDPOINT_TMPL = API_BASE_URL + "/repos/{owner}/{repo}"

    # ---- Defaults used when creating a repository ----
    DEFAULT_README_PATH = "README.md"
    DEFAULT_GITIGNORE_PATH = ".gitignore"
    DEFAULT_BRANCH = "main"

    REQUEST_TIMEOUT_SECONDS = 15.0

    @classmethod
    def get_authorization_url(cls, state: str) -> str:
        """
        Generate GitHub OAuth authorization URL.
        """
        params = {
            "client_id": cls.CLIENT_ID,
            "redirect_uri": cls.REDIRECT_URI,
            "scope": " ".join(cls.DEFAULT_SCOPE),
            "state": state,
        }

        return f"{cls.AUTHORIZE_URL}?{urlencode(params)}"

    @classmethod
    def build_auth_headers(cls, access_token: str) -> dict:
        """
        Standard headers required for authenticated GitHub REST API calls.
        """
        return {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": cls.API_VERSION_HEADER,
        }
