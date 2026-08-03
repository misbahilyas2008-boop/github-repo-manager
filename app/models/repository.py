import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum as SqlEnum, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.session import Base


class RepositoryVisibility(str, enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"


class RepositoryStatus(str, enum.Enum):
    PENDING = "pending"      # create request accepted, GitHub calls in progress
    CREATED = "created"      # repo + README pushed successfully
    FAILED = "failed"        # something went wrong (see last_error)


class Repository(Base):
    """
    Local record of a GitHub repository created through the agent.
    Mirrors the GitHub repo but stores just enough metadata for
    dashboard listing, analytics, and linking to later modules
    (change detection, PRs, code review, etc.).
    """

    __tablename__ = "repositories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # FK to your existing users table (assumed to exist from the auth module)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_login: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    visibility: Mapped[RepositoryVisibility] = mapped_column(
        SqlEnum(RepositoryVisibility, name="repository_visibility"), default=RepositoryVisibility.PRIVATE
    )
    status: Mapped[RepositoryStatus] = mapped_column(
        SqlEnum(RepositoryStatus, name="repository_status"), default=RepositoryStatus.PENDING
    )

    github_repo_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, unique=True)
    html_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    clone_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    default_branch: Mapped[str] = mapped_column(String(100), default="main")

    has_readme: Mapped[bool] = mapped_column(Boolean, default=False)
    has_gitignore: Mapped[bool] = mapped_column(Boolean, default=False)

    last_error: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user = relationship("User", back_populates="repositories", lazy="joined")
