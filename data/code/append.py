import sys
sys.path.append('../')
from loadcsv import *

appendcsv2db(fname='kmt.csv',dbname='db.sqlite')

import os
from astropy.io import ascii
PATH = '/data/www/vlti/data'
filename = 'kmt.csv'
df = ascii.read(os.path.join(PATH,filename))
for i in range(len(df)):
    name = df[i]['Event']
    print(name)
    if 'Gaia' in name:
        continue
        os.system('python dw_gaia.py --name {}'.format(name))
    elif 'KMT' in name:
        os.system('python dw.py --name {}'.format(name))
