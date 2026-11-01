from fastapi import FastAPI

from api.routes import router

app = FastAPI()
app.include_router(router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
