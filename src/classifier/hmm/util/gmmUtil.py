import numpy as np
import classifier.hmm.config.config as c

from classifier.hmm.gestureGMM import GestureGMM

class GMM_Util():
    ''' util class for training gmms '''
    
    
    def __init__(self):
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
                        [ 0, 1, 2, 3, ... , n_bin] #n_frame
                      ],
                      [
                        [ 0, 1, 2, 3, ... , n_bin], #0
                        [ 0, 1, 2, 3, ... , n_bin], #1
                        ...
                        [ 0, 1, 2, 3, ... , n_bin] #n_frame
                      ]
                    ]
        '''
        n_frames = len(data[0])
        cData = self._convertData(data)
        for i in range(n_frames):
            self._gmms.append(self._train(cData[i]))
        return self._gmms

    def _averageScore(self, gmm, test):
        return np.average(gmm.score(test))

    def _train(self, data):
        gmm = GestureGMM(c.n_components_gmm, covariance_type=c.covariance_type_gmm, init_params='', n_iter=c.n_iter_gmm, n_init=c.n_init_gmm)
        gmm.fit(data)
        l = self._averageScore(gmm, data)
        return gmm
        

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


    def sample(self, data):
        self.trainGmms(data)
        return self._gmms