# app.py
import streamlit as st
from src.dh import (
    generate_dh_parameters,
    serialize_parameters,
    generate_keys,
    serialize_public_key,
    deserialize_public_key,
    compute_shared_secret,
    derive_symmetric_key,
    encrypt_message,
    decrypt_message,
)
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom CSS for styling
st.markdown(
    """
    <style>
    .stSidebar {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    .stHeader {
        color: #2c3e50;
        font-size: 24px;
        font-weight: bold;
    }
    .stSuccess {
        color: #28a745;
        font-weight: bold;
    }
    .stError {
        color: #dc3545;
        font-weight: bold;
    }
    .stMarkdown {
        color: #333333;
    }
    .message {
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        max-width: 70%;
    }
    .client-message {
        background-color: #DCF8C6;
        margin-right: auto;
        margin-left: 0;
    }
    .server-message {
        background-color: #ECECEC;
        margin-left: auto;
        margin-right: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Streamlit app title
st.markdown(
    "<h1 style='text-align: center; color: #2c3e50;'>🔒 Secure Messaging App using Diffie-Hellman Key Exchange 🔒</h1>",
    unsafe_allow_html=True,
)

# Sidebar for user input
st.sidebar.markdown(
    "<h2 style='color: #2c3e50;'>⚙️ Configuration</h2>",
    unsafe_allow_html=True,
)
st.sidebar.write("Configure the client and server for secure messaging. 🛠️")

# Dropdown to select encryption algorithm
encryption_algo = st.sidebar.selectbox(
    "🔐 Select Encryption Algorithm",
    options=["AES-256", "ChaCha20", "Blowfish"],
    index=0,  # Default to AES-256
    help="Choose the symmetric encryption algorithm for secure messaging.",
)

# Slider to select key size
key_size = st.sidebar.slider(
    "🔑 Select Key Size (bits)",
    min_value=128,
    max_value=512,
    value=256,  # Default to 256 bits
    step=64,
    help="Choose the key size for the Diffie-Hellman key exchange.",
)

# Checkbox to enable logging
enable_logging = st.sidebar.checkbox(
    "📝 Enable Logging",
    value=True,
    help="Enable logging for debugging and auditing purposes.",
)

# Button to reset the session
if st.sidebar.button("🔄 Reset Session"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.sidebar.success("Session reset successfully! ✅")
    logger.info("Session reset.")

# Display current configuration status
st.sidebar.markdown(
    "<h3 style='color: #2c3e50;'>📊 Current Configuration Status</h3>",
    unsafe_allow_html=True,
)
if "parameters" in st.session_state:
    st.sidebar.markdown(
        "<p class='stSuccess'>✅ Diffie-Hellman parameters generated.</p>",
        unsafe_allow_html=True,
    )
if "client_private_key" in st.session_state:
    st.sidebar.markdown(
        "<p class='stSuccess'>✅ Client keys generated.</p>",
        unsafe_allow_html=True,
    )
if "server_private_key" in st.session_state:
    st.sidebar.markdown(
        "<p class='stSuccess'>✅ Server keys generated.</p>",
        unsafe_allow_html=True,
    )
if "client_shared_secret" in st.session_state:
    st.sidebar.markdown(
        "<p class='stSuccess'>✅ Shared secrets computed.</p>",
        unsafe_allow_html=True,
    )

# Initialize session state
if "parameters" not in st.session_state:
    st.session_state.parameters = generate_dh_parameters()
    st.session_state.parameters_bytes = serialize_parameters(st.session_state.parameters)
    logger.info("Diffie-Hellman parameters generated.")

if "client_private_key" not in st.session_state:
    st.session_state.client_private_key, st.session_state.client_public_key = generate_keys(st.session_state.parameters)
    st.session_state.client_public_key_bytes = serialize_public_key(st.session_state.client_public_key)
    logger.info("Client keys generated.")

if "server_private_key" not in st.session_state:
    st.session_state.server_private_key, st.session_state.server_public_key = generate_keys(st.session_state.parameters)
    st.session_state.server_public_key_bytes = serialize_public_key(st.session_state.server_public_key)
    logger.info("Server keys generated.")

if "client_shared_secret" not in st.session_state:
    st.session_state.client_shared_secret = compute_shared_secret(st.session_state.client_private_key, st.session_state.server_public_key, st.session_state.parameters.parameter_numbers().p)
    st.session_state.client_symmetric_key = derive_symmetric_key(st.session_state.client_shared_secret)
    logger.info("Client shared secret computed.")

if "server_shared_secret" not in st.session_state:
    st.session_state.server_shared_secret = compute_shared_secret(st.session_state.server_private_key, st.session_state.client_public_key, st.session_state.parameters.parameter_numbers().p)
    st.session_state.server_symmetric_key = derive_symmetric_key(st.session_state.server_shared_secret)
    logger.info("Server shared secret computed.")

# Calculate the number of bytes required to represent the shared secret
client_shared_secret_bytes = (st.session_state.client_shared_secret.bit_length() + 7) // 8
server_shared_secret_bytes = (st.session_state.server_shared_secret.bit_length() + 7) // 8

# Display shared secrets (for demonstration purposes)
st.write("### 🔑 Shared Secrets")
st.write(f"Client's shared secret: `{st.session_state.client_shared_secret.to_bytes(client_shared_secret_bytes, 'big').hex()}`")
st.write(f"Server's shared secret: `{st.session_state.server_shared_secret.to_bytes(server_shared_secret_bytes, 'big').hex()}`")

# Secure messaging section
st.write("### 💬 Secure Messaging")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []  # Stores all messages (client and server)

# Create two columns for client and server inputs
col1, col2 = st.columns(2)

# Client input
with col1:
    st.header("👤 Client")
    client_message = st.text_input("✉️ Enter your message (Client)")
    if st.button("🚀 Send from Client"):
        if client_message:
            try:
                # Encrypt the message
                encrypted_message = encrypt_message(st.session_state.client_symmetric_key, client_message)
                # Store the encrypted message in session state
                st.session_state.messages.append(("Client", encrypted_message))
                st.success("✅ Client message encrypted and sent!")
                logger.info("Client message encrypted and sent.")
            except Exception as e:
                st.error(f"❌ Error encrypting client message: {e}")
                logger.error(f"Client message encryption error: {e}")

# Server input
with col2:
    st.header("🖥️ Server")
    server_message = st.text_input("✉️ Enter your message (Server)")
    if st.button("🚀 Send from Server"):
        if server_message:
            try:
                # Encrypt the message
                encrypted_message = encrypt_message(st.session_state.server_symmetric_key, server_message)
                # Store the encrypted message in session state
                st.session_state.messages.append(("Server", encrypted_message))
                st.success("✅ Server message encrypted and sent!")
                logger.info("Server message encrypted and sent.")
            except Exception as e:
                st.error(f"❌ Error encrypting server message: {e}")
                logger.error(f"Server message encryption error: {e}")

# Display messages in a WhatsApp-like format
st.write("### 📩 Message History")
for sender, encrypted_message in st.session_state.messages:
    if sender == "Client":
        # Decrypt and display client message on the left
        try:
            decrypted_message = decrypt_message(st.session_state.client_symmetric_key, encrypted_message)
            st.markdown(f"<div class='message client-message'><b>Client:</b> {decrypted_message}</div>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"❌ Error decrypting client message: {e}")
    elif sender == "Server":
        # Decrypt and display server message on the right
        try:
            decrypted_message = decrypt_message(st.session_state.server_symmetric_key, encrypted_message)
            st.markdown(f"<div class='message server-message'><b>Server:</b> {decrypted_message}</div>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"❌ Error decrypting server message: {e}")