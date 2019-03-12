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

from collections import Counter
from argparse import ArgumentParser, FileType


def parse_patterns_file(patterns_file, runs):
    patterns = [Counter() for i in range(runs)]

    with patterns_file as file:
        reader = csv.DictReader(file, delimiter=' ')

        for row in reader:
            for i in range(runs):
                patterns[i][row['canonical_label']] = int(row['count_%d' % (i + 1)])

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

    if len(sampled_patterns) == 0:
        return int(len(exact_patterns) == 0)

    return len(exact_patterns & sampled_patterns) / float(len(sampled_patterns))


def recall(exact_patterns, sampled_patterns):
    exact_patterns = set(exact_patterns)
    sampled_patterns = set(sampled_patterns)

    if len(exact_patterns) == 0:
        return int(len(sampled_patterns) == 0)

    return len(exact_patterns & sampled_patterns) / float(len(exact_patterns))


def avg_relative_error(exact_patterns, sampled_patterns, T_k):
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

    parser.add_argument('T_k',
        type=int,
        help="number of unique subgraph patterns")

    parser.add_argument('-t', '--tau',
        type=float,
        default=0.001,
        help="coefficient to multiply frequency thresholds (default 0.001)")

    parser.add_argument('-r', '--runs',
        type=int,
        default=5,
        help="number of runs provided for reservoir sampling (default 5)")

    args = vars(parser.parse_args())

    T_k = args['T_k']
    runs = args['runs']
    tau_coefficient = args['tau']

    exact_pattern_counts = parse_patterns_file(args['exact_patterns_file'], 1)[0]
    exact_pattern_freqs = pattern_frequencies(exact_pattern_counts)

    sampled_pattern_counts = parse_patterns_file(args['sampled_patterns_file'], runs)
    sampled_pattern_freqs = [pattern_frequencies(c) for c in sampled_pattern_counts]

    for threshold in [0.001, 0.01, 0.1, 0.2, 1, 2, 10]:
        tau = threshold * tau_coefficient
        print("\nThreshold", tau)

        exact_patterns = threshold_frequencies(exact_pattern_freqs, tau)

        are = 0
        prec = 0
        rec = 0

        for pattern_freqs in sampled_pattern_freqs:
            sampled_patterns = threshold_frequencies(pattern_freqs, tau)

            are += avg_relative_error(exact_patterns, sampled_patterns, T_k)
            prec += precision(exact_patterns, sampled_patterns)
            rec += recall(exact_patterns, sampled_patterns)

        print("ARE      :", are / float(runs))
        print("precision:", prec / float(runs))
        print("recall   :", rec / float(runs))


if __name__ == '__main__':
    main()
