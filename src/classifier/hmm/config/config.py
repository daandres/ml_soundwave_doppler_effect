### CLASSIFICATOR ###

classificator = 0

if classificator == 0:                      # use hmm for default gestures
    classList = [0, 1, 2, 4, 6, 7]    # classes to be trained and classified
    names = ["paul", "ppasler", "Sebastian", "Daniel", "Benjamin"]                            # datanames to train from
    trainedModel = "allGestures"
elif classificator == 1:
    classList = [0, 1, 5, 6, 7]             # classes to be trained and classified
    names = ["paul"]                        # datanames to train from
    trainedModel = "hmmGestures"

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
covariance_type_gmm='tied'
n_iter_gmm=5                           
n_components_gmm=8                      # Number mixture components 
n_mix=components                        # Number of frames
n_init_gmm = 1


### TRAIN HMM ###
n_tries = 1
covariance_type='tied'                  # String describing the type of covariance parameters used by the model. Must be one of 'spherical', 'tied', 'diag', 'full'. 
algorithm='viterbi'                     # 'map'
n_components=components                 # Number of frames
n_iter=10                               # Number of iterations to perform.
logprobBound = -100

### Live Classification ###
classificationTreshhold = 0.05          # Percantage (0.1 = 10%)






