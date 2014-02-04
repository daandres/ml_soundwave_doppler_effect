
import dataUtil as d
from numpy.testing.decorators import deprecated


def loadRaw(gesture):
    dp = d.DataUtil()
    return dp.loadRaw3dGesture(gesture)

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