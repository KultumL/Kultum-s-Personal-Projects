"""
Stock Explainer API (Beginner-friendly)

Key idea:
- Gemini is ONLY called when you request it using `?explain=true`
- Otherwise you always get reliable fallback text.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .endpoints import router

load_dotenv()

app = FastAPI()
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")

@app.get("/")
def serve_index():
    return FileResponse("frontend/index.html")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def home():
    return {"message": "Stock Explainer API is running!"}

