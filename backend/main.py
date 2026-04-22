import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv()

from database import init_db
from auth import get_current_user
from routers import auth, diary, gallery, anniversary, config, counter

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
Path("./db").mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="TwoSpace API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(diary.router)
app.include_router(gallery.router)
app.include_router(anniversary.router)
app.include_router(config.router)
app.include_router(counter.router)


@app.get("/api/uploads/{filename}")
async def serve_upload(filename: str, _: dict = Depends(get_current_user)):
    path = UPLOAD_DIR / filename
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404)
    return FileResponse(path)
