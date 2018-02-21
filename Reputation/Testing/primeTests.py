import sys
import os
import falcon

from math import ceil
from collections import deque
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from src.Reputation.Resource import calculations as cal
from src.Reputation.Resource.db import dbing
from src.Reputation.Resource import priming

"""
This script is written to be run from the command line like this:
python3 primeTests.py
"""

## Thanks Brady for letting me take notes from your code

def setupPrimeTest():
    baseDirPath = dbing.setupTmpBaseDir()
    assert baseDirPath.startswith("/tmp/reputation")
    assert baseDirPath.endswith("test")

    dbDirPath = os.path.join(baseDirPath, "reputation/db")
    os.makedirs(dbDirPath)
    assert os.path.exists(dbDirPath)

    priming.setup(dbDirPath=dbDirPath)
    assert dbing.gDbDirPath == dbDirPath

    dbing.cleanupTmpBaseDir(baseDirPath)
    assert not os.path.exists(baseDirPath)

    print("Prime setup functioning properly.")

def testPrimeTest():
    priming.setupTest()
    assert os.path.exists(dbing.gDbDirPath)

    dbing.cleanupTmpBaseDir(dbing.gDbDirPath)
    assert not os.path.exists(dbing.gDbDirPath)

    print("Prime test setup funcitoning properly.")

def runPrimeTests():
    setupPrimeTest()
    testPrimeTest()

runPrimeTests()
