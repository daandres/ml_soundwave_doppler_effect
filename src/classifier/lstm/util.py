# Install PyBrain 0.3.1 or greater from https://github.com/pybrain/pybrain
from pybrain.tools.customxml.networkwriter import NetworkWriter
from pybrain.tools.customxml.networkreader import NetworkReader
from pybrain.datasets import SequenceClassificationDataSet
from pybrain.supervised.trainers import RPropMinusTrainer, BackpropTrainer
    # Optimization learners imports
from pybrain.optimization import *  # @UnusedWildImport

import numpy as np
from gestureFileIO import GestureFileIO
import time

def save(net, ds, filename=""):
    save_network(net, filename)
    save_dataset(ds, filename)
    return

def save_network(net, filename=""):
    if filename == "":
        filename = time.time()[:-3]
    NetworkWriter.writeToFile(net, filename + '.xml')
    print("networked saved in " + filename + '.xml')
    return

def save_dataset(ds, filename=""):
    if filename == "":
        filename = time.time()[:-3]
    ds.saveToFile(filename + '.data')
    print("dataset saved in " + filename + '.data')
    return

def load_network(filename=""):
    if filename == "":
        raise Exception("No network loaded because no network name provided")
    net = NetworkReader.readFrom(filename + '.xml')
    print("networked loaded from " + filename + '.xml')
    return net

def parseNetworkFilename(filename):
    components = filename.split("_")
    netValues = {}
    for comp in components:
        if(comp[0] == "n" and comp[1] == "C"):
            netValues['nclasses'] = comp[2:]
        elif(comp[0] == "n"):
            netValues['neurons'] = comp[1:]
        elif(comp[0] == "e"):
            netValues['epochs'] = comp[1:]
        elif(comp[0] == "l"):
            netValues['layer'] = comp[1:]
        elif(comp[0] == "o"):
            netValues['outneurons'] = comp[1:]
        elif(comp[0] == "t"):
            netValues['trainer'] = comp[1:]
    return netValues

def load_dataset(filename=""):
    if filename == "":
        raise Exception("No dataset loaded because no network name provided")
    ds = SequenceClassificationDataSet.loadFromFile(filename + '.data')
    print("dataset loaded from " + filename + '.data')
    return ds

def load(filename):
    return load_network(filename), load_dataset(filename)

def createPyBrainDatasetFromSamples(classes, inputs, outputs, relative="", average="false", merge67="false"):
#         np.set_printoptions(precision=2, threshold=np.nan)
    labels = {0:'Right-To-Left-One-Hand',
              1:'Top-to-Bottom-One-Hand',
              2:'Entgegengesetzt with two hands',
              3:'Single-push with one hand',
              4:'Double-push with one hand',
              5:'Rotate one hand',
              6:'Background silent',
              7:'Background loud'}
    nClasses = len(classes)
    g = GestureFileIO(relative=relative)
    data = [0] * 8
    getData = None
    if(average == "false"):
        getData = g.getGesture3DNormalized
    else:
        getData = g.getGesture3DDiffAvg
    if(merge67 == "true"):
        merge67 = True
    else:
        merge67 = False
    for i in classes:
        data[i] = getData(i, [], merge67)
        if(i == 6 and merge67):
            data7 = getData(7, [], merge67)
            data[i] = np.append(data[i], data7, axis=0)
        print("data " + str(i) + " loaded shape: " + str(np.shape(data[i])))
    print("data loaded, now creating dataset")
    ds = SequenceClassificationDataSet(inputs, outputs, nb_classes=nClasses, class_labels=labels.values())
    for target in classes:
        tupt = getTarget(target, outputs)
        print("Target " + str(tupt))
        for x in data[target]:
            ds.newSequence()
            for y in x:
                tup = tuple(y)
                ds.appendLinked(tup, tupt)
    print("DS entries " + str(ds.getNumSequences()))
    return ds

def getTarget(y, dim):
    if(dim == 1):
        target = np.zeros((dim,))
        target[0] = y
        return target
    if y >= dim:
        raise Exception("wrong dimension chosen for target")
    elif y < 0:
        raise Exception("target is negative")
    assert(y >= 0 and y < dim)
    target = np.zeros((dim,))
    target[y] = 1
    return target

# Average frequency
# TODO aktuelle Ruhe Frequenz messen und davon average nehmen.
avg = None
def getAverage():
    global avg
    if avg == None:
        g = GestureFileIO()
        avg = g.getAvgFrequency()
    return avg

def printNetwork(net):
    for mod in net.modules:
        print("Module: " + str(mod.name))
        if mod.paramdim > 0:
            print("\t--parameters: " + str(mod.params))
        for conn in net.connections[mod]:
            print("\t-connection to " + str(conn.outmod.name))
            if conn.paramdim > 0:
                print("\t\t- parameters" + str(conn.params))
    if hasattr(net, "recurrentConns"):
        print("Recurrent connections")
        for conn in net.recurrentConns:
            print("\t-" + str(conn.inmod.name) + " to " + str(conn.outmod.name))
            if conn.paramdim > 0:
                print("\t\t- parameters " + str(conn.params))


def getGradientTrainAlgo(method="rprop"):
    if(method == "rprop"):
        return RPropMinusTrainer
    elif(method == "backprop"):
        return BackpropTrainer
    else:
        raise Exception("No train Alog specified")

def getOptimizationTrainAlgo(method="GA"):
    if(method == "GA"):
        return GA
    elif(method == "HillClimber"):
        return HillClimber
    elif(method == "MemeticSearch"):
        return MemeticSearch
    elif(method == "NelderMead"):
        return NelderMead
    elif(method == "CMAES"):
        return CMAES
    elif(method == "OriginalNES"):
        return OriginalNES
    elif(method == "ES"):
        return ES
    elif(method == "MultiObjectiveGA"):
        return MultiObjectiveGA
    else:
        raise Exception("No train Alog specified")


def createArraySix(dim):
    array = np.zeros((dim,))
    for i in range(dim):
        array[i] = 6
    return array
