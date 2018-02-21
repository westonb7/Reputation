import falcon
import ioflo.app.run

from valetServer import *
from Resource.resource import Resource
from Resource import helping
from Resource import behaving

# This is the "main" file for this project

api = application = falcon.API()

resource = Resource()
api.add_route('/resource', resource)

# To run the app use this command on the terminal command line:
# python3 app.py -f ./flo/main.flo -v concise  

def mainRun():
    #from reputation import __version__
    args = ioflo.app.run.parseArgs(version="0.1.3")

    ioflo.app.run.run(  name=args.name,
                        period=float(args.period),
                        real=args.realtime,
                        retro=args.retrograde,
                        filepath=args.filename,
                        behaviors=args.behaviors,
                        mode=args.parsemode,
                        username=args.username,
                        password=args.password,
                        verbose=args.verbose,
                        consolepath=args.console,
                        statistics=args.statistics )

mainRun()
