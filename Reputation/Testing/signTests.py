import sys
import os
import falcon
import pytest

from falcon import testing
from math import ceil
from os import path
from collections import defaultdict
from pytest import approx
from ioflo.base import storing

try:
    import simplejson as json
except ImportError:
    import json

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from src.Reputation.Resource import resource
from src.Reputation.Resource import priming
from src.Reputation.Resource import helping
from src.Reputation.Resource.db import dbing

"""
This script is written to be run from the command line like this:
python3 signTests.py
"""

store = storing.Store(stamp=0.0)

@pytest.fixture
def client():
    return testing.TestClient(resource.create(store=store))

def testOnGet(client):
    priming.setupTest()
    dbing.testDbSetup()
    docA = {'title':'Error', 'description':'A valid query is required.'}
    docB = {'title':'Error', 'description':'Reputee could not be found.'}
    docC = {"reputee": "foo", "clout": {"score": 2.0}, "confidence": 0.5, "reach": {"score": 2.0, "confidence": 1}, "clarity": {"score": 2.0, "confidence": 0.5}}

    result = client.simulate_get('/signResource/')
    #print(result.content)
    assert result.json == docA
    assert result.status == falcon.HTTP_400

    result = client.simulate_get('/signResource/', query_string="name=789798bazelgeuse")
    #print(result.content)
    assert result.json == docB
    assert result.status == falcon.HTTP_400

    ser = json.dumps({"reputee": "foo", "clout": {
                    "score": 2.0},
                    "confidence": 0.5, "reach": {
                    "score": 2.0,
                    "confidence": 1}, "clarity": {
                    "score": 2.0,
                    "confidence": 0.5}})
    dbing.repPutTxn("foo", ser, dbName="reputation")

    result = client.simulate_get('/signResource/', query_string="name=foo")
    #print(result.content)
    assert result.json == docC
    assert result.status == falcon.HTTP_200

    helping.cleanupBaseDir(dbing.gDbDirPath)

    print("signed on_get() functioning properly")

def testPost(client):
    headers = {"Signature": "123;456"}
    ser = json.dumps({"test":"test"})
    did, sk = helping.createTestDid()

    bodyA = ser
    bodyB = b'{"reputer": "foo", "repute": ' \
            b'{"rid": 1, "feature": "clarity", "value": 1}}'
    bodyC = b'{"reputer": "foo", "reputee": "' + did.encode('utf-8') + b'"}'
    bodyD = b'{"reputer": "foo", "reputee": "' + did.encode('utf-8') + b'", "repute": ' \
            b'{"rid": 1, "feature": "clarity", "value": 5}}'

    priming.setupTest()
    dbing.testDbSetup()

    result = client.simulate_post('/signResource/')
    assert result.content == b'{"title": "Error", "description": "Invalid or missing Signature header."}'
    assert result.status == falcon.HTTP_400

    headers["Signature"] = 'signer="' + helping.signResource(bodyA, sk) + '"'

    result = client.simulate_post('/signResource/', headers=headers)
    assert result.content == b'{"title": "Error", "description": "Could not decode the request body."}'
    assert result.status == falcon.HTTP_400

    result = client.simulate_post("/signResource", headers=headers, body=bodyB)
    assert result.content == b'{"title": "Error", "description": "Request must contain reputee field."}'
    assert result.status == falcon.HTTP_400

    result = client.simulate_post("/signResource", headers=headers, body=bodyC)
    assert result.content == b'{"title": "Error", "description": "Could not validate the request body. Unverifiable signature"}'
    assert result.status == falcon.HTTP_400

    headers["Signature"] = 'signer="' + helping.signResource(bodyC, sk) + '"'

    result = client.simulate_post("/signResource", headers=headers, body=bodyC)
    assert result.content == b'{"title": "Error", "description": "Request must contain repute field."}'
    assert result.status == falcon.HTTP_400

    headers["Signature"] = 'signer="' + helping.signResource(bodyD, sk) + '"'

    result = client.simulate_post('/signResource/', headers=headers, body=bodyD)
    assert result.content == b'{"message": "POST recieved"}'
    assert result.status == falcon.HTTP_202

    helping.cleanupBaseDir(dbing.gDbDirPath)

    print("signed on_post() functioning properly")


def runSignTests():
    clientName = client()
    testOnGet(clientName)
    testPost(clientName)

    return True

runSignTests()




# http --json POST localhost:8000/resource test:="{"reputer":"name", "reputee":"foo", "repute":{"rid":"xyz1527577345774", "feature":"Reach", "value":"5"}}"
# http --json POST localhost:8000/resource reputer=name reputee=foo repute:="rid"="xyz1527577345774", feature=Reach, value=5}"
