import falcon
from collections import defaultdict

## Define the S function described in the document:

def sFunction(x, a, b):
    c = (a+b)/2.0
    if x <= a:
        return 0
    if x > a and x <= c:
        return (2.0 * ((x-a)/(b-a))**2) 
    if x > c and x <= b:
        return (1.0 - 2.0*(((x-b)/(b-a))**2))
    if x > b:
        return 1
    return 0

def fuzzyAnd(x, y):
    return min(x,y)

def fuzzyOr(x,y):
    return max(x,y)

def fuzzyNot(x):
    return 1 - x

def compensatoryAnd(a, b, gamma=1):
    if gamma == 1:
        return a + b - a*b
    elif gamma == 0:
        return a*b
    return 0

## Define a function to calculate score, can be used for either reach or clarity

def findScore(scoreList):
    avg = 0
    total = len(scoreList)
    if total <= 0:
        return 0
    for val in scoreList:
        avg += val
    return (avg/total)  

def runningScore(avg, total):
    if total <= 0:
        return 0
    return (avg/total)

def runningConf(total, type):
    if type == 0:
        return sFunction(total, 2.0, 6.0)
    elif type == 1:
        return sFunction(total, 4.0, 8.0)
    return 0

## Define a function to calculate confidence, can be used for reach or clarity

def findConfidence(confList, type):
    total = len(confList)
    if type == "reach": ## In case someone attempts to use this function with 'reach'/'clarity' as type
        type = 0
    elif type == "clarity":
        type = 1

    if total > 0 and type == 0:
        return sFunction(total, 2.0, 6.0)  ## Using floats to prevent python from coercing values into ints
    elif total > 0 and type == 1:
        return sFunction(total, 4.0, 8.0)
    else:
        return 0

## Define function to calculate clout score

def findCloutScore(reachScore, reachConf, clarityScore, clarityConf):
    cloutScore = 0.0       ## Declare a float to prevent integer coecion problems
    cloutScore = (((reachScore*reachConf) + (clarityScore*clarityConf)) / 2.0) / 10.0
    return cloutScore


def findCloutConfidence(reachConf, clarityConf):
    return min(reachConf, clarityConf)

## Define function to calculate scores and confidences for reach, clarity, and clout

def calculateScores(reputeeScores, reputee):
    errorMessage = {
        'message':'Missing reach or clarity data for this reputee'
    }
    if "Reach" in reputeeScores[reputee]:
        reachScore = findScore(reputeeScores[reputee]["Reach"])
        reachConf = findConfidence(reputeeScores[reputee]["Reach"], 0) 
    else:
        return errorMessage

    if "Clarity" in reputeeScores[reputee]:
        clarityScore = findScore(reputeeScores[reputee]["Clarity"])
        clarityConf = findConfidence(reputeeScores[reputee]["Clarity"], 1)
    else:
        return errorMessage

    cloutScore = findCloutScore(reachScore, reachConf, clarityScore, clarityConf)
    cloutConf = findCloutConfidence(reachConf, clarityConf)

    return_obj = {
        'reputee':reputee,
        'clout':{ 'score':cloutScore, 'confidence':cloutConf },
        'reach':{ 'score':reachScore, 'confidence':reachConf },
        'clarity':{ 'score':clarityScore, 'confidence':clarityConf }
    }

    return return_obj
