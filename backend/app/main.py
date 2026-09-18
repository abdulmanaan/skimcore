from fastapi import FastAPI

app = FastAPI(
    title="Skimcore",
    description="Find the video worth watching, and skip the rest.",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}
