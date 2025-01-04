import math

def quadratic_sieve(n):
    """
    Quadratic Sieve Algorithm for factorizing a number.
    :param n: The number to be factorized.
    :return: A list of factors.
    """
    def sieve_range(n):
        """ Helper function for simple sieving """
        is_prime = [True] * (n + 1)
        p = 2
        while p * p <= n:
            if is_prime[p]:
                for i in range(p * p, n + 1, p):
                    is_prime[i] = False
            p += 1
        return [x for x in range(2, n + 1) if is_prime[x]]

    primes = sieve_range(100)  # Use small primes for sieving
    x = math.ceil(math.sqrt(n))
    for k in range(1, 1000):
        candidate = x + k
        remainder = (candidate * candidate) % n
        for prime in primes:
            if remainder % prime == 0:
                factor = math.gcd(candidate, n)
                if factor != 1 and factor != n:
                    return factor
    return None
