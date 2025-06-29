# association/Apriori.py

from association.Transaction import Transaction
from association.Rule import Rule
import pandas as pd
from itertools import combinations

class Apriori:
    def __init__(self, transactions: list[Transaction], min_support: float, min_confidence: float):
        self.transactions = transactions
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.rules = set()
        self.frequent_itemsets = []

    def run(self):
        self.frequent_itemsets = self._get_frequent_itemsets()
        self.rules = self._generate_rules()
        return self.rules

    def _calculate_support(self, itemset):
        count = sum(1 for t in self.transactions if itemset.issubset(t.items))
        return count / len(self.transactions)

    def _get_frequent_itemsets(self):
        all_frequent = []
        itemsets = set()

        # Generate 1-itemsets
        for t in self.transactions:
            itemsets.update(t.items)
        L1 = [{i} for i in itemsets]

        k = 1
        current_L = L1
        while current_L:
            valid_L = []
            seen = set()
            for itemset in current_L:
                frozen = frozenset(itemset)
                if frozen in seen:
                    continue
                support = self._calculate_support(frozen)
                if support >= self.min_support:
                    valid_L.append(frozen)
                    seen.add(frozen)

            if not valid_L:
                break
            all_frequent.extend(valid_L)

            # Generate candidates of length k+1
            current_L = [a.union(b) for a in valid_L for b in valid_L if len(a.union(b)) == k + 1]
            k += 1

        return all_frequent

    def _generate_rules(self):
        rules = set()
        for itemset in self.frequent_itemsets:
            if len(itemset) < 2:
                continue
            for i in range(1, len(itemset)):
                for antecedent in combinations(itemset, i):
                    antecedent = frozenset(antecedent)
                    consequent = itemset - antecedent
                    if not consequent:
                        continue
                    sup = self._calculate_support(itemset)
                    conf = sup / self._calculate_support(antecedent)
                    lift = conf / self._calculate_support(consequent)
                    if conf >= self.min_confidence:
                        rules.add(Rule(antecedent, consequent, sup, conf, lift))
        return rules
