import math
from collections import defaultdict

# Functions to load data
def load_data(data_file_name,label_file):
    docs = defaultdict(set)
    with open(data_file_name,'r') as data_file:
        for line in data_file:
            parts = line.strip().split()
            if len(parts) != 2:
                continue
            doc_id,word_id = int(parts[0]), int(parts[1])
            docs[doc_id].add(word_id)
    labels = {}
    with open(label_file,'r') as label_file:
        for idx,line in  enumerate(label_file,start=1):
            labels[idx] = int(line.strip())
    return docs,labels

#testing load_data function
#print(load_data('datasets/p1/trainData.txt','datasets/p1/trainLabel.txt'))


def load_words(words_file):
    #mapping word_id to actual word
    word_map = {}
    with open(words_file,'r') as words_file:
        for idx, line in enumerate(words_file,start=1):
            word_map[idx] = line.strip()
    return word_map
#testing load_words function
#print(load_words('datasets/p1/words.txt'))


# Naive Bayes functions

def train_naive_bayes(train_doc,train_labels,V):
    '''
    train naive bayes classifier using max-likelihood estimation
    train_doc: list of sets; each set contains word_ids present in that document
    train_labels: list of integer labels (1 or 2)
    V: int; size of vocabulary
    '''
    num_docs = len(train_doc)
    class_count = [0,0] # idx 0 for label 1 , idx 1 for label 2
    #Create a matrix to coount how many documents in each class contains each word
    # used V+1 s that word_id i corresponds to index i, and we ignore index 0
    word_counts = [[0]*(V+1) for i in range(2)]

    #count documents per class and word occurences in each class
    for i in range(num_docs):
        label = train_labels[i]
        class_index = label -1 #convert label (1 or 2) to index (0 or 1)
        class_count[class_index] += 1
        for word_id in train_doc[i]:
            if 1 <= word_id <= V:
                word_counts[class_index][word_id] += 1 # increment count of word_id in class
    
    #compute class priors using the fraction  of documents that belong to each class
    class_priors = [count/num_docs for count in class_count]

    #compute conditional probs with Laplace smoothing
    cond_probs = [[0]*(V+1) for i in range(2)]
    for Class in range(2):
        for word_id in range(1,V+1):
            cond_probs[Class][word_id] = (word_counts[Class][word_id] + 1)/(class_count[Class] + V)
    return class_priors, cond_probs

# predict function
def compute_log_prob(doc, class_priors, cond_probs,V):
    '''
    doc: set of word_ids present in the document
    class_priors: list of class priors
    cond_probs: list of conditional probabilities
    '''
    log_probs = [0,0]
    for Class in range(2):
        log_prob = math.log(class_priors[Class])
        total = 0.0
        # sum the contributions of each word not in the document
        for word_id in range(1,V+1):
            total += math.log(1-cond_probs[Class][word_id])
        log_prob += total
        # adjust score for each word present in the document
        for word_id in doc:
            if 1 <= word_id <= V:
                log_prob += math.log(cond_probs[Class][word_id]/(1-cond_probs[Class][word_id]))
        log_probs[Class] = log_prob
    return log_probs

def classify(doc, class_priors,cond_probs,V):
    '''
    classify a doc by computing the log scores for each class and choosing the class with the higher score
    '''
    scores= compute_log_prob(doc,class_priors,cond_probs,V)
    # if the log score for class 1 is higher than class 2, return 1, else return 2
    if scores[0] > scores[1]:
        return 1
    else:
        return 2
    
def evaluate_acc(test_doc,test_labels,class_priors,cond_probs,V):
    '''
    evaluate classifier's accuracy i.e ((TP+TN)/N)
    '''
    correct = 0
    total = len(test_doc)
    for i in range(total):
        pred = classify(test_doc[i],class_priors,cond_probs,V)
        if pred == test_labels[i]:
            correct += 1
    return correct/total

def main():
    # load data
    train_docs_dict, train_labels_dict = load_data('datasets/p1/trainData.txt','datasets/p1/trainLabel.txt')
    test_docs_dict, test_labels_dict = load_data('datasets/p1/testData.txt','datasets/p1/testLabel.txt')
    # load vocabulary to determine size of vocabulary i.e V
    vocab = load_words('datasets/p1/words.txt')
    V = len(vocab)

    # convert dictionaries to lists (sorted by doc_id) so that each doc and its label are aligned
    train_ids = sorted(train_docs_dict.keys())
    train_docs = [train_docs_dict[doc_id] for doc_id in train_ids]
    train_labels = [train_labels_dict[doc_id] for doc_id in train_ids]

    test_ids = sorted(test_docs_dict.keys())
    test_docs = [test_docs_dict[doc_id] for doc_id in test_ids]
    test_labels = [test_labels_dict[doc_id] for doc_id in test_ids]

    print("Number of training documents:", len(train_docs))
    print("Number of testing documents:", len(test_docs))
    print("Vocabulary size:", V)

    # Train naive bayes classifier on training set
    class_priors, cond_probs = train_naive_bayes(train_docs, train_labels, V)

    #eval classifier on training set
    train_acc = evaluate_acc(train_docs,train_labels,class_priors,cond_probs,V)

    #eval classifier on test set
    test_acc = evaluate_acc(test_docs,test_labels,class_priors,cond_probs,V)

    print("Training accuracy:", train_acc)
    print("Test accuracy:", test_acc)

if __name__ == '__main__':
    main()  