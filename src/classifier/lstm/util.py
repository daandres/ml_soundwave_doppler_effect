# Install PyBrain 0.3.1 or greater from https://github.com/pybrain/pybrain
from pybrain.tools.customxml.networkwriter import NetworkWriter
from pybrain.tools.customxml.networkreader import NetworkReader
from pybrain.datasets import SequenceClassificationDataSet
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

def load_dataset(filename=""):
    if filename == "":
        raise Exception("No dataset loaded because no network name provided")
    ds = SequenceClassificationDataSet.loadFromFile(filename + '.data')
    print("dataset loaded from " + filename + '.data')
    return ds

def load(filename):
    return load_network(filename), load_dataset(filename)

def createPyBrainDatasetFromSamples(classes, inputs, outputs, relative="", average="false"):
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
    for i in classes:
        data[i] = getData(i, [])
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
