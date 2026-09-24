from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.video import Video


class Topic(TimestampMixin, Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)

    video_links: Mapped[list["TopicVideo"]] = relationship(
        back_populates="topic",
        cascade="all, delete-orphan",
        order_by="TopicVideo.rank",
    )


class TopicVideo(Base):
    __tablename__ = "topic_videos"

    topic_id: Mapped[int] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"), primary_key=True
    )
    video_id: Mapped[int] = mapped_column(
        ForeignKey("videos.id", ondelete="CASCADE"), primary_key=True
    )
    rank: Mapped[int] = mapped_column(Integer, index=True)

    topic: Mapped["Topic"] = relationship(back_populates="video_links")
    video: Mapped["Video"] = relationship(back_populates="topic_links")
