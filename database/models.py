
from sqlalchemy import (
    Column,
    Boolean,
    Integer,
    String,
    DateTime,
    ForeignKey,
    BigInteger,
    func,
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
    adult = Column(Boolean, nullable=False, server_default=expression.false())

    watched_movies = relationship("WatchedMovies", back_populates="user")

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    tmdb_id = Column(Integer, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    rating = Column(String)
    year = Column(Integer)
    genres = Column(JSONB)
    duration = Column(Integer)
    poster = Column(String, nullable=True)

class WatchedMovies(Base):
    __tablename__ = "watched_movies"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    movie_id = Column(Integer, ForeignKey("movies.id"))
    watched_at = Column(DateTime(timezone=True), default=func.now())

    user = relationship("User", back_populates="watched_movies")
    movie = relationship("Movie")
