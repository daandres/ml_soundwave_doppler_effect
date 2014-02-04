
import dataUtil as d

def loadRaw(path = ["../data/gesture_0.txt"]):
    if type(path) == str:
        path = [path]
    dp = d.DataUtil()
    return dp.loadRaw3DArray(path)

def loadData(path = ["../data/gesture_0.txt"]):
    dp = d.DataUtil()
    data = loadRaw(path)
    data = dp.reduceBins(data)
    data = dp.normalize(data)
    data = dp.normalizeBound(data)
    data = dp.cutRelevantAction(data)
    data = dp.round(data)
    data = dp.cutBad(data)
    #data = dp.cutPeak(data)
    return data

def loadSplitData(path = ["../data/gesture_0.txt"]):
    dp = d.DataUtil()
    data = loadData(path)
    return dp.splitData(data)