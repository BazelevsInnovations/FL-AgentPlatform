import asyncio
import uuid

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from fl_platform.db.base import Base
from fl_platform.db.models import Project


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest_asyncio.fixture
async def sample_project(db_session: AsyncSession) -> Project:
    project = Project(
        id=uuid.uuid4(),
        name="Test Film",
        script_text="INT. OFFICE - DAY\\n\\nJOHN enters the room.\\n\\nJOHN\\nHello, world.\\n\\nFADE OUT.",
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    return project
