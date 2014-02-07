n_tries = 1

covariance_type=['tied']#, 'tied', 'diag', 'full'] #String describing the type of covariance parameters used by the model. Must be one of 'spherical', 'tied', 'diag', 'full'. 
algorithm=['viterbi']#, 'map']
n_components=13 # Number of states in the model.
n_iter=5 # Number of iterations to perform.
logprobBound = -100


n_tries_gmm = 1
covariance_type_gmm='tied'
n_iter_gmm=10
n_components_gmm=2
n_mix=n_components
n_init_gmm = 1
algorithm_gmm='viterbi'
logprobBound_gmm = -100
