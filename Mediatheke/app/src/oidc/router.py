"""OIDC Authentication Router."""
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.config import Config as StarletteConfig

from ...core.config import get_settings
from ...core.db.database import get_db
from ..user.model import User, Role
from ..authentication import service as auth_service

router = APIRouter(
    prefix="/auth/oidc",
    tags=["OIDC"],
)

settings = get_settings()

starlette_config = StarletteConfig(environ={
    "OIDC_CLIENT_ID": settings.oidc_client_id,
    "OIDC_CLIENT_SECRET": settings.oidc_client_secret,
    "OIDC_SERVER_METADATA_URL": settings.oidc_server_metadata_url,
})

oauth = OAuth(starlette_config)

oauth.register(
    name="oidc",
    client_kwargs={"scope": "openid email profile"},
    server_metadata_url=settings.oidc_server_metadata_url,
)


@router.get("/login")
async def oidc_login(request: Request):
    """Redirect to the OIDC provider's authorization endpoint."""
    if not settings.oidc_client_id:
        raise HTTPException(status_code=501, detail="OIDC is not configured")

    redirect_uri = settings.oidc_redirect_uri
    return await oauth.oidc.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def oidc_callback(request: Request, db: Session = Depends(get_db)):
    """Handle the OIDC callback, exchange code for tokens, create/find user, return JWT."""
    if not settings.oidc_client_id:
        raise HTTPException(status_code=501, detail="OIDC is not configured")

    try:
        token = await oauth.oidc.authorize_access_token(request)
    except OAuthError as exc:
        raise HTTPException(status_code=401, detail=f"OIDC authentication failed: {exc.error}")

    userinfo = token.get("userinfo")
    if not userinfo:
        raise HTTPException(status_code=401, detail="Failed to get userinfo from OIDC provider")

    email = userinfo.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="OIDC provider did not return an email address")

    # Get or create the user
    user = db.query(User).filter(User.email == email).first()

    if not user:
        username = userinfo.get("preferred_username") or userinfo.get("name") or email.split("@")[0]
        role = db.query(Role).filter(Role.name == "user").first()
        if not role:
            role = Role(name="user")
            db.add(role)
            db.flush()

        user = User(
            email=email,
            username=username,
            hashed_password="",  # OIDC users don't have a password
            role=role,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Generate our JWT
    access_token = auth_service.create_access_token(user)

    # Redirect back to frontend with the token
    frontend_url = f"{settings.url_schema}://{settings.host_url}"
    redirect_url = f"{frontend_url}/?token={access_token}"
    return RedirectResponse(url=redirect_url)
