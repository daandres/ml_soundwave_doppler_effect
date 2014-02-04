
import dataUtil as d
from numpy.testing.decorators import deprecated


@deprecated
def loadRaw(path = ["../data/gesture_0.txt"]):
    if type(path) == str:
        path = [path]
    dp = d.DataUtil()
    return dp.loadRaw3DArray(path)

def loadData(gesture):
    dp = d.DataUtil()
    data= dp.loadRaw3dGesture(gesture)
    data = dp.reduceBins(data)
    data = dp.normalize(data)
    data = dp.normalizeBound(data)
    data = dp.cutRelevantAction(data)
    data = dp.round(data)
    data = dp.cutBad(data)
    #data = dp.cutPeak(data)
    return data

def splitData(data):
    dp = d.DataUtil()
    return dp.splitData(data)

def loadSplitData(gesture):
    dp = d.DataUtil()
    data = loadData(gesture)
    return dp.splitData(data)