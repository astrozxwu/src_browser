import os,argparse
from astropy.io import ascii
from astropy.stats import mad_std
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--name', '-n', help='source name')
args = parser.parse_args()
n = args.name
os.system('mkdir {}'.format(n))
os.chdir('{}'.format(n))

os.system('wget "http://gsaweb.ast.cam.ac.uk/alerts/alert/{}/lightcurve.csv" -q -O Gaia.csv'.format(n))
with open('Gaia.csv','r') as f:
    lines = f.readlines()
    lines = lines[1:]
with open('Gaia.csv','w') as f:
    lines[0] = 'Date,JD,averagemag\n'
    f.writelines(lines)
Gaia = ascii.read('Gaia.csv', format='csv',encoding="utf-8")
Gaia = Gaia[Gaia['averagemag'] != 'null']
Gaia = Gaia[Gaia['averagemag'] != 'untrusted']
tGaia = Gaia['JD']
magGaia = np.array(Gaia['averagemag'], dtype='f4')
std = max(mad_std(magGaia[tGaia <= 2459000]),0.01)  #  df_bright[df_bright['Name'] == n]['HistoricStdDev']
if np.isnan(std):
        std = 0.01
x2 = np.array([tGaia, magGaia,
                   np.ones(len(Gaia['JD'])) * std]).transpose()
np.savetxt('{}_Gaia-G.txt'.format(n), x2,fmt='%.5f', delimiter='  ')
os.remove('Gaia.csv')
