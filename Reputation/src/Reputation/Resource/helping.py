import falcon
import os
import shutil
import tempfile
from .db import dbing

from collections import defaultdict
from .calculations import *
from ioflo.aid import getConsole

try:
    import simplejson as json
except ImportError:
    import json

try:
    import msgpack
except ImportError:
    pass

console = getConsole()


def cleanupBaseDir(baseDirPath):
    if os.path.exists(baseDirPath):
        shutil.rmtree(baseDirPath)

# This is the function used to take and calculate the scores for the reputes

def getAll(reputee, entries):
    reachList = []
    clarityList = []
    #print(entries)

    for entry in entries:
        #print(entry)
        if entry['reputee'] == reputee:
            if entry['repute']['feature'] == "Reach":
                reachList.append(entry['repute']['value'])
            elif entry['repute']['feature'] == "Clarity":
                clarityList.append(entry['repute']['value'])

    if len(reachList) == 0 and len(clarityList) == 0:
        return False

    reachScore = findScore(reachList)
    reachConf = findConfidence(reachList, 0)
    clarityScore = findScore(clarityList)
    clarityConf = findConfidence(clarityList, 1)
    cloutScore = findCloutScore(reachScore, reachConf, clarityScore, clarityConf)
    cloutConf = findCloutConfidence(reachConf, clarityConf)

    allList = [cloutScore, cloutConf, reachScore, reachConf, clarityScore, clarityConf]

    #print("getAll() success!")
    return allList
