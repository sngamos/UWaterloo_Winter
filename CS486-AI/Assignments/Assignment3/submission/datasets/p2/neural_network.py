# version 1.1

from typing import List
import numpy as np

from operations import *

class NeuralNetwork():
    '''
    A class for a fully connected feedforward neural network (multilayer perceptron).
    :attr n_layers: Number of layers in the network
    :attr activations: A list of Activation objects corresponding to each layer's activation function
    :attr loss: A Loss object corresponding to the loss function used to train the network
    :attr learning_rate: The learning rate
    :attr W: A list of weight matrices. The first row corresponds to the biases.
    '''

    def __init__(self, n_features: int, layer_sizes: List[int], activations: List[Activation], loss: Loss,
                 learning_rate: float=0.01, W_init: List[np.ndarray]=None):
        '''
        Initializes a NeuralNetwork object
        :param n_features: Number of features in each training examples
        :param layer_sizes: A list indicating the number of neurons in each layer
        :param activations: A list of Activation objects corresponding to each layer's activation function
        :param loss: A Loss object corresponding to the loss function used to train the network
        :param learning_rate: The learning rate
        :param W_init: If not None, the network will be initialized with this list of weight matrices
        '''

        sizes = [n_features] + layer_sizes
        if W_init:
            assert all([W_init[i].shape == (sizes[i] + 1, sizes[i+1]) for i in range(len(layer_sizes))]), \
                "Specified sizes for layers do not match sizes of layers in W_init"
        assert len(activations) == len(layer_sizes), \
            "Number of sizes for layers provided does not equal the number of activations provided"

        self.n_layers = len(layer_sizes)
        self.activations = activations
        self.loss = loss
        self.learning_rate = learning_rate
        self.W = []
        for i in range(self.n_layers):
            if W_init:
                self.W.append(W_init[i])
            else:
                rand_weights = np.random.randn(sizes[i], sizes[i+1]) / np.sqrt(sizes[i])
                biases = np.zeros((1, sizes[i+1]))
                self.W.append(np.concatenate([biases, rand_weights], axis=0))

    def forward_pass(self, X) -> (List[np.ndarray], List[np.ndarray]):
        '''
        Executes the forward pass of the network on a dataset of n examples with f features. Inputs are fed into the
        first layer. Each layer computes Z_i = g(A_i) = g(Z_{i-1}W[i]).
        :param X: The training set, with size (n, f)
        :return A_vals: a list of a-values for each example in the dataset. There are n_layers items in the list and
                        each item is an array of size (n, layer_sizes[i])
                Z_vals: a list of z-values for each example in the dataset. There are n_layers items in the list and
                        each item is an array of size (n, layer_sizes[i])
        '''

        #####################################
        # YOUR CODE HERE
        #####################################
        n =  X.shape[0]
        A_vals = []
        Z_vals = []
        A_prev = X #initial activation is the input
        for i in range(self.n_layers):
            # add column of ones to incorporate bias since first row of W[i] are bias weights 
            A_with_bias = np.concatenate((np.ones((n, 1)), A_prev), axis=1)
            # calc linear combination of weights and activations
            Z = np.dot(A_with_bias, self.W[i])
            Z_vals.append(Z)
            # for hidden layers, apply non-linear activation, for output layer, use identity activation
            if i < self.n_layers - 1:
                A=Z
            else:
                A = self.activations[i].value(Z)
            A_vals.append(A)
            A_prev = A
        return A_vals, Z_vals
    
    def backward_pass(self, A_vals, dLdyhat) -> List[np.ndarray]:
        '''
        Executes the backward pass of the network on a dataset of n examples with f features. The delta values are
        computed from the end of the network to the front.
        :param A_vals: a list of a-values for each example in the dataset. There are n_layers items in the list and
                       each item is an array of size (n, layer_sizes[i])
        :param dLdyhat: The derivative of the loss with respect to the predictions (y_hat), with shape (n, layer_sizes[-1])
        :return deltas: A list of delta values for each layer. There are n_layers items in the list and
                        each item is an array of size (n, layer_sizes[i])
        '''

        #####################################
        # YOUR CODE HERE
        #####################################

        #init list for deltas
        deltas = [None] * self.n_layers
        n = dLdyhat.shape[0]
        # for output layer, with identity activation, delta is just the derivative of the loss
        deltas[-1] = dLdyhat

        # propagate error backwards for hidden layers
        for i in reversed(range(self.n_layers-1)):
            # when propagating the error, remove the bias weight from next layer
            W_no_bias = self.W[i+1][1:, :]
            #back propogate delta
            print("deltas i+1",deltas[i+1])
            print("W_no_bias",W_no_bias)
            print("self.activations[i].derivative(A_vals[i])",self.activations[i].derivative(A_vals[i]))
            deltas[i] = np.dot(deltas[i+1], W_no_bias.T) * self.activations[i].derivative(A_vals[i])
            
        return deltas

    def update_weights(self, X, Z_vals, deltas) -> List[np.ndarray]:
        '''
        Having computed the delta values from the backward pass, update each weight with the sum over the training
        examples of the gradient of the loss with respect to the weight.
        :param X: The training set, with size (n, f)
        :param Z_vals: a list of z-values for each example in the dataset. There are n_layers items in the list and
                       each item is an array of size (n, layer_sizes[i])
        :param deltas: A list of delta values for each layer. There are n_layers items in the list and
                       each item is an array of size (n, layer_sizes[i])
        :return W: The newly updated weights (i.e. self.W)
        '''

        #####################################
        # YOUR CODE HERE
        #####################################
        n = X.shape[0]  # number of training examples

        # ----------------
        # 1) Update layer 0 weights
        # The "input to layer 0" is X. We prepend a column of ones for the bias.
        # grad_W^0 = (A_prev_with_bias)^T @ deltas[0]
        # where A_prev_with_bias is [1, X].
        A_prev_with_bias = np.concatenate([np.ones((n, 1)), X], axis=1)
        grad_W0 = np.dot( A_prev_with_bias.T,deltas[0])  # shape: (f+1, layer_sizes[0])
        self.W[0] -= self.learning_rate * grad_W0

        # ----------------
        # 2) Update subsequent layers
        # For layer i, the "input to layer i" is the activation of Z_vals[i-1].
        # We apply the stored activation function (unless it's the output layer with identity).
        for i in range(1, self.n_layers):
            # Recompute the activation that was fed into layer i
            if i == 1:
                # the input to layer 1 is the activation of Z_vals[0]
                # if the first layer is not the output layer, apply self.activations[0]
                if self.n_layers > 1:
                    A_prev = self.activations[0].value(Z_vals[0])
                else:
                    # if there's only one layer in total, then it's output => identity
                    A_prev = Z_vals[0]
            else:
                # input to layer i is activation of Z_vals[i-1]
                # For hidden layers, apply self.activations[i-1].
                # If i-1 is the last layer, it might be identity for regression.
                if i == self.n_layers - 1:
                    # the previous layer was the last hidden layer, so apply its activation
                    A_prev = self.activations[i-1].value(Z_vals[i-1])
                else:
                    A_prev = self.activations[i-1].value(Z_vals[i-1])

            # Prepend a column of ones to incorporate the bias
            A_prev_with_bias = np.concatenate([np.ones((n, 1)), A_prev], axis=1)
            grad_Wi = np.dot(A_prev_with_bias.T, deltas[i])  # shape: (layer_sizes[i-1]+1, layer_sizes[i])
            self.W[i] -= self.learning_rate * grad_Wi

        return self.W

    def train(self, X: np.ndarray, y: np.ndarray, epochs: int) -> (List[np.ndarray], List[float]):
        '''
        Trains the neural network model on a labelled dataset.
        :param X: The training set, with size (n, f)
        :param y: The targets for each example, with size (n, 1)
        :param epochs: The number of epochs to train the model
        :return W: The trained weights
                epoch_losses: A list of the training losses in each epoch
        '''

        epoch_losses = []
        for epoch in range(epochs):
            A_vals, Z_vals = self.forward_pass(X)   # Execute forward pass
            y_hat = Z_vals[-1]                      # Get predictions
            L = self.loss.value(y_hat, y)           # Compute the loss
            print("Epoch {}/{}: Loss={}".format(epoch, epochs, L))
            epoch_losses.append(L)                  # Keep track of the loss for each epoch

            dLdyhat = self.loss.derivative(y_hat, y)         # Calculate derivative of the loss with respect to output
            deltas = self.backward_pass(A_vals, dLdyhat)     # Execute the backward pass to compute the deltas
            self.W = self.update_weights(X, Z_vals, deltas)  # Calculate the gradients and update the weights

        return self.W, epoch_losses

    def evaluate(self, X: np.ndarray, y: np.ndarray, metric) -> float:
        '''
        Evaluates the model on a labelled dataset
        :param X: The examples to evaluate, with size (n, f)
        :param y: The targets for each example, with size (n, 1)
        :param metric: A function corresponding to the performance metric of choice (e.g. accuracy)
        :return: The value of the performance metric on this dataset
        '''

        A_vals, Z_vals = self.forward_pass(X)       # Make predictions for these examples
        y_hat = Z_vals[-1]
        metric_value = metric(y_hat, y)     # Compute the value of the performance metric for the predictions
        return metric_value
