import heapq
from collections import defaultdict, Counter
import math
import copy
import matplotlib.pyplot as plt

def read_words(filename):
    with open (filename, "r") as f:
        words = f.read().splitlines()
    return words
read_words("datasets/p1/words.txt")