from datetime import datetime

import time


def slugify_time(tt=None):
    if not tt:
        tt = time.time()
    slug_time = datetime.fromtimestamp(tt).strftime('%Y%m%d-%H%M%S')
    return slug_time


def get_datetime_by_string(datetime_str=None):
    if datetime_str:
        datetime_object = datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
        return datetime_object
    return None

