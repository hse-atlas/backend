from sqlalchemy import ForeignKey, text, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.database import Base, str_uniq, int_pk, str_null_true
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import date
import re

class UsersBase(Base):
    __tablename__ = "users"
    id: Mapped[int_pk]
    login: Mapped[str_uniq]
    email: Mapped[str_uniq]
    password: Mapped[str]

    extend_existing = True

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id})"

class UserRegisterData(BaseModel):
    email: EmailStr = Field(..., description="email")
    password: str = Field(..., min_length=5, max_length=50, description="Password from 5 to 50 lenght")
    login: str = Field(..., min_length=3, max_length=50, description="login")

class UserLoginData(BaseModel):
    email: EmailStr = Field(..., description="email")
    password: str = Field(..., min_length=5, max_length=50, description="Password from 5 to 50 lenght")
