from pyhpo.similarity.base import SimScore, SimilarityBase
from typing import List
import pyhpo

class CustomJaccardIC(SimilarityBase):
    def __call__(
        self,
        term1: 'pyhpo.HPOTerm',
        term2: 'pyhpo.HPOTerm',
        kind: str,
        dependencies: List[float]
    ) -> float:

        if term1 == term2:
            return 1.0

        common = sum([
            x.information_content[kind] for x in
            term1.common_ancestors(term2)
        ])
        union = sum([
            x.information_content[kind] for x in
            (term1.all_parents | term2.all_parents)
        ])
        if term1 in term2.all_parents and term2 in term1.all_parents:
            union +=0
        elif term1 in term2.all_parents:
            union += term2.information_content[kind]
        elif term2 in term1.all_parents:
            union+= term1.information_content[kind]
        else:
            union += (term1.information_content[kind] + term2.information_content[kind])
        try:
            return common/union
        except ZeroDivisionError:
            return 0.0
SimScore.register('custom_jaccardIC', CustomJaccardIC)