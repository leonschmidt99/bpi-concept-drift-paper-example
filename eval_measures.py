#!/usr/bin/env python3
import csv
import json
import sys
import threading
import matplotlib.pyplot as plt

from statistics import mean

from scipy.stats import ks_2samp

from constants import LETTERS

READ_KS_FROM_JSON = False

ks_count = 0

LINE_UP = '\033[1A'
LINE_DOWN = '\033[1B'
LINE_CLEAR = '\x1b[2K'


def sudden_drift_detect(pop_size: int, n_threads: int) -> None:
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
    if READ_KS_FROM_JSON:
        print("Reading KS results from json...")
        with open('data/ks_test_results.json', 'r') as f:
            json_pair_ks_map = json.load(f)
            pair_ks_map = {
                tuple(int(a.strip()) for a in pair.strip().replace('(', '').replace(')', '').split(',')): json_pair_ks_map[pair]
                for pair in json_pair_ks_map
            }
    else:
        print("Calculating KS results and writing to json...")
        if n_threads == 1:
            pair_ks_map = {
                pair: ks_test(pair_j_map[pair], pop_size, len(pair_j_map))
                for pair in pair_j_map
            }
        else:
            pair_ks_map = {}
            threads = []
            print(f"Spawning up to {n_threads} threads to perform {len(pair_j_map)} tests...")
            print("(one extra thread may be created if #tests % #threads != 0)")
            print("This may take a while...")
            all_pairs = [pair for pair in pair_j_map]
            step_size = len(all_pairs) // n_threads
            for i in range(0, len(all_pairs), step_size):
                thread_pairs = all_pairs[i:i+step_size]
                print(f"Thread {len(threads)}: 0/{len(thread_pairs)}")
                t = threading.Thread(target=ks_test_thread, args=(len(threads), n_threads, thread_pairs, pair_j_map, pair_ks_map, pop_size))
                threads.append(t)

            for i in range(n_threads):
                threads[i].start()

            for i in range(n_threads):
                threads[i].join()

        with open('data/ks_test_results.json', 'w') as f:
            json.dump({str(k): v for k, v in pair_ks_map.items()}, f, indent=4)

    # Step 3
    print("Step 3: Taking average and plotting...")
    fig, ax = plt.subplots()
    num_traces = len(pair_j_map[LETTERS[0], LETTERS[0]])
    num_stats = len(pair_ks_map[LETTERS[0], LETTERS[0]])

    x_data = [i for i in range(num_traces)]
    side_pad = [1 for _ in range(pop_size - 1)]
    y_data = side_pad + [1] + [
        mean([pair_ks_map[pair][i] for pair in pair_ks_map])
        for i in range(num_stats)
    ] + side_pad

    ax.plot(x_data, y_data)
    ax.set(xlabel='Trace Index', ylabel='p-value', title='Sudden Drift Detection')
    ax.grid()

    fig.savefig('data/sudden_drift_detect.png')
    plt.show()


def ks_test(j_measures: list, pop_size: int, total: int = 0, mt: bool = False) -> list:
    if total > 0 and not mt:  # only do debug printing when total is specified
        global ks_count
        ks_count += 1
        print(f"KS test {ks_count}/{total}", end='\r')
    i = pop_size
    ks_tests = []
    while i+pop_size <= len(j_measures):
        # only need p value, not the test statistic
        ks_tests.append(ks_2samp(j_measures[i-pop_size:i], j_measures[i:i+pop_size])[1])
        i += 1
    return ks_tests


def ks_test_thread(id: int, n_threads: int, pairs: list, pair_j_map: dict, pair_ks_map: dict, pop_size: int) -> None:
    for i, pair in enumerate(pairs):
        pair_ks_map[pair] = ks_test(pair_j_map[pair], pop_size)
        print(LINE_UP * (n_threads - id), end=LINE_CLEAR)
        print(f"Thread {id}: {i+1}/{len(pairs)} pairs")
        print(LINE_DOWN * (n_threads - id), end=LINE_CLEAR)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Using default population size of 400.")
        pop_size = 400
    else:
        pop_size = int(sys.argv[1])

    if len(sys.argv) < 3:
        print("Using default number of threads 1.")
        n_threads = 1
    else:
        n_threads = int(sys.argv[2])
    sudden_drift_detect(pop_size, n_threads)
