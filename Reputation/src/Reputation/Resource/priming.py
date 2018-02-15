import falcon

import lmdb
import libnacl

from .db import dbing

def setup():
    repDbEnv = dbing.repDbSetup()
    print("Hello from priming.py!")

    return True