from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt

from app.core import security
from app.core.config import settings
from app.core.database import get_db
from app.core.mail import send_reset_password_email
from app.models.user import User
from app.schemas.token import Token, TokenPayload
from app.schemas.msg import Msg

router = APIRouter()

@router.post("/login/access-token", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    elif not user.is_verified:
        raise HTTPException(status_code=400, detail="Email not verified")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.email, expires_delta=access_token_expires
        ),
        "refresh_token": security.create_refresh_token(user.email),
        "token_type": "bearer",
    }

@router.post("/login/refresh-token", response_model=Token)
def refresh_token(
    refresh_token: str = Body(...), db: Session = Depends(get_db)
) -> Any:
    """
    Refresh access token using a refresh token
    """
    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        if token_data.type != "refresh":
            raise HTTPException(status_code=400, detail="Invalid refresh token")
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Invalid refresh token")
    
    user = db.query(User).filter(User.email == token_data.sub).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=400, detail="User not found or inactive")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.email, expires_delta=access_token_expires
        ),
        "refresh_token": security.create_refresh_token(user.email),
        "token_type": "bearer",
    }

@router.post("/password-recovery/{email}", response_model=Msg)
async def recover_password(email: str, db: Session = Depends(get_db)) -> Any:
    """
    Password recovery
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = security.create_password_reset_token(email)
    await send_reset_password_email(email=user.email, token=password_reset_token)
    return {"msg": "Password recovery email sent"}

@router.post("/reset-password/", response_model=Msg)
def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    db: Session = Depends(get_db),
) -> Any:
    """
    Reset password
    """
    email = security.verify_password_reset_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    hashed_password = security.get_password_hash(new_password)
    user.hashed_password = hashed_password
    db.add(user)
    db.commit()
    return {"msg": "Password updated successfully"}
