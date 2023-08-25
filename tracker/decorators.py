import datetime

from config.settings import REDIS


def increment_request_count(view_func):
    def wrapped_view(request, *args, **kwargs):
        user_id = request.user.id
        date = datetime.date.today()
        cache_key = f'request_count_{user_id}_{date}'
        request_count = REDIS.get(cache_key)
        if request_count is None:
            REDIS.set(cache_key, 1)
        else:
            REDIS.incr(cache_key)
        return view_func(request, *args, **kwargs)

    return wrapped_view
