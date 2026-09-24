from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.analysis import Analysis
    from app.models.topic import TopicVideo


class Channel(TimestampMixin, Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True)
    youtube_channel_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    logo_url: Mapped[str | None] = mapped_column(String(512))
    subscriber_count: Mapped[int | None] = mapped_column(BigInteger)

    videos: Mapped[list["Video"]] = relationship(back_populates="channel")


class Video(TimestampMixin, Base):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(primary_key=True)
    youtube_video_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    channel_id: Mapped[int] = mapped_column(
        ForeignKey("channels.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(500))
    thumbnail_url: Mapped[str] = mapped_column(String(512))
    duration_seconds: Mapped[int] = mapped_column(Integer)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    channel: Mapped["Channel"] = relationship(back_populates="videos")
    transcript: Mapped[Optional["Transcript"]] = relationship(
        back_populates="video", cascade="all, delete-orphan"
    )
    analysis: Mapped[Optional["Analysis"]] = relationship(
        back_populates="video", cascade="all, delete-orphan"
    )
    topic_links: Mapped[list["TopicVideo"]] = relationship(
        back_populates="video", cascade="all, delete-orphan"
    )


class Transcript(TimestampMixin, Base):
    __tablename__ = "transcripts"

    id: Mapped[int] = mapped_column(primary_key=True)
    video_id: Mapped[int] = mapped_column(
        ForeignKey("videos.id", ondelete="CASCADE"), unique=True
    )
    language: Mapped[str] = mapped_column(String(10))
    segments: Mapped[list[dict]] = mapped_column(JSONB)

    video: Mapped["Video"] = relationship(back_populates="transcript")
