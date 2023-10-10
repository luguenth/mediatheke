"""Auth Router."""
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..user import schema

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from ..user import crud
from ...core.db.database import get_db
from ..user.model import User
from ..authentication import service as auth
from ..authentication import schema as auth_schemas

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

limiter = Limiter(
    key_func=get_remote_address
)

@router.post("/login", response_model=auth_schemas.Token)
@limiter.limit("5/minute", error_message="Please don't spam login attempts, if you forgot your password, please contact us.")
def login(
        request: Request,
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)):
    """Login a user."""
    user: User = crud.get_user_by_email(db, form_data.username)    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password")
    if not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password")

    # Generate a JWT token and return it
    access_token = auth.create_access_token(user)

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=auth_schemas.Token)
@limiter.limit("5/minute", error_message="If you're having trouble registering, please contact us. Don't spam register attempts.")
def register(
        request: Request,
        response: Response,
        user: schema.UserCreate,
        db: Session = Depends(get_db)):
    """Register a new user."""
    user_db = crud.get_user_by_email(db, user.email)
    if user_db:
        raise HTTPException(
            status_code=400,
            detail="Email already registered")
    user = crud.create_user(db, user)
    access_token = auth.create_access_token(user)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(response: Response):
    """Logout a user."""
    response.delete_cookie(key="access_token")
    return {"message": "Logged out"}


# test route only for logged in users
@router.get("/test")
def test(
    current_user: User = Depends(auth.get_current_user)):
    """Test route for logged in users."""
    return {"message": f"Hello {current_user.username}"}

