from __future__ import absolute_import, unicode_literals

from datetime import datetime

from django.db.models import F

from config.settings import REDIS, REQUEST_COST
from celery.utils.log import get_task_logger
from celery import shared_task

from tracker.models import RequestLog

logger = get_task_logger(__name__)


@shared_task(name="update_costs")
def update_costs():
    cache_key_prefix = 'request_count_'
    cache_keys = REDIS.keys(f'{cache_key_prefix}*')
    for cache_key in cache_keys:
        request_count_num = REDIS.getdel(cache_key).decode()
        if request_count_num != 0:
            cache_key = cache_key.decode()
            user_id, date = cache_key.split("_")[2], cache_key.split("_")[3],
            aware_date = datetime.strptime(date, "%Y-%m-%d")
            result = RequestLog.objects.filter(
                user_id=user_id,
                date=aware_date
            ).update(
                cost=(F('count') + request_count_num) * REQUEST_COST,
                count=F('count') + request_count_num
            )
            if result == 0:
                RequestLog.objects.create(
                    user_id=user_id,
                    date=aware_date,
                    cost=float(request_count_num) * REQUEST_COST,
                    count=float(request_count_num)
                )
