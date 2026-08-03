import uuid
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, field_validator

from models.repository import RepositoryVisibility, RepositoryStatus


class RepositoryCreateRequest(BaseModel):
    """
    Payload for POST /api/repos
    (No AI generation yet — description/readme are optional and default to
    hardcoded content if omitted, per the "test the GitHub flow first" plan.)
    """

    name: str = Field(..., min_length=1, max_length=100, description="Desired repository name")
    description: str | None = Field(default=None, max_length=1000)
    visibility: RepositoryVisibility = Field(default=RepositoryVisibility.PRIVATE)
    auto_init_readme: bool = Field(
        default=True, description="Whether to push a README.md right after creation"
    )
    auto_init_gitignore: bool = Field(
        default=False, description="Whether to push a default .gitignore right after creation"
    )

    @field_validator("name")
    @classmethod
    def name_must_be_reasonable(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Repository name cannot be empty.")
        return value.strip()


class RepositoryResponse(BaseModel):
    """
    What we return to the frontend after a repo is created (or while pending).
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    owner_login: str
    description: str | None
    visibility: RepositoryVisibility
    status: RepositoryStatus

    github_repo_id: int | None
    html_url: str | None
    clone_url: str | None
    default_branch: str

    has_readme: bool
    has_gitignore: bool
    last_error: str | None

    created_at: datetime
    updated_at: datetime


class RepositoryListResponse(BaseModel):
    total: int
    items: list[RepositoryResponse]
