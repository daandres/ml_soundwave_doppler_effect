# http://stackoverflow.com/questions/12689293/event-sequences-recurrent-neural-networks-pybrain
from pybrain.tools.shortcuts import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.datasets import SequenceClassificationDataSet
from pybrain.structure import SigmoidLayer
from pybrain.structure import LSTMLayer

import itertools
import numpy as np

data = np.loadtxt("example_sales").T
print(data)

datain = data[:-1, :]
dataout = data[1:, :]

INPUTS = 32
OUTPUTS = 32
HIDDEN = 350

def validate(ds, net):
    confmat = np.zeros((OUTPUTS, OUTPUTS))
    for i in range(ds.getNumSequences()):
        net.reset()
        out = None
        target = None
        j = 0
        for dataIter in ds.getSequenceIterator(i):
            data = dataIter[0]
            target = dataIter[1]
            print(str(i) + "\t" + str(j) + "\tbefore activate")
            out = net.activate(data)
            print(str(i) + "\t" + str(j) + "\tafter activate")
            j += 1
        confmat[np.argmax(target)][np.argmax(out)] += 1
    sumWrong = 0
    sumAll = 0
    for i in range(OUTPUTS):
        for j in range(OUTPUTS):
            if i != j:
                sumWrong += confmat[i][j]
            sumAll += confmat[i][j]
    error = sumWrong / sumAll
    print(confmat)
    print("error: " + str(100. * error) + "%")

net = buildNetwork(INPUTS, HIDDEN, OUTPUTS, hiddenclass=LSTMLayer, outclass=SigmoidLayer, recurrent=True, outputbias=False)

ds = SequenceClassificationDataSet(INPUTS, OUTPUTS, nb_classes=OUTPUTS)

for _ in range(2000):
    ds.newSequence()
    for x, y in itertools.izip(datain, dataout):
        ds.appendLinked(tuple(x), tuple(y))

print(str(ds.getNumSequences()))
net.randomize()

trainer = BackpropTrainer(net, ds, verbose=True)


trainer.trainEpochs(1)

# net.reset()
# for i in range(ds.getNumSequences()):
#     net.reset()
#     for data in ds.getSequence(i):
#         nextact = np.argmax(net.activate(data))
#     print (nextact)
validate(ds, net)

