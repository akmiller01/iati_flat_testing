import random
import math

answer = random.randint(0,1000)
print("The correct answer is %s" % answer)

def response(j):
    return [] if j<=answer else 500

def outputVerbose(output):
    return "Invalid" if output==500 else "Valid"


lastPos = 1000
curPos = lastPos/2
lastOutput = 500
def recursiveSearch(curPos,lastPos,lastOutput):
    output = response(curPos)
    delta = int(math.ceil(abs((curPos-lastPos)/2)))
    #Stopped moving with valid output
    if (curPos-lastPos)==0 and output!=500:
        return curPos
    #Last move was from invalid to valid with a delta of 1
    elif lastOutput == 500 and output != 500 and abs(curPos-lastPos)==1:
        return curPos
    elif delta==0:
        delta = 1
    lastPos = curPos
    print("Guess: {} is {}, moving by {}".format(curPos,outputVerbose(output),delta))
    if output==500:
        curPos -= delta
        return recursiveSearch(curPos,lastPos,lastOutput)
    else:
        curPos += delta
        return recursiveSearch(curPos,lastPos,lastOutput)
        
guess = recursiveSearch(curPos,lastPos,lastOutput)
print("Guessed answer: {}".format(guess))
    
    