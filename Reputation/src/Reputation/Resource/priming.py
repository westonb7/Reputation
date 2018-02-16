import falcon
import os
import lmdb
import libnacl

from .db import dbing


def setup(dbDirPath=None):
    repDbEnv = dbing.repDbSetup(baseDirPath=dbDirPath)
    #print("Hello from priming.py!")

    return True

def setupTest():
	baseDirPath = dbing.setupTmpBaseDir()
	dbDirPath = os.path.join(baseDirPath, "reputation/db")
	os.makedirs(dbDirPath)

	setup(dbDirPath=dbDirPath)