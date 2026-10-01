from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.auth.security import (
    create_access_token,
    verify_password,
)


def authenticate_user(
    db: Session,
    email: str,
    password: str,
):
    """
    Authenticate a user using email and password.
    """

    query = text(
        """
        SELECT
            id,
            email,
            full_name,
            role,
            password_hash,
            is_active
        FROM users
        WHERE email = :email
        LIMIT 1
        """
    )

    user = db.execute(
        query,
        {"email": email},
    ).mappings().first()

    if user is None:
        return None

    if not user["is_active"]:
        return None

    if not verify_password(
        password,
        user["password_hash"],
    ):
        return None

    access_token = create_access_token(
        subject=str(user["id"]),
        role=user["role"],
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "role": user["role"],
        },
    }