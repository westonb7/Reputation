import falcon
import os
import shutil
import tempfile
import base64
import libnacl
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


def verify(sig, msg, vk):
    """
    Returns True if signature sig of message msg is verified with
    verification key vk Otherwise False
    All of sig, msg, vk are bytes
    """
    try:
        result = libnacl.crypto_sign_open(sig + msg, vk)
    except Exception as ex:
        return False
    return (True if result else False)


def keyToKey64u(key):
    """
    Convert and return bytes key to unicode base64 url-file safe version
    """
    return base64.urlsafe_b64encode(key).decode("utf-8")


def key64uToKey(key64u):
    """
    Convert and return unicode base64 url-file safe key64u to bytes key
    """
    return base64.urlsafe_b64decode(key64u.encode("utf-8"))

