from huey import RedisHuey, crontab
from app import check_price, find_price

huey = RedisHuey()


@huey.periodic_task(crontab(minute='*/1'))
def check_for_price_change():
    check_price()
