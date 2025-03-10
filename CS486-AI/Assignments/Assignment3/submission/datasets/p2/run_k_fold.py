import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from neural_network import NeuralNetwork
from operations import ReLU, Sigmoid, Identity, MeanSquaredError, mean_absolute_error

# ---------------- Global Variables and Parameters ----------------
DATA_PATH = "/Users/amos/Library/CloudStorage/OneDrive-SingaporeUniversityofTechnologyandDesign/Documents/6.UW/CS486-AI/Assignments/Assignment3/submission/datasets/p2/data/wine_quality.csv"
TARGET_FEATURE = "quality"

EPOCHS = 500
LEARNING_RATE = 0.001
K_FOLDS = 5

# Network Architecture:
# 11 input features, hidden layers: [32, 32, 16], output: 1 node with Identity activation.
LAYER_SIZES = [32, 32, 16, 1]
ACTIVATIONS = [ReLU(), ReLU(), Sigmoid(), Identity()]
LOSS = MeanSquaredError()

# ---------------- Helper Function: Load Dataset ----------------
def load_dataset(csv_path, target_feature):
    data = pd.read_csv(csv_path)  # Adjust delimiter (e.g., sep=";") if necessary.
    y = np.expand_dims(data[target_feature].to_numpy().astype(float), axis=1)
    X = data.drop([target_feature], axis=1).to_numpy()
    return X, y

# ---------------- Load and Shuffle Data ----------------
X, y = load_dataset(DATA_PATH, TARGET_FEATURE)
n_samples = X.shape[0]

# Shuffle the dataset
indices = np.arange(n_samples)
np.random.shuffle(indices)
X = X[indices]
y = y[indices]

# ---------------- Create k-Fold Splits ----------------
fold_size = n_samples // K_FOLDS
fold_indices = []
for i in range(K_FOLDS):
    if i < K_FOLDS - 1:
        fold_indices.append(indices[i*fold_size:(i+1)*fold_size])
    else:
        fold_indices.append(indices[i*fold_size:])

# ---------------- Containers for Results ----------------
# To record training loss per epoch for each fold
epoch_losses_all_folds = np.zeros((K_FOLDS, EPOCHS))
# To record the validation MAE for each fold
val_mae_scores = []

# ---------------- k-Fold Cross Validation Loop ----------------
for k in range(K_FOLDS):
    # Define validation indices for the current fold and training indices for the others.
    val_idx = fold_indices[k]
    train_idx = np.concatenate([fold_indices[i] for i in range(K_FOLDS) if i != k], axis=0)
    X_train, y_train = X[train_idx], y[train_idx]
    X_val, y_val = X[val_idx], y[val_idx]
    
    print(f"Starting Fold {k+1}/{K_FOLDS} ...")
    
    # Create a new network instance for this fold.
    net = NeuralNetwork(n_features=X.shape[1], layer_sizes=LAYER_SIZES, activations=ACTIVATIONS,
                        loss=LOSS, learning_rate=LEARNING_RATE)
    
    fold_epoch_losses = []
    # Train for EPOCHS epochs on this fold's training set.
    for epoch in range(EPOCHS):
        A_vals, Z_vals = net.forward_pass(X_train)
        y_hat = Z_vals[-1]  # For regression, output is the last layer's pre-activation.
        loss_epoch = LOSS.value(y_hat, y_train)
        fold_epoch_losses.append(loss_epoch)
        
        dLdyhat = LOSS.derivative(y_hat, y_train)
        deltas = net.backward_pass(A_vals, dLdyhat)
        net.update_weights(X_train, Z_vals, deltas)
    
    epoch_losses_all_folds[k, :] = np.array(fold_epoch_losses)
    
    # After training, evaluate on the validation set.
    fold_mae = net.evaluate(X_val, y_val, mean_absolute_error)
    val_mae_scores.append(fold_mae)
    print(f"Fold {k+1} Validation MAE: {fold_mae:.4f}")

# ---------------- Compute and Plot Average Training Loss ----------------
avg_epoch_loss = np.mean(epoch_losses_all_folds, axis=0)

plt.figure(figsize=(10, 6))
plt.plot(np.arange(EPOCHS), avg_epoch_loss, label="Average Training Loss")
plt.xlabel("Epoch Number")
plt.ylabel("Average Training Loss (MSE)")
plt.title("Average Training Loss vs. Epoch (5-Fold Cross Validation)")
plt.legend()
plt.grid(True)
plt.show()

# ---------------- Report Validation MAE ----------------
val_mae_scores = np.array(val_mae_scores)
avg_val_mae = np.mean(val_mae_scores)
std_val_mae = np.std(val_mae_scores)

print("-----------------------------------------------------")
print("5-Fold Cross Validation Results:")
print(f"Average Validation MAE: {avg_val_mae:.4f}")
print(f"Validation MAE Standard Deviation: {std_val_mae:.4f}")
print("-----------------------------------------------------")
