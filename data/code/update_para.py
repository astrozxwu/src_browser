from astropy.io import ascii
import sys
sys.path.append('../')
from loadcsv import *

df = ascii.read('listpage.dat')
update(picker_key='Event',picker_list=df['Event'],key='t_E',value_list=df['t_E'],dbname='db.sqlite')
update(picker_key='Event',picker_list=df['Event'],key='t_0',value_list=df['t_0'],dbname='db.sqlite')
#update(picker_key='Event',picker_list=df['Event'],key='u_0',value_list=df['u_0'],dbname='db.sqlite')
