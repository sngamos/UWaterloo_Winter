import math
import heapq
import copy

#paths to datasets
trainData = 'dataset/trainData.txt'
trainLabel = 'dataset/trainLabel.txt'
testData = 'dataset/testData.txt'
testLabel = 'dataset/testLabel.txt'
wordMap = 'dataset/words.txt'

'''
structure of data:
train/testData.txt: each line is <docID> <wordID>: tells you a certain <wordID> is in <docID>
train/testLabel.txt: each line is <#line> <label (1 or 2)>: each #line is a docID, the value at the #line (1/2) represents which subreddit the document belongs to
words.txt: each line is <#line> <word string>: each #line is a wordID, the string at each #line is the word corresponding to the wordID 
'''

#load/parse data, returns 2 dicts, docs and labels, where docs maps docID to a list of wordIDs, and labels maps docID to a label

def loadData(data_file,label_file):
    docs = {}
    with open(data_file,'r') as file:
        for line in file:
            docID,wordID = map(int,line.strip().split())
            if docID not in docs: #create new docID if key has not been seen before
                docs[docID] = [] 
            docs[docID].append(wordID)
    labels = {}
    with open(label_file,'r') as file:
        for index, line in enumerate(file):
            labels[index] = int(line.strip()) #maps docID to label
    return docs,labels


# entropy calculation function

def get_entropy(class_counts):
    total = sum(class_counts.values())
    if total ==0:
        return 1.0 # max uncertainty when no data is present
    ent = 0.0
    for count in class_counts.values():
        if count >0:
            p =  count/total #probability of class, no. of instances of class/total instances
            ent -= p*math.log2(p) #entropy formula
    return ent

# majority class determination function, finds the most common label in data set

def majority_class(docIDs,labels):
    class_counts = {} #create empty dict for each class to count occurrences
    for docID in docIDs: #go thru each docID
        label = labels[docID] #get label for docID
        if label not in class_counts: #create new key if label has not been seen before
            class_counts[label] = 0
        class_counts[label] += 1 #increment count for label
    max_count = 0 
    majority_class = None
    for label,count in class_counts.items(): 
        if count > max_count: #find label with highest count
            max_count = count #update max count
            majority_class = label #update majority class
    return majority_class

# decision tree node class
'''
Each node has:
- list of docIDs in that node
- set of features (word IDs) that have been used in the path to that node from root
- flag to indicate if node is a leaf
- the predicted class (majority class) if node is a leaf
- feature used to split at that node if node is not a leaf
- left and right children nodes
'''

class DecisionTreeNode:
    def __init__(self,docIDs,used_features=None): 
        self.docIDs = docIDs
        self.used_features = used_features if used_features is not None else set()
        self.leaf = True
        self.predicted_class = None
        self.feature = None
        self.left = None
        self.right = None
    #function to assign majority class to leaf node
    def compute_prediction(self,labels):
        self.predicted_class = majority_class(self.docIDs,labels)

class CandidateSplit:
    def __init__(self,node, split_feature,info_gain, left_docIDs,right_docIDs):
        self.node = node
        self.split_feature = split_feature
        self.info_gain = info_gain
        self.left_docIDs = left_docIDs
        self.right_docIDs = right_docIDs



# identify best feature to split on
def best_split_for_node(node,docs,labels,mode):
    '''
    1. count class frequencies in current node, then compute entropy
    2. for each candidate feature not in node.used_features,
        a. determine the docIDs that have the feature and those that don't
        b. compute entropy of left and right splits
        c. calculate information gain IG based o mode (avg or weighted)
    '''
    class_counts = {}
    for docID in node.docIDs:
        label = labels[docID]
        if label not in class_counts:
            class_counts[label] = 0
        class_counts[label] += 1
    entropy = get_entropy(class_counts)
    best_candidate = None
    best_IG = -1 #initialize best information gain
    # determine candidate features by collecting all word IDs in the node's docIDs
    candidate_features = set()
    for docID in node.docIDs:
        candidate_features.update(docs[docID])
    # remove features that have already been used
    candidate_features -= node.used_features
    # for each candidate feature, compute information gain
    for feature in candidate_features:
        #split docIDs into left and right based on if they contain the feature
        left_docIDs = [docID for docID in node.docIDs if feature in docs[docID]]
        right_docIDs = [docID for docID in node.docIDs if feature not in docs[docID]]
        #skip trivial splits
        if len(left_docIDs) == 0 or len(right_docIDs) == 0:
            continue
        #compute class distribution for left and right splits
        left_counts = {}
        for docID in left_docIDs:
            label = labels[docID]
            if label not in left_counts:
                left_counts[label] = 0
            left_counts[label] += 1
        right_counts = {}
        for docID in right_docIDs:
            label = labels[docID]
            if label not in right_counts:
                right_counts[label] = 0
            right_counts[label] += 1
        #compute entropy of left and right splits
        left_entropy = get_entropy(left_counts)
        right_entropy = get_entropy(right_counts)

        #compute information gain
        if mode == 'average':
            info_gain = entropy - 0.5 * (left_entropy + right_entropy)
        elif mode == 'weighted':
            info_gain = entropy - (len(left_docIDs)/len(node.docIDs))*left_entropy - (len(right_docIDs)/len(node.docIDs))*right_entropy
        else:
            raise ValueError('mode must be either average or weighted')
        
        if info_gain > best_IG:
            best_IG = info_gain
            best_candidate = feature
            best_left = left_docIDs
            best_right = right_docIDs
    
    if best_candidate is None:
        return None
    
    return CandidateSplit(node,best_candidate,best_IG,best_left,best_right)

# build tree iteratively using priority queue
def build_tree_iterative(train_docs,train_labels,mode,max_internal_nodes = 100):
    root = DecisionTreeNode(list(train_docs.keys())) #init root node with all docIDs from dataset
    root.compute_prediction(train_labels) #assign majority class to root node
    heap = [] #priority queue to store candidate splits
    counter = 0 #counter to keep track of internal nodes
    candidate = best_split_for_node(root,train_docs,train_labels,mode) #find best split for root node
    if candidate is not None:
        heapq.heappush(heap,(-candidate.info_gain,counter,candidate)) #push candidate split to heap, use negative info gain to get max value
    internal_nodes =0
    while internal_nodes<max_internal_nodes and heap:
        neg_ig, _,cand = heapq.heappop(heap)
        if -neg_ig <=0: 
            break #stop if no more positive information gain

        #expand candidate's node with the best features
        parent = cand.node
        parent.leaf = False
        parent.split_feature = cand.split_feature

        #update set of features used in path to this node
        used_features = copy.deepcopy(parent.used_features)
        used_features.add(cand.split_feature)

        # create left and right children nodes
        left_node = DecisionTreeNode(list(cand.left_docIDs),used_features)
        right_node = Decision = DecisionTreeNode(list(cand.right_docIDs),used_features)

        #compute majority class for left and right nodes
        left_node.compute_prediction(train_labels)
        right_node.compute_prediction(train_labels)

        #link children to parent
        parent.left = left_node
        parent.right = right_node

        internal_nodes += 1

        for child in [left_node,right_node]:
            candidate_child = best_split_for_node(child,train_docs,train_labels,mode)
            if candidate_child is not None:
                heapq.heappush(heap,(-candidate_child.info_gain,counter,candidate_child))
                counter += 1
    return root

# predict function
def traverse_tree(doc,root,docs):
    if root.leaf:
        return root.predicted_class
    if doc[root.split_feature] in docs:
        return traverse_tree(doc,root.left,docs)
    else:
        return traverse_tree(doc,root.right,docs)
        