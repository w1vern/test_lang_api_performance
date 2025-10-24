
from fastapi import Depends, FastAPI
from sqlalchemy import text
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession
from db import session_manager
import time

from pydantic import BaseModel


class Data(BaseModel):
    field1: str
    field2: int


app = FastAPI(docs_url="/api/docs",
              redoc_url="/api/redoc",
              openapi_url="/api/openapi.json",
              swagger_ui_parameters={
                  "tryItOutEnabled": True,
              })


@app.get("/api/test1")
async def default(session: AsyncSession = Depends(session_manager.session)) -> list[Data]:
    start = time.time()
    sql = text("""
        SELECT field1, field2 
        FROM data
        WHERE field2 > 995
    """)
    result = await session.execute(sql)
    return [Data(field1=row.field1, field2=row.field2) for row in result]

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        #reload=True,
        workers=10,
        log_level="critical"
    )
