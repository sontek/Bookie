from __future__ import absolute_import

from celery import Celery
from ConfigParser import ConfigParser
from datetime import timedelta
from os import environ
from os import path


def load_ini():
    selected_ini = environ.get('BOOKIE_INI', 'bookie.ini')
    if selected_ini is None:
        msg = "Please set the BOOKIE_INI env variable!"
        raise Exception(msg)

    cfg = ConfigParser()
    ini_path = path.join(
        path.dirname(
            path.dirname(
                path.dirname(__file__)
            )
        ),
        selected_ini
    )
    cfg.readfp(open(ini_path))

    # Hold onto the ini config.
    return dict(cfg.items('app:bookie', raw=True))


INI = load_ini()


celery = Celery(
    'bookie.celery',
    broker=INI.get('celery_broker'),
    include=['bookie.celery.tasks'])

# Optional configuration, see the application user guide.
celery.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
    CELERY_CONCURRENCY=1,
    CELERY_RESULT_BACKEND=INI.get('celery_broker'),
    CELERYBEAT_SCHEDULE={
        'hourly_stats': {
            'task': 'bookie.celery.tasks.hourly_stats',
            'schedule': timedelta(seconds=60*60),
        },
        'fetch_unfetched': {
            'task': 'bookie.celery.tasks.fetch_unfetched_bmark_content',
            'schedule': timedelta(seconds=60),
        },
    }
)

if __name__ == '__main__':
    celery.start()
