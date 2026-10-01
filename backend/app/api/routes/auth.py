from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.db import get_db
from app.api.auth.service import authenticate_user
from app.api.auth.dependencies import get_current_user, CurrentUser


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Login using email and password.

    OAuth2PasswordRequestForm uses:
    username = email
    password = password
    """

    result = authenticate_user(
        db=db,
        email=form_data.username,
        password=form_data.password,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return result


@router.get("/me")
def get_me(
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    Return information about the currently authenticated user.
    """

    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
    }


@router.post("/logout")
def logout(
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    JWT logout acknowledgement.

    Because JWT authentication is stateless, the client
    should remove/discard the access token.
    """

    return {
        "message": "Logout successful. Please discard the access token.",
    }