
import asyncio
from db import session_manager
from sqlalchemy import text


async def main() -> None:
    async with session_manager.context_session() as session:
        sql = text("""
        SELECT lang_code, AVG(time) AS avg_time
        FROM time
        GROUP BY lang_code
    """)
    result = await session.execute(sql)
    rows = result.mappings().all()
    print(rows)


if __name__ == "__main__":
    asyncio.run(main())