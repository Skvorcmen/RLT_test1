from sqlalchemy import Column, Integer, BigInteger, DateTime, ForeignKey, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True)
    creator_id = Column(String, nullable=False, index=True)
    video_created_at = Column(DateTime, nullable=False, index=True)
    views_count = Column(BigInteger, default=0)
    likes_count = Column(BigInteger, default=0)
    comments_count = Column(BigInteger, default=0)
    reports_count = Column(BigInteger, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    snapshots = relationship("VideoSnapshot", back_populates="video", cascade="all, delete-orphan")


class VideoSnapshot(Base):
    __tablename__ = "video_snapshots"

    id = Column(String, primary_key=True)
    video_id = Column(String, ForeignKey("videos.id"), nullable=False, index=True)
    views_count = Column(BigInteger, default=0)
    likes_count = Column(BigInteger, default=0)
    comments_count = Column(BigInteger, default=0)
    reports_count = Column(BigInteger, default=0)
    delta_views_count = Column(BigInteger, default=0)
    delta_likes_count = Column(BigInteger, default=0)
    delta_comments_count = Column(BigInteger, default=0)
    delta_reports_count = Column(BigInteger, default=0)
    created_at = Column(DateTime, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    video = relationship("Video", back_populates="snapshots")

