import asyncpg
from typing import Optional


class Database:

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool: Optional[asyncpg.Pool] = None


    async def connect(self):
        if self.pool is None:
            self.pool = await asyncpg.create_pool(self.dsn)

    async def disconnect(self):
        if self.pool:
            await self.pool.close()
            self.pool = None

    async def fetch(self, query: str, *args):
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)

    async def execute(self, query: str, *args):
        async with self.pool.acquire() as connection:
            return await connection.execute(query, *args)
        
    
db = Database("postgresql://usuario:contraseña@localhost:5432/mibasededatos")