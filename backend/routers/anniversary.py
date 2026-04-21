from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from auth import get_current_user
from database import get_db
from models import Anniversary
from schemas import AnniversaryCreate, AnniversaryOut

router = APIRouter(prefix="/api/anniversaries", tags=["anniversary"])


def _calc(ann: Anniversary) -> AnniversaryOut:
    today = date.today()
    origin = ann.date
    days_passed = (today - origin).days

    if ann.is_yearly:
        # 今年的纪念日
        try:
            this_year = origin.replace(year=today.year)
        except ValueError:
            # 2月29日闰年处理
            this_year = origin.replace(year=today.year, day=28)
        if this_year < today:
            try:
                next_d = origin.replace(year=today.year + 1)
            except ValueError:
                next_d = origin.replace(year=today.year + 1, day=28)
        else:
            next_d = this_year
    else:
        next_d = origin  # 一次性纪念日，下一个就是本身

    days_until = max(0, (next_d - today).days)
    return AnniversaryOut(
        id=ann.id,
        title=ann.title,
        date=ann.date,
        is_yearly=ann.is_yearly,
        days_passed=days_passed,
        next_date=next_d,
        days_until_next=days_until,
    )


@router.get("", response_model=list[AnniversaryOut])
async def list_anniversaries(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    result = await db.execute(select(Anniversary).order_by(Anniversary.date))
    anns = result.scalars().all()
    return [_calc(a) for a in anns]


@router.post("", response_model=AnniversaryOut, status_code=status.HTTP_201_CREATED)
async def create_anniversary(
    body: AnniversaryCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    ann = Anniversary(title=body.title, date=body.date, is_yearly=body.is_yearly)
    db.add(ann)
    await db.commit()
    await db.refresh(ann)
    return _calc(ann)


@router.delete("/{ann_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_anniversary(
    ann_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    ann = await db.get(Anniversary, ann_id)
    if not ann:
        raise HTTPException(status_code=404, detail="纪念日不存在")
    await db.delete(ann)
    await db.commit()
