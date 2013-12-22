from pybrain.tools.customxml.networkwriter import NetworkWriter
from pybrain.tools.customxml.networkreader import NetworkReader
from pybrain.datasets import SequenceClassificationDataSet
import numpy as np
from src.gestureFileIO import GestureFileIO
import time

def save(net, ds, filename=""):
    if filename == "":
        filename = time.time()[:-3]
    NetworkWriter.writeToFile(net, filename + '.xml')
    print "networked saved in ", filename + '.xml'
    if ds is not None:
        ds.saveToFile(filename + '.data')
    print "dataset saved in ", filename + '.data'
    return


def load_network(filename=""):
    if filename == "":
        raise Exception("No network loaded because no network name provided")
    net = NetworkReader.readFrom(filename + '.xml')
    print "networked loaded from ", filename + '.xml'
    return net

def load_dataset(filename=""):
    if filename == "":
        raise Exception("No dataset loaded because no network name provided")
    ds = SequenceClassificationDataSet.loadFromFile(filename + '.data')
    print "dataset loaded from ", filename + '.data'
    return ds

def load(filename):
    return load_network(filename), load_dataset(filename)


def getTrainingSet(classes, inputs, outputs, filename, createNew=False, save=False, relative=""):
    ds = None
    if createNew:
        ds = createPyBrainDatasetFromSamples(classes, inputs, outputs, save, filename, relative)
    else:
        ds = load_dataset(relative + filename)
    return ds

def createPyBrainDatasetFromSamples(classes, inputs, outputs, save=False, filename=None, relative=""):
#         np.set_printoptions(precision=2, threshold=np.nan)
    nClasses = len(classes)
    g = GestureFileIO(relative=relative)
    data = [0] * 8
    for i in classes:
        data[i] = g.getGesture3D(i, [])
        print "data ", i, " loaded shape: ", np.shape(data[i])
    print "data loaded, now creating dataset"
    ds = SequenceClassificationDataSet(inputs, outputs, nb_classes=nClasses)
    for target in classes:
        tupt = getTarget(target, outputs)
        for x in data[target]:
            ds.newSequence()
            for y in x:
                tup = tuple(y)
                ds.appendLinked(tup, tupt)
    print "DS entries" , ds.getNumSequences()
    if save:
        ds.saveToFile(relative + filename)
    return ds

def getTarget(y, dim):
    if y >= dim:
        raise Exception("wrong dimension chosen for target")
    elif y < 0:
        raise Exception("target is negative")
    assert(y >= 0 and y < dim)
    target = np.zeros((dim,))
    target[y] = 1
    return target


