import gzip as gz
import io

def gzfitshead(fits):
    if not isinstance(fits, str):
        fits = str(fits)
    with gz.open(fits, 'rb') as fil:
        with io.TextIOWrapper(fil, encoding='utf-8') as dec:
            head = fil.read().split(b'DATASUM')[0]
    head = str(head)
    lines = [head[i*80:i*80+80] for i in range(len(head)//80)]
    header = {}
    for line in lines:
        key, extra = line.split('=')
        key = key.split()[0]
        if '/' in extra:
            extra = extra.split('/')[0]
        try:
            value = eval(extra)
            header[key] = value
        except NameError:
            pass
    return header

