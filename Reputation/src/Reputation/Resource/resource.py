import falcon
from .db import dbing

from collections import defaultdict
from .calculations import *

try:
    import simplejson as json
except ImportError:
    import json

# This file contains the "resource" object that is used to handle GET and POST requests

RESOURCE_BASE_PATH = "/resource"

class Resource(object):
    # Sample GET request: 
    # http localhost:8000/resource?name=foo

    def  __init__(self, store=None, **kwa):

        super(**kwa)
        self.store = store


    def on_get(self, req, resp, reputeeName=None):

        reputeeName = req.get_param('name')

        if reputeeName == None:
            raise falcon.HTTPError(falcon.HTTP_400, 'Error', 'A valid query is required.')

        try:
            reputeeName = reputeeName.lower()
            result = dbing.repGetTxn(reputeeName, dbName='reputation')
        except dbing.DatabaseError:
            raise falcon.HTTPError(falcon.HTTP_400, 'Error', 'Reputee could not be found.')
 #       else:
        resp.body = json.dumps(result)
        resp.status = falcon.HTTP_200


    def on_post(self, req, resp):   

    # Sample POST request:
    # http --json POST localhost:8000/resource test:='{"reputer":"name", "reputee":"foo", "repute":{"rid":"xyz12345", "feature":"Clarity", "value":"5"}}'
    # http --json POST localhost:8000/resource test:='{"reputer":"name", "reputee":"foo", "repute":{"rid":"xyz12346", "feature":"Reach", "value":"5"}}'

        doc_jsn = {"message":"POST recieved"}

        try:
            streamData = req.stream.read()
            if not streamData:
                raise falcon.HTTPError(falcon.HTTP_400, 'Error', 'Invalid JSON document')
        except Exception:
            raise falcon.HTTPError(falcon.HTTP_400, 'Error', 'Invalid JSON document')

        try:
            streamData = json.loads(streamData)
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_422, 'Error', 'Could not decode the request body ')

        # If there's a better way to format the POST body, I'd like to change it
        # Access the data in the POST body, and format it for the databse

        reputer = streamData['test']['reputer']
        reputee = streamData['test']['reputee']
        rid = str(streamData['test']['repute']['rid'])
        feature = streamData['test']['repute']['feature']
        value = int(streamData['test']['repute']['value'])

        key = reputee + '-' + rid
        ser = json.dumps({"reputer": reputer,
                            "reputee": reputee,
                            "repute": {"rid": rid, "feature": feature, "value": value}})
        
        # Enter the data into the databse

        dbing.repPutTxn(key, ser)    
        dbing.repPutTxn(reputee, ser, dbName="unprocessed")
        resp.status = falcon.HTTP_201
        resp.body = json.dumps({'Message': 'entry successfully created.'})

        resp.body = json.dumps(doc_jsn, ensure_ascii=False)
        resp.status = falcon.HTTP_202

        #dbing.repPutTxn(reputee, rid, feature, str(value))

# Define a function to load the object

def loadResource(app, store):

    resource = Resource(store=store)
    app.add_route('{}'.format(RESOURCE_BASE_PATH), resource)

def create(store):
    app = falcon.API()
    loadResource(app, store=store)
    return app


"""
example of what prints on post request
Parsed Request:
POST /resource (1, 1)
lodict([('host', 'localhost:8000'), ('user-agent', 'HTTPie/0.9.9'), ('accept-encoding', 'gzip, deflate'), ('accept', 'application/json, */*'), ('connection', 'keep-alive'), ('content-type', 'application/json'), ('content-length', '112')])
bytearray(b'{"test": {"reputer": "name", "reputee": "foo", "repute": {"rid": "xyz12349", "feature": "Reach", "value": "9"}}}')

example of reputee_scores
{'foo': {'Clarity': [5, 5, 5, 5, 2], 'Reach': [2, 2, 9, 9]}}

example of reputee_rids
{'xyz12345': 'foo', 'xyz12344': 'foo', 'xyz12343': 'foo', 'xyz12342': 'foo', 'xyz12341': 'foo', 'xyz12346': 'foo', 'xyz12347': 'foo', 'xyz12348': 'foo', 'xyz12349': 'foo'}

example of reputee_calculated
{'foo': {'reputee': 'foo', 'clout': {'score': 0.16499999999999998, 'confidence': 0.125}, 'reach': {'score': 5.5, 'confidence': 0.5}, 'clarity': {'score': 4.4, 'confidence': 0.125}}}
"""

