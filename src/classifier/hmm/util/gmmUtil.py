import numpy as np
from gestureGMM import GestureGMM
import config.config as c

import util as u


class GMM_Util():
    '''
    class for training gmms
    
    n_components  = Number of mixture components
    
    n_iter        = Number of EM iterations to perform.
    
    n_init        = Number of initializations to perform. the best results is kept

    '''
    
    
    def __init__(self, n_components = c.n_components_gmm, covariance_type=c.covariance_type_gmm, n_iter = c.n_iter_gmm, n_init = c.n_init_gmm):
        self.n_components = n_components
        self.covariance_type = covariance_type
        self.n_iter = n_iter
        self.n_init = n_init
        self._gmms = []


    def trainGmms(self, data):
        '''
        returns trained gmms
        
        data    = np.arry-like: 
        data     :  [ 
        gesture  :    [
        frames   :      [ 0, 1, 2, 3, ... , n_bin], #0
                        [ 0, 1, 2, 3, ... , n_bin], #1
                        ...
                        [ 0, 1, 2, 3, ... , n_bin] #i_frame
                      ],
                      [
                        [ 0, 1, 2, 3, ... , n_bin], #0
                        [ 0, 1, 2, 3, ... , n_bin], #1
                        ...
                        [ 0, 1, 2, 3, ... , n_bin] #i_frame
                      ]
                    ]
        '''
        n_frames = len(data[0])
        cData = self._convertData(data)
        for i in range(n_frames):
            gmm = GestureGMM(self.n_components, covariance_type=self.covariance_type, init_params='wmc', n_iter=self.n_iter, n_init=self.n_init)
            gmm.fit(cData[i])
            self._gmms.append(gmm)
        return self._gmms

    def testGmms(self, data):
        '''
        tests given gmms
        '''
        
        n_frames = len(data[0])
        cData = self._convertData(data)
        means = []
        for i in range(n_frames):
            means.append(np.mean(self._gmms[i].score(cData[i])))
        return means

    # DATA
    def _convertData(self, data):
        '''
        returns converted data 
        
        returns    = np.arry-like: 
        data     :  [ 
        class    :    [
        frames   :      [ 0, 1, 2, 3, ... , n_bin], #0
                        [ 0, 1, 2, 3, ... , n_bin], #0
                        ...
                        [ 0, 1, 2, 3, ... , n_bin]  #0
                      ],
                      [
                        [ 0, 1, 2, 3, ... , n_bin], #1
                        [ 0, 1, 2, 3, ... , n_bin], #1
                        ...
                        [ 0, 1, 2, 3, ... , n_bin]  #1
                      ]
                    ]
        
        
        '''
        n_frames = len(data[0])
        cData = [[] for i in range(n_frames)]
        for i in range(n_frames):
            for gesture in data:
                cData[i].append(list(gesture[i]))
        return np.array(cData)


    def sample(self, dataPath = None, data=None):
        if data == None:
            if dataPath==None:
                data = u.loadData()
            else:
                data = u.loadData(dataPath)
        self.trainGmms(data)
        print np.shape(data)
        return self._gmms
    


if __name__ == "__main__":
    mg = GMM_Util()
    
    print "train"
    data = u.loadData(["../data/gesture_0.txt"])
    gmms = mg.trainGmms(data)

    print "0"
    print mg.testGmms(data)
    
    print "5"
    data = u.loadData(["../data/gesture_5.txt"])
    print mg.testGmms(data)
    
    print "clean"
    data = u.loadData(["../data/clean.txt"])
    print mg.testGmms(data)
