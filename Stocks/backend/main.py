"""
Stock Explainer API (Beginner-friendly)

Key idea:
- Gemini is ONLY called when you request it using `?explain=true`
- Otherwise you always get reliable fallback text.
"""

import os
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .endpoints import router

load_dotenv()

app = FastAPI(title="Stock Explainer API")

origins_env = os.getenv("FRONTEND_ORIGINS", "").strip()
if origins_env:
    allow_origins = [o.strip() for o in origins_env.split(",") if o.strip()]
else:
    allow_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Static frontend 
if os.path.isdir("frontend/assets"):
    app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")

@app.get("/", include_in_schema=False)
def serve_index():
    # Serve the frontend index if it exists; otherwise show API message.
    if os.path.isfile("frontend/index.html"):
        return FileResponse("frontend/index.html")
    return {"message": "Stock Explainer API is running!"}


# Health endpoint
@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}

# API routes
app.include_router(router)
