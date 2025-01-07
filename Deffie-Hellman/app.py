# app.py
import streamlit as st
from src.dh import generate_dh_parameters, serialize_parameters, generate_keys, serialize_public_key, deserialize_public_key, compute_shared_secret, derive_symmetric_key, encrypt_message, decrypt_message
import os

# Streamlit app title
st.title("Secure Messaging App using Diffie-Hellman Key Exchange")

# Sidebar for user input
st.sidebar.header("Configuration")
st.sidebar.write("Configure the client and server for secure messaging.")

# Step 1: Generate DH parameters
if "parameters" not in st.session_state:
    st.session_state.parameters = generate_dh_parameters()
    st.session_state.parameters_bytes = serialize_parameters(st.session_state.parameters)

# Step 2: Generate client and server keys
if "client_private_key" not in st.session_state:
    st.session_state.client_private_key, st.session_state.client_public_key = generate_keys(st.session_state.parameters)
    st.session_state.client_public_key_bytes = serialize_public_key(st.session_state.client_public_key)

if "server_private_key" not in st.session_state:
    st.session_state.server_private_key, st.session_state.server_public_key = generate_keys(st.session_state.parameters)
    st.session_state.server_public_key_bytes = serialize_public_key(st.session_state.server_public_key)

# Step 3: Compute shared secrets
if "client_shared_secret" not in st.session_state:
    st.session_state.client_shared_secret = compute_shared_secret(st.session_state.client_private_key, st.session_state.server_public_key)
    st.session_state.client_symmetric_key = derive_symmetric_key(st.session_state.client_shared_secret)

if "server_shared_secret" not in st.session_state:
    st.session_state.server_shared_secret = compute_shared_secret(st.session_state.server_private_key, st.session_state.client_public_key)
    st.session_state.server_symmetric_key = derive_symmetric_key(st.session_state.server_shared_secret)

# Display shared secrets (for demonstration purposes)
st.write("### Shared Secrets")
st.write(f"Client's shared secret: `{st.session_state.client_shared_secret.hex()}`")
st.write(f"Server's shared secret: `{st.session_state.server_shared_secret.hex()}`")

# Secure messaging section
st.write("### Secure Messaging")

# Client message input
client_message = st.text_input("Client: Enter your message")
if st.button("Send from Client"):
    if client_message:
        # Encrypt the message
        encrypted_message = encrypt_message(st.session_state.client_symmetric_key, client_message)
        st.session_state.client_message = encrypted_message
        st.success("Client message encrypted and sent!")

# Server message decryption
if "client_message" in st.session_state:
    decrypted_message = decrypt_message(st.session_state.server_symmetric_key, st.session_state.client_message)
    st.write(f"Server received: `{decrypted_message}`")

# Server message input
server_message = st.text_input("Server: Enter your message")
if st.button("Send from Server"):
    if server_message:
        # Encrypt the message
        encrypted_message = encrypt_message(st.session_state.server_symmetric_key, server_message)
        st.session_state.server_message = encrypted_message
        st.success("Server message encrypted and sent!")

# Client message decryption
if "server_message" in st.session_state:
    decrypted_message = decrypt_message(st.session_state.client_symmetric_key, st.session_state.server_message)
    st.write(f"Client received: `{decrypted_message}`")