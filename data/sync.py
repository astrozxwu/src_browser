import os
ulens_dir = '/data/wwwdata/ulens/'
vlti_dir = '/data/www/vlti/data/'

sync_list = ['Gaia22bpl','Gaia22bfy','Gaia22buv','Gaia21fkl','Gaia22dkv','ASASSN-22kb','Gaia22eia','Gaia22duy','Gaia20agb','Gaia22daq']

for i in sync_list:
    os.system('rsync -avzhP {} {}'.format(ulens_dir+i+'/*.txt',vlti_dir+i+'/'))
