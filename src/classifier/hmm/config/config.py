n_tries = 10

covariance_type=['tied'] #String describing the type of covariance parameters used by the model. Must be one of 'spherical', 'tied', 'diag', 'full'. 
algorithm=['viterbi']#, 'map']
n_components=13 # Number of states in the model.
n_iter=5 # Number of iterations to perform.


covariance_type_gmm='tied'
n_iter_gmm=5
n_components_gmm=8
n_mix=n_components
n_init_gmm =5
algorithm_gmm='viterbi'

dataNames = ["ppasler", "Alex", "Benjamin", "Daniel"]
