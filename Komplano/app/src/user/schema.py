"""Schemas for User"""
from pydantic import BaseModel, EmailStr, Field
from typing import Annotated


class UserBase(BaseModel):
    """Pydantic Base Class for User"""
    email: EmailStr


class UserCreate(UserBase):
    """Pydantic Class for User Creation"""
    username: str
    email: EmailStr
    password: str = Field(min_length=8)


class User(UserBase):
    """Pydantic Class for User"""
    id: int
    username: str

    class Config:
        """Pydantic Config Class for User"""
        from_attributes: bool = True
