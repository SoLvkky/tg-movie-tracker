from sqlalchemy import (
    Column,
    Boolean,
    Integer,
    String,
    DateTime,
    ForeignKey,
    BigInteger,
    func,
    text
)
from sqlalchemy.orm import (
    relationship,
)
from sqlalchemy.sql import expression
from sqlalchemy.dialects.postgresql import JSONB
from database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, nullable=False, unique=True, index=True)
    username = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    adult = Column(Boolean, nullable=False, default=expression.false(), server_default=expression.false())
    start_code = Column(Integer, nullable=False, default=0, server_default=text("0"))
    locale = Column(String, nullable=False, default="en-US", server_default="en-US")

    watched_content = relationship("WatchedContent", back_populates="user")

class Content(Base):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True)
    tmdb_id = Column(Integer, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    media_type = Column(Integer)
    year = Column(Integer)
    genres = Column(JSONB)
    poster = Column(String, nullable=True)

class WatchedContent(Base):
    __tablename__ = "watched_content"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    content_id = Column(Integer, ForeignKey("content.id"))
    watched_at = Column(DateTime(timezone=True), default=func.now())

    user = relationship("User", back_populates="watched_content")
    movie = relationship("Content")
