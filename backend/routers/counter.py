from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from auth import get_current_user
from database import get_db
from models import Counter
from schemas import CounterCreate, CounterOut

router = APIRouter(prefix="/api/counters", tags=["counter"])


@router.get("", response_model=list[CounterOut])
async def list_counters(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    result = await db.execute(select(Counter).order_by(Counter.created_at))
    return result.scalars().all()


@router.post("", response_model=CounterOut, status_code=status.HTTP_201_CREATED)
async def create_counter(
    body: CounterCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    counter = Counter(title=body.title, emoji=body.emoji)
    db.add(counter)
    await db.commit()
    await db.refresh(counter)
    return counter


@router.post("/{counter_id}/increment", response_model=CounterOut)
async def increment_counter(
    counter_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    counter = await db.get(Counter, counter_id)
    if not counter:
        raise HTTPException(status_code=404, detail="统计卡片不存在")
    counter.count += 1
    await db.commit()
    await db.refresh(counter)
    return counter


@router.delete("/{counter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_counter(
    counter_id: int,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    counter = await db.get(Counter, counter_id)
    if not counter:
        raise HTTPException(status_code=404, detail="统计卡片不存在")
    await db.delete(counter)
    await db.commit()
