from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import init_schema
from .todo_list import router as todo_list_router


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    init_schema()
    yield


app = FastAPI(title="POC SDD API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(todo_list_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
