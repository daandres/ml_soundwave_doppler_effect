import numpy as np

from classifier.hmm.gestureHMM import GestureHMM
from gmmUtil import GMM_Util
import classifier.hmm.config.config as c
import sys



class HMM_Util:
    ''' util class for training hmms '''
    
    
    def __init__(self):
        self.ggmm = GMM_Util()

    def _averageScore(self, model, test):
        ''' build average model score with test data ''' 
        
        problist = []
        for t in test:
            problist.append(model.score(t))
        return np.average(problist)
    
    def _createGMMS(self, obs):
        ''' create gmms for hmm '''
        
        self.ggmm = GMM_Util()
        return self.ggmm.trainGmms(obs)
    
    def buildModel(self, obs, test):
        ''' building hmm model '''
        logprob = -sys.maxint - 1
        model = None

        i = 0
        while logprob < c.logprobBound:
            ### init HMM instance ###
            gmms = self._createGMMS(obs)
            #gmms = None
            m = GestureHMM(c.n_components, n_mix=c.n_mix, gmms=gmms, covariance_type=c.covariance_type, algorithm=c.algorithm, n_iter=c.n_iter, params='', thresh=1e-4)
            ### fit the model ###        
            m = m.fit(obs)
            l = self._averageScore(m, test)
            if 0 > l > logprob:
                logprob = l
                model = m
            i += 1
            if i >= c.n_tries:
                break
        print "states: " + str(c.n_components) + "\tlikeli: " + str(round(logprob, 2))
        return model, logprob
