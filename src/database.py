from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os


# For local Dockerfile:
# "postgresql+psycopg://kubsu:kubsu@host.docker.internal:5432/kubsu"

# For local use:
# "postgresql+psycopg://kubsu:kubsu@127.0.0.1:5432/kubsu"

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg://kubsu:kubsu@127.0.0.1:5432/kubsu"
)
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
