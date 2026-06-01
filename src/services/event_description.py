import logging

from fastapi import HTTPException
from google import genai
from google.genai import errors as genai_errors
from sqlalchemy.orm import Session

from config import Settings
from models.events import EventDescriptionGenerateRequest
from schemas.organizer_group import OrganizerGroupSchema

logger = logging.getLogger(__name__)


def _build_gemini_error_detail(exc: genai_errors.APIError) -> dict[str, object]:
    return {
        "provider": "gemini",
        "message": exc.message or "Gemini request failed",
        "status": exc.status,
        "status_code": exc.code,
        "details": exc.details,
    }


def _build_event_description_prompt(
    request: EventDescriptionGenerateRequest,
    organizer_group_name: str | None,
) -> str:
    details = [
        f"Current description: {request.existing_description}",
    ]

    if request.event_name:
        details.append(f"Event name: {request.event_name}")

    if organizer_group_name:
        details.append(f"Organizer group: {organizer_group_name}")

    if request.place:
        details.append(f"Place: {request.place}")

    if request.start_time:
        details.append(f"Start time: {request.start_time}")

    if request.end_time:
        details.append(f"End time: {request.end_time}")

    details_text = "\n".join(details)

    return (
        "Rewrite the event description below so it sounds polished, natural, "
        "and engaging, while preserving the original meaning and any concrete details. "
        "Return only the new description text without quotes, bullets, or extra commentary.\n\n"
        f"{details_text}"
    )


def generate_event_description(
    request: EventDescriptionGenerateRequest,
    db: Session,
) -> str:
    settings = Settings()
    api_key = settings.GEMINI_API_KEY
    gemini_model = settings.GEMINI_MODEL
    
    if api_key is None or not api_key.get_secret_value().strip():
        raise HTTPException(
            status_code=503,
            detail="Gemini API key is not configured",
        )

    ## This *should* be unreachable due to validation in Settings
    if gemini_model is None or not gemini_model.strip():
        raise HTTPException(
            status_code=503,
            detail="Gemini model is not configured",
        )

    client = genai.Client(api_key=api_key.get_secret_value())

    organizer_group_name = None
    if request.organizer_group_id is not None:
        organizer_group = (
            db.query(OrganizerGroupSchema)
            .filter(OrganizerGroupSchema.id == request.organizer_group_id)
            .first()
        )
        if organizer_group is not None:
            if organizer_group.name is not None:
                organizer_group_name = str(organizer_group.name)

    prompt = _build_event_description_prompt(request, organizer_group_name)

    try:
        response = client.models.generate_content(
            model=gemini_model,
            contents=(
                "You are a helpful assistant that rewrites event descriptions "
                "into concise, polished copy.\n\n"
                f"{prompt}"
            ),
        )
    except genai_errors.APIError as exc:
        logger.exception("Gemini request failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=_build_gemini_error_detail(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Gemini request failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="Failed to generate event description",
        ) from exc

    try:
        suggested_description = (response.text or "").strip()
    except (AttributeError, TypeError) as exc:
        logger.exception("Unexpected Gemini response payload: %s", response)
        raise HTTPException(
            status_code=502,
            detail="Gemini returned an unexpected response",
        ) from exc

    if not suggested_description:
        raise HTTPException(
            status_code=502,
            detail="Gemini returned an empty description",
        )

    return suggested_description