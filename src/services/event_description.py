import logging

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from config import Settings
from models.events import EventDescriptionGenerateRequest
from schemas.organizer_group import OrganizerGroupSchema

logger = logging.getLogger(__name__)


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
    token = settings.OPENAI_API_TOKEN

    if token is None or not token.get_secret_value().strip():
        raise HTTPException(
            status_code=503,
            detail="OpenAI API token is not configured",
        )

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
        response = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {token.get_secret_value()}",
                "Content-Type": "application/json",
            },
            json={
                "model": "gpt-4o-mini",
                "temperature": 0.7,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant that rewrites event descriptions "
                            "into concise, polished copy."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=30.0,
        )
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        logger.exception("OpenAI request failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="Failed to generate event description",
        ) from exc
    except httpx.RequestError as exc:
        logger.exception("OpenAI request could not be completed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="Failed to reach the OpenAI service",
        ) from exc

    payload = response.json()

    try:
        suggested_description = (
            payload["choices"][0]["message"]["content"].strip()
        )
    except (KeyError, IndexError, AttributeError, TypeError) as exc:
        logger.exception("Unexpected OpenAI response payload: %s", payload)
        raise HTTPException(
            status_code=502,
            detail="OpenAI returned an unexpected response",
        ) from exc

    if not suggested_description:
        raise HTTPException(
            status_code=502,
            detail="OpenAI returned an empty description",
        )

    return suggested_description