n_tries = 5

covariance_type=['tied'] #String describing the type of covariance parameters used by the model. Must be one of 'spherical', 'tied', 'diag', 'full'. 
algorithm=['viterbi']#, 'map']
n_components=13 # Number of states in the model.
n_iter=10 # Number of iterations to perform.


covariance_type_gmm='tied'
n_iter_gmm=10
n_components_gmm=4
n_mix=n_components
n_init_gmm = 5
algorithm_gmm='viterbi'