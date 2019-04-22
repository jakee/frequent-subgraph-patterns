import os
import csv
import time
import uuid

import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime, timedelta
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
from algorithms.fsm.dynamic.optimized_reservoir import DynamicOptimizedReservoirAlgorithm

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
        'optimal': DynamicOptimizedReservoirAlgorithm
    }

}


def run_simulation(simulators, edges, T_k, window_size=0):
    ms = timedelta(microseconds=1)

    np.random.shuffle(edges)

    accuracy_metrics = defaultdict(lambda: defaultdict(list))
    performance_metrics = defaultdict(list)

    if window_size > 0:
        sliding_window = deque()

    start_time = time.time()

    for idx, edge_to_add in enumerate(edges):

        edge_to_remove = None

        if window_size > 0:
            sliding_window.append(edge_to_add)

            if len(sliding_window) > window_size:
                    edge_to_remove = sliding_window.popleft()


        for algorithm in ['exact', 'naive', 'optimal']:

            edge_op_start = datetime.now()

            simulators[algorithm].add_edge(edge_to_add)

            if edge_to_remove != None:
                simulators[algorithm].remove_edge(edge_to_remove)

            edge_op_end = datetime.now()

            performance_metrics[algorithm].append((edge_op_end - edge_op_start) / ms)


        if idx % ACCURACY_SAMPLE_INTERVAL == 0:
            exact_patterns = +simulators['exact'].patterns
            exact_freqs = pattern_frequencies(exact_patterns)
            exact_t_freqs = threshold_frequencies(exact_freqs, 0.005)

            for algo_type in ['naive', 'optimal']:

                algo_patterns = +simulators[algo_type].patterns
                algo_freqs = pattern_frequencies(algo_patterns)
                algo_t_freqs = threshold_frequencies(algo_freqs, 0.005)

                prec = precision(exact_t_freqs, algo_t_freqs)
                rec = recall(exact_t_freqs, algo_t_freqs)
                are = avg_relative_error(exact_t_freqs, algo_t_freqs, T_k)

                accuracy_metrics[algo_type]['precision'].append(prec)
                accuracy_metrics[algo_type]['recall'].append(rec)
                accuracy_metrics[algo_type]['avg_relative_error'].append(are)

    end_time = time.time()

    return end_time - start_time, accuracy_metrics, performance_metrics


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

    parser.add_argument('output_dir',
        help="path to the directory for output files")

    parser.add_argument('reservoir_size',
        type=int,
        help="reservoir size required for naive and optimal algorithms")

    parser.add_argument('T_k',
        type=int,
        help="number of possible k-node subgraph patterns")

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
    output_dir = args['output_dir']
    M = args['reservoir_size']
    T_k = args['T_k']
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
    print("T_k:           ", T_k)
    print("times:         ", times)
    print("window size:   ", window_size)
    print("input graph:   ", in_file.name)
    print("output dir:    ", output_dir, "\n")


    ExactAlgorithm = ALGORITHMS[stream]['exact']
    NaiveAlgorithm = ALGORITHMS[stream]['naive']
    OptimizedAlgorithm = ALGORITHMS[stream]['optimal']


    if window_size and stream != 'dynamic':
        msg = "sliding window is only used with %s stream setting" % (stream)
        raise ValueError(msg)


    # read the input graph from the edge file
    with in_file as edge_file:
        edge_reader = csv.reader(edge_file, delimiter=' ')
        edges = [make_edge(*tuple(int(x) for x in row)) for row in edge_reader]


    # run simulations and collect the duration and metrics from each run
    durations = []
    run_accuracy_metrics = []
    run_performance_metrics = []

    print("SIMULATIONS", "\n")

    for i in range(times):
        print("Running simulation", i + 1, "...")

        simulators = {
            'exact': ExactAlgorithm(k=k),
            'naive': NaiveAlgorithm(k=k, M=M),
            'optimal': OptimizedAlgorithm(k=k, M=M)
        }

        duration, acc_metrics, perf_metrics = run_simulation(simulators, edges, T_k, window_size)

        print("Done, run took", duration, "seconds.", "\n")

        durations.append(duration) 
        run_accuracy_metrics.append(acc_metrics)
        run_performance_metrics.append(perf_metrics)


    avg_duration = np.mean(durations)

    print("Average duration of a run was", avg_duration, "seconds.", "\n")

    ec_edge_op_durations = [x['exact'] for x in run_performance_metrics]
    nrs_edge_op_durations = [x['naive'] for x in run_performance_metrics]
    ors_edge_op_durations = [x['optimal'] for x in run_performance_metrics]

    print("Average edge operation durations")
    print("EC:  %d ms" % (np.mean(ec_edge_op_durations)))
    print("NRS: %d ms" % (np.mean(nrs_edge_op_durations)))
    print("ORS: %d ms" % (np.mean(ors_edge_op_durations)))

    identifier = uuid.uuid4() # unique identifier for files

    print("Plots of performance")

    perf_plot_path = os.path.join(output_dir, "%s_performance_plot.pdf" % (identifier))

    x_values = np.arange(len(ec_edge_op_durations[0]))

    ec_avg_edge_op_durations = np.mean(ec_edge_op_durations, axis=0)
    nrs_avg_edge_op_durations = np.mean(nrs_edge_op_durations, axis=0)
    ors_avg_edge_op_durations = np.mean(ors_edge_op_durations, axis=0)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(x_values, ec_avg_edge_op_durations, label="EC")
    ax.plot(x_values, nrs_avg_edge_op_durations, label="NRS")
    ax.plot(x_values, ors_avg_edge_op_durations, label="ORS")
    ax.legend()
    plt.title("edge op durations, k="+str(k))
    plt.savefig(perf_plot_path)

    print("Saved figure to", perf_plot_path)


    print("Plots of accuracy", "\n")

    for algo_type in ['naive', 'optimal']:
        algo_acc_metrics = [d[algo_type] for d in run_accuracy_metrics]

        avg_precision = np.mean([c['precision'] for c in algo_acc_metrics], axis=0)
        avg_recall = np.mean([c['recall'] for c in algo_acc_metrics], axis=0)
        avg_are = np.mean([c['avg_relative_error'] for c in algo_acc_metrics], axis=0)

        x_values = [ACCURACY_SAMPLE_INTERVAL * i for i in range(1, len(avg_precision) + 1)]

        fig = plt.figure()
        ax = fig.add_subplot(311)

        ax.plot(x_values, avg_precision)
        plt.title("precision")

        ax = fig.add_subplot(312)

        ax.plot(x_values, avg_recall)
        plt.title("recall")

        ax = fig.add_subplot(313)

        ax.plot(x_values, avg_are)
        plt.title("average relative error")

        fig.suptitle('%s fully dynamic algorithm performance' % (algo_type), fontsize=16)

        plt.tight_layout()

        acc_plot_path = os.path.join(output_dir, "%s_%s_vs_ec_accuracy_plot.pdf" % (identifier, algo_type))

        plt.savefig(acc_plot_path)

        print("Saved figure to", acc_plot_path)


if __name__ == '__main__':
    main()
