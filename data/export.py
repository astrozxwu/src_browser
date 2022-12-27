import sys
sys.path.append('../')
from db2csv import *

db2csv(fname='out.csv',dbname='db.sqlite')
