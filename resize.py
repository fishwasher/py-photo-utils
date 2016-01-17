import os
import glob
import Image
import shutil
import datetime

USE_DATE = False # add date stamp to file name: set to False if images already renamed

# adjust time difference before proceeding
TIMESHIFT = {
    'hr': 0,
    'min': 0
}

LOGFILE = {
    'name': 'resize-log.txt',
    'file': None
}

#LOGFILENAME = 'resize-log.txt'

# renditions: large, medium, small, thumbnail (square)
RENDITIONS = {
    'l': {'size': (2000, 2000), 'quality': 85, 'square': False},
    'm': {'size': (1200, 1200), 'quality': 85, 'square': False},
    's': {'size': (640, 640), 'quality': 85, 'square': False},
    'tn': {'size': (320, 160), 'quality': 85, 'square': True},
}

ORIG_EXT = ".JPG"

#logfile = None

def log(msg, nl=False):
    print msg
    if LOGFILE['file'] is not None:
        sep = ' ' if nl==False else '\n'
        LOGFILE['file'].write(msg + sep)


def format_time(ts):
    h = TIMESHIFT['hr']
    m = TIMESHIFT['min']
    s = (h * 60 * 60) + (m * 60)
    ts = ts + s
    d = datetime.datetime.fromtimestamp(ts)
    return d.strftime("%y%m%d-%H%M")


def make_filename(old_name, size_label, ts=0, ext='.jpg'):
    old_name = old_name.lower().replace('_', '-')
    name,suf = os.path.splitext(old_name)
    new_name = '%s-%s-%s%s' % (format_time(ts), name, size_label, ext) if ts and USE_DATE else '%s-%s%s' % (name, size_label, ext)
    return new_name

def process_image(orig_fname):
    #log("processing '%s'..." % orig_fname)
    ext = os.path.splitext(orig_fname)[1]
    st = os.stat(orig_fname)
    ts = st.st_mtime
    #im = Image.open(orig_fname)
    for label,conf in RENDITIONS.iteritems():
        im = Image.open(orig_fname)
        log('resizing to %s...' % label)
        im.thumbnail(conf['size'], Image.ANTIALIAS)
        #new_fname = make_filename(orig_fname, label, ts, '.jpg')
        #q = conf['quality']
        #im.save(new_fname, "JPEG", quality=q)
        #shutil.copystat(orig_fname, new_fname)
        if conf['square']:
            #crop_square(new_fname)
            rat = float(im.size[0]) / float(im.size[1])
            minsize = min(im.size)
            x = ((im.size[0] - minsize) / 2) if rat>1 else 0;
            y = ((im.size[1] - minsize) / 2) if rat<1 else 0;
            box = (x, y, x+minsize, y+minsize)
            log('cropping to box (%s, %s, %s, %s)' % box, True)
            im = im.crop(box)
        new_fname = make_filename(orig_fname, label, ts, '.jpg')
        q = conf['quality']
        im.save(new_fname, "JPEG", quality=q)
        shutil.copystat(orig_fname, new_fname)
    log("done", True)


def do_the_job():
    LOGFILE['file'] = open(LOGFILE['name'], 'w')
    for fn in glob.iglob('*.JPG'):
        log("processing '%s'..." % fn, True)
        process_image(fn)
    log("Done!", True)


do_the_job()