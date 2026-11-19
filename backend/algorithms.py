"""
DSA2-P065: Keyword Search Analyzer - Core String-Matching Algorithms
--------------------------------------------------------------------
Algorithms Implemented:
1. Aho-Corasick Automaton (Optimal Multi-Pattern Search)
   - Data Structure: Prefix Tree (Trie) + Failure Links (BFS) + Output Links
   - Time Complexity:  O(N + M + Z)
       N = length of target text
       M = sum of lengths of all patterns
       Z = total number of pattern occurrences
   - Space Complexity: O(M * Σ) where Σ is the alphabet size

2. Knuth-Morris-Pratt (KMP) Multi-Pattern Baseline (For Comparison)
   - Data Structure: Longest Proper Prefix which is also Suffix (LPS) Table
   - Time Complexity:  O(K * N + M) where K is the number of unique patterns
   - Space Complexity: O(max_pattern_length)
"""

from collections import deque
import time
from typing import List, Dict, Any


class TrieNode:
    """Represents a single state in the Aho-Corasick Automaton."""
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.fail: 'TrieNode' = None
        self.output: List[str] = []


class AhoCorasickAutomaton:
    """
    Encapsulates the Aho-Corasick state machine for simultaneous
    multi-pattern string matching in a single linear pass.
    """
    def __init__(self):
        self.root = TrieNode()
        self.node_count = 1
        self.build_comparisons = 0

    def insert_pattern(self, pattern: str) -> None:
        """Inserts a single pattern into the Trie."""
        current = self.root
        for char in pattern:
            self.build_comparisons += 1
            if char not in current.children:
                current.children[char] = TrieNode()
                self.node_count += 1
            current = current.children[char]
        if pattern not in current.output:
            current.output.append(pattern)

    def build_failure_links(self) -> None:
        """
        Constructs failure transitions and dictionary suffix links using
        Breadth-First Search (BFS) so mismatches fall back in O(1) amortized time.
        """
        queue = deque()

        # Depth-1 nodes always fail back to the root
        for char, child in self.root.children.items():
            child.fail = self.root
            queue.append(child)

        # Traverse level-by-level to wire deeper failure links
        while queue:
            current_node = queue.popleft()

            for char, child_node in current_node.children.items():
                queue.append(child_node)

                # Follow parent's failure chain until a matching transition is found
                fallback = current_node.fail
                while fallback is not None and char not in fallback.children:
                    self.build_comparisons += 1
                    fallback = fallback.fail

                if fallback is not None and char in fallback.children:
                    self.build_comparisons += 1
                    child_node.fail = fallback.children[char]
                else:
                    child_node.fail = self.root

                # Inherit output patterns from the failure state (Output Links)
                child_node.output.extend(child_node.fail.output)

    def search(self, text: str) -> Dict[str, Any]:
        """Scans the input text in one pass and returns all match positions."""
        search_comparisons = 0
        matches = []
        current_node = self.root

        for index, char in enumerate(text):
            # Follow failure links on character mismatch
            while current_node is not None and char not in current_node.children:
                search_comparisons += 1
                current_node = current_node.fail

            search_comparisons += 1
            if current_node is not None and char in current_node.children:
                current_node = current_node.children[char]
            else:
                current_node = self.root

            # Record all patterns ending at this index
            for matched_pattern in current_node.output:
                start_idx = index - len(matched_pattern) + 1
                matches.append({
                    "pattern": matched_pattern,
                    "start": start_idx,
                    "end": index + 1
                })

        return {
            "matches": matches,
            "search_comparisons": search_comparisons
        }


def run_aho_corasick(text: str, patterns: List[str]) -> Dict[str, Any]:
    """Executes Aho-Corasick and returns match results + performance metrics."""
    clean_patterns = list({p for p in patterns if p})
    
    t_start = time.perf_counter()
    automaton = AhoCorasickAutomaton()
    for pat in clean_patterns:
        automaton.insert_pattern(pat)
    automaton.build_failure_links()
    t_build = time.perf_counter()

    search_res = automaton.search(text)
    t_end = time.perf_counter()

    matches = sorted(search_res["matches"], key=lambda m: (m["start"], m["end"]))
    total_comparisons = automaton.build_comparisons + search_res["search_comparisons"]

    return {
        "algorithm": "Aho-Corasick Automaton",
        "time_complexity": "O(N + M + Z)",
        "build_time_ms": round((t_build - t_start) * 1000, 4),
        "search_time_ms": round((t_end - t_build) * 1000, 4),
        "total_time_ms": round((t_end - t_start) * 1000, 4),
        "comparisons": total_comparisons,
        "memory_units": automaton.node_count,  # Total Trie nodes allocated
        "total_matches": len(matches),
        "matches": matches
    }


def _compute_lps_array(pattern: str) -> tuple[List[int], int]:
    """Helper for KMP: builds the Longest Proper Prefix-Suffix (LPS) table."""
    m = len(pattern)
    lps = [0] * m
    comparisons = 0
    length = 0
    i = 1

    while i < m:
        comparisons += 1
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        elif length != 0:
            length = lps[length - 1]
        else:
            lps[i] = 0
            i += 1

    return lps, comparisons


def run_kmp_multi(text: str, patterns: List[str]) -> Dict[str, Any]:
    """
    Executes KMP sequentially for each pattern to benchmark against Aho-Corasick.
    """
    clean_patterns = list({p for p in patterns if p})
    n = len(text)
    matches = []
    build_comparisons = 0
    search_comparisons = 0
    max_lps_size = 0

    t_start = time.perf_counter()

    for pat in clean_patterns:
        m = len(pat)
        max_lps_size = max(max_lps_size, m)
        lps, b_comp = _compute_lps_array(pat)
        build_comparisons += b_comp

        i = 0  # index for text
        j = 0  # index for pattern
        while i < n:
            search_comparisons += 1
            if pat[j] == text[i]:
                i += 1
                j += 1

            if j == m:
                matches.append({
                    "pattern": pat,
                    "start": i - j,
                    "end": i
                })
                j = lps[j - 1]
            elif i < n and pat[j] != text[i]:
                if j != 0:
                    j = lps[j - 1]
                else:
                    i += 1

    t_end = time.perf_counter()
    matches.sort(key=lambda m: (m["start"], m["end"]))

    return {
        "algorithm": "KMP (Multi-Pass)",
        "time_complexity": "O(K·N + M)",
        "build_time_ms": 0.0,  # Interleaved per pattern
        "search_time_ms": round((t_end - t_start) * 1000, 4),
        "total_time_ms": round((t_end - t_start) * 1000, 4),
        "comparisons": build_comparisons + search_comparisons,
        "memory_units": max_lps_size,  # Auxiliary LPS array size
        "total_matches": len(matches),
        "matches": matches
    }