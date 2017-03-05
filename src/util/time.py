import time
import datetime


def slugify_time(tt=None):
    if not tt:
        tt = time.time()
    slug_time = datetime.datetime.fromtimestamp(tt).strftime('%Y%m%d-%H%M%S')
    return slug_time
