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


def setupTmpBaseDir(baseDirPath=""):
    if not baseDirPath:
        baseDirPath = tempfile.mkdtemp(prefix="reputation", suffix="test", dir="/tmp")

    baseDirPath = os.path.abspath(os.path.expanduser(baseDirPath))
    return baseDirPath


def cleanupTmpBaseDir(baseDirPath):
    if os.path.exists(baseDirPath):
        while baseDirPath.startswith("/tmp/reputation"):
            if baseDirPath.endswith("test"):
                shutil.rmtree(baseDirPath)
                break
            baseDirPath = os.path.dirname(baseDirPath)


def cleanupBaseDir(baseDirPath):
    if os.path.exists(baseDirPath):
        shutil.rmtree(baseDirPath)


def getAll(reputee, entries):
    reach_list = []
    clarity_list = []

    for entry in entries:
        if entry['reputee'] == reputee:
            if entry['repute']['feature'] == "reach":
                reach_list.append(entry['repute']['value'])
            elif entry['repute']['feature'] == "clarity":
                clarity_list.append(entry['repute']['value'])

    if len(reach_list) == 0 and len(clarity_list) == 0:
        return False

    reach_s = find_score(reach_list)
    reach_c = find_confidence(reach_list, 0)
    clarity_s = find_score(clarity_list)
    clarity_c = find_confidence(clarity_list, 1)
    clout_s = find_clout_score(reach_s, reach_c, clarity_s, clarity_c)
    clout_c = find_clout_confidence(reach_c, clarity_c)

    allList = [clout_s, clout_c, reach_s, reach_c, clarity_s, clarity_c]

    return allList
