from datetime import datetime, date
from sqlalchemy import Integer, String, Text, DateTime, Date, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class Diary(Base):
    __tablename__ = "diaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    mood: Mapped[str] = mapped_column(String(20), nullable=False, default="love")
    author_id: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    images: Mapped[list["DiaryImage"]] = relationship("DiaryImage", back_populates="diary", cascade="all, delete-orphan")


class DiaryImage(Base):
    __tablename__ = "diary_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    diary_id: Mapped[int] = mapped_column(Integer, ForeignKey("diaries.id", ondelete="CASCADE"), nullable=False)
    filename: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    diary: Mapped["Diary"] = relationship("Diary", back_populates="images")


class Anniversary(Base):
    __tablename__ = "anniversaries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    is_yearly: Mapped[bool] = mapped_column(Boolean, default=True)
