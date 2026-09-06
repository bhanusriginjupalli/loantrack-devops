import os
import time
from contextlib import contextmanager

from psycopg_pool import ConnectionPool


def get_database_url() -> str:
    host = os.getenv("DATABASE_HOST", "localhost")
    port = os.getenv("DATABASE_PORT", "5432")
    database = os.getenv("POSTGRES_DB", "loantrack")
    user = os.getenv("POSTGRES_USER", "loantrack_user")
    password = os.getenv("POSTGRES_PASSWORD", "change_me")

    return (
        f"postgresql://{user}:{password}"
        f"@{host}:{port}/{database}"
    )


def create_pool_with_retry(
    max_retries: int = 10,
    initial_delay: float = 1.0,
) -> ConnectionPool:
    database_url = get_database_url()
    delay = initial_delay

    for attempt in range(1, max_retries + 1):
        try:
            pool = ConnectionPool(
                conninfo=database_url,
                min_size=1,
                max_size=10,
                open=True,
            )

            with pool.connection() as connection:
                connection.execute("SELECT 1")

            print(
                f"Database connection established on attempt {attempt}."
            )
            return pool

        except Exception as exc:
            print(
                f"Database connection attempt {attempt}/{max_retries} "
                f"failed: {exc}"
            )

            if attempt == max_retries:
                raise

            print(f"Retrying in {delay:.1f} seconds...")
            time.sleep(delay)
            delay = min(delay * 2, 10.0)

    raise RuntimeError("Unable to establish database connection")


@contextmanager
def get_connection(pool: ConnectionPool):
    with pool.connection() as connection:
        yield connection