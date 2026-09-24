from typing import TYPE_CHECKING
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.video import Video


class Analysis(TimestampMixin, Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    video_id: Mapped[int] = mapped_column(
        ForeignKey("videos.id", ondelete="CASCADE"), unique=True
    )

    # Signal Score and its parts
    signal_score: Mapped[float] = mapped_column(Float, index=True)
    filler_ratio: Mapped[float] = mapped_column(Float)
    first_point_seconds: Mapped[int] = mapped_column(Integer)
    promo_seconds: Mapped[int] = mapped_column(Integer)
    concept_density: Mapped[float] = mapped_column(Float)
    repetition_ratio: Mapped[float] = mapped_column(Float)

    # Format of video
    video_format: Mapped[str | None] = mapped_column(String(40))
    tone: Mapped[str | None] = mapped_column(String(40))
    level: Mapped[str | None] = mapped_column(String(40))
    pace: Mapped[str | None] = mapped_column(String(40))

    overview: Mapped[str | None] = mapped_column(Text)
    skip_if: Mapped[str | None] = mapped_column(Text)
    model_name: Mapped[str | None] = mapped_column(String(80))

    video: Mapped["Video"] = relationship(back_populates="analysis")
    key_points: Mapped[list["KeyPoint"]] = relationship(
        back_populates="analysis",
        cascade="all, delete-orphan",
        order_by="KeyPoint.position",
    )


class KeyPoint(Base):
    __tablename__ = "key_points"

    id: Mapped[int] = mapped_column(primary_key=True)
    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"), index=True
    )
    position: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    start_seconds: Mapped[int] = mapped_column(Integer)
    source_excerpt: Mapped[str] = mapped_column(Text)

    analysis: Mapped["Analysis"] = relationship(back_populates="key_points")
