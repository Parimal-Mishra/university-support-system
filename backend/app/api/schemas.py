"""API request and response models for the ABES AI University Support System."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)


class RetrievalRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)


class SourceResponse(BaseModel):
    source_number: int
    rank: int
    score: float
    chunk_id: str
    document_name: str
    document_title: str
    document_type: str
    relative_source: str


class GroundingClaimResponse(BaseModel):
    claim: str
    supported: bool
    source_numbers: list[int]
    reason: str


class GroundingResponse(BaseModel):
    decision: str
    overall_reason: str
    claims: list[GroundingClaimResponse]
    source_count: int


class ChatResponse(BaseModel):
    query: str
    answer: str
    model: str
    grounding: GroundingResponse
    sources: list[SourceResponse]


class RetrievalResponse(BaseModel):
    query: str
    results: list[SourceResponse]


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
