"""
Calculate the accuracy of sampled subgraph pattern frequencies.

A command-line tool that takes the discovered subgraph patterns
from exact counting and reservoir sampling runs on a graph and
compares their frequencies.

The resulting Precision, Recall and Average Relative Error values
reflect how accurately the reservoir sampling scheme maintains
the distribution of different subgraph patterns when compared
to the exact counting scheme.
"""

import csv
import math
import pprint

from argparse import ArgumentParser, FileType


def parse_patterns_file(patterns_file):
    with patterns_file as file:
        reader = csv.DictReader(file, delimiter=' ')
        patterns = {row['canonical_label']: int(row['count']) for row in reader}

    return patterns


def pattern_frequencies(pattern_counts):
    """Calculate the relative frequency of each pattern."""
    N = float(sum(pattern_counts.values()))
    return {ptrn: count / N for ptrn, count in pattern_counts.items()}


def threshold_frequencies(pattern_freqs, tau):
    """Filter for pattern frequencies where freq >= τ."""
    return {ptrn: freq for ptrn, freq in pattern_freqs.items() if freq >= tau}


def precision(exact_patterns, sampled_patterns):
    exact_patterns = set(exact_patterns)
    sampled_patterns = set(sampled_patterns)

    return len(exact_patterns & sampled_patterns) / float(len(sampled_patterns))


def recall(exact_patterns, sampled_patterns):
    exact_patterns = set(exact_patterns)
    sampled_patterns = set(sampled_patterns)

    return len(exact_patterns & sampled_patterns) / float(len(exact_patterns))


def average_relative_error(exact_patterns, sampled_patterns, T_k):
    are = 0

    for pattern in exact_patterns:
        p_i = exact_patterns[pattern]
        q_i = sampled_patterns[pattern] if pattern in sampled_patterns else 0

        are += abs(q_i - p_i) / p_i

    return are / float(T_k)


def main():
    parser = ArgumentParser(description="Calculate accuracy of FSM sampling runs.")

    parser.add_argument('exact_patterns_file',
        type=FileType('r'),
        help="path to the file that contains exact counting patterns")

    parser.add_argument('sampled_patterns_file',
        type=FileType('r'),
        help="path to the file that contains reservoir sampling patterns")

    args = vars(parser.parse_args())

    exact_pattern_counts = parse_patterns_file(args['exact_patterns_file'])
    exact_pattern_freqs = pattern_frequencies(exact_pattern_counts)

    sampled_pattern_counts = parse_patterns_file(args['sampled_patterns_file'])
    sampled_pattern_freqs = pattern_frequencies(sampled_pattern_counts)

    for threshold in [0.2, 0.4, 0.7, 0.9, 1.0, 1.3]:
        tau = threshold * 0.001
        print("\nThreshold", threshold)

        exact_patterns = threshold_frequencies(exact_pattern_freqs, tau)
        sampled_patterns = threshold_frequencies(sampled_pattern_freqs, tau)

        print("ARE      :", average_relative_error(exact_patterns, sampled_patterns, 611))
        print("precision:", precision(exact_patterns, sampled_patterns))
        print("recall   :", recall(exact_patterns, sampled_patterns))


if __name__ == '__main__':
    main()
