# Assignment 4 (Part 3): Documentation


## Server 1

### Vulnerability Explanation
Server 1’s login endpoint is vulnerable because it lacks any actual credential verification. Although the code logs errors if a user is not allowed or not registered, it ultimately returns a response indicating `"Authentication successful"` regardless of the data provided. In short, no signature verification occurs—making the endpoint trivially bypassable.

### Exploitation Steps
1. **Select an Allowed User:** Choose a valid user, e.g., `test1`.
2. **Send a Forged Login Request:** Craft a POST request to `http://<server1_address>:8001/login/test1` (server_1 runs on port 8001).
3. **Provide Arbitrary Data:** Supply any arbitrary payload (or even no valid signature at all) in the POST body.
4. **Receive Success Response:** Due to the lack of proper checks, the server responds with `"Authentication successful"`, granting unauthorized access.


## Server 2

### Vulnerability Explanation
Server 2’s login endpoint is flawed because it incorrectly compares the provided authentication data against part of the stored public key string. The code first checks if the decoded request data equals an expected substring from the public key. If it does, it skips proper cryptographic verification. An attacker can therefore simply send the expected string (often the public key or a substring thereof) as the signature.

### Exploitation Steps
1. **Choose a Valid User:** For example, `test1`.
2. **Determine the Expected Signature:** Review the stored public key string for `test1` (hardcoded in the server) and note that if it contains a semicolon, the part after the semicolon is used; otherwise, the whole string is considered.
3. **Craft the Attack Request:** Send a POST request to `http://<server2_address>:8002/login/test1` (server_2 runs on port 8002) with the expected string as the request body.
4. **Bypass Verification:** Since the endpoint improperly validates the signature by mere string comparison, the server will respond with `"Authentication successful"`, allowing the attacker to log in.


## Server 3

### Vulnerability Explanation
Server 3 uses a time-dependent message for authentication, where the message is generated based on the current year and month (e.g., `"2025-03"`). Because this message remains constant for the entire month, a valid signature obtained once (via a legitimate login) can be replayed later during the same month. This replay attack enables an attacker to use a previously captured signature to gain unauthorized access.

### Exploitation Steps
1. **Capture a Valid Signature:** Monitor or perform a legitimate login for a user (e.g., `test1`) and capture the valid signature produced. The signature is generated over the message formatted as `"YYYY-MM"`.
2. **Understand the Time Window:** Note that the message remains unchanged throughout the month.
3. **Replay the Signature:** At any later time during the same month, resend a POST request to `http://<server3_address>:8003/login/test1` (server_3 runs on port 8003) using the captured signature as the request body.
4. **Gain Access:** Since the server uses the same predictable message for verification, it will accept the replayed signature and return `"Authentication successful"`, thus allowing unauthorized login.
