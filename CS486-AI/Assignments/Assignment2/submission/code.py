import heapq
from collections import defaultdict, Counter
import math
import copy
import matplotlib.pyplot as plt

def entropy(class_counts):
    # compute the entropy given the dict of class counts
    total = sum(class_counts.values())
    if total == 0:
        return 1.0
    else:
        entropy =0.0
        for count in class_counts.values():
            if count > 0:
                p = count/total
                entropy -= p*math.log2(p)
    return entropy

def majority_class(doc_ids,labels):
    # return the majority class label among given doc_ids
    if not doc_ids:
        print("ERROR: please input doc_ids")
        return None
    count = Counter([labels[doc] for doc in doc_ids])
    return count.most_common(1)[0][0]
    

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
##print(load_data('/Users/amos/Library/CloudStorage/OneDrive-SingaporeUniversityofTechnologyandDesign/Documents/6.UW/CS486-AI/Assignments/Assignment2/dataset/trainData.txt','/Users/amos/Library/CloudStorage/OneDrive-SingaporeUniversityofTechnologyandDesign/Documents/6.UW/CS486-AI/Assignments/Assignment2/dataset/trainLabel.txt')[0])

def load_words(words_file):
    #mapping word_id to actual word
    word_map = {}
    with open(words_file,'r') as words_file:
        for idx, line in enumerate(words_file,start=1):
            word_map[idx] = line.strip()
    return word_map
#testing load_words function
#print(load_words('/Users/amos/Library/CloudStorage/OneDrive-SingaporeUniversityofTechnologyandDesign/Documents/6.UW/CS486-AI/Assignments/Assignment2/dataset/words.txt'))

# --- Decision Tree Node Class ---
class DecisionTreeNode:
    def __init__(self,doc_ids,used_features=None):
        self.doc_ids = doc_ids
        self.used_features = used_features if used_features is not None else set()
        self.is_leaf = True
        self.predicted_class = None
        self.split_feature = None
        self.left = None
        self.right = None
        self.information_gain = 0.0
    
    def compute_prediction(self,labels):
        self.predicted_class = majority_class(self.doc_ids,labels)

class CandidateSplit:
    def __init__(self, node, split_feature, info_gain, left_doc_ids, right_doc_ids):
        self.node = node
        self.split_feature = split_feature
        self.info_gain = info_gain
        self.left_doc_ids = left_doc_ids
        self.right_doc_ids = right_doc_ids
    
    def __lt__(self, other):
        return self.info_gain > other.info_gain
    
# --- Tree Building Functions---

def best_split_for_node(node,docs,labels,mode):
    # for given node, search over all candidate features, return candidate split (CandidateSplit obj) that max info_gain
    # mode: average or weighted
    best_candidate = None
    # count class freq in this node
    count_total = Counter([labels[doc] for doc in node.doc_ids])
    N = len(node.doc_ids)
    I_E  = entropy(count_total)

    # gather all candidate features that occur in at least one doc in this node
    feature_counts = defaultdict(lambda: [set(),set()]) # feature -> [docs with feature, docs without feature]
    for doc in node.doc_ids:
        for feature in docs[doc]:
            if feature in node.used_features:
                continue
            feature_counts[feature][0].add(doc)
    #considering features that do not appear in some docs
    for feature in list(feature_counts.keys()):
        docs_with = feature_counts[feature][0]
        docs_without = set(node.doc_ids) - docs_with
        feature_counts[feature][1] = docs_without
    # try each candidate feature
    for feature, (docs_with,docs_without) in feature_counts.items():
        N1 = len(docs_with)
        N2 = len(docs_without)
        # skip trivial splits
        if N1 == 0 or N2 == 0:
            continue
        count_left = Counter([labels[doc] for doc in docs_with])
        count_right = Counter([labels[doc] for doc in docs_without])
        I_left = entropy(count_left)
        I_right = entropy(count_right)
        if mode == 'average':
            info_gain = I_E - 0.5*(I_left+I_right)
        elif mode == 'weighted':
            info_gain = I_E - (N1/N)*I_left - (N2/N)*I_right
        else:
            raise ValueError("Unknown mode: %s" % mode)
        if (best_candidate is None) or (info_gain > best_candidate.info_gain):
            best_candidate = CandidateSplit(node, feature, info_gain, docs_with, docs_without)

    return best_candidate


def build_tree_iter(train_docs,train_labels,mode,max_interval_nodes=100):
    # innit the tree with root lead containing all training nodes
    root = DecisionTreeNode(list(train_docs.keys()))
    root.compute_prediction(train_labels)

    #priority queue: each candidate split is stored, use negative info_gain so that highest info_gain comes out first, include counter to break ties
    heap = []
    counter =0
    candidate = best_split_for_node(root,train_docs,train_labels,mode)
    if candidate is not None:
        heapq.heappush(heap, (-candidate.info_gain, counter, candidate))
        counter +=1
    
    internal_nodes =0
    # for recording accuracy evaluation
    train_acc_list =[]
    # update test accuracy externally below

    #tree structure updated in-place
    while internal_nodes < max_interval_nodes and heap:
        # pop candidate with highest info_gain
        neg_ig, _, cand = heap.heappop(heap)
        # if candidate info_gain is not positive, we stop early
        if -1*neg_ig <= 0:
            break
        # perform split on cand.node using cand.split_feature
        parent = cand.node
        parent.is_leaf = False
        parent.split_feature = cand.split_feature
        parent.information_gain = cand.info_gain
        # update used features along the branch, children inherit parent's used features plus split feature
        used_feats = copy.deepcopy(parent.used_features)
        used_feats.add(cand.split_feature)
        #create left and right children nodes
        left_node = DecisionTreeNode(list(cand.left_doc_ids), used_feats)
        right_node = DecisionTreeNode(list(cand.right_doc_ids), used_feats)
        left_node.compute_prediction(train_labels)
        right_node.compute_prediction(train_labels)
        parent.left = left_node
        parent.right = right_node
        internal_nodes +=1

        #compute candidate splits and push into priority queue for each new leaf
        for child in [left_node,right_node]:
            cand_child = best_split_for_node(child,train_docs,train_labels,mode)
            if cand_child is not None:
                heapq.heappush(heap,(-1*cand_child.info_gain, counter, cand_child))
        
    return root

# --- Tree evaluation ---
def traverse_tree(doc,root,docs):
    #traverse the tree from the root to a leaf
    # if the document contains the node's split_feature, go left, else go right
    node = root
    while not node.is_leaf:
        feat = node.split_feature
        if feat in docs[doc]:
            node = node.left
        else:
            node = node.right
    return node.predicted_class

def eval_tree(root, docs,labels):
    # eval tree's accuracy given docs and labels
    correct = 0
    total = len(docs)
    for doc in docs:
        pred = traverse_tree(doc,root,docs)
        if pred == labels[doc]:
            correct+=1
    return (correct/total)*100

# ---print tree function ---
def print_tree(node, words_map=None, indent=0):
    prefix = " " * indent
    if node.is_leaf:
        print(f"{prefix}Leaf: Predict = {node.predicted_class}")
    else:
        # If a words_map is provided, convert the feature id to its corresponding word.
        feat_str = node.split_feature if words_map is None else words_map.get(node.split_feature, f"ID:{node.split_feature}")
        print(f"{prefix}Internal Node: Feature = {feat_str}, IG = {node.information_gain:.4f}")
        print(f"{prefix}  Left:")
        print_tree(node.left, words_map, indent + 4)
        print(f"{prefix}  Right:")
        print_tree(node.right, words_map, indent + 4)

# --- main function ---

def run_main(trainDataFile, trainLabelFile, testDataFile,testLabelFile, mode, max_internal_nodes=100):
    # 1.load data
    train_docs, train_labels = load_data(trainDataFile,trainLabelFile)
    test_docs, test_labels = load_data(testDataFile,testLabelFile)

    # 2. build tree, record accuracy after each internal node is added
    train_acc_list = []
    test_acc_list = []

    #building tree iteratively. build tree and record the predictions after each split
    root = DecisionTreeNode(list(train_docs.keys()))
    root.compute_prediction(train_labels)

    #priority queue for canidate splits
    heap = []
    counter =0
    candidate = best_split_for_node(root,train_docs,train_labels,mode)
    if candidate is not None:
        heapq.heappush(heap, (-candidate.info_gain, counter, candidate))
        counter +=1
    internal_nodes =0
    # record initial accuracy (0 split)
    train_acc_list.append(eval_tree(root,train_docs,train_labels))
    test_acc_list.append(eval_tree(root,test_docs,test_labels))
    while internal_nodes < max_internal_nodes and heap: 
        neg_info_gain, _, cand = heapq.heappop(heap)
        if -1*neg_info_gain <= 0:
            break
        #expand candidate node
        parent = cand.node
        parent.is_leaf = False
        parent.split_feature = cand.split_feature
        parent.information_gain = cand.info_gain
        used_feats = copy.deepcopy(parent.used_features)
        used_feats.add(cand.split_feature)
        left_node = DecisionTreeNode(list(cand.left_doc_ids), used_feats)
        right_node = DecisionTreeNode(list(cand.right_doc_ids), used_feats)
        left_node.compute_prediction(train_labels)
        right_node.compute_prediction(train_labels)
        parent.left = left_node
        parent.right = right_node
        internal_nodes+=1

        #for each new leaf, add new candidate splits
        for child in [left_node,right_node]:
            candidate_child = best_split_for_node(child,train_docs,train_labels,mode)
            if candidate_child is not None:
                heapq.heappush(heap, (-1*candidate_child.info_gain, counter, candidate_child))
                counter +=1

        #after adding a new node, evaluate accuracy on training and test data
        train_acc = eval_tree(root,train_docs,train_labels)
        test_acc = eval_tree(root,test_docs,test_labels)
        train_acc_list.append(train_acc)
        test_acc_list.append(test_acc)
        print(f"Nodes: {internal_nodes}, Train Acc: {train_acc:.2f}%, Test Acc: {test_acc:.2f}%")

    #printing tree
    #print("\nfinal tree structure:")
    #print_tree(root)
    return train_acc_list, test_acc_list

# --- plotting function ---

def plot_accuracies(train_acc,test_acc,mode):
    plt.figure(figsize=(8,6))
    x = list(range(len(train_acc)))
    plt.plot(x,train_acc,label='Training Accuracy')
    plt.plot(x,test_acc,label='Test Accuracy')
    plt.xlabel('Number of Internal Nodes')
    plt.ylabel('Accuracy (%)')
    plt.title(f'Decision Tree Accuracy ({mode.capitalize()} Info Gain)')
    plt.legend()
    plt.grid(True)
    plt.show()

# --- main function ---

if __name__ == '__main__':
    # names of files 
    trainDataFile = 'dataset/trainData.txt'
    trainLabelFile = 'dataset/trainLabel.txt' 
    testDataFile = 'dataset/testData.txt'
    testLabelFile = 'dataset/testLabel.txt'

    modes = ['average','weighted']
    results = {}
    for mode in modes:
        print(f"\nRunning experiment using mode : {mode}")
        train_acc, test_acc = run_main(trainDataFile, trainLabelFile, testDataFile, testLabelFile, mode)
        results[mode] = (train_acc, test_acc)
        plot_accuracies(train_acc,test_acc,mode)
