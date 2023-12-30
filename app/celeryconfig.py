from settings import settings

enable_utc = True
timezone = 'Asia/Almaty'

broker_url = settings.redis.url
result_backend = settings.redis.url

task_serializer = 'json'
result_serializer = 'pickle'
accept_content = ['pickle', 'json']

default_retry_delay = 3

# The visibility timeout defines the number of seconds to wait for the worker to acknowledge the task
# before the message is redelivered to another worker.
# The default visibility timeout for Redis is 3600 seconds.
broker_transport_options = {'visibility_timeout': 60}
visibility_timeout = 60

# After this time (in seconds) the results of the tasks stored in result backend are deleted.
result_expires = 30

# Socket timeout for connections to Redis from the result backend in seconds (int/float)
redis_socket_connect_timeout = 5

# Socket timeout for reading/writing operations to the Redis server in seconds (int/float),
# used by the redis result backend.
redis_socket_timeout = 5

# Socket TCP keepalive to keep connections healthy to the Redis server, used by the redis result backend.
redis_socket_keepalive = True

broker_connection_retry_on_startup = True
task_create_missing_queues = True

result_backend_transport_options = {
    'global_keyprefix': 'tortoise_',
    'retry_policy': {'timeout': 5.0},
    'visibility_timeout': 60,
}

imports = [
    "app.tasks.rvc",
]
