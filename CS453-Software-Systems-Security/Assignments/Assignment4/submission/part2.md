# Assignment 4 (Part 2): Documentation

## Requirements

- **Operating System:** UNIX-like (Ubuntu, macOS, or WSL on Windows)
- **Python Version:** 3.7 or later

### Dependencies & Libraries

- **Flask:** Used to create the HTTP server.
- **cryptography:** Provides functions to parse OpenSSH keys and verify Ed25519 signatures.
- **requests:** Provides functions to make HTTP post requests in /attack endpoint to implement attack logic in part 3.

**Installation Command:**

```bash
pip install Flask cryptography
```

## Setup & Running the Server

1. **Prepare the Environment:**
   - Optionally, create a virtual environment:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
2. **Save the Server Code:**
   - Save server implementation in a file named `part2_server.py`.

3. **Launch the Server:**
   - Run the server with:
     ```bash
     python3 part2_server.py
     ```
   - The server will bind to `0.0.0.0` on port `8000`.

## Client Interaction

The server exposes two endpoints:

- **Registration Endpoint:**  
  - **Path:** `/register/<uid>`
  - **Method:** POST
  - **Body:** An OpenSSH-encoded Ed25519 public key.
  - **Behavior:**  
    - Accepts only users from the set `{test1, test2, test3, test4, test5}`.
    - Rejects duplicate registrations or invalid keys with appropriate HTTP status codes.

- **Login Endpoint:**  
  - **Path:** `/login/<uid>`
  - **Method:** POST
  - **Body:** A binary signature (generated over the fixed message "Authenticate").
  - **Behavior:**  
    - Verifies that the signature corresponds to the previously registered public key.
    - Rejects login attempts for unregistered users, invalid signatures, or disallowed usernames.

The provided `portal_a4.sh` script is used to interact with the server. It generates keys, sends registration requests, and verifies logins.

## Development Approach

- **Registration Flow:**  
  1. Validate that `<uid>` is within the allowed set.
  2. Ensure the user is not already registered.
  3. Retrieve and clean the POST data.
  4. Parse the OpenSSH-encoded public key and ensure it is an Ed25519 key.
  5. Store the key in an in-memory dictionary.

- **Login Flow:**  
  1. Confirm the `<uid>` is allowed and registered.
  2. Retrieve the binary signature from the POST data.
  3. Verify the signature against the fixed message `b"Authenticate"` using the stored public key.
  4. Return appropriate HTTP status codes based on verification success or failure.

- **Error Handling:**  
  The server returns precise HTTP error codes (403, 409, 406, 401, etc.) for invalid requests, ensuring clear feedback for debugging and correct client behavior.
