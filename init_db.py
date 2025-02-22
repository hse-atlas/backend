import logging
import os
from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, ForeignKey, func, TIMESTAMP
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Mapped, mapped_column

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получение строки подключения из переменной окружения, если она не задана – используется значение по умолчанию.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:Rfdrfp08@db:5432/Atlas")

# Создание асинхронного движка
engine = create_async_engine(DATABASE_URL)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


class AdminsBase(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(),
                                                 onupdate=func.now())

    # Связь: один админ может иметь много проектов
    projects: Mapped[List["ProjectsBase"]] = relationship("ProjectsBase", back_populates="owner")

    def __repr__(self):
        return f"<AdminsBase(id={self.id}, email={self.email})>"


class ProjectsBase(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("admins.id"), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Добавляем поля created_at и updated_at
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(),
                                                 onupdate=func.now())

    # Связи
    owner: Mapped["AdminsBase"] = relationship("AdminsBase", back_populates="projects")
    users: Mapped[List["UsersBase"]] = relationship("UsersBase", back_populates="project")

    def __repr__(self):
        return f"<ProjectsBase(id={self.id}, name={self.name})>"


class UsersBase(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(),
                                                 onupdate=func.now())

    # Связь: пользователь принадлежит одному проекту
    project: Mapped["ProjectsBase"] = relationship("ProjectsBase", back_populates="users")

    def __repr__(self):
        return f"<UsersBase(id={self.id}, email={self.email})>"


async def init_db():
    """Создает все таблицы в базе данных."""
    try:
        logger.info("Создание таблиц в базе данных...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Таблицы успешно созданы!")
    except Exception as e:
        logger.error(f"Ошибка при создании таблиц: {e}")


if __name__ == '__main__':
    import asyncio

    asyncio.run(init_db())
