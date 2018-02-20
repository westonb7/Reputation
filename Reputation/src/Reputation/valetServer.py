import sys
import os
import falcon

from collections import deque

from ioflo.aid import odict
from ioflo.aio.http import Valet
from ioflo.base import doify
from ioflo.aid import getConsole
from ioflo.aid.sixing import *

from Resource import resource
from Resource import priming

console = getConsole()

# This file defines behaviors run by the main.flo script which control the server

@doify('ValetServerOpen', ioinits=odict(
                                        valet="",
                                        port=odict(ival=8000),
                                        dbDirPath="",
                                        keepDirPath="",
                                        test="",
                                        preload="",
                                        fakeHidKind=odict(ival=False),
                                        ))
def valetServerOpen(self, buffer=False, **kwa):
    if buffer:
        wlog = WireLog(buffify=True, same=True)
        result = wlog.reopen()
    else:
        wlog = None

    port = int(self.port.value)
    app = falcon.API()
    resource.loadResource(app, store=self.store)

    test = True if self.test.value else False  # use to load test environment
    preload = True if self.preload.value else False  # load test db if test and True
    wlog = None

    prime = priming.setup()

    #self.dbDirPath.value = dbing.gDbDirPath
    #self.keepDirPath.value = keeping.gKeepDirPath

    self.valet.value = Valet(
                            port=port,
                            bufsize=131072,
                            wlog=wlog,
                            store=self.store,
                            app=app,
                            timeout=0.5,
                            )

    result = self.valet.value.servant.reopen()
    if not result:
        console.terse("Error opening server '{0}' at '{1}'\n".format(
                            self.valet.name,
                            self.valet.value.servant.ha))
        return


    console.concise("Opened server '{0}' at '{1}'\n".format(
                            self.valet.name,
                            self.valet.value.servant.ha,))


@doify('ValetServerService',ioinits=odict(valet=""))
def valetServerService(self, **kwa):
    if self.valet.value:
        self.valet.value.serviceAll()


@doify('ValetServerClose', ioinits=odict(valet="",))
def valetServerClose(self, **kwa):
    if self.valet.value:
        self.valet.value.servant.closeAll()

        console.concise("Closed server '{0}' at '{1}'\n".format(
                            self.valet.name,
                            self.valet.value.servant.eha))

