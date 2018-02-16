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

console = getConsole()


@doify('ReputationProcessReputation', ioinits=odict(test=""))
def reputationProcessReputation(self, **kwa):
    if dbing.gDbEnv:
        dt = datetime.datetime.now(tz=datetime.timezone.utc)
        stamp = int(dt.timestamp() * 1000000)
        date = timing.iso8601(dt, aware=True)

        console.verbose("Updating reputation at '{}'\n".format(date))

        try:
            entries = dbing.repGetEntries(dbName='unprocessed')
        except dbing.DatabaseError as exception:
            console.terse("Error processing reputation. {}".format(exception))

        if len(entries) > 0:
            for entry in entries:
                result = getAll(entry['reputee'], dbing.repGetEntries())
                if result != False:
                    ser = json.dumps({"reputee": entry['reputee'], "clout": {
                        "score": result[0],
                        "confidence": result[1]}, "reach": {
                        "score": result[2],
                        "confidence": result[3]}, "clarity": {
                        "score": result[4],
                        "confidence": result[5]}})
                    try:
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
