import sys
import os
import os.path
from datetime import datetime
import re
import exifread

# setting JPEG image modification and access time to EXIF original time

# See also https://gist.github.com/ikoblik/7089165

# used via jpgtime.bat
# command line arguments:
# - path to image directory, or '-' for current directory (default)

try:
  import win32file, win32con
  # https://github.com/mhammond/pywin32
  WIN_32 = True
except:
  WIN_32 = False

IS_TEST = False

EXIF_DATE_SPLIT_PAT = re.compile(r'\D+')

def get_dir_path():
    input = sys.argv[1:]
    dir_path = input[0] if len(input) > 0 else os.getcwd()
    return dir_path

def get_exif_timestamp(fpath):
    key = 'EXIF DateTimeOriginal'
    try:
        tags = None
        with open(fpath, 'rb') as fp:
            tags = exifread.process_file(fp)
        timestr = str(tags[key]) # format: '2017:07:30 14:57:50'
        tt = tuple([int(x) for x in EXIF_DATE_SPLIT_PAT.split(timestr)])
        dt = datetime(*tt)
        ts = datetime.timestamp(dt)
        return ts
    except Exception as x:
        print("Could not extract '%s' from %s -- %s" % (key, os.path.basename(fpath), x))
        return None

def set_file_times(fpath, ts):
    if WIN_32:
        # https://yiyibooks.cn/__trs__/meikunyuan6/pywin32/pywin32/PyWin32/win32file__SetFileTime_meth.html
        dt = datetime.fromtimestamp(ts)
        filehandle = win32file.CreateFile(fpath, win32file.GENERIC_WRITE, 0, None, win32con.OPEN_EXISTING, 0, None)
        win32file.SetFileTime(filehandle, *(dt,)*3)
        filehandle.close()
    else:
        os.utime(fpath, (ts,)*2)

class ImageTimeFixer(object):

    def __init__(self, dir_path=None, is_test=False):
        self.dirpath = dir_path if dir_path is not None else os.path.dirname(os.path.abspath(__file__))
        self.istest = is_test

    def _getpath(self, fname):
        return os.path.join(self.dirpath, fname)

    def _is_valid_file(self, fname):
        if fname:
            ext = os.path.splitext(fname)[1]
            if ext in ['.jpg', '.JPG', '.jpeg'] and os.path.isfile(self._getpath(fname)):
                return True
        return False

    def _getpiclist(self):
        return [f for f in os.listdir(self.dirpath) if self._is_valid_file(f)]

    def _set_time(self, filepath, timestamp):
        #log = "changing access and modification time of '%s'" % (filepath)
        if self.istest:
            print('testing %s' % filepath)
            return
        try:
            #os.utime(filepath, (timestamp, timestamp))
            set_file_times(filepath, timestamp)
            log = "%s: OK" % filepath
        except IOError:
            log = "%s: FAIL!"  % filepath
        print(log)

    def process(self):
        pic_names = self._getpiclist()
        if len(pic_names) == 0:
            print("No valid images found in '%s'" % self.dirpath)
        for fn in pic_names:
            fp = self._getpath(fn)
            ts = get_exif_timestamp(fp)
            if ts is None:
                print('skipping %s' % fn)
            else:
                self._set_time(fp, ts)


print("Testing time fixing utility" if IS_TEST else "Time fixing started")

if WIN_32:
    print('Using pywin32')
    
dirpath = get_dir_path()

fixer = ImageTimeFixer(dirpath, IS_TEST)
fixer.process()

print("Done!")