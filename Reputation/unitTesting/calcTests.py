import sys
import os
import falcon

from math import ceil
from collections import deque
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from src.Reputation.Resource import calculations as cal

##########
## This script is written to be run from the command line like this:
## python3 calcTests.py
##########

def sFunctionTest():

    assert cal.s_function(1,2,3) == 0
    assert cal.s_function(9,3,4) == 1
    assert cal.s_function(5,2,6) == 0.875
    assert cal.s_function(5,5,6) == 0
    assert cal.s_function(3,2,4) == 0.5
    assert cal.s_function(4,2,4) == 1
    assert cal.s_function(3,2,6) == 0.125
    assert cal.s_function(15,4,20) == 0.8046875
    assert cal.s_function(25,1,51) == 0.4608
    assert cal.s_function(26,1,51) == 0.5
    assert cal.s_function(27,1,51) == 0.5392
    assert cal.s_function(10,1,51) == 0.0648
    assert cal.s_function(40,1,51) == 0.9032

    print("s_function() functioning properly")

def findScoreTest():

    sList0 = []
    sList1 = [1]
    sList2 = [1,2]
    sList3 = [1,2,3]
    sList4 = [1,2,3,4]

    assert cal.find_score(sList0) == 0
    assert cal.find_score(sList1) == 1
    assert cal.find_score(sList2) == 1.5
    assert cal.find_score(sList3) == 2
    assert cal.find_score(sList4) == 2.5


    print("find_score() functioning properly")

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

    assert cal.find_confidence(cList0, type0) == 0
    assert cal.find_confidence(cList1, type0) == 0
    assert cal.find_confidence(cList2, type0) == 0
    assert cal.find_confidence(cList3, type0) == 0.125
    assert cal.find_confidence(cList4, type0) == 0.5
    assert cal.find_confidence(cList5, type0) == 0.875
    assert cal.find_confidence(cList6, type0) == 1

    assert cal.find_confidence(cList0, type1) == 0
    assert cal.find_confidence(cList1, type1) == 0
    assert cal.find_confidence(cList2, type1) == 0
    assert cal.find_confidence(cList5, type1) == 0.125
    assert cal.find_confidence(cList6, type1) == 0.5
    assert cal.find_confidence(cList7, type1) == 0.875
    assert cal.find_confidence(cList8, type1) == 1

    print("find_confidence() functioning properly")

def findClScoreTest():

    assert cal.find_clout_score(0,0,0,0) == 0
    assert cal.find_clout_score(2,2,2,2) == 0.4
    assert cal.find_clout_score(1,1,1,1) == 0.1
    assert cal.find_clout_score(2,4,1,3) == 0.55
    assert cal.find_clout_score(3,6,4,5) == 1.9

    print("find_clout_score() functioning properly")

def findClConfTest():

    assert cal.find_clout_confidence(0,0) == 0
    assert cal.find_clout_confidence(2,2) == 2
    assert cal.find_clout_confidence(2,5) == 2
    assert cal.find_clout_confidence(5,2) == 2  
    assert cal.find_clout_confidence(21,9) == 9

    print("find_clout_confidence() functioning properly")

# def calScoresTest():

#   repName0 = "foo"
#   repName1 = "bar"
#   repName2 = "foobar"
#   repName3 = "fubar"

#   scores0 = {'foo': {'Clarity': [5, 5, 5, 5, 2], 'Reach': [2, 2, 9, 9]}}
#   scores1 = {'bar': {'Clarity': [7, 9, 1, 3], 'Reach': [3, 1, 4, 8, 5]}}
#   scores2 = {'foobar': {'Clarity': [], 'Reach': [5, 5, 9, 9, 7, 7]}}
#   scores3 = {'fubar': {'Clarity': [5, 5, 9, 9, 7, 7]}}

#   testScore0 = cal.calculate_scores(scores0, repName0)
#   testScore1 = cal.calculate_scores(scores1, repName1)
#   testScore2 = cal.calculate_scores(scores2, repName2)
#   testScore3 = cal.calculate_scores(scores3, repName3)

#   assert ceil(testScore0["clout"]["score"] * 1000) == 165
#   assert testScore0["clout"]["confidence"] == 0.125
#   assert testScore0["reach"]["score"] == 5.5
#   assert testScore0["reach"]["confidence"] == 0.5
#   assert testScore0["clarity"]["score"] == 4.4
#   assert testScore0["clarity"]["confidence"] == 0.125

#   assert ceil(testScore1["clout"]["score"] * 1000) == 184
#   assert testScore1["clout"]["confidence"] == 0
#   assert testScore1["reach"]["score"] == 4.2
#   assert testScore1["reach"]["confidence"] == 0.875
#   assert testScore1["clarity"]["score"] == 5.0
#   assert testScore1["clarity"]["confidence"] == 0

#   assert testScore2["clarity"]["score"] == 0
#   assert testScore3["message"] != 0

#   print("calculate_scores() functioning properly")

def runCalcTests():
    sFunctionTest()
    findScoreTest()
    findConfTest()
    findClScoreTest()
    findClConfTest()
    #calScoresTest()

runCalcTests()
