from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import create_access_token, get_current_user, hash_password, verify_password
from ..database import get_db
from ..models import User
from ..schemas import LoginRequest, RegisterRequest, TokenOut, UserOut
from ..seed import SUPERADMIN_USERNAME
from ..templates import create_default_surveys_for_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    email = body.email.lower().strip()
    if email == SUPERADMIN_USERNAME:
        raise HTTPException(status_code=400, detail="This username is reserved")
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=email,
        password_hash=hash_password(body.password),
        name=body.name.strip(),
        is_superadmin=False,
    )
    db.add(user)
    db.flush()
    create_default_surveys_for_user(db, user)
    db.commit()
    db.refresh(user)
    return TokenOut(
        access_token=create_access_token(user.id),
        user=UserOut.model_validate(user),
    )


@router.post("/login", response_model=TokenOut)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    identifier = body.email.strip()
    # Superadmin username is case-insensitive; emails stay lowercased.
    if identifier.lower() == SUPERADMIN_USERNAME:
        lookup = SUPERADMIN_USERNAME
    else:
        lookup = identifier.lower()
    user = db.query(User).filter(User.email == lookup).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return TokenOut(
        access_token=create_access_token(user.id),
        user=UserOut.model_validate(user),
    )


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)
