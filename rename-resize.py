import os
import glob
from PIL import Image
import shutil
import datetime

MAXSIZE = 2000, 1600
LOGFILE = "resizer_log.txt"

def mkfname(oldname, prefix=None):
    s = oldname.lower()
    if s.startswith('img_'):
        if prefix is None: prefix = 'img-'
        s = s[4:]
    elif s.startswith('p'):
        if prefix is None: prefix = 'pic-'
        s = s[1:]
    return prefix + s
    

def do_the_job():
    logfile = open(LOGFILE, 'w')
    
    for fn in glob.iglob('*.JPG'):
        log = "'%s' -> "%fn
        try:
            st = os.stat(fn)
            d = datetime.date.fromtimestamp(st.st_mtime)
            pref = d.strftime("%y%m%d") + '-'
            im = Image.open(fn)
            im.thumbnail(MAXSIZE, Image.ANTIALIAS)
            fn2 = mkfname(fn, pref)
            im.save(fn2, "JPEG")
            shutil.copystat(fn, fn2)
            log += "'%s' OK"%fn2
            
        except IOError:
            log += "FAILED!"
            
        logfile.write(log+'\n')
        print(log)
    
do_the_job()