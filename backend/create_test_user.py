from sqlalchemy import text
from app.api.db import engine
from app.api.auth.security import hash_password


def main():
    password = "Test@12345"

    query = text("""
        INSERT INTO users
        (email, password_hash, full_name, role, is_active)
        VALUES
        (:email, :password_hash, :full_name, :role, TRUE)
    """)

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "email": "student@abes.ac.in",
                "password_hash": hash_password(password),
                "full_name": "Test Student",
                "role": "STUDENT",
            },
        )

    print("TEST USER CREATED")
    print("Email    : student@abes.ac.in")
    print("Password : Test@12345")


if __name__ == "__main__":
    main()