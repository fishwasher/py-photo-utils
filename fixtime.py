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


IS_TEST = False

LOGFILENAME = 'renamed.txt'
EXIF_DATE_PAT = re.compile(r'\D+')
NAME_SUB_PAR = re.compile(r'^(?:\d+-)+')


def _read_input():
    input = sys.argv[1:]
    size = len(input)
    dir_path = input[0] if size > 0 and input[0] != '-' else os.getcwd() #os.path.dirname(os.path.abspath(__file__))
    time_shift = 0
    use_time = True
    return dir_path, use_time, time_shift


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

    def __init__(self, dir_path=None, use_time=False, time_shift=0, is_test=False):
        self.dirpath = dir_path if dir_path is not None else os.path.dirname(os.path.abspath(__file__))
        self.timeshift = time_shift
        self.use_time = use_time
        #self.prefix = prefix
        self.istest = is_test
        self.logpath = self._getpath(LOGFILENAME)
        self.loglist = None


    def _getpath(self, fname):
        return os.path.join(self.dirpath, fname)

    def getpiclist(self):
        is_valid = lambda fname: fname and os.path.splitext(fname)[1].upper() == '.JPG' and os.path.isfile(self._getpath(fname))

        return [f for f in os.listdir(self.dirpath) if is_valid(f)]

    def get_date_strings(self, fpath):
        # try exif date first
        dt = get_exif_date(fpath) or get_file_date(fpath)
        if self.timeshift:
            dt += datetime.timedelta(seconds=self.timeshift)
        s1 = "%y%m%d-%H%M-" if self.use_time else "%y%m%d-"
        s2 = "%Y-%m-%d %H:%M"
        return dt.strftime(s1), dt.strftime(s2)
        

    def _newname(self, old_name):
        old_path = self._getpath(old_name)
        datestr, timestr = self.get_date_strings(old_path)
        #pref = self.prefix + '-' if len(self.prefix) else ''
        clean_old_name = old_name.lower().replace('_', '-')
        clean_old_name = NAME_SUB_PAR.sub('', clean_old_name)
        name = '%s%s' % (datestr, clean_old_name)
        
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
            self._rename(fn, new_name, timestr)
        #if len(self.loglist):
        #    with open(self.logpath, 'wb') as fp:
        #        fp.write('\n'.join(self.loglist))



print("Testing renaming utility" if IS_TEST else "Renaming started")
d, ut, t = _read_input()
rn = ImageRenamer(d, ut, t, IS_TEST)

rn.process()

print("Done!")
