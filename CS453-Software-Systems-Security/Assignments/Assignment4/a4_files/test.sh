#!/bin/bash
set -e

# Path to the provided client script.
CLIENT="./portal_a4.sh"

# Helper function for tests that expect a success output.
function run_test() {
    test_desc="$1"
    expected="$2"
    shift 2
    cmd="$@"
    
    echo "=================================="
    echo "Test: $test_desc"
    output=$($cmd 2>&1 || true)
    echo "Command output:"
    echo "$output"
    
    if echo "$output" | grep -q "$expected"; then
        echo "Result: PASS"
    else
        echo "Result: FAIL"
        exit 1
    fi
}

# Helper function for tests that expect a failure (i.e. the success string must NOT appear).
function run_test_neg() {
    test_desc="$1"
    unexpected="$2"
    shift 2
    cmd="$@"
    
    echo "=================================="
    echo "Test: $test_desc"
    output=$($cmd 2>&1 || true)
    echo "Command output:"
    echo "$output"
    
    if echo "$output" | grep -q "$unexpected"; then
        echo "Result: FAIL (unexpected success message found)"
        exit 1
    else
        echo "Result: PASS"
    fi
}

# Set course variables for the client script.
export USR_DEFAULT="user"   # Dummy value; not used in tests.
export KEY_DEFAULT="_"      # Keys will be saved as _<uid> and _<uid>.pub.
export NAMESPACE="assignment4"

# Clean up any previous key files.
rm -f _test1 _test1.pub _test2 _test2.pub

###############################
# Test 1: Register allowed user (test1)
###############################
run_test "Register allowed user 'test1'" "!!! IMPORTANT !!!" "$CLIENT register test1"

###############################
# Test 2: Re-register test1 should fail
###############################
# Pipe a "y" so that ssh-keygen overwrites the existing key file and then the server rejects the re-registration.
run_test_neg "Re-register 'test1' (should fail)" "!!! IMPORTANT !!!" "echo y | $CLIENT register test1"

###############################
# Test 3: Register non-allowed user (test6) should fail
###############################
run_test_neg "Register non-allowed user 'test6' (should fail)" "!!! IMPORTANT !!!" "$CLIENT register test6"

###############################
# Test 4: Login for unregistered user (test2) should fail
###############################
run_test_neg "Login unregistered user 'test2' (should fail)" "Request to server was successful." "$CLIENT login test2"

###############################
# Test 5: Login for test1 with correct private key (should succeed)
###############################
run_test "Login 'test1' with correct key" "Request to server was successful." "$CLIENT login test1"

###############################
# Test 6: Login for test1 with different private key (should fail)
# Simulate by replacing test1's key with a new key pair.
###############################
echo "Backing up original key for test1..."
mv _test1 _test1.bak
mv _test1.pub _test1.pub.bak

echo "Generating new (wrong) key pair for test1..."
ssh-keygen -t ed25519 -C "${USR_DEFAULT}@${NAMESPACE}" -f _test1 -P "" >/dev/null

run_test_neg "Login 'test1' with wrong key (should fail)" "Request to server was successful." "$CLIENT login test1"

# Restore original key for test1.
echo "Restoring original key for test1..."
mv _test1.bak _test1
mv _test1.pub.bak _test1.pub 2>/dev/null || true

###############################
# Test 7: Register and login for allowed user (test2)
###############################
rm -f _test2 _test2.pub
run_test "Register allowed user 'test2'" "!!! IMPORTANT !!!" "$CLIENT register test2"
run_test "Login 'test2' with correct key" "Request to server was successful." "$CLIENT login test2"

echo "=================================="
echo "All tests passed successfully."

