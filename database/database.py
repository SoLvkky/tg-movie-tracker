from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from bot.config import settings

engine = create_async_engine(settings.DATABASE_URL)

class Base(DeclarativeBase):
    pass

AsyncSessionLocal = async_sessionmaker(
    engine,
    autoflush=False,
    expire_on_commit=False
)

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session