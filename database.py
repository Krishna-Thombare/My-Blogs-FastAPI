from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from config import settings

engine = create_async_engine(settings.database_url)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# A blueprint that knows how to create mapped classes. Keeps track of all our models.
class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:   # Async generator
        yield session