import math

from math import gcd

def is_power(n):
    """
    Check if a number is a perfect power.
    :param n: The number to check.
    :return: True if n is a perfect power, False otherwise.
    """
    for b in range(2, int(math.log2(n)) + 1):
        a = int(n ** (1 / b))
        if a ** b == n:
            return True
    return False

def aks_primality_test(n):
    """
    AKS Primality Test
    :param n: The number to test for primality.
    :return: True if n is prime, False otherwise.
    """
    if n <= 1:
        return False
    if n <= 3:
        return True
    if is_power(n):
        return False
    r = 2
    max_r = int(n ** 0.5) + 1
    while r < max_r:
        if gcd(n, r) > 1:
            break
        r += 1
    for a in range(1, min(n, r)):
        if pow(a, n, n) != a % n:
            return False
    return True
