import os
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload
from auth import get_current_user
from database import get_db
from models import Diary, DiaryImage
from schemas import DiaryCreate, DiaryUpdate, DiaryOut, DiaryListOut, DiaryImageOut

router = APIRouter(prefix="/api/diaries", tags=["diary"])

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB

# 从 auth 模块引入用户名映射
from auth import USERS


def _user_name(author_id: int) -> str:
    u = USERS.get(author_id)
    return u["name"] if u else "未知"


def _image_url(filename: str) -> str:
    return f"/uploads/{filename}"


async def _get_diary_with_images(db: AsyncSession, diary_id: int):
    result = await db.execute(
        select(Diary).where(Diary.id == diary_id).options(selectinload(Diary.images))
    )
    return result.scalar_one_or_none()


def _diary_to_out(diary: Diary) -> DiaryOut:
    return DiaryOut(
        id=diary.id,
        title=diary.title,
        content=diary.content,
        mood=diary.mood,
        author_id=diary.author_id,
        author_name=_user_name(diary.author_id),
        created_at=diary.created_at,
        updated_at=diary.updated_at,
        images=[
            DiaryImageOut(id=img.id, filename=img.filename, url=_image_url(img.filename), created_at=img.created_at)
            for img in diary.images
        ],
    )


@router.get("", response_model=DiaryListOut)
async def list_diaries(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    offset = (page - 1) * limit
    total_result = await db.execute(select(func.count()).select_from(Diary))
    total = total_result.scalar_one()

    sort_col = Diary.created_at.asc() if order == "asc" else Diary.created_at.desc()
    result = await db.execute(
        select(Diary).order_by(sort_col).offset(offset).limit(limit).options(selectinload(Diary.images))
    )
    diaries = result.scalars().unique().all()

    return DiaryListOut(
        items=[_diary_to_out(d) for d in diaries],
        total=total,
        page=page,
        limit=limit,
    )


@router.post("", response_model=DiaryOut, status_code=status.HTTP_201_CREATED)
async def create_diary(
    body: DiaryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    diary = Diary(title=body.title, content=body.content, mood=body.mood, author_id=current_user["id"])
    if body.created_at is not None:
        diary.created_at = body.created_at
    db.add(diary)
    await db.commit()
    diary = await _get_diary_with_images(db, diary.id)
    return _diary_to_out(diary)


@router.get("/{diary_id}", response_model=DiaryOut)
async def get_diary(
    diary_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    diary = await _get_diary_with_images(db, diary_id)
    if not diary:
        raise HTTPException(status_code=404, detail="日记不存在")
    return _diary_to_out(diary)


@router.put("/{diary_id}", response_model=DiaryOut)
async def update_diary(
    diary_id: int,
    body: DiaryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    diary = await db.get(Diary, diary_id)
    if not diary:
        raise HTTPException(status_code=404, detail="日记不存在")
    if diary.author_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="无权编辑他人日记")
    if body.title is not None:
        diary.title = body.title
    if body.content is not None:
        diary.content = body.content
    if body.mood is not None:
        diary.mood = body.mood
    if body.created_at is not None:
        diary.created_at = body.created_at
    await db.commit()
    diary = await _get_diary_with_images(db, diary_id)
    return _diary_to_out(diary)


@router.delete("/{diary_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_diary(
    diary_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    diary = await _get_diary_with_images(db, diary_id)
    if not diary:
        raise HTTPException(status_code=404, detail="日记不存在")
    if diary.author_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="无权删除他人日记")
    for img in diary.images:
        _delete_file(img.filename)
    await db.delete(diary)
    await db.commit()


@router.post("/{diary_id}/images", response_model=DiaryImageOut, status_code=status.HTTP_201_CREATED)
async def upload_image(
    diary_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    diary = await db.get(Diary, diary_id)
    if not diary:
        raise HTTPException(status_code=404, detail="日记不存在")
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="仅支持 JPEG/PNG/GIF/WebP")

    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="图片不能超过 10MB")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    (UPLOAD_DIR / filename).write_bytes(content)

    img = DiaryImage(diary_id=diary_id, filename=filename)
    db.add(img)
    await db.commit()
    await db.refresh(img)
    return DiaryImageOut(id=img.id, filename=img.filename, url=_image_url(img.filename), created_at=img.created_at)


@router.delete("/{diary_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    diary_id: int,
    image_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    diary = await db.get(Diary, diary_id)
    if not diary:
        raise HTTPException(status_code=404, detail="日记不存在")
    if diary.author_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="无权操作")
    img = await db.get(DiaryImage, image_id)
    if not img or img.diary_id != diary_id:
        raise HTTPException(status_code=404, detail="图片不存在")
    _delete_file(img.filename)
    await db.delete(img)
    await db.commit()


def _delete_file(filename: str):
    path = UPLOAD_DIR / filename
    try:
        path.unlink(missing_ok=True)
    except Exception:
        pass
