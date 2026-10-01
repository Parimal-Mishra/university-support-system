from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.auth.security import decode_access_token, oauth2_scheme
from app.api.db import get_db


@dataclass
class CurrentUser:
    id: int
    email: str
    role: str
    full_name: str | None = None


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> CurrentUser:
    payload = decode_access_token(token)
    user_id = int(payload["sub"])

    row = db.execute(
        text("""
            SELECT id, email, role, full_name, is_active
            FROM users
            WHERE id = :id
            LIMIT 1
        """),
        {"id": user_id},
    ).mappings().first()

    if not row or not row["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive or does not exist.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return CurrentUser(
        id=row["id"],
        email=row["email"],
        role=row["role"],
        full_name=row["full_name"],
    )


def require_roles(*allowed_roles: str):
    def dependency(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this resource.",
            )
        return current_user

    return dependency
