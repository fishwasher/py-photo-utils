import functools

#pat = re.compile(r'^\$');
def checksum(s):
    #s = pat.sub(s, '')
    #lst = list(s.replace('$', '', 1))
    lst = [ord(c) for c in s.replace('$', '', 1)]
    return '%.2X' % functools.reduce(lambda x,y: x ^ y, lst)