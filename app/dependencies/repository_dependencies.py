"""
NOTE: `get_current_user` is assumed to already exist from your completed
login/OAuth module (it likely decodes the JWT/session and returns the User
row, which stores the encrypted GitHub access_token after refresh).
Adjust the import path below to match your actual auth module location.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from core.exceptions import GitHubTokenMissingException
from database.session import get_db
from controllers.repository_controller import RepositoryController
from services.github_service import GitHubService

# from dependencies.auth import get_current_user  # <-- your existing auth dependency
# from models.user import User


def get_github_access_token(current_user=Depends(lambda: None)) -> str:
    """
    Placeholder wiring: replace `current_user` dependency with your real
    `get_current_user` from the auth module. It must expose a valid,
    already-refreshed GitHub access token (e.g. current_user.github_access_token).
    """
    # Example of real implementation once wired to your auth module:
    #
    # def get_github_access_token(current_user: User = Depends(get_current_user)) -> str:
    #     if not current_user.github_access_token:
    #         raise GitHubTokenMissingException()
    #     return current_user.github_access_token

    if current_user is None or not getattr(current_user, "github_access_token", None):
        raise GitHubTokenMissingException()

    return current_user.github_access_token


def get_github_service(access_token: str = Depends(get_github_access_token)) -> GitHubService:
    return GitHubService(access_token=access_token)


def get_repository_controller(
    db: Session = Depends(get_db),
    github_service: GitHubService = Depends(get_github_service),
) -> RepositoryController:
    return RepositoryController(db=db, github_service=github_service)
