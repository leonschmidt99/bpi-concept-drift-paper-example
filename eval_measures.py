#!/usr/bin/env python3
import csv
import sys
import matplotlib.pyplot as plt

from statistics import mean

from scipy.stats import ks_2samp

from constants import LETTERS


ks_count = 0


def sudden_drift_detect(pop_size: int) -> None:
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
    pair_j_map = dict()
    with open('data/global_measures.csv', 'r', newline='') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            if (row[0], row[1]) not in pair_j_map:
                pair_j_map[(row[0], row[1])] = [row[-1]]
            else:
                pair_j_map[(row[0], row[1])].append(row[-1])
    # print(pair_j_map)

    # Step 2
    print(f"Step 2: Applying KS test to {len(pair_j_map)} pairs...")
    pair_ks_map = {
        pair: ks_test(pair_j_map[pair], pop_size, len(pair_j_map))
        for pair in pair_j_map
    }
    print()
    # print(pair_ks_map)

    # Step 3
    print("Step 3: Taking average and plotting...")
    fig, ax = plt.subplots()
    num_traces = len(pair_j_map[LETTERS[0], LETTERS[0]])
    num_stats = len(pair_ks_map[LETTERS[0], LETTERS[0]])

    x_data = [i for i in range(num_traces)]
    side_pad = [1 for _ in range(pop_size - 1)]
    y_data = side_pad + [
        mean([pair_ks_map[pair][i] for pair in pair_ks_map])
        for i in range(num_stats)
    ] + side_pad

    ax.plot(x_data, y_data)
    ax.set(xlabel='Trace Index', ylabel='p-value', title='Sudden Drift Detection')
    ax.grid()

    fig.savefig('data/sudden_drift_detect.png')
    plt.show()


def ks_test(j_measures: list, pop_size: int, total: int = 0) -> list:
    if total > 0:  # only do debug printing when total is specified
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

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Using default population size of 400.")
        pop_size = 400
    else:
        pop_size = int(sys.argv[1])
    sudden_drift_detect(pop_size)
