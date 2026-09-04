from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import create_pool_with_retry
from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting LoanTrack backend...")
    print("Initializing database connection pool...")

    pool = create_pool_with_retry()

    app.state.db_pool = pool

    print("LoanTrack backend is ready.")

    yield

    print("Closing database connection pool...")
    pool.close()


app = FastAPI(
    title="LoanTrack API",
    version="1.0.0",
)

app.include_router(router)