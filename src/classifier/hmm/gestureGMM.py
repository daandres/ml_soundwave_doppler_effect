import numpy as np
from sklearn.hmm import GMMHMM
from sklearn.mixture import GMM
import string
from numpy.random import RandomState
import util as u

class GestureGMM(GMM):
    def __init__(self, n_components=1, covariance_type='diag',
                 random_state=None, thresh=1e-2, min_covar=1e-3,
                 n_iter=1000, n_init=1, params='stwmc', init_params='stwmc'):
        
#         if random_state == None:
#             random_state = random_state = RandomState([1, 3, 5, 7, 11, 13])
#             
        GMM.__init__(self, n_components, covariance_type,
                 random_state, thresh, min_covar,
                 n_iter, n_init, params, init_params)
        

if __name__ == "__main__":
    print "#### START ####"
    h = GMM()
    print "hello"
    hmm = GestureGMM()
    print "hello"
    data = u.loadData(["../data/gesture_0.txt"])
    
    hmm.fit(data[0])
    hmm.score(data[0])
    print "#### END ####"