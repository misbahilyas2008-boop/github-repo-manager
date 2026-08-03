class AppException(Exception):
    """
    Base exception for all application-level (non-HTTP) errors.
    Controllers/routes translate these into proper HTTPException responses.
    """

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class GitHubAPIException(AppException):
    """
    Raised when a call to the GitHub REST API fails or returns an error payload.
    """

    def __init__(self, message: str, status_code: int = 502, github_response: dict | None = None):
        self.github_response = github_response or {}
        super().__init__(message, status_code)


class RepositoryAlreadyExistsException(AppException):
    """
    Raised when the user already has a repository with the same name on GitHub.
    """

    def __init__(self, repo_name: str):
        super().__init__(
            message=f"A repository named '{repo_name}' already exists on this GitHub account.",
            status_code=409,
        )


class GitHubTokenMissingException(AppException):
    """
    Raised when the authenticated user has no valid GitHub access token stored.
    """

    def __init__(self):
        super().__init__(
            message="No valid GitHub access token found for this user. Please reconnect your GitHub account.",
            status_code=401,
        )
