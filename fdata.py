import os,re,time
import numpy as np
import config
from astropy.io import ascii
import pandas as pd
from itertools import filterfalse
from datetime import datetime

PATH = config.data_path
def get_color(fn):
    defaults = ['#2f7ed8', '#0d233a', '#8bbc21', '#910000', '#1aadce','#492970', '#f28f43', '#77a1e5', '#c42525', '#a6c96a']
    bands = ['-g','-r','-i','-G','-R','-B','-V','-o','-c','-I']
    for i in bands:
        if i in fn:
            return defaults[bands.index(i)]

def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time, datetime):
        diff = now - time
    elif not time:
        diff = 0
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "1 minute ago"
        if second_diff < 3600:
            return str(second_diff // 60) + " minutes ago"
        if second_diff < 7200:
            return "1 hour ago"
        if second_diff < 86400:
            return str(second_diff // 3600) + " hours ago"
    if day_diff == 1:
        return "1 day ago"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff // 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff // 30) + " months ago"
    return str(day_diff // 365) + " years ago"

def getmdtime(events):
    mdtime = []
    for i in events:
        if i not in os.listdir(PATH):
            mdtime.append('--')
            continue
        tt = datetime.fromtimestamp(os.path.getmtime(os.path.join(PATH,i)))
        mdtime.append(pretty_date(tt))
    return mdtime




def getdata(event_name):
    if event_name not in os.listdir(PATH):
        return []
    series = []
    l = os.listdir(os.path.join(PATH,event_name))
    pattern1 = re.compile(r'{}_.+\.txt'.format(event_name))
    l1 = list(filter(lambda x: pattern1.match(x) is not None, l))
    for f in l1:
        try:
            df = np.genfromtxt(os.path.join(PATH,event_name,f), dtype=None, encoding=None)
            #if 'LZK' in f:
            #    print(np.isnan(df[0]).any())
            # df = list(filterfalse(math.isnan, df))
            info = f.split('_')[1].split('.')[0]
            info = info.replace('-', ' ')
            headers = ['x','y','err','fwhm','code']
            df_pd = pd.DataFrame(df.tolist(),columns=headers[:len(df[0])])
            df_pd = df_pd[df_pd['err'].notna()]
            df_pd = df_pd[df_pd['y'].notna()]
            series.append({'name': info, 'data': df_pd.to_dict(orient='records'),'type': 'scatter','color':get_color(f)})
        except:
            pass

    pattern2 = re.compile(r'KMT[SCA][0-9][0-9]_[I]\.pysis'.format(event_name))
    l2 = list(filter(lambda x: pattern2.match(x) is not None, l))
    for f in l2:
        try:
            df = np.loadtxt(os.path.join(PATH,event_name,f), usecols=(0, 3, 4))
            if df[0][0] < 2450000:
                df = df.T
                df[0] = df[0] + 2450000
                df = df.T
        except:
            continue
        headers = ['x','y','err']
        df_pd = pd.DataFrame(df,columns=headers)
        info = f.split('.')[0]
        # info = info.replace('-', ' ')
        series.append({'name': info, 'data': df_pd.to_dict('records'), 'type': 'scatter'})
    return series
