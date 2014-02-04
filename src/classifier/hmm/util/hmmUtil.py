import numpy as np

from classifier.hmm.gestureHMM import GestureHMM
from gmmUtil import GMM_Util
import classifier.hmm.config.config as c
import sys



class HMM_Util:
    def __init__(self):
        self.ggmm = GMM_Util()

    def printModels(self, models):
        for model in models.values():
            self.printModel(model)
    
    def printModel(self, model):
        if model == None:
            print "no model found"
        else:
            print model
            print "Transition matrix"
            print model.transmat_
            print model.gmms_
            
    #         print("means and vars of each hidden state")
    #         for i in range(model.n_components):
    #             print("%dth hidden state" % i)
    #             #print("mean = ", model.means_[i])
    #             print("var = ", np.diag(model.covars_[i]))
    #             print()
    
    def _averageScore(self, model, test):
        problist = []
        for t in test:
            problist.append(model.score(t))
        return np.average(problist)

    def _averageDecode(self, model, test):
        declist = []
        for t in test:
            declist.append(model.decode(t)[0])
        return np.average(declist)
    
    def _createGMMS(self, obs):
        self.ggmm = GMM_Util()
        return self.ggmm.trainGmms(obs)
    
    def buildModel(self, obs, test):
        logprob = -sys.maxint - 1
        model = None

        for cov_type in c.covariance_type:
            print "cov_type: " + cov_type
            for algo in c.algorithm:
                print "  algo: " + algo
                for i in range(c.n_tries):
                    ### init HMM instance ###
                    gmms = self._createGMMS(obs)
                    m = GestureHMM(c.n_components, n_mix=c.n_mix, gmms=gmms, covariance_type=cov_type, algorithm=algo, n_iter=c.n_iter, params='stmc', thresh=1e-4)
                    ### fit the model ###        
                    m = m.fit(obs)
                    l = self._averageScore(m, test)
                    d = self._averageDecode(m, test)
                    print "    " + str(i+1) + ") "+ str(l)
                    if 0 > l > logprob:
                        logprob = l
                        model = m
        print "8==D~~ states: " + str(c.n_components) + "\tlikeli: " + str(round(logprob, 2))
        return model, logprob
    
    def setModelType(self, modelType):
        self.modelType = modelType
