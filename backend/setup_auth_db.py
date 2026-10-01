from pathlib import Path

from sqlalchemy import text

from app.api.db import engine


def main():
    """
    Create the authentication database tables.
    """

    sql_file = Path(__file__).parent / "sql" / "auth_users.sql"

    if not sql_file.exists():
        raise FileNotFoundError(
            f"SQL file not found: {sql_file}"
        )

    sql = sql_file.read_text(encoding="utf-8")

    statements = [
        statement.strip()
        for statement in sql.split(";")
        if statement.strip()
    ]

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))

    print("=" * 50)
    print("AUTH DATABASE SETUP COMPLETED")
    print("=" * 50)


if __name__ == "__main__":
    main()