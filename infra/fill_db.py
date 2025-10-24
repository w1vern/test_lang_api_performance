
import asyncio
import random
from uuid import uuid4
from db import session_manager
from sqlalchemy import text
from secrets import token_urlsafe


async def main() -> None:
    await session_manager.create_db_and_tables()
    async with session_manager.context_session() as session:
        for i in range(100):
            for j in range(1000):
                await session.execute(text("INSERT INTO data (id, field1, field2) VALUES (:id, :a, :b)"), {"id": uuid4(), "a": token_urlsafe(8), "b": random.randint(0, 1000)})
            await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
