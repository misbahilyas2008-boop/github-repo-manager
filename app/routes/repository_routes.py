import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from controllers.repository_controller import RepositoryController
from core.exceptions import AppException
from dependencies.repository_dependencies import get_repository_controller
from schemas.repository import (
    RepositoryCreateRequest,
    RepositoryListResponse,
    RepositoryResponse,
)

# from dependencies.auth import get_current_user
# from models.user import User

router = APIRouter(prefix="/api/repos", tags=["Repositories"])


@router.post(
    "",
    response_model=RepositoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new GitHub repository (hardcoded README, no AI yet)",
)
async def create_repository(
    payload: RepositoryCreateRequest,
    controller: RepositoryController = Depends(get_repository_controller),
    # current_user: User = Depends(get_current_user),
):
    try:
        # replace with real user id once auth dependency is wired in:
        # user_id = current_user.id
        user_id = uuid.uuid4()  # TODO: remove — placeholder for standalone testing

        repository = await controller.create_repository(user_id=user_id, payload=payload)
        return repository

    except AppException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.get(
    "",
    response_model=RepositoryListResponse,
    summary="List repositories created by the current user",
)
def list_repositories(
    controller: RepositoryController = Depends(get_repository_controller),
    # current_user: User = Depends(get_current_user),
):
    user_id = uuid.uuid4()  # TODO: replace with current_user.id

    repositories = controller.list_repositories(user_id=user_id)
    return RepositoryListResponse(total=len(repositories), items=repositories)
