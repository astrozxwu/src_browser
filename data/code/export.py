import sys
sys.path.append('../')
from loadcsv import *

db2csv(fname='out.csv',dbname='db.sqlite')
