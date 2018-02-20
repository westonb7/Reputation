import falcon
import os
import lmdb
import libnacl

from .db import dbing

# This file defines functions used in setting up the environment

def setup(dbDirPath=None):
    repDbEnv = dbing.repDbSetup(baseDirPath=dbDirPath)
    #print("Hello from priming.py!")

    return True


def setupTest():
	baseDirPath = dbing.setupTmpBaseDir()
	dbDirPath = os.path.join(baseDirPath, "reputation/db")
	os.makedirs(dbDirPath)

	setup(dbDirPath=dbDirPath)