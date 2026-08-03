import logging
import uuid

from sqlalchemy.orm import Session

from config.github import GitHubConfig
from core.exceptions import GitHubAPIException, RepositoryAlreadyExistsException
from models.repository import Repository, RepositoryStatus, RepositoryVisibility
from schemas.repository import RepositoryCreateRequest
from services.github_service import GitHubService
from utils.github_utils import (
    default_gitignore_content,
    default_readme_content,
    slugify_repo_name,
)

logger = logging.getLogger(__name__)


class RepositoryController:
    """
    Orchestrates repository creation:
    1. Talk to GitHub (create repo, push README/.gitignore)
    2. Persist local record for dashboard/analytics
    3. Handle partial failures gracefully (repo created on GitHub but DB write failed, etc.)
    """

    def __init__(self, db: Session, github_service: GitHubService):
        self.db = db
        self.github_service = github_service

    async def create_repository(
        self,
        user_id: uuid.UUID,
        payload: RepositoryCreateRequest,
    ) -> Repository:
        repo_name = slugify_repo_name(payload.name)
        is_private = payload.visibility == RepositoryVisibility.PRIVATE

        # 1. Create a local "pending" row first so we always have a trace,
        #    even if the GitHub call fails halfway through.
        local_repo = Repository(
            user_id=user_id,
            name=repo_name,
            owner_login="",  # filled in once GitHub confirms creation
            description=payload.description,
            visibility=payload.visibility,
            status=RepositoryStatus.PENDING,
        )
        self.db.add(local_repo)
        self.db.commit()
        self.db.refresh(local_repo)

        try:
            github_repo = await self.github_service.create_repository(
                name=repo_name,
                description=payload.description,
                private=is_private,
            )
        except RepositoryAlreadyExistsException:
            self._mark_failed(local_repo, "Repository name already exists on GitHub.")
            raise
        except GitHubAPIException as exc:
            self._mark_failed(local_repo, exc.message)
            raise

        owner_login = github_repo["owner"]["login"]

        local_repo.owner_login = owner_login
        local_repo.github_repo_id = github_repo["id"]
        local_repo.html_url = github_repo["html_url"]
        local_repo.clone_url = github_repo["clone_url"]
        local_repo.default_branch = github_repo.get("default_branch") or GitHubConfig.DEFAULT_BRANCH
        self.db.commit()

        # 2. Push README (hardcoded content for now — AI generation comes later)
        if payload.auto_init_readme:
            await self._push_readme(local_repo, owner_login, repo_name, payload.description)

        # 3. Push .gitignore (optional, hardcoded for now)
        if payload.auto_init_gitignore:
            await self._push_gitignore(local_repo, owner_login, repo_name)

        local_repo.status = RepositoryStatus.CREATED
        local_repo.last_error = None
        self.db.commit()
        self.db.refresh(local_repo)

        return local_repo

    async def _push_readme(
        self, local_repo: Repository, owner: str, repo: str, description: str | None
    ) -> None:
        try:
            content = default_readme_content(repo_name=repo, description=description or "")
            await self.github_service.create_file(
                owner=owner,
                repo=repo,
                path=GitHubConfig.DEFAULT_README_PATH,
                content=content,
                commit_message="chore: initial README via AI Software Engineering Agent",
                branch=local_repo.default_branch,
            )
            local_repo.has_readme = True
            self.db.commit()
        except GitHubAPIException as exc:
            # Repo already exists on GitHub at this point — don't fail the whole
            # request, just record the issue so the user can retry pushing README.
            logger.warning("README push failed for repo %s: %s", repo, exc.message)
            local_repo.last_error = f"README push failed: {exc.message}"
            self.db.commit()

    async def _push_gitignore(self, local_repo: Repository, owner: str, repo: str) -> None:
        try:
            await self.github_service.create_file(
                owner=owner,
                repo=repo,
                path=GitHubConfig.DEFAULT_GITIGNORE_PATH,
                content=default_gitignore_content(),
                commit_message="chore: initial .gitignore via AI Software Engineering Agent",
                branch=local_repo.default_branch,
            )
            local_repo.has_gitignore = True
            self.db.commit()
        except GitHubAPIException as exc:
            logger.warning(".gitignore push failed for repo %s: %s", repo, exc.message)
            local_repo.last_error = f".gitignore push failed: {exc.message}"
            self.db.commit()

    def _mark_failed(self, local_repo: Repository, error_message: str) -> None:
        local_repo.status = RepositoryStatus.FAILED
        local_repo.last_error = error_message
        self.db.commit()

    def list_repositories(self, user_id: uuid.UUID) -> list[Repository]:
        return (
            self.db.query(Repository)
            .filter(Repository.user_id == user_id)
            .order_by(Repository.created_at.desc())
            .all()
        )
