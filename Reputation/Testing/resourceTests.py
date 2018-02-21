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
from src.Reputation.Resource import calculations as cal
from src.Reputation.Resource import resource
from src.Reputation.Resource import priming
from src.Reputation.Resource import helping
from src.Reputation.Resource.db import dbing

"""
This script is written to be run from the command line like this:
python3 resourceTests.py
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

    result = client.simulate_get('/resource/')
    assert result.json == docA
    assert result.status == falcon.HTTP_400

    result = client.simulate_get('/resource/', query_string="name=foo")
#    print(result.json)    

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

    result = client.simulate_get('/resource/', query_string="name=foo")

    assert result.json == docC
    assert result.status == falcon.HTTP_200

    helping.cleanupBaseDir(dbing.gDbDirPath)

    return True

def testPost(client):
    priming.setupTest()
    dbing.setupTestDbEnv()

    response = app.simulate_post('/reputation/foo')
    assert response.content == b'{"title":"Error","description":"Malformed URI."}'
    assert response.status == falcon.HTTP_400

    response = app.simulate_post('/reputation/')
    assert response.content == b'{"title":"Error","description":"A valid JSON document is required."}'
    assert response.status == falcon.HTTP_400

    response = app.simulate_post('/reputation/', body=b'Testing ... 1 ... 2 ... 3')
    assert response.content == b'{"title":"Error","description":"Could not decode the request body. The JSON was malformed or not encoded as UTF-8."}'
    assert response.status == falcon.HTTP_422

    ser = json.dumps({"test":"test"})
    response = app.simulate_post('/reputation/', body=ser)
    assert response.content == b'{"title":"Error","description":"The JSON was formatted incorrectly."}'
    assert response.status == falcon.HTTP_400

    ser = json.dumps({
    "reputer": "foo",
    "reputee": "bar",
    "repute":
      {
        "rid": "dda6555f-21c8-45ff-9633-f9b5cdc59f45",
        "feature": "clarity",
        "value": 5
      }
    })
    response = app.simulate_post('/reputation/', body=ser)
    assert response.content == b'{"Message":"entry successfully created."}'
    assert response.status == falcon.HTTP_201

    helping.cleanupTmpBaseDir(dbing.gDbDirPath)


def runResourceTests():
    clientName = client()
    testOnGet(clientName)
    #testOnPost(clientName)

    return True

runResourceTests()
