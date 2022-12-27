import os
import argparse
import re
parser = argparse.ArgumentParser()
parser.add_argument('--name', '-n', help='source name')
args = parser.parse_args()
name = args.name
n = name.split('-')[-1]
y = '22'
if os.path.exists(name):
    os.chdir(name)
    os.system('wget https://kmtnet.kasi.re.kr/~ulens/event/20{}/data/KB{}/pysis/pysis.tar.gz'.format(y,y+n))
    os.system('tar -xvf pysis.tar.gz')
    os.system('rm pysis.tar.gz')
else:
    os.system('mkdir '+name)
    os.chdir(name)
    os.system('wget https://kmtnet.kasi.re.kr/~ulens/event/20{}/data/KB{}/pysis/pysis.tar.gz'.format(y,y+n))
    os.system('tar -xvf pysis.tar.gz')
    os.system('rm pysis.tar.gz')
#    os.system('rm *.diapl')
#    l = os.listdir('.')
#    files = list(filter(lambda x: re.search('KMTC[0-9][0-9]_I.pysis', x) != None, l))
#    for f in files:
#        os.system('wget https://kmtnet.kasi.re.kr/~ulens/event/2022/data/KB{}/diapl/{}'.format(y+n,f.split('.')[0]+'.diapl'))
