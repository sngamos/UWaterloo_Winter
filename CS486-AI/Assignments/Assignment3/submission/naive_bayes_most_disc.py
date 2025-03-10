from collections import defaultdict
import math

# ---------------- Data Loading Functions ----------------

def load_data(data_file_name, label_file):
    # This function reads document-word pairs and document labels from files.
    # It creates a dictionary mapping each document (by its ID) to a set of word IDs.
    docs = defaultdict(set)  # Using a defaultdict to automatically create a set for each document.
    with open(data_file_name, 'r') as data_file:
        for line in data_file:
            parts = line.strip().split()  # Split each line into doc_id and word_id.
            if len(parts) != 2:
                continue  # Skip lines that do not have exactly 2 parts.
            doc_id, word_id = int(parts[0]), int(parts[1])
            docs[doc_id].add(word_id)  # Add the word_id to the set corresponding to doc_id.
    
    # Now read the labels from the label file; each line corresponds to a document's label.
    labels = {}
    with open(label_file, 'r') as label_file_obj:
        for idx, line in enumerate(label_file_obj, start=1):
            labels[idx] = int(line.strip())  # Store the label for each document (doc IDs assumed to be 1-indexed).
    return docs, labels

def load_words(words_file):
    # This function loads the vocabulary mapping: word_id -> actual word.
    word_map = {}
    with open(words_file, 'r') as words_file_obj:
        for idx, line in enumerate(words_file_obj, start=1):
            word_map[idx] = line.strip()  # Map the line number (word_id) to the word.
    return word_map

# ---------------- Naïve Bayes Training Functions ----------------

def train_naive_bayes(train_docs, train_labels, V):
    """
    Trains a Naïve Bayes classifier using maximum likelihood estimation.
    
    Parameters:
      - train_docs: List of sets, where each set contains word IDs present in a document.
      - train_labels: List of labels (1 or 2) corresponding to each document.
      - V: Vocabulary size (total number of words).
    
    Returns:
      - class_priors: List containing the prior probabilities for each class.
      - cond_probs: 2D list (2 x (V+1)) containing the conditional probability of each word given a class,
                    computed using Laplace smoothing.
    """
    num_docs = len(train_docs)
    class_counts = [0, 0]  # Counters for the two classes: index 0 for label 1 and index 1 for label 2.
    # Create a matrix to count how many documents in each class contain each word.
    # We use V+1 so that word ID i corresponds to index i (ignoring index 0).
    word_counts = [[0] * (V + 1) for _ in range(2)]
    
    # Count documents per class and count word occurrences per class.
    for i in range(num_docs):
        label = train_labels[i]
        class_index = label - 1  # Convert label (1 or 2) to index (0 or 1).
        class_counts[class_index] += 1  # Increment count for this class.
        for word_id in train_docs[i]:
            if 1 <= word_id <= V:
                word_counts[class_index][word_id] += 1  # Increment count for word in the given class.
    
    # Compute class priors: the fraction of documents that belong to each class.
    class_priors = [count / num_docs for count in class_counts]
    
    # Compute conditional probabilities with Laplace smoothing.
    # Laplace smoothing helps avoid zero probabilities.
    cond_probs = [[0] * (V + 1) for _ in range(2)]
    for c in range(2):
        for w in range(1, V + 1):
            # Laplace correction: add 1 to the numerator and 2 to the denominator.
            cond_probs[c][w] = (word_counts[c][w] + 1) / (class_counts[c] + 2)
    
    return class_priors, cond_probs

# ---------------- Prediction Functions ----------------

def compute_log_scores(doc, class_priors, cond_probs, V):
    """
    Computes the log-probability scores for each class for a given document.
    
    Instead of multiplying many small probabilities (which can lead to underflow),
    we work in the logarithmic domain and sum the log probabilities.
    
    For a class c:
      log P(c|doc) ∝ log(P(c)) + Σ (for all words not in doc: log(1 - p(w|c)))
                     + Σ (for words in doc: [log(p(w|c)) - log(1 - p(w|c))])
    """
    scores = [0, 0]
    for c in range(2):
        # Start with the log of the prior probability.
        score = math.log(class_priors[c])
        total = 0.0
        # Sum over the contribution of words that are not present in the document.
        for w in range(1, V + 1):
            total += math.log(1 - cond_probs[c][w])
        score += total
        # Adjust the score for each word present in the document.
        for w in doc:
            if 1 <= w <= V:
                score += math.log(cond_probs[c][w]) - math.log(1 - cond_probs[c][w])
        scores[c] = score
    return scores

def classify(doc, class_priors, cond_probs, V):
    """
    Classifies a document by computing the log scores for each class and choosing the class with the higher score.
    """
    scores = compute_log_scores(doc, class_priors, cond_probs, V)
    # If the log score for class 1 is higher, return label 1; otherwise, return label 2.
    return 1 if scores[0] > scores[1] else 2

# ---------------- Evaluation Function ----------------

def evaluate(docs, labels, class_priors, cond_probs, V):
    """
    Evaluates the classifier's performance by computing the accuracy.
    
    Accuracy is defined as the percentage of correctly classified documents.
    """
    correct = 0
    total = len(docs)
    for i in range(total):
        prediction = classify(docs[i], class_priors, cond_probs, V)
        if prediction == labels[i]:
            correct += 1
    return (correct / total) * 100

# ---------------- Function to Identify Discriminative Words ----------------

def print_top_discriminative_words(cond_probs, vocab, V, top_n=10):
    """
    Computes and prints the top N most discriminative words based on the absolute difference between
    log(P(word|label1)) and log(P(word|label2)). A higher difference means the word is more indicative
    of one class over the other.
    """
    discriminative_features = []
    for word_id in range(1, V + 1):
        # Compute log probabilities for both classes.
        log_prob_label1 = math.log(cond_probs[0][word_id])
        log_prob_label2 = math.log(cond_probs[1][word_id])
        # Compute the absolute difference between the log probabilities.
        diff = abs(log_prob_label1 - log_prob_label2)
        discriminative_features.append((word_id, diff))
    
    # Sort the features by the absolute difference in descending order.
    discriminative_features.sort(key=lambda x: x[1], reverse=True)
    
    print("\nTop {} Discriminative Words:".format(top_n))
    for i in range(top_n):
        word_id, diff = discriminative_features[i]
        # Print the word ID, the corresponding word, and the discriminative score.
        print("Word ID: {}, Word: '{}', |log P(word|label1) - log P(word|label2)| = {:.4f}".format(
            word_id, vocab[word_id], diff))

# ---------------- Main Execution ----------------

def main():
    # Load the training and testing data using our custom data-loading functions.
    train_docs_dict, train_labels_dict = load_data("datasets/p1/trainData.txt", "datasets/p1/trainLabel.txt")
    test_docs_dict, test_labels_dict = load_data("datasets/p1/testData.txt", "datasets/p1/testLabel.txt")
    # Load the vocabulary to determine the vocabulary size.
    vocab = load_words("datasets/p1/words.txt")
    V = len(vocab)
    
    # Convert dictionaries to lists (sorted by document ID) so that each document and its label are aligned.
    train_ids = sorted(train_docs_dict.keys())
    train_docs = [train_docs_dict[doc_id] for doc_id in train_ids]
    train_labels = [train_labels_dict[doc_id] for doc_id in train_ids]
    
    test_ids = sorted(test_docs_dict.keys())
    test_docs = [test_docs_dict[doc_id] for doc_id in test_ids]
    test_labels = [test_labels_dict[doc_id] for doc_id in test_ids]
    
    print("Number of training documents:", len(train_docs))
    print("Number of testing documents:", len(test_docs))
    print("Vocabulary size:", V)
    
    # Train the Naïve Bayes classifier on the training data.
    # This computes both the class priors and the conditional probabilities for each word given a class.
    class_priors, cond_probs = train_naive_bayes(train_docs, train_labels, V)
    
    # Evaluate the classifier on the training set.
    train_accuracy = evaluate(train_docs, train_labels, class_priors, cond_probs, V)
    # Evaluate the classifier on the testing set.
    test_accuracy = evaluate(test_docs, test_labels, class_priors, cond_probs, V)
    
    print("Training Accuracy: {:.2f}%".format(train_accuracy))
    print("Testing Accuracy: {:.2f}%".format(test_accuracy))
    
    # ---------------- Discriminative Word Features ----------------
    # Explanation:
    # Each word's discriminative power is measured by the absolute difference between log P(word|label1)
    # and log P(word|label2). A large difference implies that the word is much more indicative of one
    # class than the other. Here, we compute this difference for every word in the vocabulary,
    # sort them in descending order, and then print the top 10.
    print_top_discriminative_words(cond_probs, vocab, V, top_n=10)

if __name__ == "__main__":
    main()
