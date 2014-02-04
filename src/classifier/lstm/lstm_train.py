from pybrain.tools.validation import ModuleValidator, CrossValidator
import classifier.lstm.util as util
import time

class LSTMTrain:

    def __init__(self, config, net, data):
        self.config = config
        self.net = net
        self.data = data
        self.trainer, self.returnsNet = None, False


    def __getGradientTrainer(self):
        print("LSTM Gradient " + self.config['trainingalgo'] + " Training started")
        trainAlgo = util.getGradientTrainAlgo(self.config['trainingalgo'])
        trainer = trainAlgo(self.net.net, dataset=self.data.ds, verbose=True)
        return trainer, False

    def __getOptimizationTrainer(self):
        print("LSTM Optimization " + self.config['trainingalgo'] + " Training started")
        trainAlgo = util.getOptimizationTrainAlgo(self.config['trainingalgo'])
        l = trainAlgo(self.data.ds.evaluateModuleMSE, self.net.net, verbose=True)
        return l, True

    def __train(self, training, returnsNet):
        start = time.time()
        print("start training of " + str(self.net.epochs) + " epochs: " + str(start / 3600))
        print(self.net.getName())
        if(self.net.epochs >= 10):
            tenthOfEpochs = self.net.epochs / 10
            for i in range(10):
                inBetweenStart = time.time()
                if returnsNet: self.net.net = training(tenthOfEpochs)
                else: training(tenthOfEpochs)
                end = time.time()
                diff = end - inBetweenStart
                print("Training time of epoch " + str(i) + " : " + str(end / 3600) + "\nDiff: " + str(diff / 3600))
            lastEpochs = self.net.epochs - (tenthOfEpochs * 10)
        else:
            lastEpochs = self.net.epochs
        if(lastEpochs > 0):
            if returnsNet: self.net.net = training(lastEpochs)
            else: training(lastEpochs)
        end = time.time()
        diff = end - start
        self.net.trainedEpochs += self.net.epochs
        print("Training end: " + str(end / 3600) + "\nTotaldiff: " + str(diff / 3600))
        if(self.config['autosave_network'] == "true"):
            filename = self.net.getName() + "_" + str(time.time())
            self.net.save(filename, overwrite=False)
        self.data.validate()
        return

    def train(self, args):
        if(self.data.ds == None):
            print("Can't train without loaded data")
            return
        if(args != [] and len(args) >= 2):
            self.net.epochs = int(args[1])
        if(self.net.trainingType == "gradient"):
            if(self.trainer == None):
                self.trainer, self.returnsNet = self.__getGradientTrainer();
            self.__train(self.trainer.trainEpochs, self.returnsNet)
        elif(self.net.trainingType == "optimization"):
            if(self.trainer == None):
                self.trainer, self.returnsNet = self.__getOptimizationTrainer();
            self.__train(self.trainer.learn, self.returnsNet)
            return
        elif(self.trainingType == "crossval"):
            if(self.trainer == None):
                self.trainer, self.returnsNet = self.__getGradientTrainer();
            evaluation = ModuleValidator.classificationPerformance(self.trainer.module, self.data.ds)
            validator = CrossValidator(trainer=self.trainer, dataset=self.trainer.ds, n_folds=5, valfunc=evaluation, verbose=True, max_epochs=1)
            print(validator.validate())
        else:
            raise Exception("Cannot create trainer, no network type specified" + self.trainingType)
