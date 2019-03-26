import numpy as np

# The alpha value used in Vitter's "An efficient algorithm for sequential
# random sampling" was 1/13
ALPHA_INV = 13

def draw_V_prime(coefficient):
    return np.exp(np.log(np.random.rand()) * coefficient)


def skip_records(n, N):
    """
    Returns the number of records S to skip before selecting the next record.

    :param n: The number of records to be selected out of the pool.
    :param N: The total number of records to choose from.
    :type n: int
    :type N: int
    :returns: S, the number of records to skip
    :rtype: int
    """

    V_prime = draw_V_prime(1 / float(n))

    threshold = n * ALPHA_INV

    S = N

    if (n > 1):
        if (threshold < N):
            S, = algorithm_D(n, N, V_prime)
        else:
            S = algorithm_A(n, N)
    elif (n == 1):
        S = int(N * V_prime)

    return S
        


def algorithm_A(n, N):
    top = N - n
    N_real = float(N)

    V = np.random.rand()
    S = 0

    quot = (N - n) / N_real

    while quot > V:
        S += 1
        top -= 1
        N_real -= 1

        quot *= top / N_real

    return S



def algorithm_D(n, N, V_prime)
    n_inv = 1 / float(n)
    n_min1_inv = 1 / float(n - 1)

    qu1 = N - n + 1

    while True:
        while True:
            X = N * (1 - V_prime)
            S = int(X)

            if S < qu1:
                break

            V_prime = draw_V_prime(n_inv)

        U = np.random.rand()

        y1 = np.exp(np.log(U * N / float(qu1)) * n_min1_inv)

        V_prime = y1 * (- X / float(N + 1)) * (qu1 / float(qu1 - S))

        if V_prime <= 1:
            break

        y2 = 1
        top = N - 1

        if n - 1 > S:
            bottom = float(N - n)
            limit = N - S
        else:
            bottom = float(N - S - 1)
            limit = qu1

        for t in range(N - 1, limit - 1, -1):
            y2 *= top / bottom
            top -= 1
            bottom -= 1

        if N / float(N - X) >= y1 * np.exp(np.log(y2) * n_min1_inv):
            V_prime = draw_V_prime(n_min1_inv)
            break

        V_prime = draw_V_prime(n_inv)

    return S, V_prime
