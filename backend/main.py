from contextlib import asynccontextmanager
from os import environ

from fastapi import FastAPI
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

    yield


app = FastAPI(
    lifespan=lifespan
    ## TODO: Add exception handlers
    ## TODO: Add CORS middleware
    ## TODO: Add logging middleware
    )

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
