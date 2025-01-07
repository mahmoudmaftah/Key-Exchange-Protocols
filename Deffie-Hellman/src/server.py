# server.py
import os
import time
from dh import generate_dh_parameters, serialize_parameters, generate_keys, serialize_public_key, deserialize_public_key, compute_shared_secret, derive_symmetric_key, encrypt_message, decrypt_message

# Step 1: Generate DH parameters
parameters = generate_dh_parameters()

# Step 2: Serialize and save DH parameters to a file
parameters_bytes = serialize_parameters(parameters)
with open("dh_parameters.pem", "wb") as f:
    f.write(parameters_bytes)

# Step 3: Generate server's private and public keys
server_private_key, server_public_key = generate_keys(parameters)

# Step 4: Serialize server's public key and save it to a file
server_public_key_bytes = serialize_public_key(server_public_key)
with open("server_public_key.pem", "wb") as f:
    f.write(server_public_key_bytes)

print("Server: Public key saved to server_public_key.pem")

# Step 5: Wait for the client's public key to be available
print("Server: Waiting for client's public key...")
while not os.path.exists("client_public_key.pem"):
    time.sleep(1)  # Wait for 1 second before checking again

# Step 6: Read the client's public key from the file
with open("client_public_key.pem", "rb") as f:
    client_public_key_bytes = f.read()
client_public_key = deserialize_public_key(client_public_key_bytes)

# Step 7: Compute shared secret
server_shared_secret = compute_shared_secret(server_private_key, client_public_key, parameters.parameter_numbers().p)

# Step 8: Derive symmetric key
server_symmetric_key = derive_symmetric_key(server_shared_secret)

# Step 9: Secure messaging loop
print("Server: Secure messaging started. Type 'exit' to quit.")
while True:
    # Wait for an encrypted message from the client
    if os.path.exists("client_message.enc"):
        with open("client_message.enc", "rb") as f:
            encrypted_message = f.read()
        os.remove("client_message.enc")  # Delete the message file after reading

        # Decrypt the message
        decrypted_message = decrypt_message(server_symmetric_key, encrypted_message)
        print(f"Client: {decrypted_message}")

        # Check if the client wants to exit
        if decrypted_message.lower() == "exit":
            print("Server: Client has exited. Shutting down...")
            break

    # Send a response to the client
    message = input("Server: Enter your message: ")
    if message.lower() == "exit":
        print("Server: Exiting...")
        break

    # Encrypt the message
    encrypted_message = encrypt_message(server_symmetric_key, message)
    with open("server_message.enc", "wb") as f:
        f.write(encrypted_message)

    print("Server: Message sent. Waiting for client response...")