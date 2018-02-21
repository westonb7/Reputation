from __future__ import generator_stop
import falcon
import os
import sys
import enum
import datetime
import lmdb
import libnacl
import shutil
import tempfile

from ioflo.aid import getConsole
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

try:
    import simplejson as json
except ImportError:
    import json

MAX_DB_COUNT = 8
DATABASE_DIR_PATH = "./testDbDir"
ALT_DATABASE_DIR_PATH = "./testDbDir"

console = getConsole()
gDbDirPath = None
gDbEnv = None

class RepError(Exception):
    """
    Error clasee
    """

class DatabaseError(RepError):
    """
    Database related errors
    """


def repDbSetup(baseDirPath=None):
    global gDbEnv, gDbDirPath

    if not baseDirPath:
        baseDirPath = DATABASE_DIR_PATH

    baseDirPath = os.path.abspath(os.path.expanduser(baseDirPath))
    if not os.path.exists(baseDirPath):
        try:
            os.makedirs(baseDirPath)
        except OSError:
            baseDirPath = ALT_DATABASE_DIR_PATH
            baseDirPath = os.path.abspath(os.path.expanduser(baseDirPath))
            if not os.path.exists(baseDirPath):
                os.makedirs(baseDirPath)
    else:
        if not os.access(baseDirPath, os.R_OK | os.W_OK):
            baseDirPath = ALT_DATABASE_DIR_PATH
            baseDirPath = os.path.abspath(os.path.expanduser(baseDirPath))
            if not os.path.exists(baseDirPath):
                os.makedirs(baseDirPath)

    gDbDirPath = baseDirPath

    gDbEnv = lmdb.open(gDbDirPath, max_dbs=MAX_DB_COUNT)

    gDbEnv.open_db(b'raw')
    gDbEnv.open_db(b'unprocessed')
    gDbEnv.open_db(b'reputation')

    return gDbEnv


def testDbSetup():
    baseDirPath = setupTmpBaseDir()
    baseDirPath = os.path.join(baseDirPath, "db/reputation")
    os.makedirs(baseDirPath)
    return repDbSetup(baseDirPath=baseDirPath)


def repPutTxn(key, ser, env=None, dbName="raw"):
    global gDbEnv

    if env is None:
        env = gDbEnv

    if env is None:
        raise DatabaseError("Database environment is not set up.")

    keyb = key.encode("utf-8")
    serb = ser.encode("utf-8")  
    subDb = gDbEnv.open_db(dbName.encode("utf-8"))  
    with gDbEnv.begin(db=subDb, write=True) as txn: 
        result = txn.put(keyb, serb, overwrite=True) 
        if not result:
            raise DatabaseError("Preexisting entry at key {}".format(key))
    return True


def repGetTxn(key, env=None, dbName="raw"):
    global gDbEnv

    if env is None:
        env = gDbEnv

    if env is None:
        raise DatabaseError("Database environment is not set up.")

    subDb = gDbEnv.open_db(dbName.encode("utf-8"))
    with gDbEnv.begin(db=subDb) as txn:  
        serb = txn.get(key.encode("utf-8"))
        if serb is None:  
            raise DatabaseError("Resource not found.")

        ser = serb.decode("utf=8")
        try:
            dat = json.loads(ser)
        except ValueError as exception:
            raise DatabaseError("Resource failed desereialization. {}".format(exception))

    return dat


def repGetEntries(dbName='raw', env=None):
    global gDbEnv

    if env is None:
        env = gDbEnv

    if env is None:
        raise DatabaseError("Database environment is not set up.")

    entries = []
    subDb = gDbEnv.open_db(dbName.encode("utf-8"), dupsort=True)
    with gDbEnv.begin(db=subDb) as txn:
        with txn.cursor() as cursor:
            if cursor.first():
                while True:
                    value = cursor.value().decode()

                    try:
                        dat = json.loads(value)
                    except ValueError:
                        if cursor.next():
                            continue
                        else:
                            break

                    entries.append(dat)

                    if not cursor.next():
                        break

    return entries


def repGetEntryKeys(dbName='raw', env=None):
    global gDbEnv

    if env is None:
        env = gDbEnv

    if env is None:
        raise DatabaseError("Database environment is not set up.")

    entries = []
    subDb = gDbEnv.open_db(dbName.encode("utf-8"), dupsort=True)
    with gDbEnv.begin(db=subDb) as txn:
        with txn.cursor() as cursor:
            if cursor.first():
                while True:
                    value = cursor.key()
                    entries.append(value)

                    if not cursor.next():
                        break

    return entries


def repDeleteEntry(key, dbName='unprocessed', env=None):
    global gDbEnv

    if env is None:
        env = gDbEnv

    if env is None:
        raise DatabaseError("Database environment is not set up.")

    subDb = gDbEnv.open_db(dbName.encode("utf-8"), dupsort=True)
    with gDbEnv.begin(db=subDb, write=True) as txn:
        entry = txn.delete(key)
        if entry is None:
            raise DatabaseError("Entry could not be deleted")

    return entry


def repDeleteEntries(dbName='unprocessed', env=None):
    global gDbEnv

    if env is None:
        env = gDbEnv

    if env is None:
        raise DatabaseError("Database environment is not set up.")

    success = False
    entries = repGetEntryKeys(dbName=dbName, env=env)

    for entry in entries:
        result = repDeleteEntry(key=entry, dbName=dbName, env=env)
        if result:
            success = True

    return success

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