# Reputation

This project is for a reputation system. This reputation system takes json POST and GET requests, containing information on 'Reach' or 'Clarity' scores for a single entity, and stores the information in a database. A microthread then processes the data and calculates information returned on a GET request.

## Getting started

This reputation system is run on python3, and requires falcon, ioflo, lmdb, and libnacl to be installed. If you are running on a windows OS, you may require some additional steps or libraries to set up and run this project.

### Prerequisites

As mentioned above, this project requires python3, falcon, ioflo, lmdb, and libnacl to run. If you're using OSX, these can all be installed using homebrew. If any of these are already installed, these steps can be skipped. These can be installed in a few different ways, but for this readme, I'll be using Homebrew to perform the installations.

To install Homebrew, this command can be run from the command line:

`/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"`

Verify that Homebrew was installed correctly. You can get more information on thw installation of Homebrew using the command:

`brew doctor`

If there were issues with Homebrew's installation, this command should show the warnings.
Set usr/local/bin to occur before usr/bin

`echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bash_profile`

Install python3 with Homebrew

`brew install python3`

Install Falcon. This can be done using pip3 from the command line like so:

`pip3 install falcon`

The documentation for falcon also suggests installing ipython:

`pip3 install ipython`

Next, ioflo needs to be installed:

`pip3 install ioflo`

Next, install lmdb:

`pip3 install lmdb`

And finally, libnacl:

`pip3 install libnacl`

Httpie isn't necessary for this app to run, but it's handy to have for testing, and can be installed with this command:

`pip3 install httpie`

### Installing

The project files can be downloaded from GitHub here: `https://github.com/westonb7/Reputation`

## Testing

The testing scripts for this project can be found in the /Reputation/unitTesting/ directory of the project. The tests can be run by navigating to this directory and running them from the command line using `python3` (or just `python` if python3 is the only python installation). Each of the testing scripts can be run individually if you are interested in one specific aspect of the code, or all of the tests can be run together all at once using the testAll.py script.

### Running the tests

To run all the tests at once, navigate to the /Reputation/unitTesting/ directory in the terminal, and run this command:

`python3 testAll.py`

To run any of the tests individually, navigate to the /Reputation/unitTesting/ directory in the terminal, and run the testing script of innterest using the python3 command:

```
python3 calcTests.py
python3 helpTests.py
python3 primeTests.py
```

If a testing script has run successfully, there should be messages similar to the following:

`Prime test setup funcitoning properly.`

Otherwise, the console should print an error message if there's something wrong.

I'll be adding more testing scripts later.

## Usage

This project can be run from the command line by navigating to the /Reputation/src/Reputation/ directory, and running the following command:

`python3 app.py -f ./flo/main.flo -v concise`

If python3 is the only installation of python, then `python` can be used in place of `python3`. This command will start the program running, and it will accept POST and GET requests. This can be tested using HTTPIE from the command line. Two examples of a POST request using HTTPIE are as follows:

```
http --json POST localhost:8000/resource test:='{"reputer":"name", "reputee":"foo", "repute":{"rid":"xyz12345", "feature":"Clarity", "value":"5"}}'

http --json POST localhost:8000/resource test:='{"reputer":"name", "reputee":"foo", "repute":{"rid":"xyz12346", "feature":"Reach", "value":"5"}}'
```

Where the reputer name ("name" in this example), and the reputee name ("foo") can be changed to the proper information. The data in the repute can also be changed, where the "rid" must be a unique string, "feature" must be either "Clarity", or "Reach", and "value" must be an integer.

If successful, there should be a message similar to this:

```
Parsed Request:
POST /resource (1, 1)
lodict([('host', 'localhost:8000'), ('user-agent', 'HTTPie/0.9.9'), ('accept-encoding', 'gzip, deflate'), ('accept', 'application/json, */*'), ('connection', 'keep-alive'), ('content-type', 'application/json'), ('content-length', '112')])
bytearray(b'{"test": {"reputer": "name", "reputee": "foo", "repute": {"rid": "xyz12349", "feature": "Reach", "value": "9"}}}')
```

An example of a GET request using HTTPIE is:

`http localhost:8000/resource?name=foo`

Where "name" must be equal to the name of a reputee whose information has previously been entered into the database as part of a POST request. 
 
