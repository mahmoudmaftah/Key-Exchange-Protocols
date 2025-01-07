from cryptography.hazmat.primitives.asymmetric import dh

# Generate DH parameters
parameters = dh.generate_parameters(generator=2, key_size=2048)

# Generate private and public keys for Alice
alice_private_key = parameters.generate_private_key()
alice_public_key = alice_private_key.public_key()

# Generate private and public keys for Bob
bob_private_key = parameters.generate_private_key()
bob_public_key = bob_private_key.public_key()

# Compute shared secret
alice_shared_secret = alice_private_key.exchange(bob_public_key)
bob_shared_secret = bob_private_key.exchange(alice_public_key)

# Verify that both shared secrets match
assert alice_shared_secret == bob_shared_secret
print("Shared secret successfully computed!")