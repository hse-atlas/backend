import os
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Получение строки подключения из переменной окружения, если она не задана – используется значение по умолчанию.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Rfdrfp08@localhost:5432/Atlas")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Админ может иметь много проектов. При удалении админа связанные проекты удаляются (cascade).
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Admin(id={self.id}, email={self.email})>"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    owner_id = Column(Integer, ForeignKey("admins.id"), nullable=False)
    url = Column(String, nullable=True)

    # Связи: проект принадлежит администратору и может иметь множество пользователей.
    owner = relationship("Admin", back_populates="projects")
    users = relationship("User", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name})>"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Пользователь принадлежит проекту.
    project = relationship("Project", back_populates="users")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"


def init_db():
    """Создает все таблицы в базе данных."""
    Base.metadata.create_all(bind=engine)


if __name__ == '__main__':
    init_db()
