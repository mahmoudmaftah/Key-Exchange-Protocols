

def lucas_lehmer_test(p):
    """
    Lucas-Lehmer Test for Mersenne primes.
    :param p: The exponent of the Mersenne number.
    :return: True if 2^p - 1 is prime, False otherwise.
    """
    if p == 2:
        return True
    m = 2 ** p - 1
    s = 4
    for _ in range(p - 2):
        s = (s * s - 2) % m
    return s == 0
