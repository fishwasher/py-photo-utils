import sys
import os
import os.path
import re


# Remove time part from renamed images
# command line arguments:
# - path to image directory

IS_TEST = False

PAT_IMAGE = re.compile(r'^(\d+)-\d+(-\w+\.jpg)$')

def read_input():
    input = sys.argv[1:]
    size = len(input)
    dir_path = input[0] if size > 0 and input[0] != '-' else os.path.dirname(os.path.abspath(__file__))
    return dir_path

def rename(dirpath):
    getpath = lambda fname: os.path.join(dirpath, fname)
    for fn in os.listdir(dirpath):
        m = PAT_IMAGE.match(fn)
        if m:
            newname = m.group(1) + m.group(2)
            op = '%s -> %s' % (fn, newname)
            if IS_TEST:
                print op
                continue
            old_path = getpath(fn)
            new_path = getpath(newname)
            try:
                os.rename(old_path, new_path)
                op += ': OK'
            except IOError:
                op += ': FAIL'
            print op




print "Testing renaming utility" if IS_TEST else "Renaming started"
d = read_input()
rename(d)

print "Done!"

