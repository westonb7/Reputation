from __future__ import generator_stop

import sys
import os

from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from pytest import approx
from src.Reputation.Resource.db import dbing
from src.Reputation.Resource.helping import (setupTmpBaseDir, cleanupTmpBaseDir, getAll)
from src.Reputation.Resource import priming

from src.Reputation.Resource import calculations as cal

import pytest

try:
    import ujson as json
except ImportError:
    import json

def testGetAll():
    entries = []
    result = getAll("foo", entries)
    assert result is False

    entries = [{
      "reputer": "testName",
      "reputee": "foo",
      "repute":
      {
        "rid" : "xyz123451",
        "feature": "reach",
        "value": 4
      }
    },
    {
      "reputer": "testName",
      "reputee": "foo",
      "repute":
      {
        "rid": "xyz123452",
        "feature": "reach",
        "value": 5
      }
    },
    {
      "reputer": "testName",
      "reputee": "foo",
      "repute":
      {
        "rid": "xyz123453",
        "feature": "reach",
        "value": 6
      }
    },
    {
      "reputer": "testName",
      "reputee": "foo",
      "repute":
        {
          "rid": "xyz123454",
          "feature": "clarity",
          "value": 7
        }
    },
    {
    "reputer": "testName",
    "reputee": "foo",
    "repute":
      {
        "rid": "xyz123455",
        "feature": "clarity",
        "value": 8
      }
    },
    {
    "reputer": "testName",
    "reputee": "foo",
    "repute":
      {
        "rid": "xyz123456",
        "feature": "clarity",
        "value": 9
      }
    }
    ]

    result = getAll("foo", entries)

    assert result[0] == (0.03125)
    assert result[1] == (0)
    assert result[2] == (5.0)
    assert result[3] == (0.125)
    assert result[4] == (8.0)
    assert result[5] == (0)

    print ("getAll() functioning properly.")

def runHelpTests():
  testGetAll()

runHelpTests()

