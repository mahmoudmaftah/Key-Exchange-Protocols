


def trial_division(n):
    """
    This function returns a list of all prime factors of the input number n
    """
    factors = []
    i = 2
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            factors.append(i)
    if n > 1:
        factors.append(n)
    return factors


# test
if __name__ == "__main__":
    print(trial_division(11934243))