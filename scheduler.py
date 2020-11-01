from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fuck import work
import aioredis
import asyncio
import sys
import os

async def get_with_userid(redis, key):
    result = await redis.get(key)
    return key[len('fuck-'):], result


async def fuck_job():
    connection = await aioredis.create_redis_pool('redis://fuck-checkin-redis:6379', encoding='utf-8')
    redis = aioredis.Redis(pool_or_conn=connection)
    cookies = [get_with_userid(redis, key) for key in (await redis.keys('fuck-*'))]

    result = [(await work(userid, cookie)) for (userid, cookie) in (await asyncio.gather(*cookies))]


#    failed = filter(lambda x: not x[1], result)
#    delete_tasks = await asyncio.gather(*[redis.delete(f"fuck-{fail[0]}") for fail in failed])
    result = list(filter(lambda x: x[1], result))

    redis.close()
    await redis.wait_closed()

    print(result)
    sys.stdout.flush()

    with open('/data/scheduler.log.txt', 'a') as f:
        for i in result:
            f.write(str(i))
            f.write('\n')

if __name__ == "__main__":
    INTERVAL = int(os.environ.get('SCHEDULER_INTERVAL', 15))
    
    scheduler = AsyncIOScheduler()
    scheduler.add_job(func=fuck_job, trigger='interval', seconds=INTERVAL)
    scheduler.start()
    print("Scheduler Starting...")
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
