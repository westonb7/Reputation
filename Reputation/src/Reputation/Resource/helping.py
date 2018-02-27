import falcon
import os
import shutil
import tempfile
import base64
import libnacl
#from .db import dbing

from collections import defaultdict
from collections import OrderedDict as ODict
from .calculations import *
from . import signing
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
    rAvg = 0
    rTotal = 0
    cAvg = 0
    cTotal = 0

    for entry in entries:
        #print(entry)
        if entry['reputee'] == reputee:
            if entry['repute']['feature'] == "Reach":
                reachList.append(entry['repute']['value'])
                rAvg += entry['repute']['value']
                rTotal += 1
            elif entry['repute']['feature'] == "Clarity":
                clarityList.append(entry['repute']['value'])
                cAvg += entry['repute']['value']
                cTotal += 1

    if len(reachList) == 0 and len(clarityList) == 0:
        return False

    reachScore = findScore(reachList)
    reachConf = findConfidence(reachList, 0)
    clarityScore = findScore(clarityList)
    clarityConf = findConfidence(clarityList, 1)
    cloutScore = findCloutScore(reachScore, reachConf, clarityScore, clarityConf)
    cloutConf = findCloutConfidence(reachConf, clarityConf)

    allList = [cloutScore, cloutConf, reachScore, reachConf, clarityScore, clarityConf, rAvg, rTotal, cAvg, cTotal]

    #print("getAll() success!")
    return allList

def getAllRun(reputee, result, average=None):
    #print(entries)
    rAvg = result[6]
    rTotal = result[7]
    cAvg = result[8]
    cTotal = result[9]

    if average==None:
        if entry['repute']['feature'] == "Reach":
            reachList.append(entry['repute']['value'])
        elif entry['repute']['feature'] == "Clarity":
            clarityList.append(entry['repute']['value'])
        return allList

    if entry['reputee'] == reputee:
        if entry['repute']['feature'] == "Reach":
            reachList.append(entry['repute']['value'])
        elif entry['repute']['feature'] == "Clarity":
            clarityList.append(entry['repute']['value'])

    if len(reachList) == 0 and len(clarityList) == 0:
        return False

    reachScore = runningScore(rAvg, rTotal)
    reachConf = runningConf(rTotal, 0)
    clarityScore = runningScore(cAvg, cTotal)
    clarityConf = runningConf(cTotal, 1)
    cloutScore = findCloutScore(reachScore, reachConf, clarityScore, clarityConf)
    cloutConf = findCloutConfidence(reachConf, clarityConf)

    allList = [rAvg, rTotal, cAvg, cTotal, clarityScore, clarityConf]

    #print("getAll() success!")
    return allList

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

def makeSignedAgentReg(vk, sk, changed=None, **kwa):
    """
    Return duple of (signature,registration) of minimal self-signing
    agent registration record for keypair vk, sk

    registration is json encoded unicode string of registration record
    signature is base64 url-file safe unicode string signature generated
    by signing bytes version of registration

    Parameters:
        vk is bytes that is the public verification key
        sk is bytes that is the private signing key
        changed is ISO8601 date time stamp string if not provided then uses current datetime
        **kwa are optional fields to be added to data resource. Each keyword is
           the associated field name and the argument parameter is the value of
           that field in the data resource.  Keywords in ("did", "signer", "changed",
            "keys") will be overidden. Common use case is "issuants".


    """
    reg = ODict(did="", signer="", changed="", keys=None)  # create registration record as dict
    if kwa:
        reg.update(kwa.items())

    if not changed:
        changed = timing.iso8601(aware=True)

    did = makeDid(vk)  # create the did
    index = 0
    signer = "{}#{}".format(did, index)  # signer field value key at index
    key64u = keyToKey64u(vk)  # make key index field value
    kind = "EdDSA"

    reg["did"] = did
    reg["signer"] = signer
    reg["changed"] = changed
    reg["keys"] = [ODict(key=key64u, kind=kind)]

    registration = json.dumps(reg, indent=2)
    sig = libnacl.crypto_sign(registration.encode("utf-8"), sk)[:libnacl.crypto_sign_BYTES]
    signature = keyToKey64u(sig)

    return (signature, registration)

def parseSignatureHeader(signature):
    """
    Returns ODict of fields and values parsed from signature
    which is the value portion of a Signature header
    Signature header has format:
        Signature: headervalue
    Headervalue:
        tag = "signature"
    or
        tag = "signature"; tag = "signature"  ...
    where tag is the name of a field in the body of the request whose value
    is a DID from which the public key for the signature can be obtained
    If the same tag appears multiple times then only the last occurrence is returned
    each signature value is a doubly quoted string that contains the actual signature
    in Base64 url safe format. By default the signatures are EdDSA (Ed25519)
    which are 88 characters long (with two trailing pad bytes) that represent
    64 byte EdDSA signatures
    An option tag name = "kind" with values "EdDSA"  "Ed25519" may be present
    that specifies the type of signature. All signatures within the header
    must be of the same kind.
    The two tag fields currently supported are "did" and "signer"
    """
    sigs = ODict()
    if signature:
        clauses = signature.split(";")
        for clause in clauses:
            clause = clause.strip()
            if not clause:
                continue
            try:
                tag, value = clause.split("=", maxsplit=1)
            except ValueError as ex:
                continue
            tag = tag.strip()
            if not tag:
                continue
            value = value.strip()
            if not value.startswith('"') or not value.endswith('"') or len(value) < 3:
                continue
            value = value[1:-1]
            value = value.strip()
            sigs[tag] = value
    return sigs

def makeDid(vk, method="igo"):
    """
    Create and return Indigo Did from bytes vk.
    vk is 32 byte verifier key from EdDSA (Ed25519) keypair
    """
    # convert verkey to jsonable unicode string of base64 url-file safe
    vk64u = keyToKey64u(vk)
    did = "did:{}:{}".format(method, vk64u)
    return did


def createTestDid():
    seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
    publicKey, secretKey = libnacl.crypto_sign_seed_keypair(seed)

    return (makeDid(publicKey), secretKey)


def signResource(resource, sKey):
    sig = libnacl.crypto_sign(resource, sKey)
    sig = sig[:libnacl.crypto_sign_BYTES]

    return keyToKey64u(sig)


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


def verify64u(signature, message, verkey):
    """
    Returns True if signature is valid for message with respect to verification
    key verkey
    signature and verkey are encoded as unicode base64 url-file strings
    and message is unicode string as would be the case for a json object
    """
    sig = key64uToKey(signature)
    vk = key64uToKey(verkey)
    # msg = message.encode("utf-8")
    return (verify(sig, message, vk))


def extractDatSignerParts(dat, method="igo"):
    """
    Parses and returns did index keystr from signer field value of dat
    as tuple (did, index, keystr)
    raises ValueError if fails parsing
    """
    # get signer key from read data. assumes that resource is valid
    try:
        did, index = dat["signer"].rsplit("#", maxsplit=1)
        index = int(index)  # get index and sdid from signer field
    except (KeyError, ValueError) as ex:
        raise ValueError("Missing signer field or invalid indexed signer value")

    try:  # correct did format  pre:method:keystr
        pre, meth, keystr = did.split(":")
    except ValueError as ex:
        raise ValueError("Malformed DID value")

    if pre != "did" or meth != method:
        raise ValueError("Invalid DID value")

    return (did, index, keystr)


def extractDidSignerParts(signer, method="igo"):
    """
    Parses and returns did index keystr from signer key indexed did
    as tuple (did, index, keystr)
    raises ValueError if fails parsing
    """
    # get signer key from read data. assumes that resource is valid
    try:
        did, index = signer.rsplit("#", maxsplit=1)
        index = int(index)  # get index and sdid from signer field
    except ValueError as ex:
        raise ValueError("Invalid indexed signer value")

    try:  # correct did format  pre:method:keystr
        pre, meth, keystr = did.split(":")
    except ValueError as ex:
        raise ValueError("Malformed DID value")

    if pre != "did" or meth != method:
        raise ValueError("Invalid DID value")

    return (did, index, keystr)


def extractDidParts(did, method="igo"):
    """
    Parses and returns keystr from did
    raises ValueError if fails parsing
    """
    try:  # correct did format  pre:method:keystr
        pre, meth, keystr = did.split(":")
    except ValueError as ex:
        raise ValueError("Malformed DID value")

    if pre != "did" or meth != method:
        raise ValueError("Invalid DID value")

    return keystr


def validateSignedResource(signature, resource, verkey, method="igo"):
    """
    Returns dict of deserialized resource if signature verifies for resource given
    verification key verkey in base64 url safe unicode format
    Otherwise returns None
    signature is base64 url-file safe unicode string signature generated
        by signing bytes version of resource with privated signing key associated with
        public verification key referenced by key indexed signer field in resource
    resource is json encoded unicode string of resource record
    verkey is base64 url-file safe unicode string public verification key referenced
        by signer field in resource. This is looked up in database from signer's
        agent data resource
    method is the method string used to generate dids in the resource
    """

    try:
        try:
            rsrc = json.loads(resource, object_pairs_hook=ODict)
        except ValueError as ex:
            raise signing.ValidationError("Invalid JSON")  # invalid json

        if not rsrc:  # resource must not be empty
            raise signing.ValidationError("Empty body")

        if not isinstance(rsrc, dict):  # must be dict subclass
            raise signing.ValidationError("JSON not dict")

        if "reputee" not in rsrc:  # did field required
            raise signing.ValidationError("Missing did field")

        ddid = rsrc["reputee"]

        try:  # correct did format  pre:method:keystr
            pre, meth, keystr = ddid.split(":")
        except ValueError as ex:
            raise signing.ValidationError("Invalid format did field")

        if pre != "did" or meth != method:
            raise signing.ValidationError("Invalid format did field") # did format bad

        if len(verkey) != 44:
            raise signing.ValidationError("Verkey invalid")  # invalid length for base64 encoded key

        if not verify64u(signature, resource, verkey):
            raise signing.ValidationError("Unverifiable signature")  # signature fails

    except signing.ValidationError:
        raise

    except Exception as ex:  # unknown problem
        raise signing.ValidationError("Unexpected error")

    return rsrc

