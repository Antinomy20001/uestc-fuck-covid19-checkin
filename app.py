from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fuck import work, get_userid
import aioredis
import uuid

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OriginIndexCookie(BaseModel):
    cookie: str


async def to_redis(origin_index_cookie):
    try:
        userid = await get_userid(origin_index_cookie)
    except Exception:
        return False

    connection = await aioredis.create_redis_pool('redis://fuck-checkin-redis:6379', encoding='utf-8')
    redis = aioredis.Redis(pool_or_conn=connection)
    result = await redis.set(f'fuck-{userid}', origin_index_cookie)
    redis.close()
    await redis.wait_closed()
    return result


@app.post("/origin_index_cookie/")
async def main(origin_index_cookie: OriginIndexCookie):
    print(f"get cookies: {origin_index_cookie.cookie}")
    result = await to_redis(origin_index_cookie.cookie)
    print(result)
    return origin_index_cookie

# listen 3000
