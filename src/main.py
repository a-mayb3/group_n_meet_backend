import logging

from contextlib import asynccontextmanager

import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError 
from fastapi.responses import JSONResponse 
from starlette.middleware.sessions import SessionMiddleware

from database import get_db, init_db

from routes import events, me

import config as config

@asynccontextmanager
async def lifespan(app: FastAPI):

    ## Checking if environment variables are set
    if "POSTGRES_USER" not in os.environ:
        raise EnvironmentError("POSTGRES_USER environment variable not set")
    if "POSTGRES_DB" not in os.environ:
        raise EnvironmentError("POSTGRES_DB environment variable not set")
    if "POSTGRES_PASSWORD" not in os.environ:
        raise EnvironmentError("POSTGRES_PASSWORD environment variable not set")
    if "SESSION_SECRET_KEY" not in os.environ:
        raise EnvironmentError("SESSION_SECRET_KEY environment variable not set")

    init_db()

    yield
    pass

app = FastAPI(
    lifespan=lifespan,
    license_info={
        "name": "AGPL-3.0-or-later",
        "url":"https://www.gnu.org/licenses/agpl-3.0.html"},
    title="Group&Meet RestAPI",
    
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
    secret_key=config.SESSION_SECRET_KEY,
)

## Including routes
app.include_router(events.router)
app.include_router(me.router)

@app.head("/health")
async def health():
    return {"status": "ok"}

def main():
    import uvicorn
    uvicorn.run(app,
                host=os.getenv("BIND_ADDRESS", config.BIND_ADDRESS),
                port=int(os.getenv("PORT", config.PORT))
                )

if __name__ == "__main__":
    main()

global_logger = logging.getLogger()
global_logger.setLevel(logging.INFO)

@app.exception_handler(HTTPException) 
async def http_exception_handler(request, exc): 
    """Custom HTTP exception handler""" 
    
    logger = global_logger
    logger.error(f"HTTP error occurred: {exc.detail}")
    
    return JSONResponse( 
        status_code=exc.status_code, 
        content={ 
            "error": { 
                "message": exc.detail, 
                "type": "authentication_error" if exc.status_code == 401 else "authorization_error", 
                "status_code": exc.status_code 
             } 
          }, 
          headers=exc.headers 
      ) 

@app.exception_handler(RequestValidationError) 
async def validation_exception_handler(request, exc): 
    """Handle validation errors"""

    logger = global_logger
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

    logger = global_logger
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
