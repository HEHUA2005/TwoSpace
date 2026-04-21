import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()

from database import init_db
from routers import auth, diary, gallery, anniversary, config, counter

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))

# 在模块加载时就创建目录，StaticFiles 挂载前必须存在
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

# 静态文件（上传的图片）
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
