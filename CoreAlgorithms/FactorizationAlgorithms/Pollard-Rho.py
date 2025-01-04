import math
import random

def pollards_rho(n):
    """
    Pollard's Rho Algorithm for factorizing a number.
    :param n: The number to be factorized.
    :return: A non-trivial factor of n.
    """
    if n % 2 == 0:
        return 2
    
    # Function for generating the sequence
    def f(x):
        return (x * x + 1) % n

    x, y, d = random.randint(2, n - 1), 2, 1
    while d == 1:
        x = f(x)  # Update x
        y = f(f(y))  # Update y twice
        d = math.gcd(abs(x - y), n)  # Compute GCD
    if d == n:
        return None  # Failure, retry with a different seed
    return d


def factorize(n):
    """
    Factorizes a number using Pollard's Rho algorithm.
    :param n: The number to be factorized.
    :return: A list of factors.
    """
    factors = []
    while n > 1:
        factor = pollards_rho(n)
        if factor is None:  # Retry on failure
            continue
        factors.append(factor)
        n //= factor
    return factors


# Example: Factorizing a large number
if __name__ == "__main__":
    number = 10403  # Example: Product of 101 and 103
    factors = factorize(number)
    print(f"Factors of {number}: {factors}")
