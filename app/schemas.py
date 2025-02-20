from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, int_pk


# ======================== ORM модели ========================

class AdminsBase(Base):
    __tablename__ = "admins"

    id: Mapped[int_pk] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)

    # Связь: один админ может иметь много проектов
    projects: Mapped[List["ProjectsBase"]] = relationship("ProjectsBase", back_populates="owner")

    def __repr__(self):
        return f"<AdminsBase(id={self.id}, email={self.email})>"


class ProjectsBase(Base):
    __tablename__ = "projects"

    id: Mapped[int_pk] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("admins.id"), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Связи
    owner: Mapped["AdminsBase"] = relationship("AdminsBase", back_populates="projects")
    users: Mapped[List["UsersBase"]] = relationship("UsersBase", back_populates="project")

    def __repr__(self):
        return f"<ProjectsBase(id={self.id}, name={self.name})>"


class UsersBase(Base):
    __tablename__ = "users"

    id: Mapped[int_pk] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)

    # Связь: пользователь принадлежит одному проекту
    project: Mapped["ProjectsBase"] = relationship("ProjectsBase", back_populates="users")

    def __repr__(self):
        return f"<UsersBase(id={self.id}, email={self.email})>"


# ======================== Pydantic-схемы ========================

class RegisterData(BaseModel):
    email: EmailStr = Field(..., description="Email адрес")
    password: str = Field(
        ...,
        min_length=5,
        max_length=50,
        description="Пароль от 5 до 50 символов"
    )
    login: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Логин (от 3 до 50 символов)"
    )


class LoginData(BaseModel):
    email: EmailStr = Field(..., description="Email адрес")
    password: str = Field(
        ...,
        min_length=5,
        max_length=50,
        description="Пароль от 5 до 50 символов"
    )


# ----------------------------------------------------------------------------
# Pydantic-модели (проект)
# ----------------------------------------------------------------------------
class ProjectBase(BaseModel):
    name: str
    description: str
    owner_id: int
    url: Optional[str] = None
    user_count: int


class ProjectCreate(BaseModel):
    name: str
    description: str
    owner_id: int
    url: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None


class ProjectOut(BaseModel):
    id: int
    name: str
    description: str
    owner_id: int
    url: Optional[str] = None
    user_count: Optional[int] = None


class UserResponse(BaseModel):
    id: int
    login: str
    email: str


class ProjectDetailResponse(BaseModel):
    id: int
    name: str
    description: str
    owner_id: int
    url: Optional[str] = None
    user_count: int
    users: List[UserResponse]

    class Config:
        from_attributes = True


# ----------------------------------------------------------------------------
# Pydantic-модели (пользователь)
# ----------------------------------------------------------------------------
class UserBase(BaseModel):
    login: str
    email: str
    password: str
    project_id: int


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    login: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True


class UsersProjectOut(BaseModel):
    project_id: int
    project_name: str
    project_description: str
    users: List[UserOut]
