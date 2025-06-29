class Rule:
    def __init__(self, antecedent, consequent, support, confidence, lift):
        self.antecedent = frozenset(antecedent)
        self.consequent = frozenset(consequent)
        self.support = support
        self.confidence = confidence
        self.lift = lift

    def __eq__(self, other):
        return (self.antecedent == other.antecedent and
                self.consequent == other.consequent)

    def __hash__(self):
        return hash((self.antecedent, self.consequent))

    def __repr__(self):
        return (f"{set(self.antecedent)} → {set(self.consequent)} "
                f"(support={self.support:.2f}, confidence={self.confidence:.2f}, lift={self.lift:.2f})")
