import math

def fermat_factorization(n):
    """
    Fermat's Factorization Method
    :param n: The number to be factorized.
    :return: A tuple of two factors (a, b).
    """
    a = math.ceil(math.sqrt(n))
    b2 = a * a - n
    while not is_perfect_square(b2):
        a += 1
        b2 = a * a - n
    b = int(math.sqrt(b2))
    return a - b, a + b

def is_perfect_square(n):
    """
    Check if a number is a perfect square.
    :param n: The number to check.
    :return: True if n is a perfect square, False otherwise.
    """
    root = int(math.sqrt(n))
    return root * root == n



if __name__ == "__main__":
    number = 10403  # Example: Product of 101 and 103
    factors = fermat_factorization(number)
    print(f"Factors of {number}: {factors}")