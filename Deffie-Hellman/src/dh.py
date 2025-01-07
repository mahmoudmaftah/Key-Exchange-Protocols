# dh.py
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os
import random

# Generate DH parameters (prime p and generator g)
def generate_dh_parameters():
    # Use the cryptography library to generate a safe prime p and generator g
    parameters = dh.generate_parameters(generator=2, key_size=2048)
    return parameters

# Serialize DH parameters for sharing
def serialize_parameters(parameters):
    return parameters.parameter_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.ParameterFormat.PKCS3
    )

# Deserialize DH parameters
def deserialize_parameters(parameters_bytes):
    return serialization.load_pem_parameters(parameters_bytes)

# Generate private and public keys
def generate_keys(parameters):
    # Generate a private key (a random number)
    private_key = random.randint(2, parameters.parameter_numbers().p - 2)
    # Compute the public key: g^a mod p
    public_key = pow(parameters.parameter_numbers().g, private_key, parameters.parameter_numbers().p)
    return private_key, public_key

# Serialize public key for transmission
def serialize_public_key(public_key):
    # Convert the public key to bytes
    return public_key.to_bytes((public_key.bit_length() + 7) // 8, byteorder='big')

# Deserialize public key after receiving it
def deserialize_public_key(public_key_bytes):
    # Convert bytes back to an integer
    return int.from_bytes(public_key_bytes, byteorder='big')

# Compute shared secret
def compute_shared_secret(private_key, peer_public_key, p):
    # Compute the shared secret: (peer_public_key)^a mod p
    return pow(peer_public_key, private_key, p)

# Derive symmetric key from shared secret
def derive_symmetric_key(shared_secret):
    # Use HKDF to derive a 32-byte key for AES-256
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b'handshake data',
    )
    return hkdf.derive(shared_secret.to_bytes((shared_secret.bit_length() + 7) // 8, byteorder='big'))

# Encrypt a message using AES-256
def encrypt_message(key, message):
    iv = os.urandom(16)  # Generate a random initialization vector
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(message.encode()) + encryptor.finalize()
    return iv + ciphertext  # Return IV + ciphertext

# Decrypt a message using AES-256
def decrypt_message(key, ciphertext):
    iv = ciphertext[:16]  # Extract the IV from the beginning of the ciphertext
    ciphertext = ciphertext[16:]  # Extract the actual ciphertext
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv))
    decryptor = cipher.decryptor()
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return plaintext.decode()