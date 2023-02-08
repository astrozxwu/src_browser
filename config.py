workers = 2
threads = 2
bind = "127.0.0.1:3000"
pidfile = "gunicorn.pid"
accesslog = "gunicorn_access.log"
errorlog = "gunicorn_error.log"
pythonpath = "/home/ulens/anaconda3/env/vlti"
loglevel = "info"
reload = True
data_path = "/data/www/vlti/data"
src_path = "/data/www/vlti"
db_path = "/data/www/vlti/data/db.sqlite"
key_tags = ["AT", "UT", "AT_wide", "UT_wide"]
map_tags = {"Ongoing":"Status"}
idle_tags = []
