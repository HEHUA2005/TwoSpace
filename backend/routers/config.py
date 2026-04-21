import os
import random
from datetime import date
from fastapi import APIRouter, Depends
from auth import get_current_user, USERS
from schemas import ConfigOut, UserOut

router = APIRouter(prefix="/api/config", tags=["config"])

DEFAULT_QUOTES = [
    "你是我最好的意外。",
    "愿我们的故事，永远都有续集。",
    "遇见你，是我做过最好的事。",
    "和你在一起的每一天，都值得被记住。",
    "我喜欢你，像风喜欢九月。",
    "余生，请多指教。",
]


@router.get("", response_model=ConfigOut)
def get_config(_: dict = Depends(get_current_user)):
    start_str = os.getenv("LOVE_START_DATE", "2024-01-01")
    start = date.fromisoformat(start_str)
    love_days = (date.today() - start).days

    custom_quotes = os.getenv("QUOTES", "")
    quotes = [q.strip() for q in custom_quotes.split("|") if q.strip()] or DEFAULT_QUOTES
    quote = random.choice(quotes)

    couple_photo = os.getenv("COUPLE_PHOTO", "/uploads/couple.jpg")

    return ConfigOut(
        start_date=start,
        couple_photo=couple_photo,
        quote=quote,
        love_days=love_days,
        users=[UserOut(id=u["id"], name=u["name"], avatar=u["avatar"]) for u in USERS.values()],
    )
