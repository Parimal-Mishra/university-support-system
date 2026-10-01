"""FastAPI application for the ABES AI University Support System."""
from __future__ import annotations

from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.chat import router as chat_router
from app.api.routes.health import router as health_router
from app.api.routes.retrieve import router as retrieve_router

load_dotenv()

app = FastAPI(
    title="ABES AI University Support System",
    description="Grounded RAG backend for ABES student support.",
    version="1.0.0",
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(retrieve_router)
app.include_router(auth_router)
