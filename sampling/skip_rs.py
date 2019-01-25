import numpy as np

# magic number used by Vitter in determining when to use
# Algorithm X over Algorithm Z
UPPERCASE_T = 22.0

class SkipRS:
    w = None
    n = None

    def __init__(self, n):
        self.n = float(n)
        self.w = np.exp(-np.log(np.random.rand()) / n)


    def apply(self, t):
        if self.is_threshold_reached(t):
            S, W = algorithm_z(t, self.n, self.w)
            self.w = W
            return S
        else:
            return algorithm_x(t, self.n)


    def is_threshold_reached(self, t):
        return t > UPPERCASE_T * self.n


def algorithm_x(t, n):
    """
    Calculates the number of records to skip using Vitter's Algorithm X.

    :param t: The number of records seen
    :param n: The size of the sample
    :type t: int
    :type n: float
    :returns: S, the number of records to skip
    :rtype: int
    """
    V = np.random.rand()
    S = 0
    t = t + 1

    # num = t - n always in Vitter's pseudocode
    # as Algorithm X is only used to process
    # records in the interval [n, T*n] sequentially
    quot = (t - n) / float(t)

    while quot > V:
        S = S + 1
        t = t + 1
        quot = quot * ((t - n) / float(t))

    return S


def algorithm_z(t, n, w):
    """
    Calculates the number of records to be skipped with Vitter's Algorithm Z.

    :param t: The number of records seen
    :param n: The size of the sample
    :param w: The initial state of the random variable W
    :type t: int
    :type n: float
    :type w: float
    :returns: the number of records to skip S and a new value for W
    :rtype: (int, float)
    """
    S = 0
    W = w

    term = t - n + 1

    while True:
        U = np.random.rand()
        X = t * (W - 1.)
        S = int(X)

        # Test in U <= h(S)/cg(X) in the manner of (6.3)
        tmp = (t + 1) / term
        lhs = np.exp(np.log(((U * tmp * tmp) * (term + S)) / float(t + X)) / n)
        rhs = (((t + X) / (term + S)) * term) / float(t)

        if lhs <= rhs:
            W = rhs / lhs
            break

        # Test if U <= f(S)/cg(X)
        y = (((U * (t + 1)) / term) * (t + S + 1)) / float(t + X)

        if n < S:
            denom = t
            numer_lim = int(term) + S
        else:
            denom = t - n + S
            numer_lim = t + 1

        for numer in range(t + S, numer_lim - 1, -1):
            y = (y * numer) / float(denom)
            denom = denom - 1

        # generate W in advance 
        W = np.exp(-np.log(np.random.rand()) / n)

        if np.exp(np.log(y) / n) <= (t + X) / float(t):
            break

    return S, W
