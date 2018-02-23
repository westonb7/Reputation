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

from collections import OrderedDict as ODict
from ioflo.aid import getConsole, timing
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from ..helping import makeSignedAgentReg, key64uToKey, keyToKey64u

try:
    import simplejson as json
except ImportError:
    import json

MAX_DB_COUNT = 8
DATABASE_DIR_PATH = "./testDbDir"
ALT_DATABASE_DIR_PATH = "./testDbDir"
SEPARATOR = "\r\n\r\n"
SEPARATOR_BYTES = SEPARATOR.encode("utf-8")

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


def putSigned(key, ser, sig,  dbName="unprocessed", env=None, overWrite=True):
    """
    Put signed serialization ser with signature sig at key in named sub
    database dbName in lmdb database environment env. If overWrite is False then
    raise DatabaseError exception if entry at key key is already present.

    Parameters:
        key is key relative key str for agent data resource in database
        ser is JSON serialization of dat
        sig is signature of resource using private signing key corresponding
            to key indexed key given by signer field in dat

        dbName is name str of named sub database, Default is 'core'
        env is main LMDB database environment
            If env is not provided then use global gDbEnv
        overWrite is Boolean If False then raise error if entry at key already
            exists in database
    """
    global gDbEnv

    if env is None:
        env = gDbEnv

    if env is None:
        raise DatabaseError("Database environment not set up")

    keyb = key.encode("utf-8")
    subDb = env.open_db(dbName.encode("utf-8"))  # open named sub db named dbName within env
    with env.begin(db=subDb, write=True) as txn:  # txn is a Transaction object
        rsrcb = (ser + SEPARATOR + sig).encode("utf-8")  # keys and values must be bytes
        result = txn.put(keyb, rsrcb, overwrite=overWrite )
        if not result:
            raise DatabaseError("Preexisting entry at key {}".format(key))
    return True


def getSelfSigned(key, dbName='reputation', env=None):
    """
    Returns tuple of (dat, ser, sig) corresponding to self-signed data resource
    at key in named dbName of env.

    Raises DatabaseError exception
    IF data resource not found
    IF self-signed signature stored in resource does not verify

    In return tuple:
        dat is ODict JSON deserialization of ser
        ser is JSON serialization of dat
        sig is signature of resource using private signing key corresponding
            to key indexed key given by signer field in dat

    Agents data resources are self signing

    Parameters:
        key is key str for agent data resource in database
        dbName is name str of named sub database, Default is 'core'
        env is main LMDB database environment
            If env is not provided then use global gDbEnv
    """
    global gDbEnv

    if env is None:
        env = gDbEnv

    if env is None:
        raise DatabaseError("Database environment not set up")

    # read from database
    subDb = gDbEnv.open_db(dbName.encode("utf-8"))  # open named sub db named dbName within env
    with gDbEnv.begin(db=subDb) as txn:  # txn is a Transaction object
        rsrcb = txn.get(key.encode("utf-8"))
        if rsrcb is None:  # does not exist
            raise DatabaseError("Resource not found.")

    rsrc = rsrcb.decode("utf-8")
    ser, sep, sig = rsrc.partition(SEPARATOR)
    try:
        dat = json.loads(ser, object_pairs_hook=ODict)
    except ValueError as ex:
        raise DatabaseError("Resource failed deserialization. {}".format(ex))

    try:
        sdid, index = dat["signer"].rsplit("#", maxsplit=1)
        index = int(index)  # get index and sdid from signer field
    except (KeyError, ValueError) as ex:
            raise DatabaseError('Invalid or missing key key index')  # missing sdid or index

    if sdid != dat['key']:
        raise DatabaseError('Invalid Self-Signer key')

    try:
        key = dat['keys'][index]['key']
    except (TypeError, IndexError, KeyError) as ex:
        raise DatabaseError('Missing verification key')

    if not verify64u(sig, ser, key):
        raise DatabaseError('Self signature verification failed')

    return (dat, ser, sig)

def setupTestDbAgentsThings(dbName="reputation", overWrite=False):
    """
    Assumes lmdb database environment has been setup already

    Put test agents and things in db and return duple of dicts (agents, things)
    keyed by  name each value is triple ( did, vk, sk)  where
    vk is public verification key
    sk is private signing key
    """

    agents = ODict()
    things = ODict()

    #seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)

    dt = datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)
    changed = timing.iso8601(dt, aware=True)

    # make "ann" the agent and issuer
    seed = (b'PTi\x15\xd5\xd3`\xf1u\x15}^r\x9bfH\x02l\xc6\x1b\x1d\x1c\x0b9\xd7{\xc0_'
            b'\xf2K\x93`')

    # creates signing/verification key pair
    avk, ask = libnacl.crypto_sign_seed_keypair(seed)

    issuant = ODict(kind="dns",
                    issuer="localhost",
                    registered=changed,
                    validationURL="http://localhost:8101/demo/check")
    issuants = [issuant]  # list of issuants hid name spaces

    sig, ser = makeSignedAgentReg(avk, ask, changed=changed, issuants=issuants)

    adat = json.loads(ser, object_pairs_hook=ODict)
    adid = adat['did']

    putSigned(key=adid, ser=ser, sig=sig, dbName=dbName, overWrite=overWrite)

    agents['ann'] = (adid, avk, ask)

    # make "ivy" the issurer
    seed = (b"\xb2PK\xad\x9b\x92\xa4\x07\xc6\xfa\x0f\x13\xd7\xe4\x08\xaf\xc7'~\x86"
                   b'\xd2\x92\x93rA|&9\x16Bdi')

    # creates signing/verification key pair
    ivk, isk = libnacl.crypto_sign_seed_keypair(seed)

    issuant = ODict(kind="dns",
                issuer="localhost",
                registered=changed,
                validationURL="http://localhost:8101/demo/check")
    issuants = [issuant]  # list of issuants hid name spaces

    sig, ser = makeSignedAgentReg(ivk, isk, changed=changed, issuants=issuants)

    idat = json.loads(ser, object_pairs_hook=ODict)
    idid = idat['did']

    putSigned(key=idid, ser=ser, sig=sig, dbName=dbName, overWrite=overWrite)

    agents['ivy'] = (idid, ivk, isk)

    # make "cam" the thing
    # create  thing signed by issuer and put into database
    seed = (b'\xba^\xe4\xdd\x81\xeb\x8b\xfa\xb1k\xe2\xfd6~^\x86tC\x9c\xa7\xe3\x1d2\x9d'
            b'P\xdd&R <\x97\x01')

    cvk, csk = libnacl.crypto_sign_seed_keypair(seed)

    signer = idat['signer']  # use same signer key fragment reference as issuer isaac
    hid = "hid:dns:localhost#02"
    data = ODict(keywords=["Canon", "EOS Rebel T6", "251440"],
                 message="If found please return.")

    sig, isig, ser = makeSignedThingReg(cvk,
                                          csk,
                                            isk,
                                            signer,
                                            changed=changed,
                                            hid=hid,
                                            data=data)

    cdat = json.loads(ser, object_pairs_hook=ODict)
    cdid = cdat['did']

    putSigned(key=cdid, ser=ser, sig=isig, dbName=dbName, overWrite=overWrite)
    putHid(hid, cdid)

    things['cam'] = (cdid, cvk, csk)

    # make "fae" the finder
    seed = (b'\xf9\x13\xf0\xff\xd4\xb3\xbdF\xa2\x80\x1d\xce\xaa\xd9\x87df\xc8\x1f\x91'
            b';\x9bp+\x1bK\x1ey\xef6\xa7\xf9')


    # creates signing/verification key pair
    fvk, fsk = libnacl.crypto_sign_seed_keypair(seed)

    sig, ser = makeSignedAgentReg(fvk, fsk, changed=changed)

    fdat = json.loads(ser, object_pairs_hook=ODict)
    fdid = fdat['did']

    putSigned(key=fdid, ser=ser, sig=sig, dbName=dbName, overWrite=overWrite)

    agents['fae'] = (fdid, fvk, fsk)

    # make "ike" another issurer for demo testing

    #seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
    seed = (b'!\x85\xaa\x8bq\xc3\xf8n\x93]\x8c\xb18w\xb9\xd8\xd7\xc3\xcf\x8a\x1dP\xa9m'
                   b'\x89\xb6h\xfe\x10\x80\xa6S')

    # creates signing/verification key pair
    ivk, isk = libnacl.crypto_sign_seed_keypair(seed)

    issuant = ODict(kind="dns",
                    issuer="localhost",
                    registered=changed,
                    validationURL="http://localhost:8101/demo/check")
    issuants = [issuant]  # list of issuants hid name spaces

    sig, ser = makeSignedAgentReg(ivk, isk, changed=changed, issuants=issuants)

    idat = json.loads(ser, object_pairs_hook=ODict)
    idid = idat['did']

    putSigned(key=idid, ser=ser, sig=sig, dbName=dbName, overWrite=overWrite)

    agents['ike'] = (idid, ivk, isk)


    return (agents, things)

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