web: gunicorn config.wsgi:application
worker: celery --without-gossip --without-mingle --without-heartbeat worker -A odin -l info
