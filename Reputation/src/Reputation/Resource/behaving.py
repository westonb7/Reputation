from __future__ import generator_stop

import falcon
from .helping import *

from ioflo.aid import timing
from ioflo.aid import getConsole
from ioflo.aid.odicting import odict
from ioflo.base import doify
from .db import dbing

import datetime

try:
    import ujson as json
except ImportError:
    import json

# This file defines the behavior that processes the data from the 'unprocessed' database

console = getConsole()

@doify('ReputationProcessReputation', ioinits=odict(test=""))
def reputationProcessReputation(self, **kwa):
    if dbing.gDbEnv:

        dt = datetime.datetime.now(tz=datetime.timezone.utc)
        stamp = int(dt.timestamp() * 1000000)
        date = timing.iso8601(dt, aware=True)
        
        console.verbose("Updating reputation at '{}'\n".format(date))

        # Get the data from the 'unprocessed' database
        try:
            entries = dbing.repGetEntries(dbName='unprocessed')
        except dbing.DatabaseError as exception:
            console.terse("Error processing reputation. {}".format(exception))

        #Process the data and move the calculated scores into the 'reputation' database
        if len(entries) > 0:
            ridList = []
            #try to get ridList from db
            #try:
                #ridList = dbing.repGetTxn("ridList", dbName="reputation")
            #if ridList == None:
                #ridList = []
            for entry in entries:
                if entry['repute']['rid'] not in ridList:   #Ignore reputes with duplicate rids
                    ridList.append(entry['repute']['rid'])
                    result = getAll(entry['reputee'], dbing.repGetEntries()) 
                    #try:
                        #entryAvg = dbing.repGetTxn(entry['reputee'] + "-avg", dbName="reputation")

                    if result != False: #and entryAvg != None:
                        #newAvg = getAllRun(entry['reputee'], result, average=entryAvg)
                        #repPutTxn(entry['reputee'] + "-avg", newAvg, dbName='reputation')
                    #elif result != False:
                        #print("4")
                        ser = json.dumps({"reputee": entry['reputee'], "clout": {
                            "score": result[0],
                            "confidence": result[1]}, "reach": {
                            "score": result[2],
                            "confidence": result[3]}, "clarity": {
                            "score": result[4],
                            "confidence": result[5]}})
                        try:
                            #print("5")
                            #ridSucess = dbing.repPutTxn("ridList", ridList dbName='reputation')
                            success = dbing.repPutTxn(entry['reputee'], ser, dbName='reputation')
                        except dbing.DatabaseError as exception:
                            console.terse("Error processing reputation. {}".format(exception))
                        if not success:
                            console.terse("Error processing reputation.")

            success = dbing.repDeleteEntries()
            console.terse("Unprocessed database cleared: {}".format(str(success)))
            console.verbose("Updated reputation at '{}'\n".format(date))

        else:
            console.verbose("Updated reputation at '{}'\n".format(date))
