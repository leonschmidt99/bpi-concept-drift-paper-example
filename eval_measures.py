#!/usr/bin/env python3
import csv
import json
import matplotlib.pyplot as plt
import multiprocessing
import sys

from statistics import mean
from scipy.stats import ks_2samp

from constants import LETTERS

ks_count = 0

LINE_UP = '\033[1A'
LINE_DOWN = '\033[1B'
LINE_CLEAR = '\x1b[2K'


def sudden_drift_detect(pop_size: int, n_cores: int = None, use_json: bool = False) -> None:
    # only the one that worked best for authors
    """
    1. For each activity pair, generate vector of dimension
    #traces (consisting of the pairs j measures),
    
    2. apply univariate KS test to each vector with 
    population size pop_size

    3. take avg p-value of all activity pairs per trace
    and plot
    """

    # Step 1
    print("Step 1: Generating vectors of j measures...")
    pair_j_map = {}
    with open('data/global_measures.csv', 'r', newline='') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            if (row[0], row[1]) not in pair_j_map:
                pair_j_map[(row[0], row[1])] = [row[-1]]
            else:
                pair_j_map[(row[0], row[1])].append(row[-1])

    # Step 2
    print(f"Step 2: Applying KS test to {len(pair_j_map)} pairs...")
    if use_json:
        print("Reading KS results from json...")
        with open('data/ks_test_results.json', 'r') as f:
            json_pair_ks_map = json.load(f)
            pair_ks_map = {
                tuple(a.strip() for a in pair.strip().replace('(', '').replace(')', '').replace('\'', '').split(',')): json_pair_ks_map[pair]
                for pair in json_pair_ks_map
            }
    else:
        print("Calculating KS results and writing to json...")
        if n_cores == 1:
            pair_ks_map = {
                pair: ks_test(pair_j_map[pair], pop_size, len(pair_j_map))
                for pair in pair_j_map
            }
        else:
            if n_cores:
                print(f"Spawning {n_cores} processes...")
            else:
                print(f"Spawning {multiprocessing.cpu_count()} processes...")
            print("This may take a while...")
            with multiprocessing.Pool(processes=n_cores) as pool:
                pairs_order = list(pair_j_map.keys())
                processes = [pool.apply_async(ks_test, args=(pair_j_map[pair], pop_size)) for pair in pairs_order]
                pair_ks_map = {
                    pair: process.get()
                    for process, pair in zip(processes, pairs_order)
                }

        with open('data/ks_test_results.json', 'w') as f:
            json.dump({str(k): v for k, v in pair_ks_map.items()}, f, indent=4)

    # Step 3
    print("Step 3: Taking average and plotting...")
    num_traces = len(pair_j_map[LETTERS[0], LETTERS[0]])
    num_stats = len(pair_ks_map[LETTERS[0], LETTERS[0]])

    x_data = [i for i in range(num_traces)]
    side_pad = [1 for _ in range(pop_size - 1)]

    selected_pairs = pair_ks_map.keys()
    # selected_pairs = [('J', 'K'), ('K', 'J')]
    y_data = side_pad + [1] + [
        mean([pair_ks_map[pair][i] for pair in selected_pairs])
        for i in range(num_stats)
    ] + side_pad

    fig, ax = plt.subplots()
    ax.plot(x_data, y_data)
    ax.set(xlabel='Trace Index', ylabel='p-value', title='Sudden Drift Detection')
    ax.set_ylim(ymin=0, ymax=1)
    ax.set_xlim(xmin=0, xmax=num_traces)
    ax.grid()

    fig.savefig('data/sudden_drift_detect.png')
    plt.show()


def ks_test(j_measures: list, pop_size: int, total: int = 0) -> list:
    """
    if total > 0 and not mt:  # only do debug printing when total is specified
        global ks_count
        ks_count += 1
        print(f"KS test {ks_count}/{total}", end='\r')
    """
    i = pop_size
    ks_tests = []
    while i+pop_size <= len(j_measures):
        # only need p value, not the test statistic
        ks_tests.append(ks_2samp(j_measures[i-pop_size:i], j_measures[i:i+pop_size])[1])
        i += 1
    return ks_tests


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Using default population size of 400.")
        pop_size = 400
    else:
        pop_size = int(sys.argv[1])
        print("Population size:", pop_size)

    if len(sys.argv) < 3:
        print("Using default number of processes #cores.")
        n_cores = None
    else:
        n_cores = int(sys.argv[2])
        print("Number of processes:", n_cores)

    if len(sys.argv) < 4:
        print("Using default use_json of False.")
        use_json = False
    else:
        use_json = bool(int(sys.argv[3]))
        print("Use json:", use_json)

    sudden_drift_detect(pop_size, n_cores, use_json)
