"""Student chat endpoint."""

from fastapi import APIRouter, Depends, HTTPException

from app.api.auth.dependencies import CurrentUser, get_current_user

from app.api.schemas import (
    ChatRequest,
    ChatResponse,
    GroundingClaimResponse,
    GroundingResponse,
    SourceResponse,
)

from app.api.services.rag_service import (
    context_source_metadata,
    get_rag_service,
)


router = APIRouter(
    prefix="/api/v1",
    tags=["chat"],
)


def _fallback_answer(decision: str) -> str:
    if decision == "NOT_GROUNDED":
        return (
            "I could not verify the generated answer against the available "
            "ABES information, so I cannot provide it as a reliable answer."
        )

    return (
        "I could not reliably verify an answer from the available ABES "
        "information. Please consult the relevant official ABES source or "
        "contact the appropriate college office."
    )


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> ChatResponse:

    try:
        generated, grounding, context = get_rag_service().answer(
            request.query
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail="RAG service is temporarily unavailable.",
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="An unexpected backend error occurred.",
        ) from exc

    answer = (
        generated.answer
        if grounding.decision == "GROUNDED"
        else _fallback_answer(grounding.decision)
    )

    sources = [
        SourceResponse(**source)
        for source in context_source_metadata(context)
    ]

    grounding_response = GroundingResponse(
        decision=grounding.decision,
        overall_reason=grounding.overall_reason,
        claims=[
            GroundingClaimResponse(
                claim=claim.claim,
                supported=claim.supported,
                source_numbers=claim.source_numbers,
                reason=claim.reason,
            )
            for claim in grounding.claims
        ],
        source_count=grounding.source_count,
    )

    return ChatResponse(
        query=generated.query,
        answer=answer,
        model=generated.model,
        grounding=grounding_response,
        sources=sources,
    )