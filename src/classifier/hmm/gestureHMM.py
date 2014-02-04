import numpy as np
from sklearn.hmm import GMMHMM
import string

import config.config as c
import util.util as u

import numpy as np
from sklearn.mixture import GMM



class GestureHMM(GMMHMM):
    def __init__(self, n_components=1, n_mix=1, startprob=None, transmat=None,
                 startprob_prior=None, transmat_prior=None,
                 algorithm="viterbi", gmms=None, covariance_type='diag',
                 covars_prior=1e-2, random_state=None, n_iter=10, thresh=1e-2,
                 params=string.ascii_letters,
                 init_params=string.ascii_letters):

        GMMHMM.__init__(self, n_components, n_mix, startprob, transmat,
                 startprob_prior, transmat_prior,
                 algorithm, gmms, covariance_type,
                 covars_prior, random_state, n_iter, thresh,
                 params, init_params)
        

if __name__ == "__main__":
    print "#### START ####"
    h = GMMHMM()
    hmm = GestureHMM()
    data = u.loadData(["../data/gesture_0.txt"])
    
    hmm.fit(data)
    hmm.score(data[0])
    print "#### END ####"