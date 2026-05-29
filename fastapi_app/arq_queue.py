from arq import create_pool
from arq.connections import RedisSettings
import os

arq_pool = None

async def get_arq_pool():
    global arq_pool
    if arq_pool is None:
        arq_pool = await create_pool(
            RedisSettings.from_dsn(
                os.getenv("REDIS_URL", "redis://redis:6379")
            )
        )
        return arq_pool

async def close_arq_pool() -> None:
    # Closes TCP connection cleanly so the process doesn't hang on exit.
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None