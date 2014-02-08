### GESTURE CLASSES '''
classList = [0, 1, 5, 6, 7]             # classes to be trained and classified
names = ["paul"]                        # datanames to train from

### DATA PREPROCESSING ###
framesTotal = 32                        # incomming frames
binsTotal = 64                          # incomming bins per frame
# cut frames
framesBefore = 7
framesAfter = 8

# cut bins
bins_before = 8
leftBorder = (binsTotal/2) - bins_before # 
bins_after = 7
rightBorder = (binsTotal/2) + bins_after


components = framesTotal                # use 1 state per frame

### TRAIN GMM ###
n_tries_gmm = 1                         
covariance_type_gmm='tied'
n_iter_gmm=10                           
n_components_gmm=4                      # representation of 
n_mix=components
n_init_gmm = 1
algorithm_gmm='viterbi'
logprobBound_gmm = -100


### TRAIN HMM ###
n_tries = 1
covariance_type=['tied']#, 'tied', 'diag', 'full'] #String describing the type of covariance parameters used by the model. Must be one of 'spherical', 'tied', 'diag', 'full'. 
algorithm=['viterbi']#, 'map']
n_components=components # Number of frames
n_iter=5 # Number of iterations to perform.
logprobBound = -100

### Live Classification ###
classificationTreshhold = 0.05          # Percantage (0.1 = 10%)






