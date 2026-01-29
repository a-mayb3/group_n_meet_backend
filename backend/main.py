from fastapi import FastAPI
from routes import events
from routes import me

app = FastAPI()

app.include_router(events.router)
app.include_router(me.router)

## ...

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
