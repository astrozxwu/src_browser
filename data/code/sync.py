import os
ulens_dir = '/data/wwwdata/ulens/'
vlti_dir = '/data/www/vlti/data/'

sync_list = ['Gaia22bpl','Gaia22bfy','Gaia22buv']

for i in sync_list:
    os.system('rsync -avzhP {} {}'.format(ulens_dir+i+'/*.txt',vlti_dir+i+'/'))
