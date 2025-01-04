import random

def is_prime(n, k=10):
    """
    Miller-Rabin primality test to check if a number is prime.
    :param n: The number to check for primality.
    :param k: Number of iterations for accuracy.
    :return: True if n is probably prime, False otherwise.
    """
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False

    # Write n-1 as 2^r * d
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2

    # Miller-Rabin test
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)  # Compute a^d % n
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def generate_large_prime(bits):
    """
    Generate a large prime number with the specified number of bits.
    :param bits: The bit-length of the prime number.
    :return: A large prime number.
    """
    while True:
        candidate = random.getrandbits(bits) | (1 << bits - 1) | 1
        if is_prime(candidate):
            return candidate


# Example: Generate a 1024-bit prime number
if __name__ == "__main__":
    prime = generate_large_prime(1024)
    print(f"Generated Prime: {prime}")
