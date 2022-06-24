#!/usr/bin/env python3
import csv
import random
import sys

from constants import ACTIVITIES, LETTERS


VARIANTS = 3


def gen_log(n: int) -> None:
    with open('data/log.txt', 'w') as f:
        for var in range(VARIANTS):
            for _ in range(n):
                f.write(''.join(gen_trace(var)) + '\n')


def gen_trace(var: int = 0) -> list:
    # Step 1: setup
    trace = ["A", "B", "C"]

    # 5% chance of "not fulfilled"
    if random.random() <= 0.05:
        trace.append("D")
        return trace

    # Step 2: pre-screening
    trace.append("E")
    nexts = ["F", "G"]
    if var == 0:
        trace.append(random.choice(nexts))  # XOR 50/50
    else:
        random.shuffle(nexts)
        trace.extend(nexts)
    trace.append("H")

    # Step 3: basic live interviews
    # 10% chance of "poor", 80% chance of "good", 10% chance of "excellent"
    next_step = random.random()
    if next_step <= 0.1:
        trace.append("D")
        return trace
    elif next_step <= 0.9:
        trace.append("I")

        # AND with 50/50 for which comes first
        nexts = ["J", "K"]
        if var == 0 or var == 1:
            random.shuffle(nexts)
        trace.extend(nexts)

        trace.append("L")

        # 5% of "poor"
        if random.random() <= 0.05:
            trace.append("D")
            return trace
    
    # Step 4: advanced live interviews
    trace.append("M")
    nexts = ["O", "N"]
    if var == 0 or var == 1:
        random.shuffle(nexts)
    trace.extend(nexts)
    trace.append("P")

    # 5% chance of "poor"
    if random.random() <= 0.05:
        trace.append("D")
        return trace
    
    trace.extend(["Q", "R"])
    return trace


def write_activity_mapping() -> None:
    mapping = zip(LETTERS, ACTIVITIES)
    with open('data/activity_mapping.csv', 'w', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Activity', 'Mapping'])
        writer.writerows(mapping)


if __name__ == '__main__':
    write_activity_mapping()
    gen_log(10 if len(sys.argv) == 1 else int(sys.argv[1]))
