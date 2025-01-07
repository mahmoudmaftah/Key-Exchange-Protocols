# client.py
import os
import time
from dh import deserialize_parameters, generate_keys, serialize_public_key, deserialize_public_key, compute_shared_secret, derive_symmetric_key, encrypt_message, decrypt_message

# Step 1: Read DH parameters from the file
with open("dh_parameters.pem", "rb") as f:
    parameters_bytes = f.read()
parameters = deserialize_parameters(parameters_bytes)

# Step 2: Generate client's private and public keys
client_private_key, client_public_key = generate_keys(parameters)

# Step 3: Serialize client's public key and save it to a file
client_public_key_bytes = serialize_public_key(client_public_key)
with open("client_public_key.pem", "wb") as f:
    f.write(client_public_key_bytes)

print("Client: Public key saved to client_public_key.pem")

# Step 4: Wait for the server's public key to be available
print("Client: Waiting for server's public key...")
while not os.path.exists("server_public_key.pem"):
    time.sleep(1)  # Wait for 1 second before checking again

# Step 5: Read the server's public key from the file
with open("server_public_key.pem", "rb") as f:
    server_public_key_bytes = f.read()
server_public_key = deserialize_public_key(server_public_key_bytes)

# Step 6: Compute shared secret
client_shared_secret = compute_shared_secret(client_private_key, server_public_key, parameters.parameter_numbers().p)

# Step 7: Derive symmetric key
client_symmetric_key = derive_symmetric_key(client_shared_secret)

# Step 8: Secure messaging loop
print("Client: Secure messaging started. Type 'exit' to quit.")
while True:
    # Send a message to the server
    message = input("Client: Enter your message: ")
    if message.lower() == "exit":
        print("Client: Exiting...")
        break

    # Encrypt the message
    encrypted_message = encrypt_message(client_symmetric_key, message)
    with open("client_message.enc", "wb") as f:
        f.write(encrypted_message)

    print("Client: Message sent. Waiting for server response...")

    # Wait for a response from the server
    while not os.path.exists("server_message.enc"):
        time.sleep(1)  # Wait for 1 second before checking again

    with open("server_message.enc", "rb") as f:
        encrypted_response = f.read()
    os.remove("server_message.enc")  # Delete the message file after reading

    # Decrypt the response
    decrypted_response = decrypt_message(client_symmetric_key, encrypted_response)
    print(f"Server: {decrypted_response}")