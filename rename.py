import os
import glob
import datetime

# Rename images in place!!! Use copies only

# adjust time difference before proceeding
TIMESHIFT = {
    'hr': 0,
    'min': 0
}

#LOGFILE = "renamer_log.txt"


def format_time(ts):
    h = TIMESHIFT['hr']
    m = TIMESHIFT['min']
    s = (h * 60 * 60) + (m * 60)
    ts = ts + s
    d = datetime.datetime.fromtimestamp(ts)
    return d.strftime("%y%m%d-%H%M-")



def do_the_job():
    #logfile = open(LOGFILE, 'w')

    for fn in glob.iglob('*.JPG'):
        log = "'%s' -> "%fn
        try:
            st = os.stat(fn)
            pref = format_time(st.st_mtime)

            fn2 = '%s%s' % (pref, fn.lower().replace('_', '-'))
            os.rename(fn, fn2)
            log += "'%s' OK"%fn2

        except IOError:
            log += "FAILED!"
        print log

do_the_job()