from sklearn.mixture import GMM

class GestureGMM(GMM):
    ''' wrapper for sklearn.mixture.GMM '''
    
    def __init__(self, n_components=1, covariance_type='diag',
                 random_state=None, thresh=1e-2, min_covar=1e-3,
                 n_iter=1000, n_init=1, params='', init_params=''):
        
        GMM.__init__(self, n_components, covariance_type,
                 random_state, thresh, min_covar,
                 n_iter, n_init, params, init_params)