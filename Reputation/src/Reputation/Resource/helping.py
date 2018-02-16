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

    reach_s = findScore(reach_list)
    reach_c = findConfidence(reach_list, 0)
    clarity_s = findScore(clarity_list)
    clarity_c = findConfidence(clarity_list, 1)
    clout_s = findCloutScore(reach_s, reach_c, clarity_s, clarity_c)
    clout_c = findCloutConfidence(reach_c, clarity_c)

    allList = [clout_s, clout_c, reach_s, reach_c, clarity_s, clarity_c]

    return allList
