"""
first_follow.py - Programmatic computation of FIRST and FOLLOW sets for any CFG.
Handles epsilon (ε) transitions and computes fixed-point closure without hardcoding.
"""

from typing import Dict, Set, Tuple
from grammar.grammar import Grammar, Production, EPSILON, EOF_SYMBOL

class FirstFollowCalculator:
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.first: Dict[str, Set[str]] = {nt: set() for nt in self.grammar.non_terminals}
        self.follow: Dict[str, Set[str]] = {nt: set() for nt in self.grammar.non_terminals}
        self._compute_first()
        self._compute_follow()

    def _compute_first(self) -> None:
        """
        Computes FIRST sets for all non-terminals iteratively until convergence.
        Rules:
        1. If X is a terminal, FIRST(X) = {X}.
        2. If A -> ε is a production, then add ε to FIRST(A).
        3. If A -> Y1 Y2 ... Yk is a production:
           - Add all non-ε symbols of FIRST(Y1) to FIRST(A).
           - If Y1 derives ε, add non-ε symbols of FIRST(Y2), and so on.
           - If all Y1...Yk derive ε, then add ε to FIRST(A).
        """
        changed = True
        while changed:
            changed = False
            for prod in self.grammar.productions:
                lhs = prod.lhs
                rhs = prod.rhs

                # Case: A -> ε (empty rhs tuple)
                if not rhs:
                    if EPSILON not in self.first[lhs]:
                        self.first[lhs].add(EPSILON)
                        changed = True
                    continue

                # Case: A -> Y1 Y2 ... Yk
                all_have_epsilon = True
                for symbol in rhs:
                    if self.grammar.is_terminal(symbol):
                        if symbol not in self.first[lhs]:
                            self.first[lhs].add(symbol)
                            changed = True
                        all_have_epsilon = False
                        break
                    else:
                        # Non-terminal
                        before_len = len(self.first[lhs])
                        # Add FIRST(symbol) - {ε}
                        self.first[lhs].update(self.first[symbol] - {EPSILON})
                        if len(self.first[lhs]) > before_len:
                            changed = True

                        if EPSILON not in self.first[symbol]:
                            all_have_epsilon = False
                            break

                if all_have_epsilon:
                    if EPSILON not in self.first[lhs]:
                        self.first[lhs].add(EPSILON)
                        changed = True

    def first_of_sequence(self, sequence: Tuple[str, ...]) -> Set[str]:
        """Computes the FIRST set of a sequence of grammar symbols α = X1 X2 ... Xk."""
        if not sequence:
            return {EPSILON}

        result: Set[str] = set()
        all_have_epsilon = True

        for symbol in sequence:
            if self.grammar.is_terminal(symbol):
                result.add(symbol)
                all_have_epsilon = False
                break
            else:
                result.update(self.first[symbol] - {EPSILON})
                if EPSILON not in self.first[symbol]:
                    all_have_epsilon = False
                    break

        if all_have_epsilon:
            result.add(EPSILON)

        return result

    def _compute_follow(self) -> None:
        """
        Computes FOLLOW sets for all non-terminals iteratively until convergence.
        Rules:
        1. Place $ in FOLLOW(StartSymbol).
        2. If there is a production A -> α B β:
           - Everything in FIRST(β) except ε is in FOLLOW(B).
        3. If there is a production A -> α B, or A -> α B β where FIRST(β) contains ε:
           - Everything in FOLLOW(A) is in FOLLOW(B).
        """
        # Rule 1: Start symbol contains EOF ($)
        self.follow[self.grammar.start_symbol].add(EOF_SYMBOL)

        changed = True
        while changed:
            changed = False
            for prod in self.grammar.productions:
                lhs = prod.lhs
                rhs = prod.rhs

                for i, symbol in enumerate(rhs):
                    if self.grammar.is_non_terminal(symbol):
                        beta = rhs[i + 1:]
                        first_beta = self.first_of_sequence(beta)

                        # Rule 2: Add FIRST(β) - {ε} to FOLLOW(symbol)
                        before_len = len(self.follow[symbol])
                        self.follow[symbol].update(first_beta - {EPSILON})

                        # Rule 3: If β is empty or derives ε, add FOLLOW(lhs) to FOLLOW(symbol)
                        if EPSILON in first_beta or not beta:
                            self.follow[symbol].update(self.follow[lhs])

                        if len(self.follow[symbol]) > before_len:
                            changed = True

    def format_sets(self) -> str:
        """Returns a formatted academic summary of FIRST and FOLLOW sets."""
        lines = ["=== FIRST SETS ==="]
        for nt in sorted(self.grammar.non_terminals):
            f_set = sorted(list(self.first[nt]))
            lines.append(f"FIRST({nt:15}) = {{ {', '.join(f_set)} }}")

        lines.append("\n=== FOLLOW SETS ===")
        for nt in sorted(self.grammar.non_terminals):
            fol_set = sorted(list(self.follow[nt]))
            lines.append(f"FOLLOW({nt:15}) = {{ {', '.join(fol_set)} }}")

        return "\n".join(lines)
