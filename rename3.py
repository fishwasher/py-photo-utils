import sys
import os
import os.path
import datetime
import re
import exifread

# IN USE via rn2.bat, on PATH
# Rename in place image files with uppercase '.JPG' extension only
# command line arguments:
# - path to image directory, or '-' for current directory (default)
# - optional time adjustment string (e.g. '-1:33'); enter '-' to skip time part in file name
# - optional prefix

IS_TEST = False

LOGFILENAME = 'renamed.txt'
EXIF_DATE_PAT = re.compile(r'\D+')

def _get_time_shift(hour_min_str):
    seconds = 0
    if hour_min_str and ':' in hour_min_str:
        hstr, mstr = hour_min_str.split(':')
        sign = 1
        if hstr[0] == '-':
            sign = -1
            hstr = hstr[1:]
        mins = sign * int(hstr) * 60 + sign * int(mstr)
        seconds = mins * 60
    return seconds


def _read_input():
    input = sys.argv[1:]
    size = len(input)
    dir_path = input[0] if size > 0 and input[0] != '-' else os.getcwd() #os.path.dirname(os.path.abspath(__file__))
    time_shift = 0
    prefix = ''
    use_time = True
    if size > 1 and input[1] != '-':
        if input[1] != '-':
            use_time = False
        else:
            time_shift = _get_time_shift(input[1])
    if size > 2:
        prefix = input[2]
    return dir_path, use_time, time_shift, prefix


def get_file_date(fpath):
    # atime and ctime lack precision on Windows
    ts = os.path.getmtime(fpath)
    return datetime.datetime.fromtimestamp(ts)


def get_exif_date(fpath):
    #key = 'Image DateTime'
    key = 'EXIF DateTimeOriginal'
    try:
        tags = None
        with open(fpath, 'rb') as fp:
            tags = exifread.process_file(fp)
        timestr = str(tags[key]) # format: '2017:07:30 14:57:50'
        tt = tuple([int(x) for x in EXIF_DATE_PAT.split(timestr)])
        return datetime.datetime(*tt)
    except Exception as x:
        print("Could not extract '%s' from %s -- %s" % (key, os.path.basename(fpath), x))



class ImageRenamer(object):

    def __init__(self, dir_path=None, use_time=False, time_shift=0, prefix='', is_test=False):
        self.dirpath = dir_path if dir_path is not None else os.path.dirname(os.path.abspath(__file__))
        self.timeshift = time_shift
        self.use_time = use_time
        self.prefix = prefix
        self.istest = is_test
        self.logpath = self._getpath(LOGFILENAME)
        self.loglist = None


    def _getpath(self, fname):
        return os.path.join(self.dirpath, fname)

    def getpiclist(self):
        is_valid = lambda fname: fname and os.path.splitext(fname)[1] == '.JPG' and os.path.isfile(self._getpath(fname))

        #is_valid = lambda fname: fname and (os.path.splitext(fname)[1] == '.JPG' or
        #    fname.startswith('wp-')) and os.path.isfile(self._getpath(fname))

        return [f for f in os.listdir(self.dirpath) if is_valid(f)]

    '''
    def get_date_strings(self, fpath):
        # try exif date first
        dt = get_exif_date(fpath) # or get_file_date(fpath)
        if self.timeshift:
            dt += datetime.timedelta(seconds=self.timeshift)
        s1 = "%y%m%d-%H%M-" if self.use_time else "%y%m%d-"
        s2 = "%Y-%m-%d %H:%M"
        return dt.strftime(s1), dt.strftime(s2)
'''

    def _newname(self, old_name):
        old_path = self._getpath(old_name)
        dt = get_exif_date(old_path)
        if not dt:
            print('Failed reading EXIF date of %s' % old_name)
            return '', ''
        if self.timeshift:
            dt += datetime.timedelta(seconds=self.timeshift)

        s1 = "%y%m%d-%H%M-" if self.use_time else "%y%m%d-"
        datestr = dt.strftime(s1)

        s2 = "%Y-%m-%d %H:%M"
        timestr = dt.strftime(s2)

        pref = self.prefix + '-' if len(self.prefix) else ''
        name = '%s%s%s' % (pref, datestr, old_name.lower().replace('_', '-'))

        #name = '%s%s' % (datestr, old_name.lower().replace('_', '-').replace('wp-', '')) # remove

        return name, timestr

    def _rename(self, old_name, new_name, timestr):
        old_path = self._getpath(old_name)
        new_path = self._getpath(new_name)
        log = "renaming '%s' to '%s'" % (old_path, new_path)
        if self.istest:
            print(log)
            return
        try:
            os.rename(old_path, new_path)
            log += ": OK"
            self.loglist.append("%s,%s,%s" % (os.path.basename(old_path), os.path.basename(new_path), timestr))
        except IOError:
            log += ": FAIL!"
        print(log)

    def process(self):
        pic_names = self.getpiclist()
        if len(pic_names) == 0:
            print("No valid images found in '%s'" % self.dirpath)
        self.loglist = []
        for fn in pic_names:
            new_name, timestr = self._newname(fn)
            if not new_name:
                print('skipping %s' % fn)
            else:
                self._rename(fn, new_name, timestr)
        #if len(self.loglist):
        #    with open(self.logpath, 'wb') as fp:
        #        fp.write('\n'.join(self.loglist))



print("Testing renaming utility" if IS_TEST else "Renaming started")
d, ut, t, pref = _read_input()
rn = ImageRenamer(d, ut, t, pref, IS_TEST)

rn.process()

print("Done!")

