from bot.logger import logger
from database.models import User, Content, WatchedContent
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, JSON, func, text

# User CRUD
async def get_or_create_user(session: AsyncSession, telegram_id: int, username: str, code: int | None = None):
    logger.debug(f"get_or_create_user(telegram_id={telegram_id}, username={username}, start_code={code}) called")

    res = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = res.scalar_one_or_none()

    if user:
        logger.info(f"User {telegram_id} is already in database")
        return

    user = User(telegram_id=telegram_id, username=username, start_code=code)
    session.add(user)
    await session.commit()
    await session.refresh(user)

    logger.info(f"User {telegram_id} was added to database")
    return user

async def toggle_adult(session: AsyncSession, telegram_id: int) -> bool:
    logger.debug(f"toggle_adult(telegram_id={telegram_id}) called")

    res = await session.execute(select(User).where(User.telegram_id == telegram_id))
    user = res.scalar_one_or_none()

    if user is None:
        raise ValueError(f"User {telegram_id} not found")

    user.adult = not bool(user.adult)
    await session.commit()
    await session.refresh(user)
    return user.adult

async def get_adult(session: AsyncSession, telegram_id: int) -> bool:
    logger.debug(f"get_adult(telegram_id={telegram_id}) called")

    res = await session.execute(
        select(User.adult).where(User.telegram_id == telegram_id)
    )
    adult = res.scalar_one_or_none()

    if adult is None:
        raise ValueError(f"User {telegram_id} not found")

    return bool(adult)

async def get_user_movie_count(session: AsyncSession, user_id: int) -> int:
    logger.debug(f"get_user_movie_count(user_id={user_id}) called")

    movies = await session.scalar(
        select(func.count(WatchedContent.id))
        .join(Content, WatchedContent.content_id == Content.id)
        .where(
            WatchedContent.user_id == user_id,
            Content.media_type == 1
        )
    )

    series = await session.scalar(
        select(func.count(WatchedContent.id))
        .join(Content, WatchedContent.content_id == Content.id)
        .where(
            WatchedContent.user_id == user_id,
            Content.media_type == 2
        )
    )
    return {"movies": movies, "series": series} or {"movies": 0, "series": 0}

async def get_top_genres(session: AsyncSession, user_id: int):
    logger.debug(f"get_top_genres(user_id={user_id}) called")
    
    genre_table = func.jsonb_array_elements_text(Content.genres).table_valued("value").lateral()

    res = await session.execute(
        select(
            genre_table.c.value.label("genre"),
            func.count(WatchedContent.id).label("count")
        )
        .select_from(Content)
        .join(WatchedContent, WatchedContent.content_id == Content.id)
        .join(genre_table, text("true"))
        .where(WatchedContent.user_id == user_id)
        .group_by(genre_table.c.value)
        .order_by(func.count(WatchedContent.id).desc())
    )
    return res.all()

async def set_locale(session: AsyncSession, user_id: int, locale: str):
    logger.debug(f"set_locale(user_id={user_id}, locale={locale}) called")

    res = await session.execute(select(User).where(User.telegram_id == user_id))
    user = res.scalar_one_or_none()

    if user is None:
        raise ValueError(f"User {user_id} not found")
    
    user.locale = locale
    await session.commit()
    await session.refresh(user)
    return user.locale

async def get_locale(session: AsyncSession, user_id: int):
    logger.debug(f"get_locale(user_id={user_id}) called")

    res = await session.execute(
        select(User.locale).where(User.telegram_id == user_id)
    )
    locale = res.scalar_one_or_none()

    if locale is None:
        raise ValueError(f"User {user_id} not found")
    
    return locale

# Show CRUD
async def get_or_create_show(session: AsyncSession, tmdb_id: int, title: str, genres: JSON, year: int, poster: str, media_type: int):
    logger.debug(f"get_or_create_show(tmdb_id={tmdb_id}, title={title}, genres={genres}, year={year}, poster={poster}, media_type={media_type}) called")

    res = await session.execute(
        select(Content).where(Content.tmdb_id == tmdb_id)
    )
    content = res.scalar_one_or_none()
    
    if content:
        logger.info(f"Content {tmdb_id} : {title} is already in database")
        return content
    
    content = Content(tmdb_id=tmdb_id, title=title, genres=genres, year=year, poster=poster, media_type=media_type)
    session.add(content)
    await session.commit()
    await session.refresh(content)

    logger.info(f"Content {tmdb_id} : {title} was added to database")
    return content

async def get_media_type(session: AsyncSession, tmdb_id: int) -> str | None:
    logger.debug(f"get_media_type(tmdb_id={tmdb_id}) called")

    result = await session.scalar(
        select(Content.media_type)
        .where(Content.tmdb_id == tmdb_id)
        .limit(1)
    )
    return result

# Watched CRUD
async def add_watched(session: AsyncSession, user_id: int, content_id: int):
    logger.debug(f"add_watched(user_id={user_id}, content_id={content_id}) called")

    existing = await session.scalar(
        select(WatchedContent)
        .where(WatchedContent.user_id == user_id)
        .where(WatchedContent.content_id == content_id)
    )
    
    if existing:
        logger.info(f"User {user_id} already watched {content_id}")
        return False

    watched = WatchedContent(user_id=user_id, content_id=content_id)

    session.add(watched)
    await session.commit()
    await session.refresh(watched)

    logger.info(f"User {user_id} added watched {content_id}")
    return True

async def remove_watched(session: AsyncSession, user_id: int, content_id: int) -> bool:
    logger.debug(f"remove_watched(user_id={user_id}, content_id={content_id}) called")

    res = await session.execute(
        delete(WatchedContent)
        .where(WatchedContent.user_id == user_id)
        .where(WatchedContent.content_id == content_id)
        .returning(WatchedContent.id)
    )

    deleted = res.scalar()

    if deleted:
        await session.commit()

        logger.info(f"User {user_id} removed watched {content_id}")
        return True
    else:
        logger.info(f"User {user_id} didn't watch {content_id}")
        return False

async def get_watched(session: AsyncSession, user_id: int):
    logger.debug(f"get_watched(user_id={user_id}) called")

    res = await session.execute(
        select(Content.tmdb_id, Content.title, Content.year)
        .join(WatchedContent, WatchedContent.content_id == Content.id)
        .where(WatchedContent.user_id == user_id)
        .order_by(WatchedContent.watched_at.desc())
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

async def has_watched(session: AsyncSession, user_id: int, content_id: int) -> bool:
    logger.debug(f"has_watched(user_id={user_id}, content_id={content_id}) called")

    res = await session.scalar(
        select(WatchedContent.id)
        .where(WatchedContent.user_id == user_id, WatchedContent.content_id == content_id)
    )

    return res is not None