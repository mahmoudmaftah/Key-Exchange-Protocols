# Project Title

## Introduction and Background

### How to Check if a Large Number is Prime

- **Trial Division**  
  The most straightforward approach: test divisibility by all primes (or all odd numbers) up to the square root of the target number. This method is simple but inefficient for very large integers.

- **Fermat's Little Theorem**  
  Exploits the property \(a^{p-1} \equiv 1 \pmod{p}\) for prime \(p\). While faster than trial division, it can be tricked by Carmichael numbers, giving false positives.

- **Miller-Rabin Primality Test**  
  A probabilistic test used extensively in cryptography. It quickly determines if a number is *probably prime* or *definitely composite*. Repeated rounds (higher \(k\)) reduce the probability of error.

- **AKS Primality Test**  
  A deterministic polynomial-time test. It is mathematically significant for proving that primality can be checked in polynomial time, though often slower in practice compared to Miller-Rabin for cryptographic sizes.

- **Lucas-Lehmer Primality Test**  
  Specialized for Mersenne primes (numbers of the form \(2^p - 1\)). Very efficient if you need to specifically test Mersenne candidates.

### How to Factorize a Large Number

- **Trial Division**  
  Again, a brute-force approach checking divisibility up to \(\sqrt{n}\).

- **Pollard's Rho Algorithm**  
  A faster randomized method for factorization. Works well for numbers with small prime factors.

- **Fermat’s Factorization Method**  
  Leverages the representation of an odd integer \(n\) as a difference of two squares. Most useful when the two factors are close to each other.

- **Quadratic Sieve**  
  One of the fastest classical factorization algorithms for general integers (before the General Number Field Sieve takes over for very large numbers).

### How to Generate Large Prime Numbers

- **Random Selection + Primality Testing**  
  The common practical approach: pick a random number in the desired bit range, then test it with a fast primality check (e.g., Miller-Rabin). Keep trying until you find a prime.

### Efficient Modular Exponentiation

Modular exponentiation \((a^b \mod m)\) can be computed efficiently using the exponentiation by squaring algorithm (also known as binary exponentiation). This is crucial for cryptosystems like RSA and Diffie-Hellman, where large powers modulo some number are computed frequently.

## Overview of Key Exchange Protocols

- **Diffie-Hellman Key Exchange**  
  Allows two parties to establish a shared secret over an insecure channel. Based on the hardness of the discrete logarithm problem.


- **Elliptic Curve Diffie-Hellman (ECDH)**  
  A variant of Diffie-Hellman using elliptic curve cryptography, providing similar security with smaller keys, making it more efficient in many contexts.

## Overview of Public Key Infrastructure

- **Role of PKI**  
  Ensures trustworthy key distribution and certificate management. PKI defines protocols, services, and standards that facilitate the creation, issuance, management, and revocation of digital certificates.

- **Digital Certificates**  
  Bind a public key with an identity, typically signed by a trusted entity. Used in TLS/SSL, code signing, secure email, etc.

- **Certificate Authorities (CAs)**  
  Trusted third-party organizations (or servers) that sign certificates, vouching for the binding between a public key and an entity’s identity.

- **Registration Authorities (RAs)**  
  Entities responsible for verifying the identity of a certificate requestor before forwarding it to a CA.

- **Certificate Revocation Lists (CRLs)**  
  A list maintained by a CA of revoked certificates that are no longer valid. This helps prevent compromised keys from being used.

---

## Benchmarks

In addition to these theoretical foundations, we conducted **several benchmarks** to measure performance and scalability:

1. **Prime Generation with Varying Key Sizes**  
   - We compare the time needed to generate primes of different bit lengths (e.g., 256, 512, 1024).  
   - The plot shows how the number of primes generated grows over time, illustrating that larger key sizes require more computational effort.

2. **Time to Generate a Random Prime**  
   - We measure how long it takes, on average, to generate one prime for each bit length.  
   - This benchmark highlights the impact of key size on immediate prime generation tasks (e.g., for ephemeral keys).

These benchmarks help developers and cryptography enthusiasts understand the trade-offs between security (larger key sizes) and performance (time to generate and factor).

---

## Live Testing of a Certificate Authority

We have deployed a website where users can **test out a simple Certificate Authority (CA)** process online, request certificates, and explore how these are validated. 
Feel free to try it here:

***[**Certificate Authority Demo**](https://certificateauthority.pythonanywhere.com/strict/)***

This platform demonstrates:
- Generating a certificate signing request (CSR).
- Submitting it to the CA.
- Verifying the issued certificate.



---

**Thank you for exploring our project!** We hope this provides insight into large integer arithmetic, prime generation, and the essentials of modern cryptographic infrastructures.
