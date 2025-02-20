from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_maker
from app.schemas import (
    ProjectsBase,
    UsersBase,
    ProjectCreate,
    ProjectOut,
    ProjectUpdate,
    ProjectDetailResponse,
    UserResponse,
)

router = APIRouter(prefix="/projects", tags=["Projects CRUD"])


async def get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(
        project: ProjectCreate, session: AsyncSession = Depends(get_async_session)
):
    """
    Создает новый проект.
    """
    new_project = ProjectsBase(
        name=project.name,
        description=project.description,
        owner_id=project.owner_id,
        url=project.url,
    )
    session.add(new_project)
    await session.commit()
    await session.refresh(new_project)
    # Так как проект только создан, количество пользователей равно 0
    return ProjectOut(
        id=new_project.id,
        name=new_project.name,
        description=new_project.description,
        owner_id=new_project.owner_id,
        url=new_project.url,
        user_count=0,
    )


@router.put("/owner/{project_id}", response_model=ProjectOut)
async def update_project(
        project_id: int,
        owner_id: int,
        project: ProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Обновляет проект.
    """
    result = await session.execute(
        select(ProjectsBase).where(ProjectsBase.id == project_id)
    )
    db_project = result.scalar_one_or_none()
    if not db_project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    if db_project.owner_id != owner_id:
        raise HTTPException(
            status_code=403, detail="Нет прав для изменения этого проекта"
        )

    if project.name is not None:
        db_project.name = project.name
    if project.description is not None:
        db_project.description = project.description
    if project.url is not None:
        db_project.url = project.url

    await session.commit()
    await session.refresh(db_project)

    result_count = await session.execute(
        select(func.count(UsersBase.id)).where(UsersBase.project_id == db_project.id)
    )
    user_count = result_count.scalar() or 0

    return ProjectOut(
        id=db_project.id,
        name=db_project.name,
        description=db_project.description,
        owner_id=db_project.owner_id,
        url=db_project.url,
        user_count=user_count,
    )


@router.delete("/owner/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
        project_id: int, owner_id: int, session: AsyncSession = Depends(get_async_session)
):
    """
    Удаляет проект, если запрос исходит от его владельца.
    """
    result = await session.execute(
        select(ProjectsBase).where(ProjectsBase.id == project_id)
    )
    db_project = result.scalar_one_or_none()
    if not db_project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    if db_project.owner_id != owner_id:
        raise HTTPException(
            status_code=403, detail="Нет прав для удаления этого проекта"
        )

    await session.delete(db_project)
    await session.commit()
    return  # 204 No Content


@router.get("/owner/{owner_id}", response_model=List[ProjectOut])
async def list_projects(
        owner_id: int, session: AsyncSession = Depends(get_async_session)
):
    """
    Возвращает список всех проектов администратора с количеством пользователей.
    """
    stmt = (
        select(
            ProjectsBase.id,
            ProjectsBase.name,
            ProjectsBase.description,
            ProjectsBase.owner_id,
            func.count(UsersBase.id).label("user_count"),
        )
        .outerjoin(UsersBase, UsersBase.project_id == ProjectsBase.id)
        .where(ProjectsBase.owner_id == owner_id)
        .group_by(ProjectsBase.id)
    )
    result = await session.execute(stmt)
    projects = result.all()
    if not projects:
        raise HTTPException(status_code=404, detail="Проекты не найдены")

    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "owner_id": p.owner_id,
            "user_count": p.user_count,
        }
        for p in projects
    ]


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project_details(
        project_id: int, owner_id: int, session: AsyncSession = Depends(get_async_session)
):
    """
    Получение деталей проекта, включая список пользователей.
    """
    stmt = (
        select(
            ProjectsBase.id,
            ProjectsBase.name,
            ProjectsBase.description,
            ProjectsBase.owner_id,
            ProjectsBase.url,
            func.count(UsersBase.id).label("user_count"),
        )
        .outerjoin(UsersBase, UsersBase.project_id == ProjectsBase.id)
        .where(ProjectsBase.id == project_id, ProjectsBase.owner_id == owner_id)
        .group_by(ProjectsBase.id)
    )
    result = await session.execute(stmt)
    project_row = result.first()
    if not project_row:
        raise HTTPException(
            status_code=404, detail="Проект не найден или доступ запрещён"
        )

    result_users = await session.execute(
        select(UsersBase).where(UsersBase.project_id == project_id)
    )
    users = result_users.scalars().all()
    user_responses = [
        UserResponse(id=user.id, login=user.login, email=user.email) for user in users
    ]

    return ProjectDetailResponse(
        id=project_row.id,
        name=project_row.name,
        description=project_row.description,
        owner_id=project_row.owner_id,
        url=project_row.url,
        user_count=project_row.user_count,
        users=user_responses,
    )


@router.get("/getURL/{project_id}", response_model=str)
async def get_project_url(
        project_id: int, session: AsyncSession = Depends(get_async_session)
):
    """
    Получение URL проекта по его ID.
    """
    stmt = select(ProjectsBase.url).where(ProjectsBase.id == project_id)
    result = await session.execute(stmt)
    project_url = result.scalar_one_or_none()
    if not project_url:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return project_url
