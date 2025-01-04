import random

def fermat_primality_test(n, k=10):
    """
    Fermat's Primality Test
    :param n: The number to test for primality.
    :param k: Number of iterations for accuracy.
    :return: True if n is probably prime, False otherwise.
    """
    if n <= 1:
        return False
    if n <= 3:
        return True
    for _ in range(k):
        a = random.randint(2, n - 2)
        if pow(a, n - 1, n) != 1:
            return False
    return True
