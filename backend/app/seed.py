"""Bootstrap the fixed superadmin account."""

from __future__ import annotations

from sqlalchemy.orm import Session

from .auth import hash_password, verify_password
from .database import SessionLocal
from .models import User

SUPERADMIN_USERNAME = "netizen"
SUPERADMIN_PASSWORD = "password"
SUPERADMIN_NAME = "Super Admin"


def ensure_superadmin() -> None:
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.email == SUPERADMIN_USERNAME).first()
        if user is None:
            user = User(
                email=SUPERADMIN_USERNAME,
                password_hash=hash_password(SUPERADMIN_PASSWORD),
                name=SUPERADMIN_NAME,
                is_superadmin=True,
            )
            db.add(user)
            db.commit()
            return

        changed = False
        if not user.is_superadmin:
            user.is_superadmin = True
            changed = True
        if not verify_password(SUPERADMIN_PASSWORD, user.password_hash):
            user.password_hash = hash_password(SUPERADMIN_PASSWORD)
            changed = True
        if user.name != SUPERADMIN_NAME:
            user.name = SUPERADMIN_NAME
            changed = True
        if changed:
            db.commit()
    finally:
        db.close()
