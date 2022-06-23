#!/usr/bin/env python3
import csv
import math
import sys

from typing import Generator

from constants import LETTERS

def gen_measures(window: int):
    with open('data/relationship_matrix.csv', 'r', newline='') as f:
        reader = csv.reader(f)
        matrix = [row for row in reader]
    with open('data/local_measures.csv', 'w', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Activity', 'RC', 'RE'])
        writer.writerows(analyze_local_measures(matrix))
    with open('data/global_measures.csv', 'w', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Activity 1', 'Activity 2', 'Trace ID', 'WC', 'J measure'])
        writer.writerows(analyze_global_measures(window))


def analyze_local_measures(matrix: list) -> zip:
    # RC
    rcs = [(row.count('A'), row.count('S'), row.count('N')) for row in matrix]

    # RE
    num_activities = len(matrix[0])
    assert(num_activities > 0)
    res = [
        -(c_a / num_activities) * log2_div_p(c_a, num_activities) \
        -(c_s / num_activities) * log2_div_p(c_s, num_activities) \
        -(c_n / num_activities) * log2_div_p(c_n, num_activities)
        for c_a, c_s, c_n in rcs
    ]
    return zip(LETTERS, rcs, res)


def analyze_global_measures(window: int = 0) -> Generator[tuple, None, None]:
    with open('data/log.txt', 'r') as f:
        traces = [trace.strip() for trace in f.readlines()]
    if window == 0:
        print("No window specified. Using default window of average trace length.")
        window = sum(len(trace) for trace in traces) // len(traces)
    print(f"Window size: {window}")
    for a in LETTERS:
        for b in LETTERS:
            for trace_id, trace in enumerate(traces):
                # WC
                slta = [
                    trace[i:i+window] for i in find_all(trace, a)
                ]
                fltab = [
                    s for s in slta if b in s[1:]
                ]

                # J measure
                pta = trace.count(a) / len(trace)
                ptb = trace.count(b) / len(trace)

                pltab = len(fltab) / len(slta) if len(slta) > 0 else 0
                celtab = pltab * log2_div_p(pltab, ptb) + (1 - pltab) * log2_div_p(1 - pltab, 1 - ptb)

                fltjab = pta * celtab

                yield a, b, trace_id, len(fltab), fltjab


def find_all(a: str, b: str) -> Generator[int, None, None]:
    start = 0
    while True:
        start = a.find(b, start)
        if start == -1:
            return
        yield start
        start += 1


def log2_div_p(a: int, b: int) -> float:
    if a == 0 or b == 0:
        return 0
    return math.log2(a / b)

if __name__ == '__main__':
    gen_measures(0 if len(sys.argv) < 2 else int(sys.argv[1]))
