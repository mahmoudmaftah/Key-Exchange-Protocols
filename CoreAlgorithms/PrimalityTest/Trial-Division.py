


def is_prime(n):

    """
    Trial Division Primality Test
    :param n: The number to test for primality.
    :return: True if n is prime, False otherwise.
    """

    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


# test
if __name__ == "__main__":
    # Test with 49
    # 49 is not a prime number  
    assert is_prime(49) == False