from math import ceil, sqrt

def modular_inverse(a, p):
    """Compute the modular inverse of a modulo p using Fermat's Little Theorem."""
    return pow(a, p-2, p)

def shanks_algorithm(g, h, p):
    """
    Solves the discrete logarithm problem g^x ≡ h mod p using Shanks' Baby-Step Giant-Step algorithm.
    Returns x if found, otherwise returns None.
    """
    n = p - 1  # Assume g is a primitive root modulo p
    m = ceil(sqrt(n))

    # Precompute baby steps: g^j mod p for j = 0, 1, ..., m-1
    baby_steps = {}
    current = 1
    for j in range(m):
        baby_steps[current] = j
        current = (current * g) % p

    # Compute g^{-m} mod p
    g_inv_m = modular_inverse(pow(g, m, p), p)

    # Compute giant steps: h * (g^{-m})^i mod p for i = 0, 1, ..., m-1
    current = h
    for i in range(m):
        if current in baby_steps:
            j = baby_steps[current]
            x = i * m + j
            return x
        current = (current * g_inv_m) % p

    # If no solution is found
    return None

# Example usage
if __name__ == "__main__":
    g = 2
    h = 9
    p = 23

    x = shanks_algorithm(g, h, p)
    if x is not None:
        print(f"Discrete logarithm: {x}")  # Output: x such that 2^x ≡ 9 mod 23
    else:
        print("No solution found.")