import os

import redis
from rq import Connection, Queue, Worker

listen = ["default"]

redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
conn = redis.from_url(redis_url)

if __name__ == "__main__":
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
