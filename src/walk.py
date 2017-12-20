#!/usr/bin/env python3
import json
import os
from datetime import datetime
from functools import reduce
from subprocess import PIPE, run

ignored_dirs = ['lib', 'src', 'img', 'styles']


def is_ignored(dirname):
    return dirname.startswith('.') or dirname in ignored_dirs


def ignore(dirnames):
    dirnames[:] = [dirname for dirname in dirnames if not is_ignored(dirname)]


def pred_gen(**kwargs):
    return lambda x: all(x[k] == kwargs[k] for k in kwargs)


def get_dir(obj, ks):
    def get_dir_aux(obj, k):
        pred = pred_gen(type='directory', name=k)
        res = next(filter(pred, obj))
        return res['contents']
    return reduce(get_dir_aux, ks, obj)


def get_author_date(path):
    cmdargs = ['git', 'log', '--max-count=1', '--format=%aI', path]
    proc = run(cmdargs, stdout=PIPE)
    return (proc.stdout.decode().strip()
            or (datetime.fromtimestamp(os.path.getmtime(path))
                .astimezone().isoformat()))


walker = os.walk('.')
dirpath, dirnames, filenames = next(walker)
ignore(dirnames)

listing = []

for dirpath, dirnames, filenames in walker:
    # ignore(dirnames)
    pathsegs = dirpath.split('/')[1:]
    contents = []
    get_dir(listing, pathsegs[:-1]).append({
        'type': 'directory',
        'name': pathsegs[-1],
        'contents': contents
    })
    filenames = filter(lambda x: x.endswith('.html'), filenames)
    for name in filenames:
        path = os.path.join(dirpath, name)
        contents.append({
            'type': 'file',
            'name': name,
            'author_date': get_author_date(path)
        })
    # ISO 8601 supports lexicographical sorting
    contents.sort(key=lambda x: x['author_date'], reverse=True)

with open('listing.json', 'w') as f:
    json.dump(listing, f, indent=2)