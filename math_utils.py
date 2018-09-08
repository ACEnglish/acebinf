"""
Math/Stats helpers
"""
import math

#{{{ http://code.activestate.com/recipes/511478/ (r1)
# pylint: disable=invalid-name


def percentile(N, percent):
    """
    Find the percentile of a list of values.

    @parameter N - is a list of values.
    @parameter percent - a float value from 0.0 to 1.0.

    @return - the percentile of the values
    """
    N.sort()
    if not N:
        return None
    k = (len(N) - 1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return N[int(k)]
    d0 = N[int(f)] * (c - k)
    d1 = N[int(c)] * (k - f)
    return d0 + d1
# median is 50th percentile.
# end of http://code.activestate.com/recipes/511478/ }}}


def phi(x):
    """
    phi functino is the cumulative density function (CDF) of a standard normal (Gaussian) random variable. It is closely
    related to the error function erf(x).
    https://www.johndcook.com/erf_and_normal_cdf.pdf
    From:
        https://www.johndcook.com/blog/python_phi/
    """
    # constants
    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911

    # Save the sign of x
    sign = 1
    if x < 0:
        sign = -1
    x = abs(x) / math.sqrt(2.0)

    # A&S formula 7.1.26
    t = 1.0 / (1.0 + p * x)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x)

    return 0.5 * (1.0 + sign * y)


def p_obs(obs, mean, sd, two_tailed=True):
    """
    Calculate p-value of an observation given an estmated mean and std
    """
    x = (obs - mean) / sd
    if two_tailed:
        return 2 * (1 - phi(abs(x)))
    return 1 - phi(abs(x))
