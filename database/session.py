from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from bot.config import settings

DATABASE_URL = settings.DATABASE_URL
engine = create_async_engine(DATABASE_URL)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession)

async def get_db_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session