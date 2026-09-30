from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.database import get_db


app = FastAPI(
    title="AI-Powered University Support System",
    description="RAG-based university student support system",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "University Support System API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/database-test")
def database_test(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT 1"))
    value = result.scalar()

    return {
        "database": "connected",
        "test_result": value
    }