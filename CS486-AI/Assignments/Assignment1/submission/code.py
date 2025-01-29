"""Implementation of Problem 2, Assignment 1, CS486, Fall 2024.

Please replace 'pass  #(TODO) complete this function' with your own
implementation. Please do not change other parts of the code, including the
function signatures; however, feel free to add imports.
"""
import model
import math
import heapq

def decode(model: model.LanguageModel, k: int = 2, n: int = 3) -> str:
    """Lowest-cost-first search with frontier size limit.

    Args:
        model: A language model.
        k: the frontier size limit. Default is 2.
        n: the length of the desired sentence. Default is 3.

    Returns:
        The decoded text, where words are separated by a single space.

    Hints:
        1. model.vocab() gives you the vocabulary.
        2. model.prob(w: str, c: List[str]) gives you the probability of word
           w given previous context c.
    """
    
    frontier = [] # create a priority queue

    heapq.heappush(frontier, (0, [])) # (cost, sentence)

    while frontier: 
        # pop the lowest cost prefix
        cost, prefix = heapq.heappop(frontier)

        # if the prefix is of length n, return it
        if len(prefix) == n:
            return ' '.join(prefix)
        elif len(prefix) < n:
            for w in model.vocab():
                p = model.prob(w, prefix)
                # avoid log(0)
                if p > 0:
                    new_cost = cost - math.log(p)
                    new_prefix = prefix + [w]
                    heapq.heappush(frontier, (new_cost, new_prefix))
            # if frontier exceed size k, prune the highest cost states
            if len(frontier) > k:
                all_states = []
                while frontier:
                    all_states.append(heapq.heappop(frontier)) # all_states will be sorted in ascending order
                best_k = all_states[:k]
                for state in best_k:
                    heapq.heappush(frontier, state)
    return ''
                




if __name__ == '__main__':
    m = model.LanguageModel()
    if decode(m, 2, 3) == 'a dog barks' and decode(m, 1, 3) == 'a cat meows':
        print('success!')
    else:
        print('There might be something wrong with your implementation; please double check.')
