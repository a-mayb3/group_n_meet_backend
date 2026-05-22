#!/usr/bin/env python3

import logging
import os

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError 
from fastapi.responses import JSONResponse 
from starlette.middleware.sessions import SessionMiddleware

from database import get_db, init_db
from routes import auth, events, me, organizer_groups, user

from config import Settings

settings = Settings()

logger = logging.getLogger()
logger.setLevel(logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.debug(settings.model_dump())

    init_db()

    yield
    pass

app = FastAPI(
    lifespan=lifespan,
    license_info={
        "name": "AGPL-3.0-or-later",
        "url":"https://www.gnu.org/licenses/agpl-3.0.html"},
    title="Group&Meet RestAPI",
    root_path=settings.ROOT_PATH or ""
    )

## Adding middlewares
app.add_middleware( 
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY.get_secret_value(),
)

## Including routes
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(user.router)
app.include_router(me.router)
app.include_router(organizer_groups.router)

@app.head("/health")
async def health():
    return {"status": "ok"}

@app.exception_handler(HTTPException) 
async def http_exception_handler(request, exc): 
    """Custom HTTP exception handler""" 
    
    logger.error(f"HTTP error occurred: {exc.detail}")

    if isinstance(exc.detail, dict):
        message = exc.detail.get("message", "An error occurred")
        error_type = exc.detail.get("provider", "http_error")
        details = exc.detail
    else:
        message = exc.detail
        error_type = "authentication_error" if exc.status_code == 401 else "authorization_error"
        details = None
    
    return JSONResponse( 
        status_code=exc.status_code, 
        content={ 
            "error": { 
                "message": message, 
                "type": error_type, 
                "status_code": exc.status_code,
                **({"details": details} if details is not None else {}),
            } 
        }, 
        headers=exc.headers 
    ) 
    
@app.exception_handler(RequestValidationError) 
async def validation_exception_handler(request, exc): 
    """Handle validation errors"""

    logger.error(f"Validation error: {exc.errors()}")

    return JSONResponse( 
        status_code=422, 
        content={ 
            "error": { 
                "message": "Validation error", 
                "type": "validation_error", 
                "details": exc.errors() 
            } 
        } 
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle all other exceptions"""

    logger.error(f"Unexpected error: {exc}")

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "An unexpected error occurred.",
                "type": "internal_server_error",
                "details": str(exc)
            }
        }
    )

def main():
    """
    Entrypoint for pyproject.toml
    
    Starts the backed through uvicorn.
    Uses environment variables for host and port, with fallback to config.py values.
    """

    import uvicorn
    uvicorn.run(
        app,
        host=settings.BIND_ADDRESS,
        port=settings.PORT
    )

## In case this is run directly.
if __name__ == "__main__":
    main()  