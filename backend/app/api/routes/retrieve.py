"""Retrieval endpoint."""

from fastapi import APIRouter, Depends, HTTPException

from app.api.auth.dependencies import CurrentUser, get_current_user

from app.api.schemas import (
    RetrievalRequest,
    RetrievalResponse,
    SourceResponse,
)

from app.api.services.rag_service import (
    get_rag_service,
    source_metadata,
)


router = APIRouter(
    prefix="/api/v1",
    tags=["retrieval"],
)


@router.post(
    "/retrieve",
    response_model=RetrievalResponse,
)
def retrieve(
    request: RetrievalRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> RetrievalResponse:

    """Return ranked ABES evidence without invoking the LLM."""

    try:
        results = get_rag_service().retrieve(
            request.query
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Retrieval service is temporarily unavailable.",
        ) from exc

    sources = [
        SourceResponse(
            **source_metadata(result, index)
        )
        for index, result in enumerate(
            results,
            start=1,
        )
    ]

    return RetrievalResponse(
        query=request.query.strip(),
        results=sources,
    )