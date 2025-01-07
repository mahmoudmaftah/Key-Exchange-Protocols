def modular_exponentiation(a, b, p):
    result = 1  # Initialize result
    a = a % p  # Update a if it is more than or equal to p

    while b > 0:
        # If b is odd, multiply a with result
        if b % 2 == 1:
            result = (result * a) % p

        # b must be even now, so square a and halve b
        a = (a * a) % p
        b = b // 2

    return result

# Example usage:
if __name__ == "__main__":
    a = 2
    b = 10
    p = 1000
    print(modular_exponentiation(a, b, p))  # Output: 24 (since 2^10 % 1000 = 1024 % 1000 = 24)