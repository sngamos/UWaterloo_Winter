from typing import List
import random
import numpy as np


class LanguageModel:
    def __init__(self, index: int = 0):
        random.seed(index)
        np.random.seed(index)
        self._vocab = ['a', 'b', 'c', 'd', 'e']
        self._probs = np.random.rand(len(self._vocab), len(self._vocab))
        self._probs = self._probs / np.sum(self._probs, axis=1)[:, None]
        self._prob_vocab = np.random.rand(len(self._vocab))
        self._prob_vocab = self._prob_vocab / np.sum(self._prob_vocab)

    def vocab(self) -> List[str]:
        return self._vocab

    def prob(self, w: str, c: List[str]) -> float:
        if len(c) == 0:
            return self._prob_vocab[self._vocab.index(w)]
        return self._probs[self._vocab.index(c[-1]), self._vocab.index(w)]


if __name__ == '__main__':
    lm = LanguageModel()
    print(lm._vocab)
    print(lm._probs)
    from IPython import embed; embed(using=False)


'''
class LanguageModel:
    def __init__(self, index: int = 0):
        if index == 0:
            self._vocab = ['a', 'cat', 'meows', 'stretches', 'dog', 'barks']
            self._probs = {
                ('a', ''): 1,
                ('cat', 'a'): 0.6,
                ('meows', 'a cat'): 0.55,
                ('stretches', 'a cat'): 0.45,
                ('dog', 'a'): 0.4,
                ('barks', 'a dog'): 0.9,
                ('meows', 'a dog'): 0.05,
                ('stretches', 'a dog'): 0.05
            }
        else:
            pass

    def vocab(self) -> List[str]:
        """Returns the vocabulary of the language model."""
        return self._vocab

    def prob(self, w: str, c: List[str]) -> float:
        """Returns the probability of word w given previous context c.

        Args:
            w: The word.
            c: The previous context.

        Returns:
            The probability of word w given previous context c.
        """
        return self._probs.get((w, ' '.join(c)), 0.0)
'''
