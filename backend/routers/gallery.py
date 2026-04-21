from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from auth import get_current_user
from database import get_db
from models import DiaryImage, Diary
from schemas import GalleryImageOut

router = APIRouter(prefix="/api/gallery", tags=["gallery"])


@router.get("", response_model=list[GalleryImageOut])
async def list_gallery(
    page: int = Query(1, ge=1),
    limit: int = Query(30, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    offset = (page - 1) * limit
    result = await db.execute(
        select(DiaryImage, Diary.title)
        .join(Diary, DiaryImage.diary_id == Diary.id)
        .order_by(DiaryImage.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    rows = result.all()
    return [
        GalleryImageOut(
            id=img.id,
            filename=img.filename,
            url=f"/uploads/{img.filename}",
            diary_id=img.diary_id,
            diary_title=title,
            created_at=img.created_at,
        )
        for img, title in rows
    ]
