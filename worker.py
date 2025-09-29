from redis import Redis
from rq import Worker

redis_conn = Redis(host="redis", port=6379)

worker = Worker(queues=["default"], connection=redis_conn)
worker.work()

