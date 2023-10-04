"""Schemas for Authentication"""
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Pydantic Class for Token"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Pydantic Class for Token Data"""
    email: EmailStr | None = None