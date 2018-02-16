import sys
import os
import falcon

from math import ceil
from collections import deque
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from src.Reputation.Resource import calculations as cal

"""
This script is written to be run from the command line like this:
python3 calcTests.py
"""


def sFunctionTest():

    assert cal.sFunction(1,2,3) == 0
    assert cal.sFunction(9,3,4) == 1
    assert cal.sFunction(5,2,6) == 0.875
    assert cal.sFunction(5,5,6) == 0
    assert cal.sFunction(3,2,4) == 0.5
    assert cal.sFunction(4,2,4) == 1
    assert cal.sFunction(3,2,6) == 0.125
    assert cal.sFunction(15,4,20) == 0.8046875
    assert cal.sFunction(25,1,51) == 0.4608
    assert cal.sFunction(26,1,51) == 0.5
    assert cal.sFunction(27,1,51) == 0.5392
    assert cal.sFunction(10,1,51) == 0.0648
    assert cal.sFunction(40,1,51) == 0.9032

    print("sFunction() functioning properly")


def findScoreTest():

    sList0 = []
    sList1 = [1]
    sList2 = [1,2]
    sList3 = [1,2,3]
    sList4 = [1,2,3,4]

    assert cal.findScore(sList0) == 0
    assert cal.findScore(sList1) == 1
    assert cal.findScore(sList2) == 1.5
    assert cal.findScore(sList3) == 2
    assert cal.findScore(sList4) == 2.5


    print("findScore() functioning properly")


def findConfTest():

    type0 = 0
    type1 = 1
    cList0 = []
    cList1 = [0]
    cList2 = [0,0]
    cList3 = [0,0,0]
    cList4 = [0,0,0,0]
    cList5 = [0,0,0,0,0]
    cList6 = [0,0,0,0,0,0]
    cList7 = [0,0,0,0,0,0,0]
    cList8 = [0,0,0,0,0,0,0,0]

    assert cal.findConfidence(cList0, type0) == 0
    assert cal.findConfidence(cList1, type0) == 0
    assert cal.findConfidence(cList2, type0) == 0
    assert cal.findConfidence(cList3, type0) == 0.125
    assert cal.findConfidence(cList4, type0) == 0.5
    assert cal.findConfidence(cList5, type0) == 0.875
    assert cal.findConfidence(cList6, type0) == 1

    assert cal.findConfidence(cList0, type1) == 0
    assert cal.findConfidence(cList1, type1) == 0
    assert cal.findConfidence(cList2, type1) == 0
    assert cal.findConfidence(cList5, type1) == 0.125
    assert cal.findConfidence(cList6, type1) == 0.5
    assert cal.findConfidence(cList7, type1) == 0.875
    assert cal.findConfidence(cList8, type1) == 1

    print("findConfidence() functioning properly")


def findClScoreTest():

    assert cal.findCloutScore(0,0,0,0) == 0
    assert cal.findCloutScore(2,2,2,2) == 0.4
    assert cal.findCloutScore(1,1,1,1) == 0.1
    assert cal.findCloutScore(2,4,1,3) == 0.55
    assert cal.findCloutScore(3,6,4,5) == 1.9

    print("findCloutScore() functioning properly")


def findClConfTest():

    assert cal.findCloutConfidence(0,0) == 0
    assert cal.findCloutConfidence(2,2) == 2
    assert cal.findCloutConfidence(2,5) == 2
    assert cal.findCloutConfidence(5,2) == 2  
    assert cal.findCloutConfidence(21,9) == 9

    print("findCloutConfidence() functioning properly")

"""
def calScoresTest():

  repName0 = "foo"
  repName1 = "bar"
  repName2 = "foobar"
  repName3 = "fubar"

  scores0 = {'foo': {'Clarity': [5, 5, 5, 5, 2], 'Reach': [2, 2, 9, 9]}}
  scores1 = {'bar': {'Clarity': [7, 9, 1, 3], 'Reach': [3, 1, 4, 8, 5]}}
  scores2 = {'foobar': {'Clarity': [], 'Reach': [5, 5, 9, 9, 7, 7]}}
  scores3 = {'fubar': {'Clarity': [5, 5, 9, 9, 7, 7]}}

  testScore0 = cal.calculateScores(scores0, repName0)
  testScore1 = cal.calculateScores(scores1, repName1)
  testScore2 = cal.calculateScores(scores2, repName2)
  testScore3 = cal.calculateScores(scores3, repName3)

  assert ceil(testScore0["clout"]["score"] * 1000) == 165
  assert testScore0["clout"]["confidence"] == 0.125
  assert testScore0["reach"]["score"] == 5.5
  assert testScore0["reach"]["confidence"] == 0.5
  assert testScore0["clarity"]["score"] == 4.4
  assert testScore0["clarity"]["confidence"] == 0.125

  assert ceil(testScore1["clout"]["score"] * 1000) == 184
  assert testScore1["clout"]["confidence"] == 0
  assert testScore1["reach"]["score"] == 4.2
  assert testScore1["reach"]["confidence"] == 0.875
  assert testScore1["clarity"]["score"] == 5.0
  assert testScore1["clarity"]["confidence"] == 0

  assert testScore2["clarity"]["score"] == 0
  assert testScore3["message"] != 0

  print("calculateScores() functioning properly")
"""


def runCalcTests():
    sFunctionTest()
    findScoreTest()
    findConfTest()
    findClScoreTest()
    findClConfTest()
    #calScoresTest()

runCalcTests()
