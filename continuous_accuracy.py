import os
import csv
import time
import uuid

import numpy as np
import matplotlib.pyplot as plt

from collections import deque, defaultdict
from argparse import ArgumentParser, FileType

from graph.util import make_edge

from util.accuracy import (
    pattern_frequencies,
    threshold_frequencies,
    precision, recall, avg_relative_error
)

from algorithms.fsm.incremental.exact_counting import IncrementalExactCountingAlgorithm
from algorithms.fsm.incremental.naive_reservoir import IncrementalNaiveReservoirAlgorithm
from algorithms.fsm.incremental.optimized_reservoir import IncerementalOptimizedReservoirAlgorithm

from algorithms.fsm.dynamic.exact_counting import DynamicExactCountingAlgorithm
from algorithms.fsm.dynamic.naive_reservoir import DynamicNaiveReservoirAlgorithm

ACCURACY_SAMPLE_INTERVAL = 10

ALGORITHMS = {

    'incremental': {
        'exact': IncrementalExactCountingAlgorithm,
        'naive': IncrementalNaiveReservoirAlgorithm,
        'optimal': IncerementalOptimizedReservoirAlgorithm
    },

    'dynamic': {
        'exact': DynamicExactCountingAlgorithm,
        'naive': DynamicNaiveReservoirAlgorithm,
        'optimal': None
    }

}


def run_simulation(simulators, edges, window_size=0):
    np.random.shuffle(edges)

    accuracy_metrics = defaultdict(list)

    if window_size > 0:
        sliding_window = deque()

    start_time = time.time()

    for idx, edge_to_add in enumerate(edges):
        simulators['exact'].add_edge(edge_to_add)
        simulators['naive'].add_edge(edge_to_add)

        if window_size > 0:
            sliding_window.append(edge_to_add)

            if len(sliding_window) > window_size:
                edge_to_remove = sliding_window.popleft()
                simulators['exact'].remove_edge(edge_to_add)
                simulators['naive'].remove_edge(edge_to_add)

        if idx % ACCURACY_SAMPLE_INTERVAL == 0:
            exact_patterns = +simulators['exact'].patterns
            naive_patterns = +simulators['naive'].patterns

            exact_freqs = pattern_frequencies(exact_patterns)
            naive_freqs = pattern_frequencies(naive_patterns)

            exact_freqs = threshold_frequencies(exact_freqs, 0.005)
            naive_freqs = threshold_frequencies(naive_freqs, 0.005)

            prec = precision(exact_freqs, naive_freqs)
            rec = recall(exact_freqs, naive_freqs)
            are = avg_relative_error(exact_freqs, naive_freqs, 40)

            accuracy_metrics['precision'].append(prec)
            accuracy_metrics['recall'].append(rec)
            accuracy_metrics['avg_relative_error'].append(are)

    end_time = time.time()

    return end_time - start_time, accuracy_metrics


def main():
    parser = ArgumentParser(description="Run a FSM continuous accuracy experiment.")

    parser.add_argument("k",
        type=int,
        help="size of subgraphs (k-nodes) being mined")

    parser.add_argument('stream_setting',
        choices=['incremental', 'dynamic'],
        help="choose between incremental or fully dynamic stream setting")

    '''
    parser.add_argument('algorithm',
        choices=['exact', 'naive', 'optimal'],
        help="choose exact counting, or naive or optimised reservoir sampling")
    '''

    parser.add_argument('edge_file',
        type=FileType('r'),
        help="path to the input graph edge file")

    '''
    parser.add_argument('output_dir',
        help="path to the directory for output files")
    '''

    parser.add_argument('reservoir_size',
        type=int,
        help="reservoir size required for naive and optimal algorithms")

    parser.add_argument('-t', '--times',
        type=int,
        default=10,
        help="number of times the simulation is run in this instance")

    parser.add_argument('-w', '--windowsize',
        dest="window_size",
        type=int,
        help="size of the sliding window (requires dynamic stream setting)")

    args = vars(parser.parse_args())

    k = args['k']
    #algo = args['algorithm']
    stream = args['stream_setting']
    M = args['reservoir_size']
    times = args['times']
    window_size = args['window_size']

    in_file = args['edge_file']
    #output_dir = args['output_dir']

    print("Running the Continuous Accuracy Experiment", "\n")

    print("PARAMETERS")
    print("stream setting:", stream)
    #print("algorithm:     ", algo)
    print("k:             ", k)
    print("M:             ", M)
    print("times:         ", times)
    print("window size:   ", window_size)
    print("input graph:   ", in_file.name, "\n")


    ExactAlgorithm = ALGORITHMS[stream]['exact']
    NaiveAlgorithm = ALGORITHMS[stream]['naive']

    if ExactAlgorithm == None:
        msg = "exact algorithm is not available for %s stream setting" % (stream)
        raise NotImplementedError(msg)

    if NaiveAlgorithm == None:
        msg = "naive algorithm is not available for %s stream setting" % (stream)
        raise NotImplementedError(msg)

    if window_size and stream != 'dynamic':
        msg = "sliding window is only used with %s stream setting" % (stream)
        raise ValueError(msg)


    # read the input graph from the edge file
    with in_file as edge_file:
        edge_reader = csv.reader(edge_file, delimiter=' ')
        edges = [make_edge(*tuple(int(x) for x in row)) for row in edge_reader]


    # run simulations and collect the duration and metrics from each run
    durations = []
    run_metrics = defaultdict(list)
    run_accuracy_metrics = []

    print("SIMULATIONS", "\n")

    for i in range(times):
        print("Running simulation", i + 1, "...")

        simulators = {
            'exact': ExactAlgorithm(k=k),
            'naive': NaiveAlgorithm(k=k, M=M)
        }

        duration, accuracy_metrics = run_simulation(simulators, edges, window_size)

        print("Done, run took", duration, "seconds.", "\n")

        durations.append(duration)
        run_accuracy_metrics.append(accuracy_metrics)


    avg_duration = np.mean(durations)

    print("Average duration of a run was", avg_duration, "seconds.")


    print("Plots of accuracy")

    avg_precision = np.mean(np.asarray([d['precision'] for d in run_accuracy_metrics]), axis=0)
    avg_recall = np.mean(np.asarray([d['recall'] for d in run_accuracy_metrics]), axis=0)
    avg_are = np.mean(np.asarray([d['avg_relative_error'] for d in run_accuracy_metrics]), axis=0)

    edge_add_points = [ACCURACY_SAMPLE_INTERVAL * i for i in range(1, len(avg_precision) + 1)]

    fig = plt.figure()
    ax = fig.add_subplot(311)

    ax.plot(edge_add_points, avg_precision)
    plt.title("precision")

    ax = fig.add_subplot(312)

    ax.plot(edge_add_points, avg_recall)
    plt.title("recall")

    ax = fig.add_subplot(313)

    ax.plot(edge_add_points, avg_are)
    plt.title("average relative error")

    plt.show()


if __name__ == '__main__':
    main()
