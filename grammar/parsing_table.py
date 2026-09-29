"""
parsing_table.py - Table generator for LL(1) Predictive Parsing.
Constructs M[NonTerminal, Terminal] from FIRST and FOLLOW sets.
Detects and reports any LL(1) conflicts (FIRST/FIRST or FIRST/FOLLOW conflicts).
"""

from typing import Dict, List, Optional, Tuple, Set
from grammar.grammar import Grammar, Production, EPSILON, EOF_SYMBOL
from grammar.first_follow import FirstFollowCalculator

class ParsingTable:
    def __init__(self, grammar: Grammar, calculator: Optional[FirstFollowCalculator] = None):
        self.grammar = grammar
        self.calculator = calculator or FirstFollowCalculator(grammar)
        # Table map: (NonTerminal, Terminal) -> List[Production]
        self.table: Dict[Tuple[str, str], List[Production]] = {}
        self.conflicts: List[str] = []
        self._build_table()

    def _build_table(self) -> None:
        """
        Populates the LL(1) parsing table using the standard algorithm:
        For each production A -> α:
          1. For each terminal 'a' in FIRST(α) (a != ε):
             Add A -> α to M[A, a].
          2. If ε is in FIRST(α):
             For each terminal 'b' in FOLLOW(A) (including $):
               Add A -> α to M[A, b].
        """
        for prod in self.grammar.productions:
            lhs = prod.lhs
            rhs = prod.rhs
            first_alpha = self.calculator.first_of_sequence(rhs)

            # Rule 1
            for terminal in first_alpha:
                if terminal != EPSILON:
                    self._add_entry(lhs, terminal, prod)

            # Rule 2
            if EPSILON in first_alpha:
                for b in self.calculator.follow[lhs]:
                    self._add_entry(lhs, b, prod)

    def _add_entry(self, nt: str, term: str, prod: Production) -> None:
        key = (nt, term)
        if key not in self.table:
            self.table[key] = []
        
        # Conflict detection: If cell already has a different production
        if prod not in self.table[key]:
            if len(self.table[key]) > 0:
                existing = self.table[key][0]
                conflict_msg = (
                    f"LL(1) conflict detected at M[{nt}, {term}]:\n"
                    f"  Existing: {existing}\n"
                    f"  New:      {prod}"
                )
                self.conflicts.append(conflict_msg)
            self.table[key].append(prod)

    def is_ll1(self) -> bool:
        """Returns True if there are zero conflicts in the parsing table."""
        return len(self.conflicts) == 0

    def get_entry(self, non_terminal: str, terminal: str) -> Optional[Production]:
        """Look up the predictive production for (non_terminal, terminal)."""
        entries = self.table.get((non_terminal, terminal))
        if entries:
            return entries[0]
        return None

    def get_expected_terminals(self, non_terminal: str) -> List[str]:
        """Returns the list of terminals that have a valid entry for this non-terminal."""
        expected = []
        for (nt, term) in self.table.keys():
            if nt == non_terminal:
                expected.append(term)
        return sorted(expected)

    def to_dict_grid(self) -> Tuple[List[str], List[str], Dict[str, Dict[str, str]]]:
        """Returns row labels (NTs), column labels (Terminals), and 2D grid representation."""
        all_terminals = sorted(list(self.grammar.terminals)) + [EOF_SYMBOL]
        all_non_terminals = sorted(list(self.grammar.non_terminals))

        grid: Dict[str, Dict[str, str]] = {}
        for nt in all_non_terminals:
            grid[nt] = {}
            for t in all_terminals:
                prods = self.table.get((nt, t), [])
                if prods:
                    grid[nt][t] = " / ".join([str(p) for p in prods])
                else:
                    grid[nt][t] = ""

        return all_non_terminals, all_terminals, grid

    def format_table(self) -> str:
        """Formats the parsing table as a clean text grid."""
        nts, terms, grid = self.to_dict_grid()
        lines = ["=== LL(1) PARSING TABLE ==="]
        if not self.is_ll1():
            lines.append("WARNING: Conflicts found!")
            for c in self.conflicts:
                lines.append(f"  * {c}")
        else:
            lines.append("Status: Strictly LL(1) with 0 conflicts.")

        lines.append("")
        for nt in nts:
            valid_entries = []
            for t in terms:
                if grid[nt][t]:
                    valid_entries.append(f"{t}: {grid[nt][t]}")
            if valid_entries:
                lines.append(f"[{nt}]:")
                for entry in valid_entries:
                    lines.append(f"    {entry}")
        return "\n".join(lines)
