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

## Define a function to calculate score, can be used for either reach or clarity

def findScore(score_list):
    avg = 0
    total = len(score_list)
    if total <= 0:
        return 0
    for val in score_list:
        avg += val
    return (avg/total)  

## Define a function to calculate confidence, can be used for reach or clarity

def findConfidence(conf_list, type):
    total = len(conf_list)
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

def findCloutScore(reach_s, reach_c, clarity_s, clarity_c):
    clout_s = 0.0       ## Declare a float to prevent integer coecion problems
    clout_s = (((reach_s*reach_c) + (clarity_s*clarity_c)) / 2.0) / 10.0
    return clout_s


def findCloutConfidence(reach_c, clarity_c):
    return min(reach_c, clarity_c)

## Define function to calculate scores and confidences for reach, clarity, and clout

def calculateScores(reputee_scores, reputee):
    error_message = {
        'message':'Missing reach or clarity data for this reputee'
    }
    if "Reach" in reputee_scores[reputee]:
        reach_s = findScore(reputee_scores[reputee]["Reach"])
        reach_c = findConfidence(reputee_scores[reputee]["Reach"], 0) 
    else:
        return error_message

    if "Clarity" in reputee_scores[reputee]:
        clarity_s = findScore(reputee_scores[reputee]["Clarity"])
        clarity_c = findConfidence(reputee_scores[reputee]["Clarity"], 1)
    else:
        return error_message

    clout_s = findCloutScore(reach_s, reach_c, clarity_s, clarity_c)
    clout_c = findCloutConfidence(reach_c, clarity_c)

    return_obj = {
        'reputee':reputee,
        'clout':{ 'score':clout_s, 'confidence':clout_c },
        'reach':{ 'score':reach_s, 'confidence':reach_c },
        'clarity':{ 'score':clarity_s, 'confidence':clarity_c }
    }

    return return_obj
