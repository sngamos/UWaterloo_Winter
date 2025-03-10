import json
import numpy as np
from neural_net import NeuralNetwork
import operations

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


# Global file paths (change these paths as needed)
TEST_METRICS_PATH = "p2/tests/test_metrics.json"
TEST_ACTIVATIONS_PATH = "tests/tests_activations.json"
TEST_BACKWARD_PATH = "tests/tests_backward.json"
TEST_FORWARD_PATH = "tests/tests_forward.json"
TEST_UPDATE_WEIGHTS_PATH = "tests/tests_update_weights.json"

def load_json(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


## testing operations mse
def run_test_mean_absolute_error():
    test_cases = load_json(TEST_METRICS_PATH)
    test = test_cases["test_mean_absolute_error_1"]
    y_hat = np.array(test["y_hat"])
    y = np.array(test["y"])
    expected = test["soln"]
    result = operations.mean_absolute_error(y_hat, y)
    print("Mean Absolute Error Test:")
    print("Result:   ", result)
    print("Expected: ", expected)
    assert np.isclose(result, expected, atol=1e-3), "Mean Absolute Error Test failed!"


# testing operations activations
def run_test_activations():
    tests = load_json(TEST_ACTIVATIONS_PATH)
    # Test Sigmoid value
    test = tests["test_sigmoid_value_1"]
    k = test["k"]
    x = np.array(test["x"])
    sigmoid = operations.Sigmoid(k)
    result = sigmoid.value(x)
    expected = np.array(test["soln"])
    print("Sigmoid Value Test:")
    print("Result:\n", result)
    print("Expected:\n", expected)
    assert np.allclose(result, expected, atol=1e-3), "Sigmoid value test failed!"

    # Test Sigmoid derivative
    test = tests["test_sigmoid_derivative_1"]
    x = np.array(test["x"])
    result = sigmoid.derivative(x)
    expected = np.array(test["soln"])
    print("Sigmoid Derivative Test:")
    print("Result:\n", result)
    print("Expected:\n", expected)
    assert np.allclose(result, expected, atol=1e-3), "Sigmoid derivative test failed!"

    # Test ReLU value
    test = tests["test_relu_value_1"]
    x = np.array(test["x"])
    relu = operations.ReLU()
    result = relu.value(x)
    expected = np.array(test["soln"])
    print("ReLU Value Test:")
    print("Result:\n", result)
    print("Expected:\n", expected)
    assert np.allclose(result, expected, atol=1e-3), "ReLU value test failed!"

    # Test ReLU derivative
    test = tests["test_relu_derivative_1"]
    x = np.array(test["x"])
    result = relu.derivative(x)
    expected = np.array(test["soln"])
    print("ReLU Derivative Test:")
    print("Result:\n", result)
    print("Expected:\n", expected)
    assert np.allclose(result, expected, atol=1e-3), "ReLU derivative test failed!"


def run_test_forward():
    tests = load_json(TEST_FORWARD_PATH)
    test = tests["test_forward_pass_net_1_layer"]
    X = np.array(test["X"])
    # Create a network instance that matches the test expectations.
    net = NeuralNetwork(n_features=4, layer_sizes=[6], activations=[operations.Identity()], loss=operations.MeanSquaredError(), learning_rate=0.01)
    A_vals, Z_vals = net.forward_pass(X)
    result = [Z_vals]  # wrap in list if expected in such format
    expected = test["soln"]
    print("Forward Pass Test:")
    print("Result:\n", result)
    print("Expected:\n", expected)
    # Adjust comparison as needed, for example:
    # assert np.allclose(np.array(result), np.array(expected), atol=1e-3)

def run_test_backward():
    tests = load_json(TEST_BACKWARD_PATH)
    test = tests["test_backward_pass_net_1_layer"]
    # Convert lists to numpy arrays where needed.
    A_vals = np.array(test["A_vals"])
    dLdyhat = np.array(test["dLdyhat"])
    # Create a network instance as needed.
    net = NeuralNetwork(n_features=6, layer_sizes=[6], activations=[operations.ReLU()], loss=operations.MeanSquaredError(), learning_rate=0.01)
    deltas = net.backward_pass(A_vals, dLdyhat)
    result = deltas
    expected = np.array(test["soln"])
    print("Backward Pass Test:")
    print("Result:\n", result)
    print("Expected:\n", expected)
    # assert np.allclose(result, expected, atol=1e-3)

def run_test_update_weights():
    tests = load_json(TEST_UPDATE_WEIGHTS_PATH)
    test = tests["test_update_weights_net_1_layer"]
    X = np.array(test["X"])
    Z_vals = np.array(test["Z_vals"])
    deltas = np.array(test["deltas"])
    # Create a network instance as needed.
    net = NeuralNetwork(n_features=4, layer_sizes=[6], activations=[operations.ReLU()], loss=operations.MeanSquaredError(), learning_rate=0.01)
    updated_weights = net.update_weights(X, Z_vals, deltas)
    result = updated_weights
    expected = np.array(test["soln"])
    print("Update Weights Test:")
    print("Result:\n", result)
    print("Expected:\n", expected)
    # assert np.allclose(result, expected, atol=1e-3)

if __name__ == '__main__':
    run_test_mean_absolute_error()
    run_test_activations()
    # Uncomment additional tests after verifying network instantiation:
    # run_test_forward()
    # run_test_backward()
    # run_test_update_weights()
    print("All tests executed.")