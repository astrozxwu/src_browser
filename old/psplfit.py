import os
import re
import subprocess

import numpy as np

tpl = 's.f'
tpln, ap = tpl.split('.')
PATH = os.path.join(os.getcwd(),'data')


def set_name(name):
    line = '          if(nob.eq.1)filename=\'{}\'\n'.format(name)
    with open(tpl, 'r') as u:
        lines = u.readlines()
        lines[79] = line
    with open(tpl, 'w') as u:
        u.writelines(lines)

def free_u0():
    with open(tpl, 'r') as u:
        lines = u.readlines()
        lines[61] = 'c        kfix(2) = 1\n'
    with open(tpl, 'w') as u:
        u.writelines(lines)
    return tpl 

def set_u0(u0):
    with open(tpl, 'r') as u:
        lines = u.readlines()
        lines[29] = '        a(2)={} \n'.format(u0)

    with open(tpl, 'w') as u:
        u.writelines(lines)

    return tpl

def set_t0(t0):
    with open(tpl, 'r') as u:
        lines = u.readlines()
        lines[30] = '        a(1)={} \n'.format(t0)

    with open(tpl, 'w') as u:
        u.writelines(lines)

    return tpl
def set_tE(tE):
    with open(tpl, 'r') as u:
        lines = u.readlines()
        lines[31] = '        a(3)={} \n'.format(tE)

    with open(tpl, 'w') as u:
        u.writelines(lines)

    return tpl


def setbl(fn, bl):
    x = 0 if bl else 1
    with open(fn, 'r') as u:
        lines = u.readlines()
        lines[71] = '       kfix(8 + 3*i)={} \n'.format(x)
    with open(fn, 'w') as u:
        u.writelines(lines)


def sfit(event_name, u0,t0,tE, bl=False):
    fit = {'u0': u0, 't0': np.nan, 'tE': np.nan, 'fs': np.nan, 'fb': np.nan}
    if event_name not in os.listdir(PATH):
        return 'event folder not found' 
    path = os.path.join(PATH,event_name)#PATH + event_name + '/'
    os.chdir(path)
    l = os.listdir('.')

    if 'KMT' in event_name:
        pattern = 'KMTC[0-9][0-9]_I.pysis'
        files = list(filter(lambda x: re.search(pattern, x) != None, l))
    elif 'Gaia' in event_name:
        pattern = event_name + '_Gaia-G.txt'
        files = list(filter(lambda x: re.search(pattern, x) != None, l))
    else:
        return 'lc file not found'
    f = files[0]
    set_name(f)



    if not t0=='None':
        set_t0(t0)
    else:
        set_t0('9750.0')
    if not tE=='None':
        set_tE(tE)
    else:
        set_tE('50.0')
    if u0=='0':
        free_u0()
        fn = set_u0('0.2')
    else:
        fn = set_u0(u0)
    setbl(fn, bl)

    os.system(f'gfortran {fn}')
    subprocess.Popen(['./a.out'], stdout=subprocess.PIPE, shell=True).communicate()[0].decode('utf-8')
    if not 'fort.35' in os.listdir('.'):
        return 'fit failed , pls check parameter'
    s_u0 = '{:.2f}'.format(float(u0))
    s_bl = 1 if bl else 0
    os.system(f'mv fort.98 u0{s_u0}bl{s_bl}.log')
    para = np.loadtxt('fort.99')
    os.system(f'mv fort.99 u0{s_u0}bl{s_bl}.par')
    os.system(f'mv fort.35 u0{s_u0}bl{s_bl}.model')
    return 'success'


def loadfit(event_name):
    if event_name not in os.listdir(PATH):
        return {}, []
    path = os.path.join(PATH,event_name)#PATH + event_name + '/'
    os.chdir(path)
    l = os.listdir('.')

    par_files = list(filter(lambda x: re.search('.+.par', x) != None, l))
    pars = []
    models = []
    for par in par_files:
        try:
            para = np.loadtxt(par)
            bl = 0 if para[10] == 0 else 1
            fit = {'u0': para[1], 't0': para[0], 'tE': para[2], 'fs': para[3], 'fb': para[4], 'bl': bl,
                   'chi2': para[-1]}
            
            model = par.replace('par','model')
            df = np.loadtxt(model, usecols=(0, 1))
            if df[0][0] < 2450000:
                df = df.T
                df[0] = df[0] + 2450000
                df = df.T
            df = df[df.T[0] > 2459300]
            if np.isnan(df).any():
                continue
            u0bl = model[:-6]



            models.append(
                {'name': f'{u0bl}', 'data': df.tolist(), 'type': 'line', 'color': '#000000'})
            pars.append(fit)
        except:
            pass

    return pars, models
