import gzip
import pickle
from typing import List, Dict, OrderedDict, Tuple

import numpy as np


def cosine_similarity(a: List[float], b: List[float]) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


class BookEmbedding:

    def __init__(self, emb_path):
        with gzip.open(emb_path, 'rb') as f:
            self.asin2emb = pickle.load(f)

        self.n = len(self.asin2emb)
        self.dim = len(list(self.asin2emb.values())[0])
        print(f'Book embeddings loaded successfully: N = {self.n}, dim = {self.dim}')

    def __getitem__(self, asin: str) -> List[float]:
        """
        Get the embedding vectors of a book from the Amazon Standard Identification Number (ASIN).
        Args:
            asin: Amazon Standard Identification Number (ASIN)

        Returns:
            A list of float that represents the embedding vector.
        """
        return self.asin2emb[asin]
        # return self.asin2emb.get(asin, None) # use this line to set default if asin doesn't exist

    def _get_scores(self, unseen: str, saved: List[str]) -> List[float]:
        """
        Calculate the cosine similarity scores for (unseen, saved) pairs.
        But Why cosine similarity? Tl;DR: frequency will impact the length of the embedding vectors.
        Ref: https://stackoverflow.com/questions/38423387/why-does-word2vec-use-cosine-similarity

        Args:
            unseen: a single Amazon Standard Identification Number (ASIN)
            saved: the list of ASIN the user saved (or liked) before

        Returns:
            cosine similarity scores for (unseen, saved) pairs
        """
        x = self.asin2emb[unseen]
        scores = []
        for asin in saved:
            scores.append(cosine_similarity(self.asin2emb[unseen], self.asin2emb[asin]))

        return scores

    def recommend(self, candidates: List[str], saved: List[str], by: str = 'max') -> List[Tuple]:
        """
        Recommend book(s) based on user's saved list.
        Args:
            candidates: the list of ASINs of candidate books
            saved: the list of ASINs the user saved (or liked) before
            by: sorted by what kind of summary scores? 'max', 'avg', etc.

        Returns:

        """
        out = {}
        for unseen in candidates:
            scores = self._get_scores(unseen, saved)
            out[unseen] = {'max': max(scores),
                           'most_similar_in_saved': saved[scores.index(max(scores))],
                           'avg': sum(scores) / len(scores),
                           'raw': scores}

        return sorted(list(out.items()), key=lambda x: -x[1][by])

