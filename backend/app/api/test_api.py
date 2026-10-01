"""Basic structural validation for the FastAPI backend."""

from fastapi.routing import APIRoute

from app.api.main import app


def main() -> None:
    routes = {
        route.path
        for route in app.routes
        if isinstance(route, APIRoute)
    }

    required = {"/health", "/api/v1/chat", "/api/v1/retrieve"}
    missing = required - routes

    if missing:
        raise RuntimeError(f"Missing API routes: {sorted(missing)}")

    print("FastAPI application loaded successfully.")
    print(f"Routes: {', '.join(sorted(routes))}")
    print("FASTAPI BACKEND STRUCTURE VALIDATION COMPLETED")


if __name__ == "__main__":
    main()
