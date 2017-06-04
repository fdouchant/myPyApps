__version__ = (2, 0, 0)

import os, glob, shutil
from os.path import isfile, isdir

def rm_fr(path):
    if not hasattr(path, '__get__'):
        paths = [path]
    
    for path in paths:
        for f in glob.glob(path):
            if isfile(f):
                os.remove(f)
            elif isdir(f):
                shutil.rmtree(f)
    
    
    