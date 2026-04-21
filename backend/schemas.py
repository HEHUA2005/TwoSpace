from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel


# ── Auth ──────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    user_id: int
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    avatar: str

class TokenOut(BaseModel):
    access_token: str
    user: UserOut


# ── Diary ─────────────────────────────────────────────────────────────────────

class DiaryImageOut(BaseModel):
    id: int
    filename: str
    url: str
    created_at: datetime

    class Config:
        from_attributes = True

class DiaryCreate(BaseModel):
    title: str
    content: str = ""
    mood: str = "love"
    created_at: Optional[datetime] = None  # 不传则默认当前时间

class DiaryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    mood: Optional[str] = None
    created_at: Optional[datetime] = None

class DiaryOut(BaseModel):
    id: int
    title: str
    content: str
    mood: str
    author_id: int
    author_name: str
    created_at: datetime
    updated_at: datetime
    images: list[DiaryImageOut] = []

    class Config:
        from_attributes = True

class DiaryListOut(BaseModel):
    items: list[DiaryOut]
    total: int
    page: int
    limit: int


# ── Gallery ───────────────────────────────────────────────────────────────────

class GalleryImageOut(BaseModel):
    id: int
    filename: str
    url: str
    diary_id: int
    diary_title: str
    created_at: datetime


# ── Anniversary ───────────────────────────────────────────────────────────────

class AnniversaryCreate(BaseModel):
    title: str
    date: date
    is_yearly: bool = True

class AnniversaryOut(BaseModel):
    id: int
    title: str
    date: date
    is_yearly: bool
    days_passed: int       # 距今已过天数（从原始日期算起）
    next_date: date        # 下一个纪念日日期
    days_until_next: int   # 距下一个纪念日天数

    class Config:
        from_attributes = True


# ── Config ────────────────────────────────────────────────────────────────────

class ConfigOut(BaseModel):
    start_date: date
    couple_photo: str
    quote: str
    love_days: int
    users: list[UserOut]


# ── Counter ───────────────────────────────────────────────────────────────────

class CounterCreate(BaseModel):
    title: str
    emoji: str = "✨"

class CounterOut(BaseModel):
    id: int
    title: str
    emoji: str
    count: int
    created_at: datetime

    class Config:
        from_attributes = True
