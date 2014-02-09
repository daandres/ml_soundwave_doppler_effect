'''
Util methods for LSTM Classes.
'''

from pybrain.tools.customxml.networkwriter import NetworkWriter
from pybrain.tools.customxml.networkreader import NetworkReader
from pybrain.datasets import SequenceClassificationDataSet
from pybrain.supervised.trainers import RPropMinusTrainer, BackpropTrainer
from pybrain.optimization import GA, HillClimber, MemeticSearch, NelderMead, CMAES, OriginalNES, ES, MultiObjectiveGA
import numpy as np
from gestureFileIO import GestureFileIO
import properties.config as c
import time
'''
saves network to file. If no name is provided current timestamp is used
'''
def save_network(net, filename=""):
    if filename == "":
        filename = time.time()[:-3]
    NetworkWriter.writeToFile(net, filename + '.xml')
    print("networked saved in " + filename + '.xml')
    return

'''
Saves training- and testset to files. If no name is provided current timestamp is used
'''
def save_dataset(ds, testds, filename=""):
    if filename == "":
        filename = time.time()[:-3]
    ds.saveToFile(filename + '.data', format='pickle', protocol=0)
    print("dataset saved in " + filename + '.data')
    testds.saveToFile(filename + '_test.data', format='pickle', protocol=0)
    print("testdataset saved in " + filename + '_test.data')
    return

'''
Loads a network from file
'''
def load_network(filename=""):
    if filename == "":
        raise Exception("No network loaded because no network name provided")
    net = NetworkReader.readFrom(filename + '.xml')
    print("networked loaded from " + filename + '.xml')
    return net

'''
loads a dataset from file. Trainingset and Testsset have to exist
'''
def load_dataset(filename=""):
    if filename == "":
        raise Exception("No dataset loaded because no network name provided")
    ds = SequenceClassificationDataSet.loadFromFile(filename + '.data')
    print("dataset loaded from " + filename + '.data')
    testds = SequenceClassificationDataSet.loadFromFile(filename + '_test.data')
    print("testdataset loaded from " + filename + '_test.data')
    return ds, testds

'''
parses a network filename for variables
'''
def parseNetworkFilename(filename):
    filename = filename.split('/')
    filename = filename[-1]
    components = filename.split("_")
    netValues = {}
    for comp in components:
        if(comp[0] == "n"):
            netValues['neurons'] = comp[1:]
        elif(comp[0] == "l"):
            netValues['layer'] = comp[1:]
        elif(comp[0] == "p"):
            netValues['peepholes'] = comp[1:]
        elif(comp[0] == "o"):
            netValues['nclasses'] = comp[1:]
        elif(comp[0] == "c"):
            netValues['datacut'] = comp[1:]
        elif(comp[0] == "f"):
            netValues['datafold'] = comp[1:]
        elif(comp[0] == "t"):
            netValues['trainer'] = comp[1:]
        elif(comp[0] == "e"):
            netValues['epochs'] = comp[1:]
    return netValues

'''
Loads data from sample files, preprocesses data and creates a PyBrain DataSet
'''
def createPyBrainDatasetFromSamples(classes, outputs, relative="", average="false", merge67="false", cut=0, fold=1):
    def __loadDataFromFile(merge67="false"):
        gesturepath = c.getInstance().getPathsConfig()['gesturepath']
        g = GestureFileIO(gesturePath=gesturepath, relative=relative)
        data = [0] * nClasses
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
        return data



    def __createDataset(data):
        ds = SequenceClassificationDataSet(inputs, 1, nb_classes=nClasses, class_labels=labels.values())
        for target in classes:
            tupt = np.asarray([target])
    #         print("Target " + str(tupt))
            for x in data[target]:
                ds.newSequence()
                for y in x:
                    tup = tuple(y)
                    ds.appendLinked(tup, tupt)
        print(ds.calculateStatistics())
#         ds._convertToOneOfMany(bounds=[0, 1])
    #     print ds.getField('target')
        print("DS entries " + str(ds.getNumSequences()))
        return ds

    labels = {0:'Right-To-Left-One-Hand',
          1:'Top-to-Bottom-One-Hand',
          2:'Entgegengesetzt with two hands',
          3:'Single-push with one hand',
          4:'Double-push with one hand',
          5:'Rotate one hand',
          6:'Background silent',
          7:'Background loud'}

    nClasses = len(classes)
    data = __loadDataFromFile(merge67)
    for i in range(len(data)):
        data[i] = preprocessData(data[i], cut, fold)
    inputs = np.shape(data[0])[2]
    ds = __createDataset(data)
    return ds

'''
reduces dimensions of data as this is still representative enough
First cutting on each size 'cut' elements and then folds each 'fold' elements together.
---
@Deprecated (not used as tests have shown noise rduction reduces classification performance)
removes a noise from the quadratic value by setting to zero
'''
def preprocessData(data, cut, fold):
    # cut 'cut' datapoints from each side
    if(cut != 0):
        data = data[:, :, cut:-cut]
    # folds each 'fold' datapoints
    newData = np.zeros((data.shape[0], data.shape[1], np.ceil(data.shape[2] / fold)))
    for i in range(fold):
        newData += data[:, :, i::fold]
#     data = data[:, :, ::select]
    # remove noise
#     for i in range(len(data)):
#         temp = data[i] ** 2
#         cond = np.where(temp <= removeNoiseTreshold)
#         data[i][cond] = 0
    return newData

'''
same as preprocessData but only for a single frame 
'''
def preprocessFrame(frame, cut, fold):
    # cut 'cut' datapoints from each side
    if(cut != 0):
        frame = frame[cut:-cut]
    # folds each 'fold' datapoints
    newFrame = np.zeros((np.ceil(frame.shape[0] / fold)))
    for i in range(fold):
        newFrame += frame[i::fold]
#     frame = frame[::select]
    return newFrame

'''
Calculates average frequency 
# TODO aktuelle Ruhe Frequenz messen und davon average nehmen.
'''
avg = None
def getAverage(cut, fold):
    global avg
    # Use this if reaults are too bad by creating avg on demand with recorded gestures
    # the avg from all gestures isn't correct anymore -> hardcoded avg
    #     avg = [ 0.01405917,  0.01451394,  0.01501277,  0.01552741,  0.01608232,  0.0166838,
    #   0.017318,    0.01801043,  0.01876477,  0.01958107,  0.02046903,  0.02144034,
    #   0.02251206,  0.02370547,  0.02503494,  0.02651884,  0.02819135,  0.03008983,
    #   0.03227148,  0.03479038,  0.03773177,  0.04122532,  0.04543961,  0.05061085,
    #   0.05710018,  0.06553213,  0.07690142,  0.09310018,  0.11811639,  0.16215195,
    #   0.26233294,  0.83321468,  0.99991455,  0.4672319,   0.2171238,   0.1442126,
    #   0.10842227,  0.08702495,  0.07270665,  0.06246511,  0.0547552,   0.04876873,
    #   0.04395861,  0.03999377,  0.03669765,  0.03390901,  0.03149998,  0.02941618,
    #   0.02760306,  0.02599722,  0.02456548,  0.02327461,  0.02212122,  0.02108119,
    #   0.02013257,  0.01926706,  0.01846762,  0.01773872,  0.01707368,  0.01645111,
    #   0.01586561,  0.0153235,   0.01481276,  0.01433922]

    if avg == None:
        gesturepath = c.getInstance().getPathsConfig()['gesturepath']
        g = GestureFileIO(gesturePath=gesturepath)
        avg = g.getAvgFrequency()
        avg = preprocessFrame(avg, cut, fold)
    return avg

'''
Goes through a network and prints each module Name, each connection and each weight in a pretty format
'''
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

'''
returns Gradient Training Algorithm by Name
'''
def getGradientTrainAlgo(method="rprop"):
    if(method == "rprop"):
        return RPropMinusTrainer
    elif(method == "backprop"):
        return BackpropTrainer
    else:
        raise Exception("No train Alog specified")

'''
returns Optimzation Training Algorithm by Name
'''
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

'''
Creates NumPy Array with shape = (dim,) and containing only 6's
'''
def createArraySix(dim):
    array = np.zeros((dim,))
    for i in range(dim):
        array[i] = 6
    return array
