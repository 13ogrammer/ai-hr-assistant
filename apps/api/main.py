import pathlib

from fastapi import FastAPI
from fastapi.responses import FileResponse

from api.routes import router

STATIC_DIR = pathlib.Path(__file__).resolve().parent / "static"

app = FastAPI()
app.include_router(router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/")
def ui():
    return FileResponse(STATIC_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
