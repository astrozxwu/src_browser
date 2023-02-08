workers = 2
threads = 2
basedir = "/Volumes/data1/vltiweb"
import os

bind = "127.0.0.1:3000"
pidfile = os.path.join(basedir, "./log/gunicorn.pid")
accesslog = os.path.join(basedir, "./log/gunicorn_access.log")
errorlog = os.path.join(basedir, "./log/gunicorn_error.log")
pythonpath = "/Users/wzx/miniconda3/envs/server/bin/python"
loglevel = "info"
reload = True
data_path = os.path.join(basedir, "./data/")
src_path = os.path.join(basedir, "./")
db_path = os.path.join(basedir, "./data/db.sqlite")
key_tags = ["AT", "UT", "AT_wide", "UT_wide"]
map_tags = {"Ongoing": "Status"}
idle_tags = []
