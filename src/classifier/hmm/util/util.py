
import dataUtil as d
from numpy.testing.decorators import deprecated

dp = d.DataUtil()

def loadRaw(gesture):
    return dp.loadRaw3dGesture(gesture)

def preprocessData(data):
    data = dp.reduceBins(data)
    data = dp.normalize(data)
    data = dp.normalizeBound(data)
    data = dp.cutRelevantAction(data)
    data = dp.round(data)
    #data = dp.cutBad(data)
    #data = dp.cutPeak(data)
    return data

def loadData(gesture):
    data= dp.loadRaw3dGesture(gesture)
    data = preprocessData(data)
    return data

def splitData(data):
    return dp.splitData(data)

def loadSplitData(gesture):
    data = loadData(gesture)
    return dp.splitData(data)