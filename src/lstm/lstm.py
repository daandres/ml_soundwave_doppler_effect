from pybrain.tools.shortcuts import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.datasets import SequenceClassificationDataSet
from pybrain.structure import SigmoidLayer
from pybrain.structure import LSTMLayer

import itertools
import numpy as np

