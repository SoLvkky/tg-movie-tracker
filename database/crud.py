from bot.logger import logger
from database.models import User, Movie, WatchedMovies
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, JSON, func, text

async def get_or_create_user(session: AsyncSession, telegram_id: int, username: str | None = None):
    logger.debug(f"get_or_create_user(telegram_id={telegram_id}, username={username}) called")

    res = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = res.scalar_one_or_none()

    if user:
        logger.info(f"User {telegram_id} is already in database")
        return user

    user = User(telegram_id=telegram_id, username=username)
    session.add(user)
    await session.commit()
    await session.refresh(user)

    logger.info(f"User {telegram_id} was added to database")
    return user

async def get_or_create_movie(session: AsyncSession, tmdb_id: int, title: str, rating: str, genres: JSON, year: int, duration: int, poster: str):
    logger.debug(f"get_or_create_movie(tmdb_id={tmdb_id}, title={title}, rating={rating}, genres={genres}, year={year}, duration={duration}, poster={poster}) called")
    res = await session.execute(
        select(Movie).where(Movie.tmdb_id == tmdb_id)
    )
    movie = res.scalar_one_or_none()
    
    if movie:
        logger.info(f"Movie {tmdb_id} : {title} is already in database")
        return movie
    
    movie = Movie(tmdb_id=tmdb_id, title=title, rating=rating, genres=genres, year=year, duration=duration, poster=poster)
    session.add(movie)
    await session.commit()
    await session.refresh(movie)

    logger.info(f"Movie {tmdb_id} : {title} was added to database")
    return movie

async def add_movie_watched(session: AsyncSession, user_id: int, movie_id: int):
    logger.debug(f"add_movie_watched(user_id={user_id}, movie_id={movie_id}) called")
    existing = await session.scalar(
        select(WatchedMovies)
        .where(WatchedMovies.user_id == user_id)
        .where(WatchedMovies.movie_id == movie_id)
    )
    
    if existing:
        logger.info(f"User {user_id} already watched movie {movie_id}")
        return False

    watched = WatchedMovies(user_id=user_id, movie_id=movie_id)
    session.add(watched)
    await session.commit()
    await session.refresh(watched)

    logger.info(f"User {user_id} added watched movie {movie_id}")
    return True

async def remove_movie_watched(session: AsyncSession, user_id: int, movie_id: int) -> bool:
    logger.debug(f"remove_movie_watched(user_id={user_id}, movie_id={movie_id}) called")
    res = await session.execute(
        delete(WatchedMovies)
        .where(WatchedMovies.user_id == user_id)
        .where(WatchedMovies.movie_id == movie_id)
        .returning(WatchedMovies.id)
    )

    deleted = res.scalar()

    if deleted:
        await session.commit()

        logger.info(f"User {user_id} removed watched movie {movie_id}")
        return True
    else:
        logger.info(f"User {user_id} didn't watch movie {movie_id}")
        return False

async def get_watched_movies(session: AsyncSession, user_id: int):
    logger.debug(f"get_watched_movies(user_id={user_id}) called")
    res = await session.execute(
        select(Movie.tmdb_id, Movie.title, Movie.year)
        .join(WatchedMovies, WatchedMovies.movie_id == Movie.id)
        .where(WatchedMovies.user_id == user_id)
        .order_by(WatchedMovies.watched_at.desc())
    )
    rows = res.all()

    return [
        {
            "tmdb_id": tmdb_id,
            "title": title,
            "year": year
        }
        for tmdb_id, title, year in rows
    ]


async def has_watched(session: AsyncSession, user_id: int, movie_id: int) -> bool:
    logger.debug(f"has_watched(user_id={user_id}, movie_id={movie_id}) called")
    res = await session.scalar(
        select(WatchedMovies.id)
        .where(WatchedMovies.user_id == user_id, WatchedMovies.movie_id == movie_id)
    )

    return res is not None

async def get_user_movie_count(session: AsyncSession, user_id: int) -> int:
    logger.debug(f"get_user_movie_count(user_id={user_id}) called")
    res = await session.scalar(
        select(func.count(WatchedMovies.id)).where(WatchedMovies.user_id == user_id)
    )

    return res or 0

async def get_top_genres(session: AsyncSession, user_id: int):
    logger.debug(f"get_top_genres(user_id={user_id}) called")
    genre_table = func.jsonb_array_elements_text(Movie.genres).table_valued("value").lateral()

    res = await session.execute(
        select(
            genre_table.c.value.label("genre"),
            func.count(WatchedMovies.id).label("count")
        )
        .select_from(Movie)
        .join(WatchedMovies, WatchedMovies.movie_id == Movie.id)
        .join(genre_table, text("true"))
        .where(WatchedMovies.user_id == user_id)
        .group_by(genre_table.c.value)
        .order_by(func.count(WatchedMovies.id).desc())
    )
    return res.all()