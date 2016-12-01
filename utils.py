"""
This file doesn't have anything to do with the Lake arch as far as I can tell.
"""


scores = (3.47,
4.66,
4.47,
4.90,
4.32,
4.88,
4.75,
4.52,
4.58,
4.46,
2.90,
4.17,
4.70)

def mean(listOfNumbers):
    theSum = 0
    for item in listOfNumbers:
        theSum = theSum + item
    theMean = theSum / len(listOfNumbers)
    return theMean

mean(scores)
