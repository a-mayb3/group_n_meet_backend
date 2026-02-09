from contextlib import asynccontextmanager
from os import environ

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from database import get_db, init_db

from routes import events, me

@asynccontextmanager
async def lifespan(app: FastAPI):

    ## Checking if environment variables are set
    if "POSTGRES_USER" not in environ:
        raise EnvironmentError("POSTGRES_USER environment variable not set")
    if "POSTGRES_DB" not in environ:
        raise EnvironmentError("POSTGRES_DB environment variable not set")
    if "POSTGRES_PASSWORD" not in environ:
        raise EnvironmentError("POSTGRES_PASSWORD environment variable not set")
    if "SESSION_SECRET_KEY" not in environ:
        raise EnvironmentError("SESSION_SECRET_KEY environment variable not set")

    init_db()

    yield
    pass

app = FastAPI(
    lifespan=lifespan,
    ## TODO: Add exception handlers
    ## TODO: Add logging middleware
    
    license_info={"name": "AGPL-3.0-or-later", "url":"https://www.gnu.org/licenses/agpl-3.0.html"},
    
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
    secret_key=environ.get("SESSION_SECRET_KEY", "default_secret_key")
)

## Including routes
app.include_router(events.router)
app.include_router(me.router)

@app.head("/health")
async def health():
    return {"status": "ok"}

## In case this file is run directly...
def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
