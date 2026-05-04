from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from pydantic import EmailStr

from app.api import deps
from app.core import security
from app.core.database import get_db
from app.core.mail import send_verification_email
from app.models.user import User
from app.schemas import user as user_schema
from app.schemas.msg import Msg

router = APIRouter()
 
@router.get("/", response_model=List[user_schema.User])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.post("/register", response_model=user_schema.User)
async def register_user(
    *,
    db: Session = Depends(get_db),
    password: str = Body(...),
    email: EmailStr = Body(...),
    full_name: str = Body(None),
) -> Any:
    """
    Create new user.
    """
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user_in = user_schema.UserCreate(email=email, password=password, full_name=full_name)
    db_obj = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_active=True,  # Account is active but not verified
        is_verified=False,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    
    try:
        verification_token = security.create_email_verification_token(email)
        await send_verification_email(email=email, token=verification_token)
    except Exception:
        # We don't delete the user anymore because the link is logged to the terminal
        pass
    
    return db_obj

@router.get("/verify-email/{token}", response_model=Msg)
def verify_email(token: str, db: Session = Depends(get_db)) -> Any:
    """
    Verify email.
    """
    email = security.verify_email_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_verified = True
    db.add(user)
    db.commit()
    return {"msg": "Email verified successfully"}

@router.get("/me", response_model=user_schema.User)
def read_user_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.put("/me", response_model=user_schema.User)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update own user.
    """
    if email:
        current_user.email = email
    if full_name:
        current_user.full_name = full_name
    if password:
        current_user.hashed_password = security.get_password_hash(password)
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
