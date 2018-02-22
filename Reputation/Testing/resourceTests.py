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

    print("on_get() functioning properly")

def testPost(client):
    priming.setupTest()
    dbing.testDbSetup()

    result = client.simulate_post('/resource/')
    #print(result.content)
    assert result.content == b'{"title": "Error", "description": "Invalid JSON document"}'
    assert result.status == falcon.HTTP_400

    result = client.simulate_post('/resource/', query_string="name=foo")
    #print(result.content)
    assert result.content == b'{"title": "Error", "description": "Invalid JSON document"}'
    assert result.status == falcon.HTTP_400

    result = client.simulate_post('/resource/', body=b'Testing ... 1 ... 2 ... 3')
    #print(result.content)
    assert result.content == b'{"title": "Error", "description": "Could not decode the request body"}'
    assert result.status == falcon.HTTP_422

    ser = json.dumps({"test":"test"})
    #print(result.content)
    result = client.simulate_post('/resource/', body=ser)
    assert result.content == b'{"title": "Error", "description": "The JSON was formatted incorrectly"}'
    assert result.status == falcon.HTTP_400

    ser = json.dumps({ "test":
        {
        "reputer": "foo",
        "reputee": "bar",
        "repute":
          {
            "rid": "xyz123409876768",
            "feature": "clarity",
            "value": 5
          }
        }
    })
    result = client.simulate_post('/resource/', body=ser)
    #print(result.content)
    assert result.content == b'{"message": "POST recieved"}'
    assert result.status == falcon.HTTP_202

    helping.cleanupBaseDir(dbing.gDbDirPath)

    print("on_post() functioning properly")



def runResourceTests():
    clientName = client()
    testOnGet(clientName)
    testPost(clientName)

    return True

runResourceTests()




# http --json POST localhost:8000/resource test:="{"reputer":"name", "reputee":"foo", "repute":{"rid":"xyz1527577345774", "feature":"Reach", "value":"5"}}"
# http --json POST localhost:8000/resource reputer=name reputee=foo repute:="rid"="xyz1527577345774", feature=Reach, value=5}"
