#!/usr/bin/env python3
import csv

from constants import LETTERS


def gen_relationship_matrix() -> list:
    with open('data/log.txt', 'r') as f:
        lines = [line.strip() for line in f.readlines()]
    matrix = []
    for i in LETTERS:
        row = []
        for j in LETTERS:
            row.append(analyze_follows_relationship(lines, i, j))
            # print(f"{i} {row[-1]} {j}")
        matrix.append(row)
    with open('data/relationship_matrix.csv', 'w', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerows(matrix)
    return matrix


def analyze_follows_relationship(lines: list, i: str, j: str) -> str:
    # "j Always/Sometimes/Never follows i"
    count_follows = 0
    count_no_follows = 0
    for line in lines:
        rightmost_index = line.find(i)  # like authors intended?
        # rightmost_index = line.rfind(i)  # strict definition
        if rightmost_index == -1:
            continue  # no statement possible
        if j in line[rightmost_index + 1:]:
            count_follows += 1
        else:
            count_no_follows += 1
    if count_follows != 0 and count_no_follows != 0:
        return 'S'
    if count_follows > 0:  # and count_no_follows == 0
        return 'A'
    # count_no_follows > 0 and count_follows == 0
    return 'N'


if __name__ == '__main__':
    gen_relationship_matrix()
