import numpy as np
from sklearn.hmm import GMMHMM
from sklearn.hmm import _BaseHMM

import string

import config.config as c
import util.util as u

import numpy as np
from sklearn.mixture import GMM
from numpy.random import RandomState
from codegen import override


decoder_algorithms = ("viterbi", "map")

def logsumexp(arr, axis=0):
    """Computes the sum of arr assuming arr is in the log domain.

    Returns log(sum(exp(arr))) while minimizing the possibility of
    over/underflow.

    Examples
    --------

    >>> import numpy as np
    >>> from sklearn.utils.extmath import logsumexp
    >>> a = np.arange(10)
    >>> np.log(np.sum(np.exp(a)))
    9.4586297444267107
    >>> logsumexp(a)
    9.4586297444267107
    """
    arr = np.rollaxis(arr, axis)
    # Use the max to normalize, as with the log this is what accumulates
    # the less errors
    vmax = arr.max(axis=0)
    out = np.log(np.sum(np.exp(arr - vmax), axis=0))
    out += vmax
    return out

class GestureHMM(GMMHMM):
    def __init__(self, n_components=1, n_mix=1, startprob=None, transmat=None,
                 startprob_prior=None, transmat_prior=None,
                 algorithm="viterbi", gmms=None, covariance_type='diag',
                 covars_prior=1e-2, random_state=None, n_iter=10, thresh=1e-2,
                 params=string.ascii_letters,
                 init_params=string.ascii_letters):

        
#         if random_state == None:
#             random_state = random_state = RandomState([1, 3, 5, 7, 11, 13])
            

        GMMHMM.__init__(self, n_components, n_mix, startprob, transmat,
                 startprob_prior, transmat_prior,
                 algorithm, gmms, covariance_type,
                 covars_prior, random_state, n_iter, thresh,
                 params, init_params)

    def fit(self, obs):
        """Estimate model parameters.

        An initialization step is performed before entering the EM
        algorithm. If you want to avoid this step, pass proper
        ``init_params`` keyword argument to estimator's constructor.

        Parameters
        ----------
        obs : list
            List of array-like observation sequences (shape (n_i, n_features)).

        Notes
        -----
        In general, `logprob` should be non-decreasing unless
        aggressive pruning is used.  Decreasing `logprob` is generally
        a sign of overfitting (e.g. a covariance parameter getting too
        small).  You can fix this by getting more training data, or
        decreasing `covars_prior`.
        """

        if self.algorithm not in decoder_algorithms:
            self._algorithm = "viterbi"

        super(GMMHMM, self)._init(obs, self.init_params)

        logprob = []
        for i in range(self.n_iter):
            # Expectation step
            stats = self._initialize_sufficient_statistics()
            curr_logprob = 0
            for seq in obs:
                framelogprob = self._compute_log_likelihood(seq)
                lpr, fwdlattice = self._do_forward_pass(framelogprob)
                bwdlattice = self._do_backward_pass(framelogprob)
                gamma = fwdlattice + bwdlattice
                posteriors = np.exp(gamma.T - logsumexp(gamma, axis=1)).T
                curr_logprob += lpr
                self._accumulate_sufficient_statistics(
                    stats, seq, framelogprob, posteriors, fwdlattice,
                    bwdlattice, self.params)
            logprob.append(curr_logprob)
            #print curr_logprob

            # Check for convergence.
            if i > 0 and abs(logprob[-1] - logprob[-2]) < self.thresh:
                break

            # Maximization step
            self._do_mstep(stats, self.params)

        return self

if __name__ == "__main__":
    print "#### START ####"
    h = GMMHMM()
    hmm = GestureHMM()
    data = u.loadData(["../data/gesture_0.txt"])
    
    hmm.fit(data)
    hmm.score(data[0])
    print "#### END ####"