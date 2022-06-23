#!/usr/bin/env python3
import csv
import sys
import matplotlib.pyplot as plt

from scipy.stats import ks_2samp

from constants import LETTERS


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
    pair_ks_map = {
        pair: ks_test(pair_j_map[pair], pop_size)
        for pair in pair_j_map
    }
    # print(pair_ks_map)

    # Step 3
    fig, ax = plt.subplots()
    num_traces = len(pair_j_map[LETTERS[0], LETTERS[0]])
    



def ks_test(j_measures: list, pop_size: int) -> list:
    i = pop_size
    ks_tests = []
    while i+pop_size <= len(j_measures):
        # only need p value, not the test statistic
        ks_tests.append(ks_2samp(j_measures[i-pop_size:i], j_measures[i:i+pop_size])[1])
        i += 1
    return ks_tests

if __name__ == '__main__':
    sudden_drift_detect(400 if len(sys.argv) < 2 else int(sys.argv[1]))
