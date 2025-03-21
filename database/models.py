from sqlalchemy import String, Integer, DateTime, BigInteger, Boolean, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine


engine = create_async_engine(url='sqlite+aiosqlite:///database/db.sqlite3')

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String, default='user')
    active: Mapped[str] = mapped_column(String, default='false')


class Combination(Base):
    __tablename__ = 'combinations'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    combination: Mapped[str] = mapped_column(String)
    photo_id: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


